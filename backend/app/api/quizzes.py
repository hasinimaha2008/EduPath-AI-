import json
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.security import check_ai_rate_limit
from app.models.models import User, Quiz, Question, QuizAttempt, Document, Topic, DocumentChunk, Note, UserAnswer
from app.schemas.schemas import (
    QuizCreateRequest, QuizResponse, QuestionResponse,
    QuizSubmitRequest, QuizResultResponse, QuizAttemptHistoryItem, UserAnswerResult
)
from app.services.gemini_service import gemini_service
from app.services.intelligence_engine import intelligence_engine
from app.services.personalized_learning_service import personalized_learning_service

router = APIRouter(prefix="/quizzes", tags=["AI Quiz Generator"])

@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    req: QuizCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _rate: None = Depends(check_ai_rate_limit)
):
    source_text = ""
    topic_title = req.title or "Computer Science Foundations"

    if req.topic_id:
        t_stmt = select(Topic).where(Topic.id == req.topic_id)
        t_res = await session.execute(t_stmt)
        topic = t_res.scalar_one_or_none()
        if topic:
            topic_title = topic.name
            req.subject_id = topic.subject_id

    if req.document_id:
        doc_stmt = select(Document).where(Document.id == req.document_id, Document.user_id == current_user.id)
        doc_res = await session.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()
        if doc:
            chunk_stmt = select(DocumentChunk).where(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index)
            c_res = await session.execute(chunk_stmt)
            chunks = c_res.scalars().all()
            source_text = "\n\n".join([c.content for c in chunks[:12]])
            if not req.title:
                topic_title = doc.title
            if doc.subject_id and not req.subject_id:
                req.subject_id = doc.subject_id
            if not req.topic_id and req.subject_id:
                top_stmt = select(Topic).where(Topic.subject_id == req.subject_id).limit(1)
                matched_top = (await session.execute(top_stmt)).scalars().first()
                if matched_top:
                    req.topic_id = matched_top.id
            if not req.topic_id:
                top_stmt = select(Topic).limit(1)
                matched_top = (await session.execute(top_stmt)).scalars().first()
                if matched_top:
                    req.topic_id = matched_top.id
                    if not req.subject_id:
                        req.subject_id = matched_top.subject_id

    if req.note_id:
        note_stmt = select(Note).where(Note.id == req.note_id, Note.user_id == current_user.id)
        note_res = await session.execute(note_stmt)
        note = note_res.scalar_one_or_none()
        if note:
            source_text = note.content_markdown
            if not req.title:
                topic_title = note.title
            if note.subject_id and not req.subject_id:
                req.subject_id = note.subject_id
            if not req.topic_id and getattr(note, "topic_id", None):
                req.topic_id = note.topic_id
            if not req.topic_id and note.title:
                clean_title_part = note.title.split("–")[0].split("-")[0].strip()
                top_stmt = select(Topic).where(Topic.name.ilike(f"%{clean_title_part}%")).limit(1)
                matched_top = (await session.execute(top_stmt)).scalars().first()
                if matched_top:
                    req.topic_id = matched_top.id
            if not req.topic_id and req.subject_id:
                top_stmt = select(Topic).where(Topic.subject_id == req.subject_id).limit(1)
                matched_top = (await session.execute(top_stmt)).scalars().first()
                if matched_top:
                    req.topic_id = matched_top.id

    if not source_text:
        source_text = f"Curriculum concepts, properties, algorithms, and applications of {topic_title}."

    # Generate questions via Gemini
    generated_q_list = await gemini_service.generate_quiz(
        source_text=source_text,
        topic_name=topic_title,
        difficulty=req.difficulty,
        question_count=req.question_count,
        question_types=req.question_types,
        subtopic=req.subtopic
    )

    quiz = Quiz(
        user_id=current_user.id,
        subject_id=req.subject_id,
        topic_id=req.topic_id,
        document_id=req.document_id,
        note_id=req.note_id,
        title=f"{topic_title} – {req.difficulty.capitalize()} Assessment",
        difficulty=req.difficulty,
        total_questions=len(generated_q_list),
        time_limit_mins=max(5, len(generated_q_list) * 2)
    )
    session.add(quiz)
    await session.flush()

    question_objects = []
    for q_item in generated_q_list:
        test_cases_val = json.dumps(q_item.get("test_cases", [])) if q_item.get("test_cases") else None
        q_obj = Question(
            quiz_id=quiz.id,
            question_text=q_item.get("question_text", "Academic Concept Question"),
            question_type=q_item.get("question_type", "mcq"),
            options_json=json.dumps(q_item.get("options", [])) if q_item.get("options") else None,
            correct_answer=q_item.get("correct_answer", "").strip(),
            explanation=q_item.get("explanation", ""),
            points=q_item.get("points", 1),
            code_snippet=q_item.get("code_snippet"),
            test_cases_json=test_cases_val
        )
        session.add(q_obj)
        question_objects.append(q_obj)

    await session.commit()
    await session.refresh(quiz)

    # Return quiz WITHOUT revealing answers!
    clean_questions = []
    for q in question_objects:
        opts = json.loads(q.options_json) if q.options_json else None
        clean_questions.append(
            QuestionResponse(
                id=q.id,
                quiz_id=quiz.id,
                question_text=q.question_text,
                question_type=q.question_type,
                options=opts,
                points=q.points,
                code_snippet=q.code_snippet,
                test_cases=q.test_cases
            )
        )

    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        difficulty=quiz.difficulty,
        total_questions=quiz.total_questions,
        time_limit_mins=quiz.time_limit_mins,
        subject_id=quiz.subject_id,
        topic_id=quiz.topic_id,
        document_id=quiz.document_id,
        note_id=quiz.note_id,
        created_at=quiz.created_at,
        questions=clean_questions
    )

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Quiz).where(Quiz.id == quiz_id, Quiz.user_id == current_user.id)
    res = await session.execute(stmt)
    quiz = res.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    q_stmt = select(Question).where(Question.quiz_id == quiz.id).order_by(Question.id)
    q_res = await session.execute(q_stmt)
    questions = q_res.scalars().all()

    # Answer keys strictly hidden during active retrieval
    clean_questions = [
        QuestionResponse(
            id=q.id,
            quiz_id=quiz.id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=json.loads(q.options_json) if q.options_json else None,
            points=q.points,
            code_snippet=q.code_snippet,
            test_cases=q.test_cases
        )
        for q in questions
    ]

    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        difficulty=quiz.difficulty,
        total_questions=quiz.total_questions,
        time_limit_mins=quiz.time_limit_mins,
        subject_id=quiz.subject_id,
        topic_id=quiz.topic_id,
        document_id=quiz.document_id,
        note_id=quiz.note_id,
        created_at=quiz.created_at,
        questions=clean_questions
    )

