"""
EduPath AI - Quiz Intelligence & Answer-Key Evaluation Tests.
Validates option normalization, answer key alignment, letter-to-option mapping,
domain curriculum generation, and transparent scoring calculation.
"""

import pytest
import uuid
from app.core.database import AsyncSessionLocal
from app.services.ai.quiz_generator import quiz_generator
from app.services.intelligence_engine import intelligence_engine
from app.models.models import User, Quiz, Question, Subject, Topic

@pytest.mark.asyncio
async def test_quiz_generator_option_normalization():
    """Verify that prefixes ('A) ', 'Option B: ') are stripped and correct_answer is aligned."""
    raw_opts = ["A) Binary Search", "B) Linear Search", "C) Jump Search", "D) Interpolation Search"]
    raw_ans = "Option A: Binary Search"
    norm_opts, norm_ans = quiz_generator._normalize_options_and_answer(raw_opts, raw_ans, "Searching Algorithms")

    assert len(norm_opts) == 4
    assert norm_opts[0] == "Binary Search"
    assert norm_ans == "Binary Search"
    assert norm_ans in norm_opts

@pytest.mark.asyncio
async def test_quiz_generator_letter_answer_mapping():
    """Verify that letter-only answers ('B', 'Option B') map correctly to the right option."""
    raw_opts = ["Encapsulation", "Inheritance", "Polymorphism", "Abstraction"]
    raw_ans = "B"
    norm_opts, norm_ans = quiz_generator._normalize_options_and_answer(raw_opts, raw_ans, "OOP")

    assert norm_ans == "Inheritance"
    assert norm_ans in norm_opts

@pytest.mark.asyncio
async def test_quiz_generator_distractor_synthesis():
    """Verify that if fewer than 4 options are provided, distinct distractors are synthesized."""
    raw_opts = ["Unique Primary Option"]
    raw_ans = "Unique Primary Option"
    norm_opts, norm_ans = quiz_generator._normalize_options_and_answer(raw_opts, raw_ans, "System Architecture")

    assert len(norm_opts) == 4
    assert len(set(norm_opts)) == 4
    assert norm_ans == "Unique Primary Option"
    assert norm_ans in norm_opts

@pytest.mark.asyncio
async def test_quiz_generator_curriculum_domain_banks():
    """Verify domain question banks for DSA, DBMS, OS, Networks, and Python."""
    dsa_quiz = await quiz_generator.generate_quiz("Data Structures and Algorithms", difficulty="medium", question_count=3)
    assert len(dsa_quiz) == 3
    for q in dsa_quiz:
        assert len(q["options"]) == 4
        assert q["correct_answer"] in q["options"]
        assert len(q["explanation"]) > 10

    db_quiz = await quiz_generator.generate_quiz("Database Management Systems", difficulty="hard", question_count=2)
    assert len(db_quiz) == 2
    for q in db_quiz:
        assert q["correct_answer"] in q["options"]

@pytest.mark.asyncio
async def test_mcq_evaluation_letter_and_prefix_matching():
    """Verify intelligence engine correctly scores student answers given as letters or raw text."""
    async with AsyncSessionLocal() as db_session:
        # Create test user, subject, topic, and quiz
        unique_suffix = uuid.uuid4().hex[:8]
        user = User(
            email=f"quiz_eval_{unique_suffix}@example.com",
            full_name="Quiz Eval Student",
            hashed_password="hashed_pw_test"
        )
        db_session.add(user)
        await db_session.flush()

        subj = Subject(name=f"CS Testing {unique_suffix}", code=f"CS_{unique_suffix}", description="Quiz Testing Subject")
        db_session.add(subj)
        await db_session.flush()

        topic = Topic(name="Hashing & Hash Tables", subject_id=subj.id)
        db_session.add(topic)
        await db_session.flush()

        quiz = Quiz(
            user_id=user.id,
            subject_id=subj.id,
            topic_id=topic.id,
            title="Hashing Assessment",
            difficulty="medium",
            total_questions=2
        )
        db_session.add(quiz)
        await db_session.flush()

        q1 = Question(
            quiz_id=quiz.id,
            question_text="What is the average time complexity of a hash table lookup?",
            question_type="mcq",
            options_json='["O(1)", "O(n)", "O(log n)", "O(n^2)"]',
            correct_answer="O(1)",
            explanation="Hash tables provide O(1) expected constant time lookups.",
            points=1.0
        )
        q2 = Question(
            quiz_id=quiz.id,
            question_text="Which collision resolution strategy uses linked lists?",
            question_type="mcq",
            options_json='["Separate Chaining", "Linear Probing", "Quadratic Probing", "Double Hashing"]',
            correct_answer="Separate Chaining",
            explanation="Separate chaining stores colliding entries in linked list buckets.",
            points=1.0
        )
        db_session.add_all([q1, q2])
        await db_session.commit()

        # Case A: Student answers with option text directly
        eval_a = await intelligence_engine.evaluate_quiz_submission(
            session=db_session,
            user_id=user.id,
            quiz_id=quiz.id,
            user_answers=[
                {"question_id": q1.id, "user_response": "O(1)"},
                {"question_id": q2.id, "user_response": "Separate Chaining"}
            ],
            time_taken_seconds=30
        )
        assert eval_a["percentage"] == 100.0
        assert eval_a["score"] == 2.0

        # Case B: Student answers with option letters ("A", "Option A")
        eval_b = await intelligence_engine.evaluate_quiz_submission(
            session=db_session,
            user_id=user.id,
            quiz_id=quiz.id,
            user_answers=[
                {"question_id": q1.id, "user_response": "A"},
                {"question_id": q2.id, "user_response": "Option A"}
            ],
            time_taken_seconds=35
        )
        assert eval_b["percentage"] == 100.0
        assert eval_b["score"] == 2.0

        # Case C: Student answers one incorrectly
        eval_c = await intelligence_engine.evaluate_quiz_submission(
            session=db_session,
            user_id=user.id,
            quiz_id=quiz.id,
            user_answers=[
                {"question_id": q1.id, "user_response": "O(1)"},
                {"question_id": q2.id, "user_response": "Linear Probing"}  # Incorrect
            ],
            time_taken_seconds=25
        )
        assert eval_c["percentage"] == 50.0
        assert eval_c["score"] == 1.0
