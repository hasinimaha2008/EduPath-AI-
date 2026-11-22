import asyncio
import json
import logging
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.models import (
    User, CareerRole, Subject, Topic, Skill,
    SubjectSkillMapping, CareerSkillRequirement,
    CareerProject, CareerPathway, LearningProfile, Notification
)
from app.services.seed_data import (
    CAREER_ROLES, SUBJECTS_AND_TOPICS, SKILLS_CATALOG,
    SUBJECT_SKILL_MAPPINGS, CAREER_SKILL_REQUIREMENTS,
    CAREER_PROJECTS, CAREER_PATHWAYS
)

logger = logging.getLogger("edupath.init_db")

async def init_database():
    """
    Initializes database tables and populates the Academic-to-Industry taxonomy seed data
    supporting all 16 subjects, modules, subtopics, and emerging industry technologies.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Safe migration: ensure note_id exists on quizzes table, and study planner columns
        def _check_and_add_columns(connection):
            from sqlalchemy import inspect, text
            insp = inspect(connection)
            quiz_cols = [c["name"] for c in insp.get_columns("quizzes")]
            if "note_id" not in quiz_cols:
                connection.execute(text("ALTER TABLE quizzes ADD COLUMN note_id VARCHAR(36) REFERENCES notes(id)"))

            task_cols = [c["name"] for c in insp.get_columns("study_tasks")]
            if "task_type" not in task_cols:
                connection.execute(text("ALTER TABLE study_tasks ADD COLUMN task_type VARCHAR(50) DEFAULT 'study'"))
            if "difficulty_level" not in task_cols:
                connection.execute(text("ALTER TABLE study_tasks ADD COLUMN difficulty_level VARCHAR(30) DEFAULT 'medium'"))
            if "action_url" not in task_cols:
                connection.execute(text("ALTER TABLE study_tasks ADD COLUMN action_url VARCHAR(255)"))
            if "notes" not in task_cols:
                connection.execute(text("ALTER TABLE study_tasks ADD COLUMN notes TEXT"))

            plan_cols = [c["name"] for c in insp.get_columns("study_plans")]
            if "exam_date" not in plan_cols:
                connection.execute(text("ALTER TABLE study_plans ADD COLUMN exam_date VARCHAR(30)"))
            if "learning_priority" not in plan_cols:
                connection.execute(text("ALTER TABLE study_plans ADD COLUMN learning_priority VARCHAR(50) DEFAULT 'balanced'"))
            if "metadata_json" not in plan_cols:
                connection.execute(text("ALTER TABLE study_plans ADD COLUMN metadata_json TEXT"))
        await conn.run_sync(_check_and_add_columns)
    
    async with AsyncSessionLocal() as session:
        logger.info("Synchronizing Multi-Subject Academic Taxonomy (16 Subjects)...")

        # 1. Career Roles
        role_map = {}
        for r_data in CAREER_ROLES:
            stmt = select(CareerRole).where(CareerRole.title == r_data["title"])
            res = await session.execute(stmt)
            role = res.scalar_one_or_none()
            if not role:
                role = CareerRole(**r_data)
                session.add(role)
                await session.flush()
            role_map[role.title] = role

        # 2. Skills
        skill_map = {}
        for s_data in SKILLS_CATALOG:
            stmt = select(Skill).where(Skill.name == s_data["name"])
            res = await session.execute(stmt)
            skill = res.scalar_one_or_none()
            if not skill:
                skill = Skill(**s_data)
                session.add(skill)
                await session.flush()
            skill_map[skill.name] = skill

        # 3. Career Skill Requirements
        for role_title, req_list in CAREER_SKILL_REQUIREMENTS.items():
            role_obj = role_map.get(role_title)
            if not role_obj:
                continue
            for s_name, importance, min_prof in req_list:
                skill_obj = skill_map.get(s_name)
                if skill_obj:
                    stmt = select(CareerSkillRequirement).where(
                        CareerSkillRequirement.career_role_id == role_obj.id,
                        CareerSkillRequirement.skill_id == skill_obj.id
                    )
                    res = await session.execute(stmt)
                    if not res.scalar_one_or_none():
                        csr = CareerSkillRequirement(
                            career_role_id=role_obj.id,
                            skill_id=skill_obj.id,
                            importance_level=importance,
                            min_proficiency=min_prof
                        )
                        session.add(csr)

        # 4. Subjects & Topics (16 Subjects)
        subject_map = {}
        topic_map = {}

        for sub_data in SUBJECTS_AND_TOPICS:
            if sub_data["name"] == "DBMS":
                stmt = select(Subject).where((Subject.name == "DBMS") | (Subject.name == "Database Management Systems"))
            else:
                stmt = select(Subject).where(Subject.name == sub_data["name"])
            res = await session.execute(stmt)
            subject = res.scalar_one_or_none()

            if not subject:
                subject = Subject(
                    name=sub_data["name"],
                    code=sub_data.get("code"),
                    description=sub_data.get("description"),
                    category=sub_data.get("category", "Computer Science"),
                    icon_name=sub_data.get("icon_name", "BookOpen")
                )
                session.add(subject)
                await session.flush()
            else:
                subject.name = sub_data["name"]
                subject.code = sub_data.get("code", subject.code)
                subject.description = sub_data.get("description", subject.description)
                subject.category = sub_data.get("category", subject.category or "Computer Science")
                subject.icon_name = sub_data.get("icon_name", subject.icon_name or "BookOpen")

            subject_map[subject.name] = subject

            for t_data in sub_data["topics"]:
                t_stmt = select(Topic).where(
                    Topic.subject_id == subject.id,
                    Topic.name == t_data["name"]
                )
                t_res = await session.execute(t_stmt)
                topic = t_res.scalar_one_or_none()

                subtopics_str = json.dumps(t_data.get("subtopics", []))

                if not topic:
                    topic = Topic(
                        subject_id=subject.id,
                        name=t_data["name"],
                        description=t_data.get("description"),
                        order_index=t_data.get("order_index", 0),
                        module_name=t_data.get("module_name", "Module 1: Foundations"),
                        subtopics_json=subtopics_str,
                        is_emerging=t_data.get("is_emerging", False),
                        source_reference=t_data.get("source_reference"),
                        last_updated_date=t_data.get("last_updated_date", "2025-Q4")
                    )
                    session.add(topic)
                    await session.flush()
                else:
                    topic.description = t_data.get("description", topic.description)
                    topic.order_index = t_data.get("order_index", topic.order_index)
                    topic.module_name = t_data.get("module_name", topic.module_name)
                    topic.subtopics_json = subtopics_str
                    topic.is_emerging = t_data.get("is_emerging", topic.is_emerging)
                    topic.source_reference = t_data.get("source_reference", topic.source_reference)
                    topic.last_updated_date = t_data.get("last_updated_date", topic.last_updated_date)

                topic_map[f"{subject.name}::{topic.name}"] = topic

        # 5. Subject Skill Mappings
        for sm in SUBJECT_SKILL_MAPPINGS:
            subj_name = sm["subject_name"]
            top_name = sm["topic_name"]
            skill_name = sm["skill_name"]
            comp_name = sm["competency"]

            subj_obj = subject_map.get(subj_name)
            topic_obj = topic_map.get(f"{subj_name}::{top_name}")
            skill_obj = skill_map.get(skill_name)

            if subj_obj and topic_obj and skill_obj:
                for cr_title in sm["career_roles"]:
                    cr_obj = role_map.get(cr_title)
                    if cr_obj:
                        m_stmt = select(SubjectSkillMapping).where(
                            SubjectSkillMapping.subject_id == subj_obj.id,
                            SubjectSkillMapping.topic_id == topic_obj.id,
                            SubjectSkillMapping.skill_id == skill_obj.id,
                            SubjectSkillMapping.career_role_id == cr_obj.id
                        )
                        m_res = await session.execute(m_stmt)
                        if not m_res.scalar_one_or_none():
                            ssm = SubjectSkillMapping(
                                subject_id=subj_obj.id,
                                topic_id=topic_obj.id,
                                competency_name=comp_name,
                                skill_id=skill_obj.id,
                                career_role_id=cr_obj.id
                            )
                            session.add(ssm)

        # 6. Practical Career Projects
        for cp_data in CAREER_PROJECTS:
            cr_obj = role_map.get(cp_data["career_role_title"])
            if cr_obj:
                cp_stmt = select(CareerProject).where(
                    CareerProject.career_role_id == cr_obj.id,
                    CareerProject.title == cp_data["title"]
                )
                cp_res = await session.execute(cp_stmt)
                if not cp_res.scalar_one_or_none():
                    proj = CareerProject(
                        career_role_id=cr_obj.id,
                        title=cp_data["title"],
                        objective=cp_data["objective"],
                        difficulty=cp_data["difficulty"],
                        required_skills_json=json.dumps(cp_data["required_skills"]),
                        tools_json=json.dumps(cp_data["tools"]),
                        steps_json=json.dumps(cp_data["steps"]),
                        expected_outcome=cp_data["expected_outcome"],
                        competency_focus=cp_data["competency_focus"]
                    )
                    session.add(proj)

        # 7. Career Pathways
        for pw_data in CAREER_PATHWAYS:
            from_role = role_map.get(pw_data["from_role"])
            to_role = role_map.get(pw_data["to_role"])
            if from_role and to_role:
                pw_stmt = select(CareerPathway).where(
                    CareerPathway.from_role_id == from_role.id,
                    CareerPathway.to_role_id == to_role.id
                )
                pw_res = await session.execute(pw_stmt)
                if not pw_res.scalar_one_or_none():
                    pathway = CareerPathway(
                        from_role_id=from_role.id,
                        to_role_id=to_role.id,
                        transition_difficulty=pw_data["transition_difficulty"],
                        bridge_skills_json=json.dumps(pw_data["bridge_skills"]),
                        guidance=pw_data["guidance"]
                    )
                    session.add(pathway)

        # 8. Default Demo User & Profile Initialization
        user_stmt = select(User).where(User.email == "demo@edupath.ai")
        u_res = await session.execute(user_stmt)
        demo_user = u_res.scalar_one_or_none()
        if not demo_user:
            demo_user = User(
                email="demo@edupath.ai",
                hashed_password=get_password_hash("EduPath@2026"),
                full_name="Alex Mercer (Learner)"
            )
            session.add(demo_user)
            await session.flush()

        # Ensure all existing users have a LearningProfile
        users_stmt = select(User)
        users_res = await session.execute(users_stmt)
        all_users = users_res.scalars().all()
        for u in all_users:
            lp_stmt = select(LearningProfile).where(LearningProfile.user_id == u.id)
            lp_res = await session.execute(lp_stmt)
            if not lp_res.scalar_one_or_none():
                # Default to Python Developer or first role
                first_role_id = next(iter(role_map.values())).id if role_map else None
                user_lp = LearningProfile(
                    user_id=u.id,
                    preferred_language="en",
                    explanation_style="step_by_step",
                    daily_goal_minutes=45,
                    target_career_id=first_role_id,
                    learning_preferences_json=json.dumps({
                        "focus_areas": ["Data Structures", "Databases"],
                        "reminder_frequency": "daily"
                    })
                )
                session.add(user_lp)

            # Ensure initial welcome notification if none exist
            n_stmt = select(Notification).where(Notification.user_id == u.id).limit(1)
            n_res = await session.execute(n_stmt)
            if not n_res.scalar_one_or_none():
                welcome_notif = Notification(
                    user_id=u.id,
                    title="Welcome to EduPath AI 2.0!",
                    message="Explore your updated multi-subject curriculum, conversational voice mode, and interactive learning workspace.",
                    notification_type="task_reminder",
                    action_url="/dashboard/workspace"
                )
                session.add(welcome_notif)

        await session.commit()
        logger.info(f"Database taxonomy successfully synced: {len(subject_map)} subjects, {len(topic_map)} topics, career projects & pathways.")

if __name__ == "__main__":
    asyncio.run(init_database())

