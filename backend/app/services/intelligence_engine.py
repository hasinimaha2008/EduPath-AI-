"""
Central EduPath Intelligence Engine 2.0.
Interconnects:
- Workflow A (Weak Topic Loop): Quiz evaluations -> Mistake classification -> Topic performance -> Spaced repetition scheduler -> Weak topic notifications.
- Workflow B (Career Development Loop): Target career selection -> Demonstrated vs Missing skills -> Project recommendations -> Milestones.
- Workflow C (Document-Based Learning Loop): Document upload -> Hybrid extraction -> Executive summary -> Concept extraction -> Quiz generation -> Ready notification.
- Persistent Learning Profile (LearningProfile).
- Unified Topic Workspace aggregation.
- Real-time verifiable learning analytics (zero fabrication).
"""

import json
import logging
import re
from urllib.parse import quote
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from app.models.models import (
    User, Subject, Topic, Quiz, Question, QuizAttempt, UserAnswer,
    TopicPerformance, CareerRole, Skill, SubjectSkillMapping,
    CareerSkillRequirement, UserSkill, CareerRecommendation,
    SkillGap, CareerRoadmap, RoadmapMilestone, StudyPlan, StudyTask,
    LearningProfile, QuizMistake, Notification, CareerProject, CareerPathway,
    Note, Document
)
from app.services.gemini_service import gemini_service
from app.services.personalized_learning_service import personalized_learning_service

logger = logging.getLogger("edupath.intelligence_engine")

