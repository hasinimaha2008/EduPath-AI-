import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Quiz, Question, QuizAttempt, Document, Topic, DocumentChunk
from app.schemas.schemas import (
    QuizCreateRequest, QuizResponse, QuestionResponse,
    QuizSubmitRequest, QuizResultResponse, QuizAttemptHistoryItem
)
from app.services.gemini_service import gemini_service
from app.services.intelligence_engine import intelligence_engine

router = APIRouter(prefix="/quizzes", tags=["AI Quiz Generator"])

@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    req: QuizCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
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

    if not source_text:
        source_text = f"Curriculum concepts, properties, algorithms, and applications of {topic_title}."

    # Generate questions via Gemini
    generated_q_list = await gemini_service.generate_quiz(
        source_text=source_text,
        topic_name=topic_title,
        difficulty=req.difficulty,
        question_count=req.question_count,
        question_types=req.question_types
    )

    quiz = Quiz(
        user_id=current_user.id,
        subject_id=req.subject_id,
        topic_id=req.topic_id,
        document_id=req.document_id,
        title=f"{topic_title} – {req.difficulty.capitalize()} Assessment",
        difficulty=req.difficulty,
        total_questions=len(generated_q_list),
        time_limit_mins=max(5, len(generated_q_list) * 2)
    )
    session.add(quiz)
    await session.flush()

    question_objects = []
    for q_item in generated_q_list:
        q_obj = Question(
            quiz_id=quiz.id,
            question_text=q_item.get("question_text", "Academic Concept Question"),
            question_type=q_item.get("question_type", "mcq"),
            options_json=json.dumps(q_item.get("options", [])) if q_item.get("options") else None,
            correct_answer=q_item.get("correct_answer", "").strip(),
            explanation=q_item.get("explanation", ""),
            points=q_item.get("points", 1)
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
                points=q.points
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
            points=q.points
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
    result = await intelligence_engine.evaluate_quiz_submission(
        session=session,
        user_id=current_user.id,
        quiz_id=quiz_id,
        user_answers=raw_answers,
        time_taken_seconds=submission.time_taken_seconds
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
