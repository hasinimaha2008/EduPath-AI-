from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, CareerRole, CareerSkillRequirement, UserSkill, Skill, SkillGap
from app.schemas.schemas import SkillGapResponse, SkillGapItem, CareerRoleResponse

router = APIRouter(prefix="/skills", tags=["Skill Gap Analysis"])

@router.get("/gaps/{career_role_id}", response_model=SkillGapResponse)
async def get_skill_gaps_for_career(
    career_role_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Analyzes skill gaps against target career role, clearly distinguishing
    demonstrated (quiz-verified) skills from self-reported skills and missing skills.
    """
    role_stmt = select(CareerRole).where(CareerRole.id == career_role_id)
    role_res = await session.execute(role_stmt)
    role = role_res.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Career role not found.")

    # Fetch role requirements
    req_stmt = select(CareerSkillRequirement, Skill).join(
        Skill, CareerSkillRequirement.skill_id == Skill.id
    ).where(
        CareerSkillRequirement.career_role_id == role.id
    )
    req_res = await session.execute(req_stmt)
    requirements = req_res.all()

    # Fetch user skills
    us_stmt = select(UserSkill).where(UserSkill.user_id == current_user.id)
    us_res = await session.execute(us_stmt)
    user_skills = {us.skill_id: us for us in us_res.scalars().all()}

    SKILL_RESOURCES_MAP = {
        "SQL Querying": [
            "PostgreSQL Official Documentation (Query Planning & Window Functions)",
            "Database System Concepts (Silberschatz, Korth, Sudarshan)",
            "EduPath Smart Notes: SQL & Relational Queries"
        ],
        "Database Design & Normalization": [
            "Fundamentals of Database Systems (Elmasri & Navathe)",
            "ACM SIGMOD Papers on Relational Normalization",
            "EduPath Smart Notes: Normalization (1NF to BCNF)"
        ],
        "Python Programming": [
            "Fluent Python (Luciano Ramalho - O'Reilly)",
            "Official Python 3.12 Asynchronous I/O Documentation",
            "EduPath Smart Notes: Python Concurrency & Data Model"
        ],
        "Machine Learning & Predictive Modeling": [
            "Pattern Recognition and Machine Learning (Christopher Bishop)",
            "Scikit-Learn Comprehensive User Guide & API Reference",
            "EduPath Smart Notes: Supervised & Unsupervised Learning"
        ],
        "Deep Learning & Transformers": [
            "Deep Learning (Ian Goodfellow, Yoshua Bengio)",
            "Hugging Face Transformers Architecture Documentation",
            "EduPath Smart Notes: Neural Attention & Transformer Architectures"
        ],
        "Cloud Architecture & DevOps": [
            "The Site Reliability Workbook (Betsy Beyer et al. - Google O'Reilly)",
            "Kubernetes Official Production Best Practices & CNCF Specs",
            "EduPath Smart Notes: Container Orchestration & CI/CD"
        ],
        "Cybersecurity & Defensive Controls": [
            "OWASP Top 10 Web Application Security Risks Specification",
            "NIST Cybersecurity Framework (CSF 2.0)",
            "EduPath Smart Notes: Cryptography & Access Control"
        ],
        "Modern React & Web Engineering": [
            "Official React 18 / Next.js 14 Documentation",
            "Web Performance In Action & WCAG 2.2 Standards",
            "EduPath Smart Notes: State Synchronization & Component Lifecycle"
        ]
    }

    SKILL_PROJECTS_MAP = {
        "SQL Querying": [
            "Build an E-Commerce Analytics Dashboard with Window Functions & CTEs",
            "Design Automated Query Profiling Pipeline with EXPLAIN ANALYZE"
        ],
        "Database Design & Normalization": [
            "Architect a Normalized Multi-Tenant SaaS Relational Schema in 3NF",
            "Implement Audit Logging with Foreign Key Cascade & Composite Keys"
        ],
        "Python Programming": [
            "Develop an Async Job Queue Worker Pool with Redis Streams",
            "Build a RESTful API Microservice with Pydantic & FastAPI"
        ],
        "Machine Learning & Predictive Modeling": [
            "Train an Explainable Churn Prediction Pipeline with Scikit-learn",
            "Build Automated Cross-Validation and Hyperparameter Tuning Service"
        ],
        "Deep Learning & Transformers": [
            "Implement a Fine-Tuned Domain QA Transformer with PyTorch",
            "Build a Hybrid RAG Retrieval Engine with Vector Similarity"
        ],
        "Cloud Architecture & DevOps": [
            "Provision a Highly Available Kubernetes Cluster with Terraform",
            "Set up GitOps Automated Delivery with ArgoCD & Prometheus Alerting"
        ],
        "Cybersecurity & Defensive Controls": [
            "Build a Real-Time Packet Sniffer and Vulnerability Scanner with Scapy",
            "Implement Zero-Trust JWT Authentication with Token Rotation"
        ],
        "Modern React & Web Engineering": [
            "Build a Real-Time Collaborative Canvas with WebSockets & React 18",
            "Construct a High-Performance Accessible Design System in Tailwind"
        ]
    }

    gap_items = []
    total_prof = 0.0

    for req, skill in requirements:
        user_skill = user_skills.get(skill.id)
        is_verified = False

        if user_skill:
            prof = user_skill.proficiency_level
            total_prof += min(prof, 100.0)
            status_val = "existing" if prof >= req.min_proficiency else "needs_improvement"
            evidence_source = user_skill.source  # "demonstrated" or "self_reported"
            is_verified = (user_skill.source == "demonstrated")
            priority = "High" if (req.importance_level == "Core" and status_val != "existing") else "Medium"
            rec_text = (
                f"Current {'verified assessment' if is_verified else 'self-reported'} score: {round(prof, 1)}%. Target threshold is {round(req.min_proficiency, 1)}%. "
                f"Complete advanced topic quizzes in {skill.name} to reinforce demonstrated mastery."
            )
        else:
            prof = 0.0
            status_val = "missing"
            evidence_source = "missing"
            priority = "High" if req.importance_level == "Core" else "Low"
            rec_text = f"Begin with fundamental study notes and beginner quizzes covering {skill.name} concepts."

        resources = SKILL_RESOURCES_MAP.get(skill.name, [
            f"Official Standard Documentation for {skill.name}",
            f"ACM / IEEE Curated Textbooks on {skill.name}",
            f"EduPath AI Smart Notes on {skill.name}"
        ])
        suggested_projects = SKILL_PROJECTS_MAP.get(skill.name, [
            f"Hands-on Implementation Project showcasing {skill.name}",
            f"Automated Testing and Benchmarking Suite for {skill.name}"
        ])
        job_market_importance = "Essential Core" if req.importance_level == "Core" else "Industry Recommended"

        gap_items.append(
            SkillGapItem(
                skill_name=skill.name,
                category=skill.category,
                status=status_val,
                priority=priority,
                proficiency=prof,
                evidence_source=evidence_source,
                is_verified=is_verified,
                learning_recommendation=rec_text,
                learning_resources=resources,
                suggested_projects=suggested_projects,
                job_market_importance=job_market_importance
            )
        )

    readiness = round(total_prof / (len(requirements) * 100.0) * 100.0, 1) if requirements else 0.0

    return SkillGapResponse(
        career_role=CareerRoleResponse.model_validate(role),
        overall_readiness=readiness,
        gaps=gap_items
    )
