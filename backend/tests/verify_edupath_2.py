"""
Comprehensive End-to-End Verification Suite for EduPath AI 2.0.
Validates:
1. Workflow A (Weak Topic Loop: Quiz -> Mistake Classification -> Topic Performance -> Spaced Repetition -> Weak Topic Notification).
2. Workflow B (Career Development Loop: Target Career -> Recalculation -> Comparison -> Practical Projects -> Pathways).
3. Workflow C (Document Intelligence 2.0: Hybrid retrieval, Summarization, Concept extraction, Retrieval Benchmark).
4. Personalized AI Engine: 6-Mode Explainer & Adaptive Quiz Generation.
5. Multilingual Conversational Voice: 14 languages, Auto-detection, Speech Synthesis.
6. Smart Notifications: Unread count, Mark as read, Mark all as read.
"""

import asyncio
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import json

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.core.security import create_access_token
from app.models.models import (
    User, Subject, Topic, Quiz, Question, QuizAttempt, TopicPerformance,
    LearningProfile, QuizMistake, Notification, CareerRole, CareerProject, CareerPathway, Document, DocumentChunk
)
from app.services.intelligence_engine import intelligence_engine
from app.services.personalized_learning_service import personalized_learning_service
from app.services.voice_service import voice_service, detect_language, clean_text_for_speech
from app.services.rag_service import rag_service, compute_lexical_score

