"""
Personalized Learning Service for EduPath AI 2.0.
Provides:
- 6 Explanation Depth Modes (beginner, intermediate, advanced, step_by_step, real_world, exam_oriented)
- Adaptive Quiz Generation targeting historical student mistakes
- Spaced Repetition Revision Scheduler (Ebbinghaus forgetting curve: 1d, 3d, 7d, 14d, 30d)
- Traceable, evidence-backed learning recommendations
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from app.models.models import (
    Topic, Subject, QuizAttempt, QuizMistake, TopicPerformance,
    StudyPlan, StudyTask, LearningProfile
)
from app.services.gemini_service import gemini_service

logger = logging.getLogger("edupath.personalized_learning")

EXPLANATION_MODES = {
    "beginner": {
        "title": "Beginner / Conceptual Intuition",
        "instruction": "Explain using intuitive everyday analogies, simple language, and zero intimidating jargon. Focus on the core 'why' and foundational mental models."
    },
    "intermediate": {
        "title": "Intermediate / Academic Standard",
        "instruction": "Standard university-level coverage with formal terminology, system architecture flow, component interactions, and common edge cases."
    },
    "advanced": {
        "title": "Advanced / Systems Engineering",
        "instruction": "Deep technical analysis for senior engineers: mathematical proofs, invariant analysis, kernel/OS interactions, lock contention, memory layout, and asymptotic tradeoffs."
    },
    "step_by_step": {
        "title": "Step-by-Step / Procedural Breakdown",
        "instruction": "Granular numbered walkthrough of execution mechanics, trace tables, input-to-output state transitions, and boundary checks."
    },
    "real_world": {
        "title": "Real-World / Industry Application",
        "instruction": "Production case study: enterprise scale, high availability, microservices, incident troubleshooting, and industry tooling used in production."
    },
    "exam_oriented": {
        "title": "Exam-Oriented / High-Yield Review",
        "instruction": "Exam-focused summary: high-probability test questions, mark-scoring criteria, critical diagrams to sketch, definitions, and common student pitfalls to avoid."
    }
}

EBBINGHAUS_INTERVALS_DAYS = [1, 3, 7, 14, 30]

class PersonalizedLearningService:

    @staticmethod
    async def generate_explanation(
        topic_name: str,
        concept_name: Optional[str] = None,
        mode: str = "step_by_step",
        subject_name: Optional[str] = None,
        context_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates targeted concept explanation across the 6 depth modes.
        """
        mode_config = EXPLANATION_MODES.get(mode.lower(), EXPLANATION_MODES["step_by_step"])
        target_concept = concept_name or topic_name
        subject_label = subject_name or "Computer Science"

        prompt = f"""
You are EduPath AI Expert Pedagogical Mentor.
Subject: {subject_label}
Topic: {topic_name}
Target Concept: {target_concept}
Explanation Mode: {mode_config['title']}
Mode Guideline: {mode_config['instruction']}

{f'Context Material: {context_notes[:2500]}' if context_notes else ''}

Generate a clear, high-quality Markdown explanation perfectly tailored to this mode.
Include:
1. Clear Executive Hook & Mental Model
2. In-Depth Explanation adhering strictly to the mode's depth
3. Practical Concrete Code/Diagram Example where relevant
4. Common Misconceptions & Pitfalls
5. Quick Self-Check Question with Answer
"""
        if gemini_service.is_configured:
            try:
                response = gemini_service.chat_model.generate_content(prompt)
                return {
                    "mode": mode,
                    "mode_title": mode_config["title"],
                    "concept": target_concept,
                    "topic_name": topic_name,
                    "content": response.text.strip()
                }
            except Exception as e:
                logger.error(f"Gemini explanation error: {e}. Falling back to deterministic mode content.")

        # High-Quality Structured Fallback
        fallback_content = f"""# {target_concept} – {mode_config['title']}

## Core Concept Hook
When working with **{topic_name}** ({subject_label}), understanding **{target_concept}** is essential for designing resilient software systems.

### 1. In-Depth Breakdown ({mode.replace('_', ' ').title()})
{mode_config['instruction']}

- **State & Invariants**: Every valid execution of {target_concept} maintains predictable pre-conditions and post-conditions.
- **Resource Management**: System overhead (CPU, I/O, memory allocations) must be optimized to prevent latency degradation.
- **Failure Resilience**: Edge case boundary violations must be gracefully caught and handled.

### 2. Concrete Architectural Pattern
```text
[Client / Query Driver]
        │  1. Request / Invariant Check
        ▼
[Execution Pipeline: {target_concept}]
        │  2. Deterministic Transformation
        ▼
[Guaranteed Result & State Consistency]
```

### 3. Common Student Pitfalls & Misconceptions
- Failing to verify null/boundary input parameters.
- Confusing theoretical best-case complexity with practical p99 production latency.
- Neglecting concurrency isolation under high transaction throughput.

### 4. Self-Review Check
**Question**: What is the primary invariant preserved by {target_concept}?  
**Answer**: Deterministic state transitions and predictable asymptotic complexity bounds.
"""
        return {
            "mode": mode,
            "mode_title": mode_config["title"],
            "concept": target_concept,
            "topic_name": topic_name,
            "content": fallback_content
        }

    @staticmethod
    async def generate_adaptive_quiz(
        session: AsyncSession,
        user_id: str,
        topic_id: str,
        difficulty: str = "medium",
        question_count: int = 5
    ) -> Dict[str, Any]:
        """
        Generates an adaptive quiz tailored specifically to the user's past mistakes,
        error categories, and demonstrated weaknesses.
        """
        topic_stmt = select(Topic).where(Topic.id == topic_id)
        topic_res = await session.execute(topic_stmt)
        topic = topic_res.scalar_one_or_none()
        if not topic:
            raise ValueError(f"Topic {topic_id} not found")

        # Fetch user's historical mistakes for this topic or related topics
        mistakes_stmt = select(QuizMistake).where(
            QuizMistake.user_id == user_id,
            QuizMistake.topic_id == topic_id
        ).order_by(QuizMistake.repeated_count.desc(), QuizMistake.created_at.desc()).limit(10)
        mistakes_res = await session.execute(mistakes_stmt)
        past_mistakes = mistakes_res.scalars().all()

        # Fetch current topic performance
        tp_stmt = select(TopicPerformance).where(
            TopicPerformance.user_id == user_id,
            TopicPerformance.topic_id == topic_id
        ).limit(1)
        tp_res = await session.execute(tp_stmt)
        tp = tp_res.scalars().first()

        accuracy = tp.accuracy_percentage if tp else 50.0
        # Automatically calibrate difficulty if student accuracy is low
        effective_difficulty = difficulty
        if accuracy < 50.0:
            effective_difficulty = "beginner"
        elif accuracy >= 80.0 and difficulty == "medium":
            effective_difficulty = "advanced"

        # Construct adaptive prompt emphasizing mistake categories
        mistake_context = ""
        error_categories = set()
        if past_mistakes:
            mistake_context = "PAST STUDENT MISTAKES TO TARGET IN THIS ADAPTIVE QUIZ:\n"
            for idx, m in enumerate(past_mistakes[:4]):
                error_categories.add(m.error_category)
                mistake_context += f"- Error in {m.error_category}: Student answered '{m.user_response[:60]}' instead of '{m.correct_answer[:60]}'. Suggested fix: {m.suggested_fix or 'Reinforce foundational mechanics.'}\n"

        adaptive_notes = f"""
Adaptive Generation Rationale:
- Student historical accuracy on {topic.name}: {accuracy}% ({tp.total_attempts if tp else 0} prior attempts).
- Primary error patterns detected: {', '.join(error_categories) if error_categories else 'General topic baseline'}.
{mistake_context}
"""
        generated_questions = await gemini_service.generate_quiz(
            source_text=adaptive_notes,
            topic_name=topic.name,
            difficulty=effective_difficulty,
            question_count=question_count,
            question_types=["mcq", "multiple_select", "scenario_based"]
        )

        return {
            "topic_id": topic.id,
            "topic_name": topic.name,
            "adapted_for_user": True,
            "calibrated_difficulty": effective_difficulty,
            "historical_accuracy": accuracy,
            "targeted_error_categories": list(error_categories),
            "generation_rationale": (
                f"Generated {question_count} adaptive questions calibrated to {effective_difficulty} difficulty "
                f"addressing {len(past_mistakes)} identified historical mistake patterns in {topic.name}."
            ),
            "questions": generated_questions
        }

    @staticmethod
    async def schedule_spaced_repetition(
        session: AsyncSession,
        user_id: str,
        topic_id: str,
        latest_percentage: float
    ) -> Dict[str, Any]:
        """
        Applies Hermann Ebbinghaus forgetting curve intervals: 1d, 3d, 7d, 14d, 30d.
        Schedules revision study tasks and generates traceable evidence notifications.
        """
        # Fetch or initialize active study plan
        plan_stmt = select(StudyPlan).where(
            StudyPlan.user_id == user_id,
            StudyPlan.status == "active"
        ).order_by(StudyPlan.start_date.desc()).limit(1)
        plan_res = await session.execute(plan_stmt)
        plan = plan_res.scalars().first()

        if not plan:
            plan = StudyPlan(
                user_id=user_id,
                title="Personalized Spaced Repetition Plan",
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=30),
                daily_hours_target=1.5,
                status="active"
            )
            session.add(plan)
            await session.flush()

        # Fetch topic performance for count of attempts
        tp_stmt = select(TopicPerformance, Topic.name).join(
            Topic, TopicPerformance.topic_id == Topic.id
        ).where(
            TopicPerformance.user_id == user_id,
            TopicPerformance.topic_id == topic_id
        ).limit(1)
        tp_res = await session.execute(tp_stmt)
        tp_row = tp_res.first()
        topic_name = tp_row[1] if tp_row else "Core Topic"
        attempts = tp_row[0].total_attempts if tp_row else 1

        # Select interval based on attempt count and score
        if latest_percentage < 60.0:
            interval_days = 1  # Immediate 1-day review for struggling concepts
        else:
            idx = min(attempts - 1, len(EBBINGHAUS_INTERVALS_DAYS) - 1)
            interval_days = EBBINGHAUS_INTERVALS_DAYS[max(0, idx)]

        target_date = (datetime.now(timezone.utc).date() + timedelta(days=interval_days)).strftime("%Y-%m-%d")

        # Check if a study task already exists for this topic on that date
        task_stmt = select(StudyTask).where(
            StudyTask.study_plan_id == plan.id,
            StudyTask.topic_id == topic_id,
            StudyTask.scheduled_date == target_date
        ).limit(1)
        task_res = await session.execute(task_stmt)
        task = task_res.scalars().first()

        task_title = f"Spaced Repetition Review: {topic_name} (Interval {interval_days}d)"
        task_desc = (
            f"Ebbinghaus Day-{interval_days} recall review. Your latest quiz accuracy was {latest_percentage}%. "
            f"Review key formulas, mistake notes, and attempt 3 adaptive practice questions."
        )

        if not task:
            task = StudyTask(
                study_plan_id=plan.id,
                topic_id=topic_id,
                title=task_title,
                description=task_desc,
                scheduled_date=target_date,
                duration_minutes=30,
                priority="High" if latest_percentage < 60.0 else "Medium",
                is_completed=False
            )
            session.add(task)
        else:
            task.title = task_title
            task.description = task_desc
            task.priority = "High" if latest_percentage < 60.0 else "Medium"

        return {
            "topic_id": topic_id,
            "topic_name": topic_name,
            "interval_days": interval_days,
            "scheduled_date": target_date,
            "task_id": task.id,
            "evidence_reason": f"Scheduled interval {interval_days}d because latest score was {latest_percentage}% on attempt #{attempts}."
        }

    @staticmethod
    async def get_due_revisions(
        session: AsyncSession,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all upcoming and due spaced repetition tasks for the user with status categorization.
        """
        today_str = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")

        stmt = select(StudyTask, Topic.name, Subject.name).join(
            StudyPlan, StudyTask.study_plan_id == StudyPlan.id
        ).join(
            Topic, StudyTask.topic_id == Topic.id, isouter=True
        ).join(
            Subject, Topic.subject_id == Subject.id, isouter=True
        ).where(
            StudyPlan.user_id == user_id
        ).order_by(StudyTask.scheduled_date.asc())

        res = await session.execute(stmt)
        rows = res.all()

        revisions = []
        for task, topic_name, subject_name in rows:
            sched_date = task.scheduled_date
            if task.is_completed:
                status = "completed"
            elif sched_date < today_str:
                status = "overdue"
            elif sched_date == today_str:
                status = "due_today"
            else:
                status = "upcoming"

            revisions.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "topic_id": task.topic_id,
                "topic_name": topic_name or "Curriculum Review",
                "subject_name": subject_name or "General",
                "scheduled_date": task.scheduled_date,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "is_completed": task.is_completed,
                "status": status
            })

        return revisions

personalized_learning_service = PersonalizedLearningService()
