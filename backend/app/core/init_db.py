import asyncio
import logging
from sqlalchemy import select
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.models import (
    User, CareerRole, Subject, Topic, Skill,
    SubjectSkillMapping, CareerSkillRequirement
)
from app.services.seed_data import (
    CAREER_ROLES, SUBJECTS_AND_TOPICS, SKILLS_CATALOG,
    SUBJECT_SKILL_MAPPINGS, CAREER_SKILL_REQUIREMENTS
)

logger = logging.getLogger("edupath.init_db")

async def init_database():
    """
    Initializes database tables and populates the Academic-to-Industry taxonomy seed data.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        role_check = await session.execute(select(CareerRole).limit(1))
        if role_check.scalar_one_or_none():
            logger.info("Database taxonomy already initialized.")
            return

        logger.info("Seeding Academic-to-Industry taxonomy...")

        # 1. Career Roles
        role_map = {}
        for r_data in CAREER_ROLES:
            role = CareerRole(**r_data)
            session.add(role)
            await session.flush()
            role_map[role.title] = role

        # 2. Skills
        skill_map = {}
        for s_data in SKILLS_CATALOG:
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
                    csr = CareerSkillRequirement(
                        career_role_id=role_obj.id,
                        skill_id=skill_obj.id,
                        importance_level=importance,
                        min_proficiency=min_prof
                    )
                    session.add(csr)

        # 4. Subjects and Topics
        subject_map = {}
        topic_map = {}
        for sub_data in SUBJECTS_AND_TOPICS:
            subject = Subject(
                name=sub_data["name"],
                code=sub_data.get("code"),
                description=sub_data.get("description")
            )
            session.add(subject)
            await session.flush()
            subject_map[subject.name] = subject

            for t_data in sub_data["topics"]:
                topic = Topic(
                    subject_id=subject.id,
                    name=t_data["name"],
                    description=t_data.get("description"),
                    order_index=t_data.get("order_index", 0)
                )
                session.add(topic)
                await session.flush()
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
                        ssm = SubjectSkillMapping(
                            subject_id=subj_obj.id,
                            topic_id=topic_obj.id,
                            competency_name=comp_name,
                            skill_id=skill_obj.id,
                            career_role_id=cr_obj.id
                        )
                        session.add(ssm)

        # 6. Default Demo User
        demo_user = User(
            email="demo@edupath.ai",
            hashed_password=get_password_hash("EduPath@2026"),
            full_name="Alex Mercer (Learner)"
        )
        session.add(demo_user)

        await session.commit()
        logger.info("Database seeding successfully completed.")

if __name__ == "__main__":
    asyncio.run(init_database())
