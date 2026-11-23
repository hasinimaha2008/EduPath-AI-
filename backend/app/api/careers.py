from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import (
    User, CareerRole, CareerRecommendation, CareerSkillRequirement,
    UserSkill, Skill, CareerProject, CareerPathway
)
from app.schemas.schemas import (
    CareerRoleResponse, CareerRecommendationResponse,
    JobDescriptionAnalysisRequest, JobDescriptionAnalysisResponse
)
from app.services.intelligence_engine import intelligence_engine

router = APIRouter(prefix="/careers", tags=["Career Intelligence"])

@router.get("/roles", response_model=List[CareerRoleResponse])
async def list_career_roles(
    session: AsyncSession = Depends(get_db)
):
    stmt = select(CareerRole).order_by(CareerRole.title)
    res = await session.execute(stmt)
    roles = res.scalars().all()
    return [CareerRoleResponse.model_validate(r) for r in roles]

@router.get("/recommendations", response_model=List[CareerRecommendationResponse])
async def get_career_recommendations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns personalized career role recommendations computed by the EduPath Intelligence Engine.
    Explains the objective rationale behind each score without promising employment.
    """
    await intelligence_engine.recalculate_career_intelligence(session, current_user.id)
    await session.commit()

    stmt = select(CareerRecommendation, CareerRole).join(
        CareerRole, CareerRecommendation.career_role_id == CareerRole.id
    ).where(
        CareerRecommendation.user_id == current_user.id
    ).order_by(CareerRecommendation.match_score.desc())

    res = await session.execute(stmt)
    records = res.all()

    # Fetch user skills
    us_stmt = select(UserSkill, Skill).join(Skill, UserSkill.skill_id == Skill.id).where(UserSkill.user_id == current_user.id)
    us_res = await session.execute(us_stmt)
    user_skill_map = {us.skill_id: (us, s.name) for us, s in us_res.all()}

    # Fetch practical projects grouped by role
    proj_stmt = select(CareerProject)
    proj_res = await session.execute(proj_stmt)
    all_projects = proj_res.scalars().all()
    projects_by_role: Dict[str, list] = {}
    for p in all_projects:
        projects_by_role.setdefault(p.career_role_id, []).append({
            "title": p.title,
            "objective": p.objective,
            "difficulty": p.difficulty,
            "tools": p.tools
        })

    output = []
    for rec, role in records:
        req_stmt = select(CareerSkillRequirement, Skill).join(
            Skill, CareerSkillRequirement.skill_id == Skill.id
        ).where(CareerSkillRequirement.career_role_id == role.id)
        req_res = await session.execute(req_stmt)
        reqs = req_res.all()

        matching = []
        missing = []
        tot_w = 0.0
        dem_w = 0.0
        sr_w = 0.0

        for req, sk in reqs:
            mult = 1.5 if req.importance_level == "Core" else 1.0
            tot_w += 100.0 * mult

            if req.skill_id in user_skill_map:
                u_sk, _ = user_skill_map[req.skill_id]
                prof = min(u_sk.proficiency_level, 100.0)
                if u_sk.source == "demonstrated":
                    dem_w += prof * mult
                else:
                    sr_w += prof * mult

                if prof >= req.min_proficiency:
                    tag = " (Verified)" if u_sk.source == "demonstrated" else " (Self-Reported)"
                    matching.append(f"{sk.name}{tag}")
                else:
                    missing.append(f"{sk.name} ({round(prof, 1)}% / {round(req.min_proficiency, 1)}%)")
            else:
                missing.append(sk.name)

        demonstrated_score = round((dem_w / tot_w) * 100.0, 1) if tot_w > 0 else 0.0
        self_reported_score = round(((dem_w + sr_w) / tot_w) * 100.0, 1) if tot_w > 0 else 0.0
        domain = intelligence_engine.ROLE_DOMAINS.get(role.title, "Technology")

        output.append(
            CareerRecommendationResponse(
                id=rec.id,
                career_role=CareerRoleResponse.model_validate(role),
                domain=domain,
                match_score=rec.match_score,
                demonstrated_match_score=demonstrated_score,
                self_reported_match_score=self_reported_score,
                rationale=rec.rationale,
                missing_skills_count=len(missing),
                matching_skills=matching,
                missing_skills=missing,
                recommended_projects=projects_by_role.get(role.id, [])[:3],
                recommended_at=rec.recommended_at
            )
        )

    return output

@router.get("/compare")
async def compare_career_roles(
    role_ids: str = Query(..., description="Comma-separated IDs of 2 or more roles to compare"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Compares 2 or more career roles side-by-side (Upgrade 6):
    - Skill overlap vs role-specific requirements
    - Demonstrated readiness score for each
    - Salary expectations and market demand
    - Evidence breakdown: demonstrated, in-progress, and missing skills
    """
    id_list = [i.strip() for i in role_ids.split(",") if i.strip()]
    if len(id_list) < 2:
        raise HTTPException(status_code=400, detail="Please provide at least 2 role IDs to compare.")

    stmt = select(CareerRole).where(CareerRole.id.in_(id_list))
    res = await session.execute(stmt)
    roles = res.scalars().all()

    if len(roles) < 2:
        raise HTTPException(status_code=404, detail="One or more specified career roles were not found.")

    # Fetch user demonstrated skills
    us_stmt = select(UserSkill, Skill).join(Skill, UserSkill.skill_id == Skill.id).where(UserSkill.user_id == current_user.id)
    us_res = await session.execute(us_stmt)
    user_skill_map = {us.skill_id: (us, s.name) for us, s in us_res.all()}

    # Fetch recommendations for readiness scores
    rec_stmt = select(CareerRecommendation).where(
        CareerRecommendation.user_id == current_user.id,
        CareerRecommendation.career_role_id.in_(id_list)
    )
    rec_res = await session.execute(rec_stmt)
    rec_map = {r.career_role_id: r.match_score for r in rec_res.scalars().all()}

    compared_roles = []
    all_role_skills: Dict[str, set] = {}

    for r in roles:
        req_stmt = select(CareerSkillRequirement, Skill).join(
            Skill, CareerSkillRequirement.skill_id == Skill.id
        ).where(CareerSkillRequirement.career_role_id == r.id)
        req_res = await session.execute(req_stmt)
        reqs = req_res.all()

        demonstrated = []
        in_progress = []
        missing = []
        skill_names = set()

        for req, sk in reqs:
            skill_names.add(sk.name)
            if req.skill_id in user_skill_map:
                u_sk, _ = user_skill_map[req.skill_id]
                if u_sk.proficiency_level >= req.min_proficiency:
                    demonstrated.append({"skill": sk.name, "proficiency": u_sk.proficiency_level, "target": req.min_proficiency})
                else:
                    in_progress.append({"skill": sk.name, "proficiency": u_sk.proficiency_level, "target": req.min_proficiency})
            else:
                missing.append({"skill": sk.name, "proficiency": 0.0, "target": req.min_proficiency})

        all_role_skills[r.id] = skill_names

        compared_roles.append({
            "id": r.id,
            "title": r.title,
            "slug": r.slug,
            "salary_range": r.salary_range,
            "industry_demand": r.industry_demand,
            "icon_name": r.icon_name,
            "readiness_score": rec_map.get(r.id, 0.0),
            "demonstrated_skills": demonstrated,
            "in_progress_skills": in_progress,
            "missing_skills": missing
        })

    # Find shared vs unique skills
    sets = list(all_role_skills.values())
    shared_skills = list(set.intersection(*sets)) if sets else []

    return {
        "compared_roles": compared_roles,
        "shared_skills": shared_skills,
        "comparison_count": len(compared_roles)
    }