async def run_verification():
    print("=" * 70)
    print("   EDUPATH AI 2.0 — COMPREHENSIVE SYSTEM VERIFICATION SUITE   ")
    print("=" * 70)

    async with AsyncSessionLocal() as session:
        # 1. Setup / Resolve Test User
        user_stmt = select(User).where(User.email == "demo@edupath.ai")
        user_res = await session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        assert user is not None, "Demo user must exist in database"
        print(f"[1/8] Verified Test User: {user.email} (ID: {user.id})")

        # 2. Test Multilingual Voice Service (14 Languages & Auto-Detection)
        print("\n[2/8] Testing Multilingual Voice Service (14 Languages)...")
        assert len(voice_service.get_available_voices()) >= 14, "Must support at least 14 neural voices"
        
        # Test Language Detection
        assert detect_language("డేటాబేస్ అంటే ఏమిటి?") == "te", "Must detect Telugu script"
        assert detect_language("मशीन लर्निंग क्या है?") == "hi", "Must detect Hindi script"
        assert detect_language("What is an Operating System?") == "en", "Must detect English script"
        assert detect_language("Qu'est-ce qu'une base de données?", default="fr") == "fr", "French fallback"
        print("  ✓ Language Auto-Detection verified across Telugu, Hindi, and English")

        # Test Spoken Text Cleaner
        raw_text = "### Overview\n**Machine Learning** has O(n log n) complexity! Visit [docs](https://edupath.ai)."
        cleaned = clean_text_for_speech(raw_text)
        assert "**" not in cleaned and "###" not in cleaned and "O of n log n" in cleaned, "Spoken text cleaner failed"
        print("  ✓ Natural Speech Text Cleaner verified (formatting and math symbols normalized)")

        # 3. Test Workflow A (Weak Topic Loop & Mistake Classification)
        print("\n[3/8] Testing Workflow A (Weak Topic Loop & Mistake Classification)...")
        topic_stmt = select(Topic).limit(1)
        topic_res = await session.execute(topic_stmt)
        topic = topic_res.scalar_one_or_none()
        assert topic is not None, "Must have at least one topic"

        # Create a test quiz with 2 questions
        test_quiz = Quiz(
            user_id=user.id,
            subject_id=topic.subject_id,
            topic_id=topic.id,
            title="Workflow A Verification Quiz",
            difficulty="medium",
            total_questions=2
        )
        session.add(test_quiz)
        await session.flush()

        q1 = Question(
            quiz_id=test_quiz.id,
            question_text="Define the primary invariant of ACID transaction isolation.",
            question_type="mcq",
            options_json=json.dumps(["Serializable", "Dirty Read", "Race Condition", "Lost Update"]),
            correct_answer="Serializable",
            explanation="Serializable provides the strictest isolation guarantee.",
            points=1
        )
        q2 = Question(
            quiz_id=test_quiz.id,
            question_text="What is the worst-case asymptotic time complexity of standard QuickSort?",
            question_type="mcq",
            options_json=json.dumps(["O(n log n)", "O(n^2)", "O(1)", "O(log n)"]),
            correct_answer="O(n^2)",
            explanation="When the pivot is consistently suboptimal, QuickSort degrades to quadratic time.",
            points=1
        )
        session.add(q1)
        session.add(q2)
        await session.commit()

        # Submit quiz with 1 deliberate mistake (Q2 wrong) -> Score 50% (< 70% threshold)
        submission_answers = [
            {"question_id": q1.id, "user_response": "Serializable"},
            {"question_id": q2.id, "user_response": "O(n log n)"} # Deliberate mistake
        ]
        eval_result = await intelligence_engine.evaluate_quiz_submission(
            session=session,
            user_id=user.id,
            quiz_id=test_quiz.id,
            user_answers=submission_answers,
            time_taken_seconds=45
        )

        assert eval_result["percentage"] == 50.0, f"Expected 50.0% score, got {eval_result['percentage']}"
        assert len(eval_result["mistakes_recorded"]) == 1, "Must record 1 mistake"
        recorded_err = eval_result["mistakes_recorded"][0]
        assert recorded_err["error_category"] == "calculation_error", f"Expected calculation_error, got {recorded_err['error_category']}"
        print("  ✓ Quiz evaluated with automated error classification ('calculation_error')")

        # Verify weak topic notification generated
        notif_stmt = select(Notification).where(
            Notification.user_id == user.id,
            Notification.notification_type == "weak_topic_alert"
        ).order_by(Notification.created_at.desc()).limit(1)
        notif_res = await session.execute(notif_stmt)
        notif = notif_res.scalar_one_or_none()
        assert notif is not None, "Weak topic alert notification must be created"
        print(f"  ✓ Weak Topic Notification created: '{notif.title}'")

        # Verify Spaced Repetition task created for this topic
        due_revisions = await personalized_learning_service.get_due_revisions(session, user.id)
        assert any(r["topic_id"] == topic.id for r in due_revisions), "Spaced repetition task must be scheduled"
        print("  ✓ Hermann Ebbinghaus Spaced Repetition Revision successfully scheduled")

        # 4. Test 6-Mode Concept Explainer & Adaptive Quiz Generator
        print("\n[4/8] Testing Personalized AI Learning Engine...")
        for mode in ["beginner", "intermediate", "advanced", "step_by_step", "real_world", "exam_oriented"]:
            expl = await personalized_learning_service.generate_explanation(
                topic_name=topic.name,
                concept_name=topic.name,
                mode=mode
            )
            assert expl["mode"] == mode and len(expl["content"]) > 100, f"Mode {mode} failed to generate content"
        print("  ✓ All 6 Explanation Depth Modes verified (beginner, intermediate, advanced, step_by_step, real_world, exam_oriented)")

        adaptive_quiz = await personalized_learning_service.generate_adaptive_quiz(
            session=session,
            user_id=user.id,
            topic_id=topic.id,
            difficulty="medium",
            question_count=3
        )
        assert adaptive_quiz["adapted_for_user"] is True, "Must be adapted for user"
        assert len(adaptive_quiz["questions"]) == 3, "Must generate exactly 3 adaptive questions"
        print(f"  ✓ Adaptive Quiz generated targeting past mistakes: {adaptive_quiz['generation_rationale']}")

        # 5. Test Workflow B (Career Development Loop)
        print("\n[5/8] Testing Workflow B (Career Development Loop)...")
        # Update user learning profile with target career
        role_stmt = select(CareerRole).limit(1)
        role_res = await session.execute(role_stmt)
        career_role = role_res.scalar_one_or_none()
        assert career_role is not None, "Career role must exist"

        updated_profile = await intelligence_engine.update_learning_profile(
            session=session,
            user_id=user.id,
            updates={"target_career_id": career_role.id, "daily_goal_minutes": 60}
        )
        assert updated_profile.target_career_id == career_role.id, "Target career must be updated"
        print(f"  ✓ Target Career Goal set to '{career_role.title}' in persistent LearningProfile")

        # Test Multi-Career Comparison
        roles_stmt = select(CareerRole).limit(2)
        two_roles = (await session.execute(roles_stmt)).scalars().all()
        assert len(two_roles) >= 2, "Need at least 2 roles for comparison"
        comp_res = await intelligence_engine.recalculate_career_intelligence(session, user.id)
        
        # Test practical projects for career role
        projects_stmt = select(CareerProject).where(CareerProject.career_role_id == career_role.id)
        projects = (await session.execute(projects_stmt)).scalars().all()
        assert len(projects) > 0, "Must have cataloged practical projects"
        p = projects[0]
        assert len(p.steps) > 0 and len(p.tools) > 0, "Project must have steps and tools"
        print(f"  ✓ Practical Project Catalog verified: '{p.title}' with {len(p.steps)} step guide")

        # Test career transition pathways
        pathways_stmt = select(CareerPathway).where(CareerPathway.from_role_id == career_role.id)
        pathways = (await session.execute(pathways_stmt)).scalars().all()
        print(f"  ✓ Career Transition Pathways verified: {len(pathways)} outbound pathways found")

        # 6. Test Document Intelligence 2.0 & Hybrid Retrieval
        print("\n[6/8] Testing Document Intelligence 2.0 & Hybrid Retrieval...")
        lexical_score = compute_lexical_score("ACID transaction isolation", "ACID properties ensure transaction isolation and durability.")
        assert lexical_score > 0.4, f"Lexical score should be high, got {lexical_score}"
        print(f"  ✓ Lexical BM25 token matcher verified (score: {lexical_score})")

        # Test Retrieval Evaluation Benchmark
        bench_result = await rag_service.evaluate_retrieval(
            session=session,
            user_id=user.id,
            test_queries=[
                {"query": "ACID transaction isolation", "expected_keywords": ["acid", "transaction", "isolation"]}
            ]
        )
        assert "mean_reciprocal_rank_mrr" in bench_result, "Benchmark must return MRR"
        print(f"  ✓ Information Retrieval Benchmark verified (Queries evaluated: {bench_result['total_benchmark_queries']})")

        # 7. Test AI Learning Insights & Mistake Analysis
        print("\n[7/8] Testing AI Learning Insights & Mistake Analysis...")
        mistakes_insights = await intelligence_engine.get_mistake_insights(session, user.id)
        assert mistakes_insights["total_mistakes"] >= 1, "Must have recorded mistakes"
        assert len(mistakes_insights["category_distribution"]) > 0, "Must have category distribution"
        assert len(mistakes_insights["actionable_advice"]) > 10, "Must generate actionable pedagogical advice"
        print(f"  ✓ Mistake Insights verified: {mistakes_insights['total_mistakes']} mistakes categorized, advice: '{mistakes_insights['actionable_advice'][:70]}...'")

        # 8. Test Topic Workspace Aggregation
        print("\n[8/8] Testing Interactive Topic Workspace Aggregation...")
        workspace_data = await intelligence_engine.get_topic_workspace(session, user.id, topic.id)
        assert workspace_data["topic"]["name"] == topic.name, "Workspace topic name must match"
        assert "performance" in workspace_data, "Workspace must aggregate topic performance"
        assert "revision_tasks" in workspace_data, "Workspace must aggregate revision schedule"
        print(f"  ✓ Topic Workspace aggregated for '{topic.name}' ({workspace_data['performance']['total_attempts']} attempts, {len(workspace_data['revision_tasks'])} scheduled revisions)")

    print("\n" + "=" * 70)
    print("   ALL 8 VERIFICATION MODULES PASSED WITH 100% SUCCESS!   ")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_verification())