@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Process through Central EduPath Intelligence Engine
    raw_answers = [{"question_id": a.question_id, "user_response": a.user_response} for a in submission.answers]
    try:
        result = await intelligence_engine.evaluate_quiz_submission(
            session=session,
            user_id=current_user.id,
            quiz_id=quiz_id,
            user_answers=raw_answers,
            time_taken_seconds=submission.time_taken_seconds
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    return QuizResultResponse(**result)

@router.get("/history/attempts", response_model=List[QuizAttemptHistoryItem])
async def get_quiz_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(QuizAttempt, Quiz.title).join(
        Quiz, QuizAttempt.quiz_id == Quiz.id
    ).where(
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.completed_at.desc())

    res = await session.execute(stmt)
    records = res.all()

    history = []
    for attempt, quiz_title in records:
        history.append(
            QuizAttemptHistoryItem(
                id=attempt.id,
                quiz_id=attempt.quiz_id,
                quiz_title=quiz_title,
                score=attempt.score,
                max_score=attempt.max_score,
                percentage=attempt.percentage,
                time_taken_seconds=attempt.time_taken_seconds,
                completed_at=attempt.completed_at
            )
        )
    return history

@router.get("/attempts/{attempt_id}", response_model=QuizResultResponse)
async def get_quiz_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(QuizAttempt).where(QuizAttempt.id == attempt_id, QuizAttempt.user_id == current_user.id)
    res = await session.execute(stmt)
    attempt = res.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found.")

    ans_stmt = select(UserAnswer, Question).join(Question, UserAnswer.question_id == Question.id).where(UserAnswer.attempt_id == attempt.id)
    ans_res = await session.execute(ans_stmt)
    pairs = ans_res.all()

    evaluated_answers = []
    for ua, q in pairs:
        evaluated_answers.append(
            UserAnswerResult(
                question_id=q.id,
                question_text=q.question_text,
                user_response=ua.user_response,
                correct_answer=q.correct_answer,
                is_correct=ua.is_correct,
                score_awarded=ua.score_awarded,
                explanation=q.explanation
            )
        )

    q_stmt = select(Quiz).where(Quiz.id == attempt.quiz_id)
    q_res = await session.execute(q_stmt)
    quiz = q_res.scalar_one_or_none()
    topic_name = quiz.title if quiz else "Assessment Topic"

    topic_breakdown = {
        "topic_name": topic_name,
        "total_questions": len(evaluated_answers),
        "correct_count": sum(1 for ea in evaluated_answers if ea.is_correct),
        "accuracy": attempt.percentage,
        "mastery_status": "mastered" if attempt.percentage >= 90 else "proficient" if attempt.percentage >= 70 else "developing"
    }

    recommended_revision_topics = []
    for ea in evaluated_answers:
        if not ea.is_correct:
            clean_q = re.sub(r'\[.*?\]\s*', '', ea.question_text).strip()
            rec_title = f"{topic_name}: {clean_q[:65]}..." if len(clean_q) > 65 else f"{topic_name}: {clean_q}"
            if rec_title not in recommended_revision_topics:
                recommended_revision_topics.append(rec_title)

    if not recommended_revision_topics:
        recommended_revision_topics.append(f"Review core principles of {topic_name}")

    return QuizResultResponse(
        attempt_id=attempt.id,
        quiz_id=attempt.quiz_id,
        score=attempt.score,
        max_score=attempt.max_score,
        percentage=attempt.percentage,
        time_taken_seconds=attempt.time_taken_seconds,
        completed_at=attempt.completed_at,
        answers=evaluated_answers,
        mastery_status=topic_breakdown["mastery_status"],
        topic_breakdown=topic_breakdown,
        recommended_revision_topics=recommended_revision_topics
    )

@router.post("/generate-adaptive", response_model=QuizResponse)
async def generate_adaptive_quiz(
    req: QuizCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Generates an adaptive quiz specifically targeting the student's historical mistakes,
    error patterns, and demonstrated difficulty gaps (Upgrade 2).
    """
    if not req.topic_id:
        raise HTTPException(status_code=400, detail="topic_id is required for adaptive quiz generation.")

    adaptive_result = await personalized_learning_service.generate_adaptive_quiz(
        session=session,
        user_id=current_user.id,
        topic_id=req.topic_id,
        difficulty=req.difficulty or "medium",
        question_count=req.question_count or 5
    )

    generated_q_list = adaptive_result["questions"]
    topic_name = adaptive_result["topic_name"]

    # Fetch subject_id from Topic
    t_stmt = select(Topic.subject_id).where(Topic.id == req.topic_id)
    t_res = await session.execute(t_stmt)
    subj_id = t_res.scalar_one_or_none()

    quiz = Quiz(
        user_id=current_user.id,
        subject_id=subj_id,
        topic_id=req.topic_id,
        title=f"{topic_name} – Adaptive Mastery Assessment",
        difficulty=adaptive_result["calibrated_difficulty"],
        total_questions=len(generated_q_list),
        time_limit_mins=max(5, len(generated_q_list) * 2)
    )
    session.add(quiz)
    await session.flush()

    question_objects = []
    for q_item in generated_q_list:
        test_cases_val = json.dumps(q_item.get("test_cases", [])) if q_item.get("test_cases") else None
        q_obj = Question(
            quiz_id=quiz.id,
            question_text=q_item.get("question_text", "Adaptive Evaluation Question"),
            question_type=q_item.get("question_type", "mcq"),
            options_json=json.dumps(q_item.get("options", [])) if q_item.get("options") else None,
            correct_answer=q_item.get("correct_answer", "").strip(),
            explanation=q_item.get("explanation", ""),
            points=q_item.get("points", 1),
            code_snippet=q_item.get("code_snippet"),
            test_cases_json=test_cases_val
        )
        session.add(q_obj)
        question_objects.append(q_obj)

    await session.commit()
    await session.refresh(quiz)

    # Return questions with hidden correct answers
    clean_questions = []
    for q in question_objects:
        opts = json.loads(q.options_json) if q.options_json else None
        clean_questions.append(
            QuestionResponse(
                id=q.id,
                quiz_id=quiz.id,
                question_text=q.question_text,
                question_type=q.question_type or "mcq",
                options=opts,
                points=q.points,
                code_snippet=q.code_snippet
            )
        )

    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        difficulty=quiz.difficulty,
        total_questions=quiz.total_questions,
        time_limit_mins=quiz.time_limit_mins,
        questions=clean_questions,
        created_at=quiz.created_at
    )

