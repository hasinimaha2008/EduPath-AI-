import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.models import (
    User, Subject, Topic, Quiz, Question, QuizAttempt, UserAnswer,
    TopicPerformance, CareerRole, Skill, SubjectSkillMapping,
    CareerSkillRequirement, UserSkill, CareerRecommendation,
    SkillGap, CareerRoadmap, RoadmapMilestone, StudyPlan, StudyTask
)
from app.services.gemini_service import gemini_service

class EduPathIntelligenceEngine:
    """
    Central EduPath Intelligence Engine connecting learning activities, quiz results,
    topic performance, academic-to-industry skill mapping, career recommendations,
    skill gaps, and adaptive study planning.
    """

    @staticmethod
    async def evaluate_quiz_submission(
        session: AsyncSession,
        user_id: str,
        quiz_id: str,
        user_answers: List[Dict[str, str]],
        time_taken_seconds: int = 0
    ) -> Dict[str, Any]:
        """
        Evaluates submitted quiz, updates topic performance with repeated evidence rules,
        synchronizes user skills, and recalculates career intelligence.
        """
        # Fetch quiz and questions
        quiz_stmt = select(Quiz).where(Quiz.id == quiz_id)
        quiz_res = await session.execute(quiz_stmt)
        quiz = quiz_res.scalar_one_or_none()
        if not quiz:
            raise ValueError("Quiz not found")

        q_stmt = select(Question).where(Question.quiz_id == quiz_id)
        q_res = await session.execute(q_stmt)
        questions = q_res.scalars().all()
        q_map = {q.id: q for q in questions}

        total_score = 0.0
        max_score = sum(q.points for q in questions) or 1.0
        evaluated_answers = []

        answer_lookup = {a["question_id"]: a["user_response"] for a in user_answers}

        for q in questions:
            user_resp = answer_lookup.get(q.id, "").strip()
            # Case-insensitive comparison for MCQs
            is_correct = (user_resp.lower() == q.correct_answer.strip().lower())
            pts = q.points if is_correct else 0.0
            total_score += pts

            evaluated_answers.append({
                "question": q,
                "user_response": user_resp,
                "is_correct": is_correct,
                "score_awarded": pts,
                "feedback": q.explanation
            })

        percentage = round((total_score / max_score) * 100.0, 1)

        # Record Quiz Attempt
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

        for ea in evaluated_answers:
            ua = UserAnswer(
                attempt_id=attempt.id,
                question_id=ea["question"].id,
                user_response=ea["user_response"],
                is_correct=ea["is_correct"],
                score_awarded=ea["score_awarded"],
                feedback=ea["feedback"]
            )
            session.add(ua)

        # Update Topic Performance if linked to a topic
        topic_id = quiz.topic_id
        subject_id = quiz.subject_id

        if topic_id:
            tp_stmt = select(TopicPerformance).where(
                TopicPerformance.user_id == user_id,
                TopicPerformance.topic_id == topic_id
            )
            tp_res = await session.execute(tp_stmt)
            tp = tp_res.scalar_one_or_none()

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

            # Update linked skills via SubjectSkillMapping
            await EduPathIntelligenceEngine._sync_topic_to_user_skills(session, user_id, topic_id, tp.accuracy_percentage)

        # Re-evaluate career recommendations and gaps
        await EduPathIntelligenceEngine.recalculate_career_intelligence(session, user_id)

        await session.commit()

        return {
            "attempt_id": attempt.id,
            "quiz_id": quiz_id,
            "score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "time_taken_seconds": time_taken_seconds,
            "completed_at": attempt.completed_at,
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
        """
        Mastery requires repeated evidence:
        - Mastered: >= 90% accuracy with at least 3 attempts
        - Proficient: >= 75% accuracy with at least 2 attempts
        - Developing: 50% - 74% accuracy
        - Needs Practice: < 50% accuracy or single low attempt
        """
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
        """
        Updates verified user skill proficiency based on topic assessment results.
        """
        # Find skills mapped to this topic
        map_stmt = select(SubjectSkillMapping).where(SubjectSkillMapping.topic_id == topic_id)
        map_res = await session.execute(map_stmt)
        mappings = map_res.scalars().all()

        for m in mappings:
            us_stmt = select(UserSkill).where(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == m.skill_id
            )
            us_res = await session.execute(us_stmt)
            user_skill = us_res.scalar_one_or_none()

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
                # Weighted moving average for proficiency
                user_skill.proficiency_level = round((user_skill.proficiency_level * 0.4) + (accuracy * 0.6), 1)
                user_skill.source = "demonstrated"
                user_skill.verified = True
                user_skill.evidence_notes = f"Updated via quiz evaluation in competency: {m.competency_name}"
                user_skill.last_evaluated_at = datetime.now(timezone.utc)

    @staticmethod
    async def recalculate_career_intelligence(session: AsyncSession, user_id: str):
        """
        Recomputes career role recommendations and skill gaps based on actual demonstrated competencies.
        """
        # Fetch all career roles
        roles_stmt = select(CareerRole)
        roles_res = await session.execute(roles_stmt)
        roles = roles_res.scalars().all()

        # Fetch user's skills
        us_stmt = select(UserSkill).where(UserSkill.user_id == user_id)
        us_res = await session.execute(us_stmt)
        user_skills = {us.skill_id: us for us in us_res.scalars().all()}

        # Fetch skill details
        skills_stmt = select(Skill)
        skills_res = await session.execute(skills_stmt)
        skills_dict = {s.id: s for s in skills_res.scalars().all()}

        for role in roles:
            # Fetch required skills for this role
            req_stmt = select(CareerSkillRequirement).where(CareerSkillRequirement.career_role_id == role.id)
            req_res = await session.execute(req_stmt)
            requirements = req_res.scalars().all()

            if not requirements:
                continue

            total_weight = 0.0
            earned_weight = 0.0
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
                    user_prof = user_skill.proficiency_level
                    earned_weight += min(user_prof, 100.0) * importance_multiplier
                    if user_prof >= req.min_proficiency:
                        matching_skills.append(skill_name)
                    else:
                        missing_skills.append(f"{skill_name} (Needs improvement: {user_prof}% vs {req.min_proficiency}% req)")
                else:
                    missing_skills.append(skill_name)

                # Upsert Skill Gap
                status = "missing"
                if user_skill:
                    status = "existing" if user_skill.proficiency_level >= req.min_proficiency else "needs_improvement"

                priority = "High" if req.importance_level == "Core" and status != "existing" else "Medium"
                rec_text = f"Study foundational modules and practice quizzes for {skill_name} to meet {role.title} standards."

                sg_stmt = select(SkillGap).where(
                    SkillGap.user_id == user_id,
                    SkillGap.career_role_id == role.id,
                    SkillGap.skill_id == skill_id
                )
                sg_res = await session.execute(sg_stmt)
                sg = sg_res.scalar_one_or_none()

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

            match_score = round((earned_weight / total_weight) * 100.0, 1) if total_weight > 0 else 0.0

            rationale = (
                f"Calculated readiness of {match_score}% based on your academic quiz assessments. "
                f"You have demonstrated {len(matching_skills)} required competencies, with {len(missing_skills)} "
                f"priority skill gaps identified for target role readiness."
            )

            # Upsert Recommendation
            rec_stmt = select(CareerRecommendation).where(
                CareerRecommendation.user_id == user_id,
                CareerRecommendation.career_role_id == role.id
            )
            rec_res = await session.execute(rec_stmt)
            rec = rec_res.scalar_one_or_none()

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
    async def get_user_analytics(session: AsyncSession, user_id: str) -> Dict[str, Any]:
        """
        Calculates verified learning analytics from actual user quiz attempts and topic performances.
        Never fabricates sample stats.
        """
        # Quiz attempts stats
        attempts_stmt = select(QuizAttempt).where(QuizAttempt.user_id == user_id).order_by(QuizAttempt.completed_at.desc())
        attempts_res = await session.execute(attempts_stmt)
        attempts = attempts_res.scalars().all()

        total_quizzes = len(attempts)
        avg_score = round(sum(a.percentage for a in attempts) / total_quizzes, 1) if total_quizzes > 0 else 0.0

        # Topic performances
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
                "accuracy_percentage": tp.accuracy_percentage,
                "mastery_status": tp.mastery_status,
                "last_practiced_at": tp.last_practiced_at
            }
            if tp.mastery_status in ["proficient", "mastered"] or tp.accuracy_percentage >= 75.0:
                strong_topics.append(item)
            else:
                weak_topics.append(item)
                revision_recs.append(f"Review core principles for {topic_name} (current accuracy: {tp.accuracy_percentage}%)")

        # Activity by day
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

        if not revision_recs:
            revision_recs.append("Complete topic quizzes across DBMS and Systems Architecture to uncover priority learning areas.")

        return {
            "total_quizzes_attempted": total_quizzes,
            "average_quiz_score": avg_score,
            "learning_streak_days": streak_days,
            "total_study_hours": total_study_hours,
            "strong_topics": strong_topics,
            "weak_topics": weak_topics,
            "recent_activity": recent_activity,
            "revision_recommendations": revision_recs
        }

    @staticmethod
    async def generate_adaptive_study_plan(
        session: AsyncSession,
        user_id: str,
        title: str = "Personalized Adaptive Study Plan",
        daily_hours: float = 2.0,
        days_duration: int = 14
    ) -> StudyPlan:
        """
        Creates a realistic, non-overlapping daily and weekly study plan
        prioritizing verified weak topics and missing career skills.
        """
        # Fetch weak topics
        weak_stmt = select(TopicPerformance, Topic).join(
            Topic, TopicPerformance.topic_id == Topic.id
        ).where(
            TopicPerformance.user_id == user_id,
            TopicPerformance.mastery_status.in_(["needs_practice", "developing"])
        )
        weak_res = await session.execute(weak_stmt)
        weak_pairs = weak_res.all()

        # If user has no weak topics yet, pull fundamental curriculum topics
        candidate_topics = []
        if weak_pairs:
            candidate_topics = [(tp.topic_id, t.name, "High") for tp, t in weak_pairs]
        else:
            top_stmt = select(Topic).limit(6)
            top_res = await session.execute(top_stmt)
            candidate_topics = [(t.id, t.name, "Medium") for t in top_res.scalars().all()]

        # Create Study Plan
        plan = StudyPlan(
            user_id=user_id,
            title=title,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=days_duration),
            daily_hours_target=daily_hours,
            status="active"
        )
        session.add(plan)
        await session.flush()

        # Generate realistic tasks without schedule collisions
        start_date = datetime.now(timezone.utc).date()
        topic_idx = 0

        for day in range(min(days_duration, 14)):
            current_date = (start_date + timedelta(days=day)).strftime("%Y-%m-%d")
            
            # 2 focused tasks per day
            for task_slot in range(2):
                if candidate_topics:
                    topic_id, topic_name, priority = candidate_topics[topic_idx % len(candidate_topics)]
                    topic_idx += 1
                else:
                    topic_id, topic_name, priority = None, "Curriculum Review", "Medium"

                if task_slot == 0:
                    task_title = f"Conceptual Study & Note Generation: {topic_name}"
                    task_desc = f"Review textbook/uploaded notes and generate structured revision notes for {topic_name}."
                    duration = 50
                else:
                    task_title = f"Knowledge Evaluation & Quiz Practice: {topic_name}"
                    task_desc = f"Attempt medium/hard quiz on {topic_name} to strengthen mastery status and verify retention."
                    duration = 40

                task = StudyTask(
                    study_plan_id=plan.id,
                    topic_id=topic_id,
                    title=task_title,
                    description=task_desc,
                    scheduled_date=current_date,
                    duration_minutes=duration,
                    priority=priority,
                    is_completed=False
                )
                session.add(task)

        await session.commit()
        return plan

intelligence_engine = EduPathIntelligenceEngine()