class EduPathIntelligenceEngine:

    @staticmethod
    def _classify_error_category(question_type: str, question_text: str, user_resp: str, correct_ans: str) -> str:
        """
        Classifies student quiz mistakes into 6 standardized categories:
        - conceptual_misunderstanding
        - incorrect_application
        - calculation_error
        - misinterpretation
        - knowledge_gap
        - unclassified
        """
        user_clean = user_resp.strip().lower()
        q_lower = question_text.lower()

        # 1. Knowledge Gap (blank or generic clueless response)
        if not user_clean or user_clean in ["?", "idk", "i don't know", "not sure", "none", "no idea"]:
            return "knowledge_gap"

        # 2. Calculation / Complexity Error
        if any(term in q_lower for term in ["complexity", "o(", "time complexity", "space complexity", "calculate", "bits", "bytes", "cost", "percentage"]):
            return "calculation_error"

        # 3. Incorrect Application (Scenario or system design questions)
        if question_type in ["scenario_based", "application_oriented", "technical_interview", "programming"]:
            return "incorrect_application"

        # 4. Misinterpretation (Question contains NOT, EXCEPT, FALSE or user picked exact opposite)
        if any(term in q_lower for term in [" not ", " except ", " false ", " incorrect ", "least"]):
            return "misinterpretation"

        # 5. Conceptual Misunderstanding (Default for theory / MCQ / definition errors)
        return "conceptual_misunderstanding"

    @staticmethod
    def _generate_suggested_fix(error_category: str, topic_name: str, explanation: str) -> str:
        """
        Generates actionable pedagogical advice for the student.
        """
        fixes = {
            "conceptual_misunderstanding": f"Review core foundational axioms and mental models for {topic_name}. {explanation[:120]}",
            "incorrect_application": f"Practice real-world edge cases and system trade-offs in {topic_name}. Focus on failure modes and invariants.",
            "calculation_error": f"Revisit step-by-step mathematical derivations and asymptotic bounds for {topic_name}.",
            "misinterpretation": f"Carefully identify negative qualifiers ('NOT', 'EXCEPT') in problem prompts before selecting answers.",
            "knowledge_gap": f"Read the structured overview notes for {topic_name} before retaking the assessment.",
            "unclassified": f"Re-read the question rubric and analyze the model solution."
        }
        return fixes.get(error_category, f"Review explanation for {topic_name}: {explanation[:100]}")

    @staticmethod
    async def evaluate_quiz_submission(
        session: AsyncSession,
        user_id: str,
        quiz_id: str,
        user_answers: List[Dict[str, str]],
        time_taken_seconds: int = 0
    ) -> Dict[str, Any]:
        """
        Evaluates quiz submission, executes Workflow A:
        1. Scores all question types.
        2. Classifies mistakes and tracks repeated errors.
        3. Updates topic performance with repeated evidence rules.
        4. Triggers weak topic alerts and spaced repetition scheduling if score < 70%.
        5. Synchronizes user skills and recalculates career intelligence.
        """
        quiz_stmt = select(Quiz).where(Quiz.id == quiz_id)
        quiz_res = await session.execute(quiz_stmt)
        quiz = quiz_res.scalar_one_or_none()
        if not quiz:
            raise ValueError("Quiz not found")

        q_stmt = select(Question).where(Question.quiz_id == quiz_id)
        q_res = await session.execute(q_stmt)
        questions = q_res.scalars().all()

        total_score = 0.0
        max_score = sum(q.points for q in questions) or 1.0
        evaluated_answers = []

        answer_lookup = {a["question_id"]: a["user_response"] for a in user_answers}

        for q in questions:
            user_resp = answer_lookup.get(q.id, "").strip()
            q_type = q.question_type or "mcq"

            if q_type == "true_false":
                user_clean = user_resp.strip().lower()
                corr_clean = q.correct_answer.strip().lower()
                is_correct = (user_clean == corr_clean) or (
                    user_clean in ["true", "t", "1"] and corr_clean in ["true", "t", "1"]
                ) or (
                    user_clean in ["false", "f", "0"] and corr_clean in ["false", "f", "0"]
                )
                pts = float(q.points) if is_correct else 0.0
                fb = q.explanation
            elif q_type == "fill_in_the_blank":
                # Normalize spaces, casing, and punctuation for robust comparison
                norm_user = re.sub(r'[^a-zA-Z0-9]', '', user_resp.lower())
                norm_corr = re.sub(r'[^a-zA-Z0-9]', '', q.correct_answer.lower())
                is_correct = (norm_user == norm_corr) or (user_resp.strip().lower() == q.correct_answer.strip().lower())
                pts = float(q.points) if is_correct else 0.0
                fb = q.explanation
            elif q_type == "multiple_select":
                user_selected = {x.strip().lower() for x in user_resp.replace(";", ",").split(",") if x.strip()}
                correct_selected = {x.strip().lower() for x in q.correct_answer.replace(";", ",").split(",") if x.strip()}
                if user_selected == correct_selected and len(correct_selected) > 0:
                    is_correct = True
                    pts = float(q.points)
                    fb = q.explanation or "All correct options selected!"
                elif user_selected.issubset(correct_selected) and len(user_selected) > 0:
                    is_correct = True
                    pts = round(float(q.points) * (len(user_selected) / len(correct_selected)), 1)
                    fb = f"Partial credit: Selected {len(user_selected)} of {len(correct_selected)} correct options. {q.explanation}"
                else:
                    is_correct = False
                    pts = 0.0
                    fb = f"Incorrect selections. {q.explanation}"
            elif q_type in ["short_answer", "long_answer", "technical_interview", "programming"] or (not q.options_json and q_type in ["scenario_based", "application_oriented"]):
                eval_res = await gemini_service.evaluate_open_answer(
                    question_text=q.question_text,
                    question_type=q_type,
                    correct_answer=q.correct_answer,
                    user_response=user_resp
                )
                is_correct = eval_res.get("is_correct", False)
                score_ratio = eval_res.get("score_ratio", 1.0 if is_correct else 0.0)
                pts = round(float(q.points) * score_ratio, 1)
                fb = f"{eval_res.get('feedback', '')} | Reference Key: {q.explanation}"
            else:
                is_correct = (user_resp.lower() == q.correct_answer.strip().lower())
                pts = float(q.points) if is_correct else 0.0
                fb = q.explanation

            total_score += pts

            evaluated_answers.append({
                "question": q,
                "user_response": user_resp,
                "is_correct": is_correct,
                "score_awarded": pts,
                "feedback": fb
            })

        percentage = round((total_score / max_score) * 100.0, 1)

        # 1. Record Quiz Attempt
        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            score=total_score,
            max_score=max_score,
            percentage=percentage,
            time_taken_seconds=time_taken_seconds,
            completed_at=datetime.now(timezone.utc)
        )
        session.add(attempt)
        await session.flush()

        # 2. Record User Answers & Classify Mistakes (Upgrade 5)
        mistakes_recorded = []
        topic_id = quiz.topic_id
        subject_id = quiz.subject_id

        # Fetch topic name for context
        topic_name = "Core Topic"
        if topic_id:
            t_stmt = select(Topic.name).where(Topic.id == topic_id)
            t_res = await session.execute(t_stmt)
            t_name = t_res.scalar_one_or_none()
            if t_name:
                topic_name = t_name

        for ea in evaluated_answers:
            q = ea["question"]
            ua = UserAnswer(
                attempt_id=attempt.id,
                question_id=q.id,
                user_response=ea["user_response"],
                is_correct=ea["is_correct"],
                score_awarded=ea["score_awarded"],
                feedback=ea["feedback"]
            )
            session.add(ua)

            # If answer is incorrect, log into QuizMistake
            if not ea["is_correct"]:
                error_cat = EduPathIntelligenceEngine._classify_error_category(
                    question_type=q.question_type or "mcq",
                    question_text=q.question_text,
                    user_resp=ea["user_response"],
                    correct_ans=q.correct_answer
                )
                suggested_fix = EduPathIntelligenceEngine._generate_suggested_fix(error_cat, topic_name, q.explanation or "")

                # Check if student made mistake on this question previously
                prev_mistake_stmt = select(QuizMistake).where(
                    QuizMistake.user_id == user_id,
                    QuizMistake.question_id == q.id
                ).order_by(QuizMistake.created_at.desc()).limit(1)
                prev_mistake_res = await session.execute(prev_mistake_stmt)
                prev_mistake = prev_mistake_res.scalars().first()

                repeated_count = (prev_mistake.repeated_count + 1) if prev_mistake else 1

                mistake = QuizMistake(
                    user_id=user_id,
                    quiz_attempt_id=attempt.id,
                    question_id=q.id,
                    topic_id=topic_id,
                    error_category=error_cat,
                    user_response=ea["user_response"][:500],
                    correct_answer=q.correct_answer[:500],
                    explanation=(q.explanation or "")[:500],
                    suggested_fix=suggested_fix,
                    repeated_count=repeated_count
                )
                session.add(mistake)
                mistakes_recorded.append({
                    "question_id": q.id,
                    "error_category": error_cat,
                    "repeated_count": repeated_count,
                    "suggested_fix": suggested_fix
                })

        # 3. Update Topic Performance
        tp = None
        if topic_id:
            tp_stmt = select(TopicPerformance).where(
                TopicPerformance.user_id == user_id,
                TopicPerformance.topic_id == topic_id
            ).limit(1)
            tp_res = await session.execute(tp_stmt)
            tp = tp_res.scalars().first()

            correct_count = sum(1 for ea in evaluated_answers if ea["is_correct"])
            incorrect_count = len(evaluated_answers) - correct_count

            if not tp:
                tp = TopicPerformance(
                    user_id=user_id,
                    subject_id=subject_id or "",
                    topic_id=topic_id,
                    total_attempts=1,
                    correct_answers=correct_count,
                    incorrect_answers=incorrect_count,
                    accuracy_percentage=percentage,
                    mastery_status=EduPathIntelligenceEngine._calculate_mastery(1, percentage),
                    last_practiced_at=datetime.now(timezone.utc)
                )
                session.add(tp)
            else:
                tp.total_attempts += 1
                tp.correct_answers += correct_count
                tp.incorrect_answers += incorrect_count
                total_q = tp.correct_answers + tp.incorrect_answers
                tp.accuracy_percentage = round((tp.correct_answers / total_q) * 100.0, 1) if total_q > 0 else 0.0
                tp.mastery_status = EduPathIntelligenceEngine._calculate_mastery(tp.total_attempts, tp.accuracy_percentage)
                tp.last_practiced_at = datetime.now(timezone.utc)

            await session.flush()

            # Synchronize linked skills
            await EduPathIntelligenceEngine._sync_topic_to_user_skills(session, user_id, topic_id, tp.accuracy_percentage)

            # 4. WORKFLOW A: Weak Topic Loop & Spaced Repetition Trigger
            if percentage < 70.0 or tp.mastery_status in ["needs_practice", "developing"]:
                # Schedule Ebbinghaus spaced repetition task
                await personalized_learning_service.schedule_spaced_repetition(
                    session=session,
                    user_id=user_id,
                    topic_id=topic_id,
                    latest_percentage=percentage
                )
                # Create Weak Topic Notification
                notif = Notification(
                    user_id=user_id,
                    title=f"Weak Topic Alert: {topic_name}",
                    message=f"Score: {percentage}%. We've scheduled an adaptive spaced repetition review for {topic_name}.",
                    notification_type="weak_topic_alert",
                    action_url=f"/dashboard/workspace?topic_id={topic_id}"
                )
                session.add(notif)
            else:
                # If student demonstrated proficient score, create milestone feedback notification
                notif = Notification(
                    user_id=user_id,
                    title=f"Quiz Mastered: {topic_name} ({percentage}%)",
                    message=f"Great job! You achieved {percentage}% on {topic_name}. Your skill proficiency has been updated.",
                    notification_type="quiz_feedback",
                    action_url=f"/dashboard/workspace?topic_id={topic_id}"
                )
                session.add(notif)

        # 5. Re-evaluate Career Intelligence (Workflow B)
        await EduPathIntelligenceEngine.recalculate_career_intelligence(session, user_id)

        # Phase 4: Topic breakdown and recommended revision topics
        topic_breakdown = {
            "topic_name": topic_name,
            "total_questions": len(questions),
            "correct_count": sum(1 for ea in evaluated_answers if ea["is_correct"]),
            "accuracy": percentage,
            "mastery_status": tp.mastery_status if tp else "developing"
        }

        recommended_revision_topics = []
        for ea in evaluated_answers:
            if not ea["is_correct"]:
                q_text = ea["question"].question_text
                clean_q = re.sub(r'\[.*?\]\s*', '', q_text).strip()
                rec_title = f"{topic_name}: {clean_q[:65]}..." if len(clean_q) > 65 else f"{topic_name}: {clean_q}"
                if rec_title not in recommended_revision_topics:
                    recommended_revision_topics.append(rec_title)

        if not recommended_revision_topics and percentage < 100.0:
            recommended_revision_topics.append(f"Review core principles of {topic_name}")
        elif not recommended_revision_topics:
            recommended_revision_topics.append(f"Advanced concepts and applications in {topic_name}")

        await session.commit()

        return {
            "attempt_id": attempt.id,
            "quiz_id": quiz_id,
            "score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "time_taken_seconds": time_taken_seconds,
            "completed_at": attempt.completed_at,
            "mistakes_recorded": mistakes_recorded,
            "mastery_status": tp.mastery_status if tp else "unspecified",
            "topic_breakdown": topic_breakdown,
            "recommended_revision_topics": recommended_revision_topics,
            "answers": [
                {
                    "question_id": ea["question"].id,
                    "question_text": ea["question"].question_text,
                    "user_response": ea["user_response"],
                    "correct_answer": ea["question"].correct_answer,
                    "is_correct": ea["is_correct"],
                    "score_awarded": ea["score_awarded"],
                    "explanation": ea["question"].explanation
                }
                for ea in evaluated_answers
            ]
        }

    @staticmethod
    def _calculate_mastery(total_attempts: int, accuracy: float) -> str:
        if total_attempts >= 3 and accuracy >= 90.0:
            return "mastered"
        elif total_attempts >= 2 and accuracy >= 75.0:
            return "proficient"
        elif accuracy >= 50.0:
            return "developing"
        else:
            return "needs_practice"

    @staticmethod
    async def _sync_topic_to_user_skills(session: AsyncSession, user_id: str, topic_id: str, accuracy: float):
        map_stmt = select(SubjectSkillMapping).where(SubjectSkillMapping.topic_id == topic_id)
        map_res = await session.execute(map_stmt)
        mappings = map_res.scalars().all()

        seen_skill_ids = set()
        for m in mappings:
            if m.skill_id in seen_skill_ids:
                continue
            seen_skill_ids.add(m.skill_id)

            us_stmt = select(UserSkill).where(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == m.skill_id
            ).limit(1)
            us_res = await session.execute(us_stmt)
            user_skill = us_res.scalars().first()

            if not user_skill:
                user_skill = UserSkill(
                    user_id=user_id,
                    skill_id=m.skill_id,
                    proficiency_level=accuracy,
                    source="demonstrated",
                    evidence_notes=f"Demonstrated via quiz evaluations in competency: {m.competency_name}",
                    verified=True,
                    last_evaluated_at=datetime.now(timezone.utc)
                )
                session.add(user_skill)
            else:
                user_skill.proficiency_level = round((user_skill.proficiency_level * 0.4) + (accuracy * 0.6), 1)
                user_skill.source = "demonstrated"
                user_skill.verified = True
                user_skill.evidence_notes = f"Updated via quiz evaluation in competency: {m.competency_name}"
                user_skill.last_evaluated_at = datetime.now(timezone.utc)

    ROLE_DOMAINS = {
        "Python Developer": "Software Development",
        "Backend Developer": "Software Development",
        "Web Developer": "Web Development",
        "Database Developer": "Data Systems & Architecture",
        "Data Analyst": "Data Science",
        "Data Scientist": "Data Science",
        "Machine Learning Engineer": "Machine Learning",
        "AI Engineer": "Artificial Intelligence",
        "Cybersecurity Analyst": "Cybersecurity",
        "Cloud Solutions Architect": "Cloud Computing"
    }

    @staticmethod
    async def recalculate_career_intelligence(session: AsyncSession, user_id: str):
        """
        Recalculates explainable career recommendations, skill gaps, and checks target career status.
        Integrates student profile interests, preferred domains, projects, and clearly distinguishes
        verified academic qualifications (quizzes) from self-reported skills.
        """
        roles_stmt = select(CareerRole)
        roles_res = await session.execute(roles_stmt)
        roles = roles_res.scalars().all()

        us_stmt = select(UserSkill).where(UserSkill.user_id == user_id)
        us_res = await session.execute(us_stmt)
        user_skills = {us.skill_id: us for us in us_res.scalars().all()}

        skills_stmt = select(Skill)
        skills_res = await session.execute(skills_stmt)
        skills_dict = {s.id: s for s in skills_res.scalars().all()}

        # Fetch user's persistent learning profile
        lp_stmt = select(LearningProfile).where(LearningProfile.user_id == user_id).limit(1)
        lp_res = await session.execute(lp_stmt)
        lp = lp_res.scalars().first()

        prefs = lp.preferences if lp else {}
        interests = [str(i).lower() for i in prefs.get("interests", [])]
        preferred_domains = [str(d).lower() for d in prefs.get("preferred_domains", [])]
        career_goals = prefs.get("career_goals", "")

        for role in roles:
            req_stmt = select(CareerSkillRequirement).where(CareerSkillRequirement.career_role_id == role.id)
            req_res = await session.execute(req_stmt)
            requirements = req_res.scalars().all()

            if not requirements:
                continue

            total_weight = 0.0
            demonstrated_weight = 0.0
            self_reported_weight = 0.0
            matching_skills = []
            missing_skills = []

            for req in requirements:
                skill_id = req.skill_id
                importance_multiplier = 1.5 if req.importance_level == "Core" else 1.0
                total_weight += 100.0 * importance_multiplier

                user_skill = user_skills.get(skill_id)
                skill_obj = skills_dict.get(skill_id)
                skill_name = skill_obj.name if skill_obj else "Unknown Skill"

                if user_skill:
                    user_prof = min(user_skill.proficiency_level, 100.0)
                    if user_skill.source == "demonstrated":
                        demonstrated_weight += user_prof * importance_multiplier
                    else:
                        self_reported_weight += user_prof * importance_multiplier

                    if user_prof >= req.min_proficiency:
                        tag = " (Verified)" if user_skill.source == "demonstrated" else " (Self-Reported)"
                        matching_skills.append(f"{skill_name}{tag}")
                    else:
                        missing_skills.append(f"{skill_name} ({round(user_prof, 1)}% / {round(req.min_proficiency, 1)}%)")
                else:
                    missing_skills.append(skill_name)

                # Upsert Skill Gap
                status = "missing"
                evidence_source = "missing"
                if user_skill:
                    status = "existing" if user_skill.proficiency_level >= req.min_proficiency else "needs_improvement"
                    evidence_source = user_skill.source

                priority = "High" if req.importance_level == "Core" and status != "existing" else ("Medium" if status != "existing" else "Low")
                rec_text = f"Study foundational modules and complete topic quizzes for {skill_name} to satisfy {role.title} industry benchmarks."

                sg_stmt = select(SkillGap).where(
                    SkillGap.user_id == user_id,
                    SkillGap.career_role_id == role.id,
                    SkillGap.skill_id == skill_id
                ).limit(1)
                sg_res = await session.execute(sg_stmt)
                sg = sg_res.scalars().first()

                if not sg:
                    sg = SkillGap(
                        user_id=user_id,
                        career_role_id=role.id,
                        skill_id=skill_id,
                        status=status,
                        priority=priority,
                        learning_recommendation=rec_text
                    )
                    session.add(sg)
                else:
                    sg.status = status
                    sg.priority = priority
                    sg.learning_recommendation = rec_text

            role_domain = EduPathIntelligenceEngine.ROLE_DOMAINS.get(role.title, "Technology")

            # Domain alignment bonus (up to 8%)
            domain_bonus = 0.0
            if any(role_domain.lower() in pd or pd in role_domain.lower() for pd in preferred_domains):
                domain_bonus += 5.0
            if any(any(w in role.title.lower() for w in i.split()) for i in interests):
                domain_bonus += 3.0

            demonstrated_score = round((demonstrated_weight / total_weight) * 100.0, 1) if total_weight > 0 else 0.0
            base_score = round(((demonstrated_weight + self_reported_weight) / total_weight) * 100.0, 1) if total_weight > 0 else 0.0
            match_score = round(min(100.0, base_score + domain_bonus), 1)

            # Explainable Rationale
            domain_note = f" Matches your preferred domain of '{role_domain}'." if domain_bonus > 0 else ""
            goal_note = f" Directly aligns with your stated goal: '{career_goals}'." if career_goals else ""

            rationale = (
                f"Calculated readiness of {match_score}% (Demonstrated Academic Accuracy: {demonstrated_score}% across quizzes; "
                f"Self-Reported/Curriculum Match: {base_score}%).{domain_note}{goal_note} "
                f"You have demonstrated proficiency in {len(matching_skills)} competencies, with {len(missing_skills)} "
                f"key skill gaps identified for target role standards."
            )

            rec_stmt = select(CareerRecommendation).where(
                CareerRecommendation.user_id == user_id,
                CareerRecommendation.career_role_id == role.id
            ).limit(1)
            rec_res = await session.execute(rec_stmt)
            rec = rec_res.scalars().first()

            if not rec:
                rec = CareerRecommendation(
                    user_id=user_id,
                    career_role_id=role.id,
                    match_score=match_score,
                    rationale=rationale,
                    missing_skills_count=len(missing_skills),
                    recommended_at=datetime.now(timezone.utc)
                )
                session.add(rec)
            else:
                rec.match_score = match_score
                rec.rationale = rationale
                rec.missing_skills_count = len(missing_skills)
                rec.recommended_at = datetime.now(timezone.utc)

    @staticmethod
    async def get_or_create_learning_profile(session: AsyncSession, user_id: str) -> LearningProfile:
        """
        Retrieves user's persistent learning profile or creates default if not existing.
        """
        stmt = select(LearningProfile).where(LearningProfile.user_id == user_id).limit(1)
        res = await session.execute(stmt)
        profile = res.scalars().first()

        if not profile:
            # Default to first available career role
            role_stmt = select(CareerRole.id).limit(1)
            role_res = await session.execute(role_stmt)
            default_role_id = role_res.scalar_one_or_none()

            profile = LearningProfile(
                user_id=user_id,
                preferred_language="en",
                explanation_style="step_by_step",
                daily_goal_minutes=45,
                target_career_id=default_role_id,
                learning_preferences_json=json.dumps({
                    "focus_areas": ["Databases", "Algorithms"],
                    "reminder_frequency": "daily"
                })
            )
            session.add(profile)
            await session.commit()
            await session.refresh(profile)

        return profile

    @staticmethod
    async def update_learning_profile(
        session: AsyncSession,
        user_id: str,
        updates: Dict[str, Any]
    ) -> LearningProfile:
        """
        Updates learning profile and triggers Workflow B notifications if target career changes.
        """
        profile = await EduPathIntelligenceEngine.get_or_create_learning_profile(session, user_id)
        prev_target_career = profile.target_career_id

        if "preferred_language" in updates and updates["preferred_language"]:
            profile.preferred_language = updates["preferred_language"]
        if "explanation_style" in updates and updates["explanation_style"]:
            profile.explanation_style = updates["explanation_style"]
        if "daily_goal_minutes" in updates and updates["daily_goal_minutes"]:
            profile.daily_goal_minutes = int(updates["daily_goal_minutes"])
        if "target_career_id" in updates:
            profile.target_career_id = updates["target_career_id"]

        current_prefs = profile.preferences
        prefs_modified = False

        for k in ["interests", "preferred_domains", "career_goals", "self_reported_skills", "projects_and_experience"]:
            if k in updates and updates[k] is not None:
                current_prefs[k] = updates[k]
                prefs_modified = True

        if "learning_preferences" in updates and updates["learning_preferences"]:
            current_prefs.update(updates["learning_preferences"])
            prefs_modified = True

        if prefs_modified:
            profile.learning_preferences_json = json.dumps(current_prefs)

        # Synchronize self-reported skills into UserSkill records
        if "self_reported_skills" in updates and isinstance(updates["self_reported_skills"], list):
            skills_stmt = select(Skill)
            skills_res = await session.execute(skills_stmt)
            all_skills = skills_res.scalars().all()
            skill_name_to_obj = {s.name.lower(): s for s in all_skills}

            for sr_skill in updates["self_reported_skills"]:
                s_obj = skill_name_to_obj.get(sr_skill.strip().lower())
                if s_obj:
                    us_stmt = select(UserSkill).where(
                        UserSkill.user_id == user_id,
                        UserSkill.skill_id == s_obj.id
                    ).limit(1)
                    us_res = await session.execute(us_stmt)
                    existing_us = us_res.scalars().first()

                    if not existing_us:
                        new_us = UserSkill(
                            user_id=user_id,
                            skill_id=s_obj.id,
                            proficiency_level=75.0,
                            source="self_reported",
                            evidence_notes="Self-reported qualification in student profile",
                            verified=False,
                            last_evaluated_at=datetime.now(timezone.utc)
                        )
                        session.add(new_us)

        profile.updated_at = datetime.now(timezone.utc)

        # Trigger Workflow B notification if target career changed
        if profile.target_career_id and profile.target_career_id != prev_target_career:
            role_stmt = select(CareerRole).where(CareerRole.id == profile.target_career_id)
            role_res = await session.execute(role_stmt)
            role = role_res.scalar_one_or_none()
            if role:
                notif = Notification(
                    user_id=user_id,
                    title=f"Career Goal Updated: {role.title}",
                    message=f"You are now targeting {role.title}. We've re-aligned your skill gap curriculum and practical project milestones.",
                    notification_type="career_milestone",
                    action_url=f"/dashboard/careers"
                )
                session.add(notif)

        await session.flush()
        # Recalculate career recommendations with new profile inputs
        await EduPathIntelligenceEngine.recalculate_career_intelligence(session, user_id)

        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def get_mistake_insights(session: AsyncSession, user_id: str) -> Dict[str, Any]:
        """
        Calculates comprehensive mistake analytics (Upgrade 5):
        - Mistakes grouped by error category
        - Repeated mistakes detection
        - Improvement rate & trend
        - Actionable recommendations
        """
        stmt = select(QuizMistake, Topic.name, Question.question_text).join(
            Topic, QuizMistake.topic_id == Topic.id, isouter=True
        ).join(
            Question, QuizMistake.question_id == Question.id, isouter=True
        ).where(
            QuizMistake.user_id == user_id
        ).order_by(QuizMistake.created_at.desc())

        res = await session.execute(stmt)
        rows = res.all()

        total_mistakes = len(rows)
        category_counts: Dict[str, int] = {}
        repeated_mistakes = []
        recent_mistakes_list = []

        for mistake, topic_name, q_text in rows:
            cat = mistake.error_category or "unclassified"
            category_counts[cat] = category_counts.get(cat, 0) + 1

            item = {
                "id": mistake.id,
                "topic_name": topic_name or "General Topic",
                "question_text": (q_text or "Assessment Question")[:120],
                "error_category": cat,
                "user_response": mistake.user_response,
                "correct_answer": mistake.correct_answer,
                "explanation": mistake.explanation,
                "suggested_fix": mistake.suggested_fix,
                "repeated_count": mistake.repeated_count,
                "created_at": mistake.created_at
            }
            recent_mistakes_list.append(item)

            if mistake.repeated_count > 1:
                repeated_mistakes.append(item)

        # Calculate improvement rate from quiz attempts
        attempts_stmt = select(QuizAttempt).where(QuizAttempt.user_id == user_id).order_by(QuizAttempt.completed_at.asc())
        attempts_res = await session.execute(attempts_stmt)
        attempts = attempts_res.scalars().all()

        improvement_rate = 0.0
        if len(attempts) >= 2:
            first_half = attempts[:len(attempts)//2]
            second_half = attempts[len(attempts)//2:]
            avg_1 = sum(a.percentage for a in first_half) / len(first_half)
            avg_2 = sum(a.percentage for a in second_half) / len(second_half)
            improvement_rate = round(avg_2 - avg_1, 1)

        # Primary weakness recommendation
        top_weak_cat = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "conceptual_misunderstanding"
        category_labels = {
            "conceptual_misunderstanding": "Conceptual Axioms & Theory",
            "incorrect_application": "Real-World Application & Architecture",
            "calculation_error": "Complexity Derivations & Calculations",
            "misinterpretation": "Question Parsing & Negative Qualifiers",
            "knowledge_gap": "Foundational Prerequisite Coverage",
            "unclassified": "General Review"
        }

        actionable_advice = f"Your most frequent error type is '{category_labels.get(top_weak_cat, top_weak_cat)}' ({category_counts.get(top_weak_cat, 0)} occurrences). Focus your next revision on core principles rather than rushed multiple-choice guessing."

        return {
            "total_mistakes": total_mistakes,
            "repeated_mistakes_count": len(repeated_mistakes),
            "improvement_rate": improvement_rate,
            "category_distribution": [
                {"category": k, "label": category_labels.get(k, k), "count": v}
                for k, v in category_counts.items()
            ],
            "repeated_mistakes": repeated_mistakes[:5],
            "recent_mistakes": recent_mistakes_list[:10],
            "actionable_advice": actionable_advice
        }

    @staticmethod
    async def get_topic_workspace(session: AsyncSession, user_id: str, topic_id: str) -> Dict[str, Any]:
        """
        Aggregates all learning modalities for a specific topic (Upgrade 7):
        - Topic details & Subject context
        - User topic performance & accuracy
        - Notes generated for topic
        - Uploaded documents linked to subject
        - Recent quiz attempts
        - Due spaced repetition revision tasks
        """
        # Topic & Subject
        topic_stmt = select(Topic, Subject).join(
            Subject, Topic.subject_id == Subject.id, isouter=True
        ).where(Topic.id == topic_id)
        topic_res = await session.execute(topic_stmt)
        topic_row = topic_res.first()
        if not topic_row:
            raise ValueError(f"Topic {topic_id} not found")

        topic, subject = topic_row

        # Performance
        tp_stmt = select(TopicPerformance).where(
            TopicPerformance.user_id == user_id,
            TopicPerformance.topic_id == topic_id
        ).limit(1)
        tp_res = await session.execute(tp_stmt)
        tp = tp_res.scalars().first()

        # Notes
        notes_stmt = select(Note).where(
            Note.user_id == user_id,
            Note.topic_id == topic_id
        ).order_by(Note.created_at.desc()).limit(5)
        notes_res = await session.execute(notes_stmt)
        notes = notes_res.scalars().all()

        # Documents
        docs_stmt = select(Document).where(
            Document.user_id == user_id,
            Document.subject_id == topic.subject_id
        ).order_by(Document.created_at.desc()).limit(5)
        docs_res = await session.execute(docs_stmt)
        docs = docs_res.scalars().all()

        # Quizzes & Attempts
        attempts_stmt = select(QuizAttempt, Quiz.title).join(
            Quiz, QuizAttempt.quiz_id == Quiz.id
        ).where(
            QuizAttempt.user_id == user_id,
            Quiz.topic_id == topic_id
        ).order_by(QuizAttempt.completed_at.desc()).limit(5)
        attempts_res = await session.execute(attempts_stmt)
        attempts_rows = attempts_res.all()

        # Due Revisions for this topic
        today_str = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")
        tasks_stmt = select(StudyTask).join(
            StudyPlan, StudyTask.study_plan_id == StudyPlan.id
        ).where(
            StudyPlan.user_id == user_id,
            StudyTask.topic_id == topic_id,
            StudyTask.is_completed == False
        ).order_by(StudyTask.scheduled_date.asc())
        tasks_res = await session.execute(tasks_stmt)
        tasks = tasks_res.scalars().all()

        return {
            "topic": {
                "id": topic.id,
                "name": topic.name,
                "description": topic.description,
                "module_name": topic.module_name,
                "subtopics": topic.subtopics,
                "is_emerging": topic.is_emerging,
                "source_reference": topic.source_reference,
                "subject_id": subject.id if subject else None,
                "subject_name": subject.name if subject else "General"
            },
            "performance": {
                "total_attempts": tp.total_attempts if tp else 0,
                "correct_answers": tp.correct_answers if tp else 0,
                "incorrect_answers": tp.incorrect_answers if tp else 0,
                "accuracy_percentage": tp.accuracy_percentage if tp else 0.0,
                "mastery_status": tp.mastery_status if tp else "not_started",
                "last_practiced_at": tp.last_practiced_at if tp else None
            },
            "notes": [
                {
                    "id": n.id,
                    "title": n.title,
                    "note_type": n.note_type,
                    "content_preview": n.content[:200] + "...",
                    "created_at": n.created_at
                }
                for n in notes
            ],
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "status": d.status,
                    "file_type": d.file_type,
                    "created_at": d.created_at
                }
                for d in docs
            ],
            "quiz_attempts": [
                {
                    "attempt_id": att.id,
                    "quiz_title": title,
                    "score": att.score,
                    "max_score": att.max_score,
                    "percentage": att.percentage,
                    "completed_at": att.completed_at
                }
                for att, title in attempts_rows
            ],
            "revision_tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "scheduled_date": t.scheduled_date,
                    "is_due": t.scheduled_date <= today_str,
                    "priority": t.priority
                }
                for t in tasks
            ]
        }

    @staticmethod
    async def get_user_analytics(session: AsyncSession, user_id: str) -> Dict[str, Any]:
        """
        Calculates verified learning analytics from actual user quiz attempts and topic performances.
        Never fabricates sample stats.
        """
        attempts_stmt = select(QuizAttempt).where(QuizAttempt.user_id == user_id).order_by(QuizAttempt.completed_at.desc())
        attempts_res = await session.execute(attempts_stmt)
        attempts = attempts_res.scalars().all()

        total_quizzes = len(attempts)
        avg_score = round(sum(a.percentage for a in attempts) / total_quizzes, 1) if total_quizzes > 0 else 0.0
        highest_score = round(max([a.percentage for a in attempts]), 1) if attempts else 0.0

        # Query attempts joined with Quiz and Subject for trendlines and subject aggregation
        attempts_with_quiz_stmt = (
            select(QuizAttempt, Quiz.title, Quiz.subject_id, Subject.name)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id, isouter=True)
            .join(Subject, Quiz.subject_id == Subject.id, isouter=True)
            .where(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.completed_at.asc())
        )
        attempts_with_quiz_res = await session.execute(attempts_with_quiz_stmt)
        attempts_with_quiz = attempts_with_quiz_res.all()

        quiz_score_trends = [
            {
                "attempt_id": att.id,
                "quiz_title": title or "Assessment Quiz",
                "percentage": round(att.percentage, 1),
                "completed_at": att.completed_at.strftime("%b %d, %H:%M") if att.completed_at else "",
                "score": round(att.score, 1),
                "max_score": round(att.max_score, 1)
            }
            for att, title, s_id, s_name in attempts_with_quiz[-15:]
        ]

        tp_stmt = select(TopicPerformance, Topic.name, Subject.name).join(
            Topic, TopicPerformance.topic_id == Topic.id
        ).join(
            Subject, TopicPerformance.subject_id == Subject.id, isouter=True
        ).where(
            TopicPerformance.user_id == user_id
        )
        tp_res = await session.execute(tp_stmt)
        tp_records = tp_res.all()

        strong_topics = []
        weak_topics = []
        revision_recs = []

        for tp, topic_name, subject_name in tp_records:
            item = {
                "id": tp.id,
                "subject_name": subject_name or "General",
                "topic_name": topic_name,
                "topic_id": tp.topic_id,
                "total_attempts": tp.total_attempts,
                "correct_answers": tp.correct_answers,
                "incorrect_answers": tp.incorrect_answers,
                "accuracy_percentage": round(tp.accuracy_percentage, 1),
                "mastery_status": tp.mastery_status,
                "last_practiced_at": tp.last_practiced_at
            }
            if tp.mastery_status in ["proficient", "mastered"] or tp.accuracy_percentage >= 75.0:
                strong_topics.append(item)
            else:
                weak_topics.append(item)
                revision_recs.append(f"Review core principles for {topic_name} (accuracy: {tp.accuracy_percentage}%, attempts: {tp.total_attempts})")

        # Subject performance aggregation from real records
        subject_data: Dict[str, Dict[str, Any]] = {}
        for att, title, s_id, s_name in attempts_with_quiz:
            subj_name = s_name or "General / Core Curriculum"
            if subj_name not in subject_data:
                subject_data[subj_name] = {
                    "subject_id": s_id,
                    "subject_name": subj_name,
                    "scores": [],
                    "topics": set()
                }
            subject_data[subj_name]["scores"].append(att.percentage)

        for tp, topic_name, subj_name in tp_records:
            s_name = subj_name or "General / Core Curriculum"
            if s_name not in subject_data:
                subject_data[s_name] = {
                    "subject_id": tp.subject_id,
                    "subject_name": s_name,
                    "scores": [],
                    "topics": set()
                }
            subject_data[s_name]["topics"].add(topic_name)

        subject_performances = []
        for s_name, s_info in subject_data.items():
            avg_acc = round(sum(s_info["scores"]) / len(s_info["scores"]), 1) if s_info["scores"] else 0.0
            subject_performances.append({
                "subject_id": s_info["subject_id"],
                "subject_name": s_name,
                "quizzes_count": len(s_info["scores"]),
                "topics_practiced": len(s_info["topics"]),
                "average_accuracy": avg_acc
            })
        subject_performances.sort(key=lambda x: (x["quizzes_count"], x["average_accuracy"]), reverse=True)

        # Topic mastery completion breakdown
        mastered_cnt = sum(1 for tp, _, _ in tp_records if tp.mastery_status == "mastered")
        proficient_cnt = sum(1 for tp, _, _ in tp_records if tp.mastery_status == "proficient")
        developing_cnt = sum(1 for tp, _, _ in tp_records if tp.mastery_status == "developing")
        needs_practice_cnt = sum(1 for tp, _, _ in tp_records if tp.mastery_status == "needs_practice")
        topic_completion_stats = {
            "total_practiced": len(tp_records),
            "mastered_count": mastered_cnt,
            "proficient_count": proficient_cnt,
            "developing_count": developing_cnt,
            "needs_practice_count": needs_practice_cnt
        }

        # Activity by day (last 7 days)
        today = datetime.now(timezone.utc).date()
        days_map = {}
        for d in range(6, -1, -1):
            day_str = (today - timedelta(days=d)).strftime("%Y-%m-%d")
            days_map[day_str] = {"date": day_str, "quiz_count": 0, "questions_solved": 0}

        for a in attempts:
            day_str = a.completed_at.strftime("%Y-%m-%d")
            if day_str in days_map:
                days_map[day_str]["quiz_count"] += 1
                days_map[day_str]["questions_solved"] += int(a.max_score)

        recent_activity = list(days_map.values())
        streak_days = sum(1 for d in recent_activity if d["quiz_count"] > 0)
        total_study_hours = round(sum(a.time_taken_seconds for a in attempts) / 3600.0, 1)

        # Consistency percentage across past 14 days
        past_14_days = {(today - timedelta(days=d)).strftime("%Y-%m-%d") for d in range(14)}
        active_days_14 = {a.completed_at.strftime("%Y-%m-%d") for a in attempts if a.completed_at.strftime("%Y-%m-%d") in past_14_days}
        study_consistency = round((len(active_days_14) / 14.0) * 100.0, 1) if attempts else 0.0

        # Intelligent Insights generation
        intelligent_insights = []

        # 1. Attention
        lowest_subject = min([sp for sp in subject_performances if sp["quizzes_count"] > 0], key=lambda x: x["average_accuracy"], default=None)
        if lowest_subject and lowest_subject["average_accuracy"] < 75.0:
            intelligent_insights.append({
                "category": "attention",
                "title": f"Subject Needs Attention: {lowest_subject['subject_name']}",
                "message": f"Your average accuracy in {lowest_subject['subject_name']} is currently {lowest_subject['average_accuracy']}%. Focus on foundational lecture notes and targeted revision in this area.",
                "severity": "warning"
            })
        elif weak_topics:
            w_top = weak_topics[0]
            intelligent_insights.append({
                "category": "attention",
                "title": f"Topic Review Needed: {w_top['topic_name']}",
                "message": f"Accuracy in {w_top['topic_name']} is {w_top['accuracy_percentage']}%. We recommend spaced review tasks before your next assessment.",
                "severity": "warning"
            })
        else:
            intelligent_insights.append({
                "category": "attention",
                "title": "Syllabus Balance",
                "message": "All current topics meet target accuracy thresholds (>=75%). Continue expanding coverage across remaining subject modules.",
                "severity": "info"
            })

        # 2. Improvement
        if len(attempts_with_quiz) >= 2:
            half = len(attempts_with_quiz) // 2
            first_half = [att.percentage for att, _, _, _ in attempts_with_quiz[:half]]
            second_half = [att.percentage for att, _, _, _ in attempts_with_quiz[half:]]
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            diff = round(avg_second - avg_first, 1)
            if diff > 0:
                intelligent_insights.append({
                    "category": "improvement",
                    "title": f"Score Trajectory Rising (+{diff}%)",
                    "message": f"Your recent assessment scores ({round(avg_second, 1)}%) show a +{diff}% gain over earlier attempts ({round(avg_first, 1)}%). Keep the momentum!",
                    "severity": "success"
                })
            else:
                intelligent_insights.append({
                    "category": "improvement",
                    "title": "Consistent Assessment Pacing",
                    "message": f"Recent assessment scores are stabilizing at an average of {round(avg_second, 1)}%. Target incremental gains with deeper smart note reviews.",
                    "severity": "info"
                })
        else:
            intelligent_insights.append({
                "category": "improvement",
                "title": "Progress Baseline Established",
                "message": f"Baseline quiz accuracy established at {avg_score}%. Complete additional assessments to track your growth trajectory.",
                "severity": "info"
            })

        # 3. Difficulty
        difficult_topics = [tp for tp, _, _ in tp_records if tp.total_attempts >= 2 and tp.accuracy_percentage < 65.0]
        if difficult_topics:
            d_tp = difficult_topics[0]
            d_name = next((t_name for tp, t_name, _ in tp_records if tp.id == d_tp.id), "Core Topic")
            intelligent_insights.append({
                "category": "difficulty",
                "title": f"Persistent Difficulty: {d_name}",
                "message": f"Over {d_tp.total_attempts} attempts, accuracy has averaged {round(d_tp.accuracy_percentage, 1)}%. Breaking down subtopics and generating point-wise notes will help resolve conceptual bottlenecks.",
                "severity": "warning"
            })
        elif weak_topics:
            intelligent_insights.append({
                "category": "difficulty",
                "title": "Subtopic Precision",
                "message": f"Occasional errors detected in {weak_topics[0]['topic_name']}. Review explanation cards in the quiz review tab to strengthen retention.",
                "severity": "info"
            })
        else:
            intelligent_insights.append({
                "category": "difficulty",
                "title": "Zero Persistent Obstacles",
                "message": "No recurring conceptual stumbling blocks found in your evaluated answer history. Excellent mastery across active topics!",
                "severity": "success"
            })

        # 4. Revision
        if weak_topics:
            w_top = weak_topics[0]
            intelligent_insights.append({
                "category": "revision",
                "title": f"Priority Revision: {w_top['topic_name']}",
                "message": f"Identified as priority revision topic ({w_top['accuracy_percentage']}% accuracy). Adaptive spaced review recommended.",
                "severity": "warning"
            })
        else:
            intelligent_insights.append({
                "category": "revision",
                "title": "Knowledge Retention Maintained",
                "message": "All practiced topics demonstrate high retention. Retake a mixed-difficulty quiz periodically to prevent memory decay.",
                "severity": "success"
            })

        # Personalized practical recommendation based on real activity
        top_subject = max(subject_performances, key=lambda x: x["average_accuracy"], default=None) if subject_performances else None
        weakest_tp = min(weak_topics, key=lambda x: x["accuracy_percentage"], default=None) if weak_topics else None

        if top_subject and weakest_tp and top_subject["average_accuracy"] >= 70.0:
            personalized_rec = (
                f"You are performing well in {top_subject['subject_name']} ({top_subject['average_accuracy']}% accuracy), "
                f"but your accuracy in {weakest_tp['topic_name']} ({weakest_tp['accuracy_percentage']}%) needs improvement. "
                f"Consider reviewing the smart notes for {weakest_tp['topic_name']} and attempting a targeted revision quiz."
            )
        elif top_subject and not weakest_tp and total_quizzes > 0:
            personalized_rec = (
                f"Outstanding work across your active modules! Your highest performing subject is {top_subject['subject_name']} "
                f"({top_subject['average_accuracy']}% accuracy). Challenge yourself by generating advanced difficulty quizzes or exploring emerging topics."
            )
        elif weakest_tp:
            personalized_rec = (
                f"Your current focus should be {weakest_tp['topic_name']} where accuracy is {weakest_tp['accuracy_percentage']}%. "
                f"Use the AI Study Assistant to clarify core definitions before taking your next quiz."
            )
        else:
            personalized_rec = (
                "Welcome to your Learning Analytics Dashboard! Start by uploading your study materials, generating smart notes, "
                "or taking an AI assessment quiz to unlock personalized insights and performance trends."
            )

        if not revision_recs:
            revision_recs.append("Complete topic quizzes across your enrolled subjects to uncover priority learning areas.")

        return {
            "total_quizzes_attempted": total_quizzes,
            "average_quiz_score": avg_score,
            "highest_quiz_score": highest_score,
            "learning_streak_days": streak_days,
            "total_study_hours": total_study_hours,
            "study_consistency_percentage": study_consistency,
            "strong_topics": strong_topics,
            "weak_topics": weak_topics,
            "recent_activity": recent_activity,
            "subject_performances": subject_performances,
            "quiz_score_trends": quiz_score_trends,
            "topic_completion_stats": topic_completion_stats,
            "intelligent_insights": intelligent_insights,
            "revision_recommendations": revision_recs,
            "personalized_recommendation": personalized_rec
        }

    @staticmethod
    async def generate_adaptive_study_plan(
        session: AsyncSession,
        user_id: str,
        title: str = "Personalized Adaptive Study Plan",
        daily_hours: float = 2.0,
        days_duration: int = 14,
        focus_weak_topics: bool = True,
        subject_ids: Optional[List[str]] = None,
        topic_ids: Optional[List[str]] = None,
        exam_date: Optional[str] = None,
        learning_priority: str = "balanced",
        include_revision: bool = True,
        include_quizzes: bool = True
    ) -> StudyPlan:
        """
        Phase 7: Generates a realistic, highly adaptive daily and weekly study plan.
        Intelligently allocates time based on topic difficulty, prioritizes verified weak topics,
        embeds spaced revision and practice quizzes, connects directly to Smart Notes and Quiz generator,
        and avoids creating unrealistic or overloading timetables.
        """
        # Archive previous active plans for this student
        prev_plans_stmt = select(StudyPlan).where(
            StudyPlan.user_id == user_id,
            StudyPlan.status == "active"
        )
        prev_plans_res = await session.execute(prev_plans_stmt)
        for prev in prev_plans_res.scalars().all():
            prev.status = "archived"

        # Calculate duration based on exam date if provided
        target_exam_date = None
        if exam_date:
            try:
                ed_dt = datetime.strptime(exam_date.strip(), "%Y-%m-%d").date()
                today_dt = datetime.now(timezone.utc).date()
                diff_days = (ed_dt - today_dt).days
                if diff_days > 0:
                    days_duration = min(max(diff_days, 3), 60)
                    target_exam_date = exam_date.strip()
            except Exception:
                pass

        # Fetch student's real topic performance (zero fabrication)
        tp_stmt = select(TopicPerformance, Topic).join(
            Topic, TopicPerformance.topic_id == Topic.id
        ).where(TopicPerformance.user_id == user_id)
        tp_res = await session.execute(tp_stmt)
        tp_records = tp_res.all()

        weak_topic_dict = {}
        proficient_topic_dict = {}
        for tp, t in tp_records:
            if tp.accuracy_percentage < 70.0 or tp.mastery_status in ["needs_practice", "developing"]:
                weak_topic_dict[t.id] = (tp, t)
            else:
                proficient_topic_dict[t.id] = (tp, t)

        # Determine target career role if any (Roadmap integration)
        prof_stmt = select(LearningProfile).where(LearningProfile.user_id == user_id).limit(1)
        prof_res = await session.execute(prof_stmt)
        user_profile = prof_res.scalars().first()
        target_career_id = user_profile.target_career_id if user_profile else None

        # Build candidate topics
        candidate_topic_objs: List[Topic] = []

        if topic_ids and len(topic_ids) > 0:
            top_stmt = select(Topic).where(Topic.id.in_(topic_ids))
            top_res = await session.execute(top_stmt)
            candidate_topic_objs = list(top_res.scalars().all())
        elif subject_ids and len(subject_ids) > 0:
            top_stmt = select(Topic).where(Topic.subject_id.in_(subject_ids))
            top_res = await session.execute(top_stmt)
            candidate_topic_objs = list(top_res.scalars().all())
        else:
            # Automatic intelligent candidate selection:
            # 1. Add verified weak topics first
            if focus_weak_topics or learning_priority in ["weak_topics_first", "balanced", "exam_prep"]:
                candidate_topic_objs.extend([t for _, t in weak_topic_dict.values()])

            # 2. Add career roadmap topics if user has a target career
            if target_career_id and learning_priority in ["career_skills", "balanced"]:
                roadmap_topics_stmt = select(Topic).join(
                    SubjectSkillMapping, SubjectSkillMapping.topic_id == Topic.id
                ).where(SubjectSkillMapping.career_role_id == target_career_id).limit(4)
                roadmap_topics_res = await session.execute(roadmap_topics_stmt)
                for t in roadmap_topics_res.scalars().all():
                    if t.id not in [ct.id for ct in candidate_topic_objs]:
                        candidate_topic_objs.append(t)

            # 3. Supplement with general core topics if needed
            if len(candidate_topic_objs) < 6:
                needed = 8 - len(candidate_topic_objs)
                supp_stmt = select(Topic).limit(needed)
                supp_res = await session.execute(supp_stmt)
                for t in supp_res.scalars().all():
                    if t.id not in [ct.id for ct in candidate_topic_objs]:
                        candidate_topic_objs.append(t)

        if not candidate_topic_objs:
            fallback_stmt = select(Topic).limit(8)
            fallback_res = await session.execute(fallback_stmt)
            candidate_topic_objs = list(fallback_res.scalars().all())

        # Create new active study plan
        plan = StudyPlan(
            user_id=user_id,
            title=title,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=days_duration),
            daily_hours_target=daily_hours,
            status="active",
            exam_date=target_exam_date,
            learning_priority=learning_priority,
            metadata_json=json.dumps({
                "focus_weak_topics": focus_weak_topics,
                "included_revision": include_revision,
                "included_quizzes": include_quizzes,
                "total_candidate_topics": len(candidate_topic_objs)
            })
        )
        session.add(plan)
        await session.flush()

        # Generate structured task items per topic with difficulty-based duration
        generated_tasks_pool = []
        for topic in candidate_topic_objs:
            is_weak = topic.id in weak_topic_dict
            is_proficient = topic.id in proficient_topic_dict

            # Difficulty-based duration & priority allocation
            if is_weak:
                difficulty = "hard"
                study_duration = 55
                revision_duration = 40
                quiz_duration = 35
                priority = "High"
            elif is_proficient:
                difficulty = "medium"
                study_duration = 45
                revision_duration = 30
                quiz_duration = 30
                priority = "Medium"
            else:
                difficulty = "medium"
                study_duration = 40
                revision_duration = 30
                quiz_duration = 25
                priority = "Medium"

            # 1. Conceptual Study Task (Smart Notes Integration)
            study_task = {
                "topic_id": topic.id,
                "topic_name": topic.name,
                "title": f"Conceptual Study & Note Review: {topic.name}",
                "description": f"Study textbook theory and review structured smart notes covering foundational principles of {topic.name}.",
                "duration_minutes": study_duration,
                "priority": priority,
                "task_type": "study",
                "difficulty_level": difficulty,
                "action_url": f"/dashboard/notes?topic={quote(topic.name)}"
            }
            generated_tasks_pool.append(study_task)

            # 2. Practice Quiz Task (AI Quiz Generator Integration)
            if include_quizzes:
                quiz_task = {
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "title": f"Practice Quiz Assessment: {topic.name}",
                    "description": f"Attempt an interactive assessment on {topic.name} to verify retention and enhance topic mastery status.",
                    "duration_minutes": quiz_duration,
                    "priority": priority,
                    "task_type": "quiz",
                    "difficulty_level": difficulty,
                    "action_url": f"/dashboard/quiz?topic_id={topic.id}"
                }
                generated_tasks_pool.append(quiz_task)

            # 3. Spaced Revision Session (Spaced repetition)
            if include_revision:
                revision_task = {
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "title": f"Targeted Spaced Revision: {topic.name}",
                    "description": f"Re-read key formulas, edge cases, and high-yield flash summaries for {topic.name} to prevent knowledge decay.",
                    "duration_minutes": revision_duration,
                    "priority": "High" if is_weak else "Medium",
                    "task_type": "revision",
                    "difficulty_level": difficulty,
                    "action_url": f"/dashboard/notes?topic={quote(topic.name)}&mode=revision"
                }
                generated_tasks_pool.append(revision_task)

        # Distribute tasks realistically across schedule days
        # Daily limit: max 2 to 3 tasks per day to prevent student burnout (realistic timetable)
        daily_max_tasks = 2 if daily_hours <= 2.0 else 3
        start_date = datetime.now(timezone.utc).date()
        pool_idx = 0

        for day in range(days_duration):
            current_date_str = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
            day_minutes_accumulated = 0

            # Special case for final 1-2 days before target exam: Exam Simulation
            if target_exam_date and (days_duration - day) <= 2:
                exam_sim_task = StudyTask(
                    study_plan_id=plan.id,
                    topic_id=candidate_topic_objs[0].id if candidate_topic_objs else None,
                    title="High-Yield Exam Simulation & Diagnostic Speed Test",
                    description="Comprehensive timed examination sprint covering all priority concepts and mistake diagnostics.",
                    scheduled_date=current_date_str,
                    duration_minutes=min(int(daily_hours * 60), 90),
                    priority="High",
                    task_type="exam_prep",
                    difficulty_level="hard",
                    action_url="/dashboard/quiz",
                    is_completed=False
                )
                session.add(exam_sim_task)
                continue

            for _ in range(daily_max_tasks):
                if pool_idx >= len(generated_tasks_pool):
                    break

                task_data = generated_tasks_pool[pool_idx]
                pool_idx += 1

                task_record = StudyTask(
                    study_plan_id=plan.id,
                    topic_id=task_data["topic_id"],
                    title=task_data["title"],
                    description=task_data["description"],
                    scheduled_date=current_date_str,
                    duration_minutes=task_data["duration_minutes"],
                    priority=task_data["priority"],
                    task_type=task_data["task_type"],
                    difficulty_level=task_data["difficulty_level"],
                    action_url=task_data["action_url"],
                    is_completed=False
                )
                session.add(task_record)
                day_minutes_accumulated += task_data["duration_minutes"]

                if day_minutes_accumulated >= (daily_hours * 60):
                    break

        await session.commit()
        return plan

    @staticmethod
    async def reschedule_missed_tasks(
        session: AsyncSession,
        user_id: str,
        plan_id: Optional[str] = None,
        start_from_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Intelligently identifies missed/overdue tasks and redistributes them across
        upcoming available schedule days without overloading any single day.
        """
        today_date = datetime.now(timezone.utc).date()
        today_str = today_date.strftime("%Y-%m-%d")

        # Find target study plan
        if plan_id:
            plan_stmt = select(StudyPlan).where(StudyPlan.id == plan_id, StudyPlan.user_id == user_id)
        else:
            plan_stmt = select(StudyPlan).where(
                StudyPlan.user_id == user_id,
                StudyPlan.status == "active"
            ).order_by(StudyPlan.created_at.desc()).limit(1)

        plan_res = await session.execute(plan_stmt)
        plan = plan_res.scalar_one_or_none()
        if not plan:
            return {"rescheduled_count": 0, "message": "No active study plan found."}

        # Query all incomplete tasks with scheduled_date < today_str
        missed_stmt = select(StudyTask).where(
            StudyTask.study_plan_id == plan.id,
            StudyTask.is_completed == False,
            StudyTask.scheduled_date < today_str
        ).order_by(StudyTask.scheduled_date.asc())
        missed_res = await session.execute(missed_stmt)
        missed_tasks = missed_res.scalars().all()

        if not missed_tasks:
            return {
                "rescheduled_count": 0,
                "message": "All past scheduled tasks are completed. No overdue tasks to reschedule."
            }

        # Query future tasks to avoid overloading days
        future_stmt = select(StudyTask).where(
            StudyTask.study_plan_id == plan.id,
            StudyTask.scheduled_date >= today_str
        )
        future_res = await session.execute(future_stmt)
        future_tasks = future_res.scalars().all()

        tasks_per_day: Dict[str, int] = {}
        for ft in future_tasks:
            tasks_per_day[ft.scheduled_date] = tasks_per_day.get(ft.scheduled_date, 0) + 1

        # Redistribution algorithm: allocate max 2 tasks per day
        target_start = datetime.strptime(start_from_date, "%Y-%m-%d").date() if start_from_date else today_date
        current_check_date = target_start
        rescheduled_items = []

        for task in missed_tasks:
            # Find next date with capacity (< 2 tasks)
            while tasks_per_day.get(current_check_date.strftime("%Y-%m-%d"), 0) >= 2:
                current_check_date += timedelta(days=1)

            dest_date_str = current_check_date.strftime("%Y-%m-%d")
            old_date = task.scheduled_date
            task.scheduled_date = dest_date_str
            task.priority = "High"  # Missed tasks are automatically elevated
            task.notes = f"Automatically rebalanced from {old_date} by Adaptive Planner."
            tasks_per_day[dest_date_str] = tasks_per_day.get(dest_date_str, 0) + 1

            rescheduled_items.append({
                "task_id": task.id,
                "title": task.title,
                "previous_date": old_date,
                "new_date": dest_date_str
            })

        await session.commit()
        return {
            "rescheduled_count": len(rescheduled_items),
            "message": f"Successfully rebalanced {len(rescheduled_items)} missed tasks into a realistic, non-overloading schedule.",
            "rescheduled_tasks": rescheduled_items
        }

    @staticmethod
    async def get_adaptive_planner_recommendations(
        session: AsyncSession,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Analyzes real student performance data to generate proactive, practical recommendations
        for the study planner (weak topic revisions, quiz retakes, exam pacing).
        """
        recommendations = []
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # 1. Check recent quiz scores (< 70% accuracy)
        recent_attempts_stmt = select(QuizAttempt, Quiz).join(
            Quiz, QuizAttempt.quiz_id == Quiz.id
        ).where(QuizAttempt.user_id == user_id).order_by(QuizAttempt.completed_at.desc()).limit(5)
        recent_res = await session.execute(recent_attempts_stmt)

        for attempt, quiz in recent_res.all():
            if attempt.percentage < 70.0 and quiz.topic_id:
                topic_stmt = select(Topic).where(Topic.id == quiz.topic_id)
                top_res = await session.execute(topic_stmt)
                topic = top_res.scalar_one_or_none()
                top_name = topic.name if topic else "Curriculum Topic"

                recommendations.append({
                    "id": f"rec-rev-{attempt.id[:8]}",
                    "recommendation_type": "weak_topic_revision",
                    "topic_id": quiz.topic_id,
                    "topic_name": top_name,
                    "reason": f"You scored {attempt.percentage:.1f}% on a recent {top_name} assessment.",
                    "suggested_action": f"Schedule a 45-minute Smart Notes deep-dive and spaced revision session for {top_name}.",
                    "estimated_duration_minutes": 45,
                    "priority": "High"
                })
                break  # one targeted quiz recommendation is enough

        # 2. Check overdue tasks in active plan
        active_plan_stmt = select(StudyPlan).where(
            StudyPlan.user_id == user_id,
            StudyPlan.status == "active"
        ).order_by(StudyPlan.created_at.desc()).limit(1)
        active_res = await session.execute(active_plan_stmt)
        active_plan = active_res.scalar_one_or_none()

        if active_plan:
            overdue_stmt = select(func.count(StudyTask.id)).where(
                StudyTask.study_plan_id == active_plan.id,
                StudyTask.is_completed == False,
                StudyTask.scheduled_date < today_str
            )
            overdue_count = (await session.execute(overdue_stmt)).scalar() or 0

            if overdue_count > 0:
                recommendations.append({
                    "id": "rec-rebalance-missed",
                    "recommendation_type": "missed_tasks_rebalance",
                    "topic_id": None,
                    "topic_name": None,
                    "reason": f"You have {overdue_count} overdue task(s) from past dates.",
                    "suggested_action": "Use the one-click Adaptive Rebalance to redistribute missed tasks without exceeding daily study targets.",
                    "estimated_duration_minutes": 0,
                    "priority": "High"
                })

            # 3. Check exam countdown
            if active_plan.exam_date:
                try:
                    ed_dt = datetime.strptime(active_plan.exam_date, "%Y-%m-%d").date()
                    now_dt = datetime.now(timezone.utc).date()
                    countdown = (ed_dt - now_dt).days
                    if 0 < countdown <= 14:
                        recommendations.append({
                            "id": "rec-exam-pacing",
                            "recommendation_type": "exam_pacing",
                            "topic_id": None,
                            "topic_name": None,
                            "reason": f"Target examination date is in {countdown} day(s).",
                            "suggested_action": "Prioritize high-yield mock quizzes and final formula review sessions.",
                            "estimated_duration_minutes": 60,
                            "priority": "High"
                        })
                except Exception:
                    pass

        return recommendations

    @staticmethod
    async def get_planner_progress(
        session: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Calculates real-time daily and weekly progress, schedule adherence rate,
        learning streak, and upcoming exam countdown.
        """
        today_date = datetime.now(timezone.utc).date()
        today_str = today_date.strftime("%Y-%m-%d")
        week_ago_str = (today_date - timedelta(days=7)).strftime("%Y-%m-%d")

        active_plan_stmt = select(StudyPlan).where(
            StudyPlan.user_id == user_id,
            StudyPlan.status == "active"
        ).order_by(StudyPlan.created_at.desc()).limit(1)
        active_res = await session.execute(active_plan_stmt)
        plan = active_res.scalar_one_or_none()

        if not plan:
            return {
                "today_date": today_str,
                "today_total_tasks": 0,
                "today_completed_tasks": 0,
                "today_minutes_scheduled": 0,
                "today_minutes_completed": 0,
                "week_adherence_percentage": 0.0,
                "overdue_tasks_count": 0,
                "exam_countdown_days": None,
                "learning_streak_days": 0,
                "weak_topics_covered_count": 0
            }

        # Today's tasks
        today_tasks_stmt = select(StudyTask).where(
            StudyTask.study_plan_id == plan.id,
            StudyTask.scheduled_date == today_str
        )
        today_res = await session.execute(today_tasks_stmt)
        today_tasks = today_res.scalars().all()

        today_completed = sum(1 for t in today_tasks if t.is_completed)
        today_scheduled_mins = sum(t.duration_minutes for t in today_tasks)
        today_completed_mins = sum(t.duration_minutes for t in today_tasks if t.is_completed)

        # Weekly adherence (tasks scheduled between week_ago_str and today_str)
        week_tasks_stmt = select(StudyTask).where(
            StudyTask.study_plan_id == plan.id,
            StudyTask.scheduled_date >= week_ago_str,
            StudyTask.scheduled_date <= today_str
        )
        week_res = await session.execute(week_tasks_stmt)
        week_tasks = week_res.scalars().all()
        week_completed = sum(1 for t in week_tasks if t.is_completed)
        week_adherence = round((week_completed / len(week_tasks)) * 100.0, 1) if week_tasks else 100.0

        # Overdue tasks
        overdue_stmt = select(func.count(StudyTask.id)).where(
            StudyTask.study_plan_id == plan.id,
            StudyTask.is_completed == False,
            StudyTask.scheduled_date < today_str
        )
        overdue_count = (await session.execute(overdue_stmt)).scalar() or 0

        # Exam countdown
        countdown = None
        if plan.exam_date:
            try:
                ed_dt = datetime.strptime(plan.exam_date, "%Y-%m-%d").date()
                countdown = max(0, (ed_dt - today_date).days)
            except Exception:
                pass

        # Weak topics practiced in active plan
        weak_covered_stmt = select(func.count(func.distinct(StudyTask.topic_id))).where(
            StudyTask.study_plan_id == plan.id,
            StudyTask.is_completed == True,
            StudyTask.topic_id.isnot(None)
        )
        weak_covered = (await session.execute(weak_covered_stmt)).scalar() or 0

        # Streak calculation from quiz attempts
        attempts_stmt = select(QuizAttempt.completed_at).where(
            QuizAttempt.user_id == user_id
        ).order_by(QuizAttempt.completed_at.desc())
        att_res = await session.execute(attempts_stmt)
        attempt_dates = set()
        for dt_val in att_res.scalars().all():
            if dt_val:
                attempt_dates.add(dt_val.date())

        streak = 0
        curr_check = today_date
        while curr_check in attempt_dates:
            streak += 1
            curr_check -= timedelta(days=1)
        if streak == 0 and (today_date - timedelta(days=1)) in attempt_dates:
            curr_check = today_date - timedelta(days=1)
            while curr_check in attempt_dates:
                streak += 1
                curr_check -= timedelta(days=1)

        return {
            "today_date": today_str,
            "today_total_tasks": len(today_tasks),
            "today_completed_tasks": today_completed,
            "today_minutes_scheduled": today_scheduled_mins,
            "today_minutes_completed": today_completed_mins,
            "week_adherence_percentage": week_adherence,
            "overdue_tasks_count": overdue_count,
            "exam_countdown_days": countdown,
            "learning_streak_days": streak,
            "weak_topics_covered_count": weak_covered
        }

intelligence_engine = EduPathIntelligenceEngine()