@router.get("/{career_id}/projects")
async def get_career_projects(
    career_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Returns practical portfolio project recommendations for a career role (Upgrade 6).
    Each project includes steps, tools, and competency focus.
    """
    stmt = select(CareerProject).where(CareerProject.career_role_id == career_id)
    res = await session.execute(stmt)
    projects = res.scalars().all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "objective": p.objective,
            "difficulty": p.difficulty,
            "required_skills": p.required_skills,
            "tools": p.tools,
            "steps": p.steps,
            "expected_outcome": p.expected_outcome,
            "competency_focus": p.competency_focus
        }
        for p in projects
    ]

@router.get("/{career_id}/pathways")
async def get_career_pathways(
    career_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Returns transition pathways from or to this career role (Upgrade 6).
    """
    stmt = select(CareerPathway, CareerRole).join(
        CareerRole, CareerPathway.to_role_id == CareerRole.id
    ).where(
        CareerPathway.from_role_id == career_id
    )
    res = await session.execute(stmt)
    outbound = [
        {
            "id": pw.id,
            "target_role_id": r.id,
            "target_role_title": r.title,
            "transition_difficulty": pw.transition_difficulty,
            "bridge_skills": pw.bridge_skills,
            "guidance": pw.guidance
        }
        for pw, r in res.all()
    ]

    return {"outbound_pathways": outbound}

@router.post("/analyze-jd", response_model=JobDescriptionAnalysisResponse)
async def analyze_job_description(
    req: JobDescriptionAnalysisRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Job Description Skill Extractor & Competency Gap Analyzer.
    Parses live job description text, extracts required skills, compares against student's
    persisted UserSkill records (differentiating verified demonstrated vs self-reported),
    and recommends portfolio bridge projects and targeted study topics.
    """
    import re
    jd_text = req.job_description_text.strip()
    if not jd_text:
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")

    # 1. Fetch catalog skills from DB to match
    sk_stmt = select(Skill)
    sk_res = await session.execute(sk_stmt)
    all_db_skills = sk_res.scalars().all()
    skill_lookup = {s.name.lower(): s.name for s in all_db_skills}

    # Common CS tech vocabulary dictionary
    taxonomy_skills = [
        "Python", "SQL", "Docker", "Kubernetes", "React", "FastAPI", "TypeScript",
        "JavaScript", "Git", "CI/CD", "PostgreSQL", "MySQL", "MongoDB", "Redis",
        "Linux", "AWS", "Azure", "GCP", "REST APIs", "GraphQL", "Microservices",
        "System Design", "Data Structures", "Algorithms", "Unit Testing", "Java",
        "C++", "Go", "Rust", "Node.js", "Django", "Machine Learning", "PyTorch",
        "TensorFlow", "HTML", "CSS", "Agile", "DevOps"
    ]
    for s_name in taxonomy_skills:
        skill_lookup.setdefault(s_name.lower(), s_name)

    # 2. Extract skills present in JD text
    jd_lower = jd_text.lower()
    extracted_set = set()
    for s_lower, canonical in skill_lookup.items():
        pattern = r'\b' + re.escape(s_lower) + r'\b'
        if re.search(pattern, jd_lower):
            extracted_set.add(canonical)

    # If few skills matched, add fallback heuristic matches
    if len(extracted_set) < 2:
        extracted_set.update(["Python", "SQL", "Git", "REST APIs"])

    extracted_skills = sorted(list(extracted_set))

    # 3. Fetch user skills
    us_stmt = select(UserSkill, Skill).join(Skill, UserSkill.skill_id == Skill.id).where(UserSkill.user_id == current_user.id)
    us_res = await session.execute(us_stmt)
    user_skills_data = us_res.all()

    user_skills_map = {}
    for us, sk in user_skills_data:
        user_skills_map[sk.name.lower()] = {
            "name": sk.name,
            "source": us.source,
            "proficiency": us.proficiency_level
        }

    # 4. Classify skills into verified demonstrated, self-reported, and missing
    verified_dem = []
    self_reported = []
    missing = []

    for sk_name in extracted_skills:
        sk_key = sk_name.lower()
        if sk_key in user_skills_map:
            u_info = user_skills_map[sk_key]
            if u_info["source"] == "demonstrated" and u_info["proficiency"] >= 50.0:
                verified_dem.append(f"{sk_name} ({round(u_info['proficiency'], 1)}% Verified)")
            else:
                self_reported.append(f"{sk_name} (Self-Reported)")
        else:
            missing.append(sk_name)

    # 5. Compute Match Scores
    total_req = len(extracted_skills)
    demonstrated_score = round((len(verified_dem) / total_req) * 100.0, 1) if total_req > 0 else 0.0
    self_reported_score = round((len(self_reported) / total_req) * 100.0, 1) if total_req > 0 else 0.0
    overall_match = round(min(100.0, demonstrated_score + (self_reported_score * 0.7)), 1)

    if overall_match >= 75.0:
        readiness = "Ready for Applications"
    elif overall_match >= 45.0:
        readiness = "Minor Preparation Needed"
    else:
        readiness = "Significant Bridge Needed"

    # 6. Recommends bridge projects and topics for missing skills
    proj_stmt = select(CareerProject).limit(3)
    proj_res = await session.execute(proj_stmt)
    projects = [
        {
            "title": p.title,
            "objective": p.objective,
            "difficulty": p.difficulty,
            "tools": p.tools,
            "focus_skills": missing[:2] if missing else ["Advanced System Architecture"]
        }
        for p in proj_res.scalars().all()
    ]

    recommended_topics = [f"Foundations of {m}" for m in missing[:4]] if missing else ["Advanced Concurrency & Scalability"]

    # 7. Summary Analysis
    summary = (
        f"Analysis for '{req.job_title}': Identified {total_req} core skill competencies from the job description. "
        f"You demonstrate {len(verified_dem)} verified skills and {len(self_reported)} self-reported competencies, "
        f"achieving an overall readiness index of {overall_match}%. "
        f"{'You are well positioned to apply.' if overall_match >= 75 else 'Bridge the identified competency gaps with the recommended projects to strengthen your candidate profile.'}"
    )

    return JobDescriptionAnalysisResponse(
        job_title=req.job_title or "Software Engineer",
        company_name=req.company_name,
        overall_match_percentage=overall_match,
        demonstrated_match_score=demonstrated_score,
        self_reported_match_score=self_reported_score,
        readiness_status=readiness,
        extracted_required_skills=extracted_skills,
        verified_demonstrated_skills=verified_dem,
        self_reported_skills=self_reported,
        missing_skills=missing,
        recommended_bridge_projects=projects,
        recommended_study_topics=recommended_topics,
        summary_analysis=summary
    )
