import json
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Conversation, ChatMessage, Document
from app.schemas.schemas import ChatMessageResponse, CitationItem
from app.services.rag_service import rag_service
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/assistant", tags=["AI Study Assistant"])

class AssistantAskRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    document_id: Optional[str] = None
    subject_id: Optional[str] = None

class AssistantAskResponse(BaseModel):
    conversation_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse

@router.post("/ask", response_model=AssistantAskResponse)
async def ask_study_assistant(
    req: AssistantAskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Resolve or create conversation
    conv = None
    if req.conversation_id:
        stmt = select(Conversation).where(
            Conversation.id == req.conversation_id,
            Conversation.user_id == current_user.id
        )
        res = await session.execute(stmt)
        conv = res.scalar_one_or_none()

    if not conv:
        title_snippet = question[:40] + "..." if len(question) > 40 else question
        conv = Conversation(
            user_id=current_user.id,
            subject_id=req.subject_id,
            document_id=req.document_id,
            title=title_snippet
        )
        session.add(conv)
        await session.flush()

    # 2. Record User Message
    user_msg = ChatMessage(
        conversation_id=conv.id,
        sender_role="user",
        content=question
    )
    session.add(user_msg)
    await session.flush()

    # 3. Retrieve relevant chunks from documents via RAG (if user has uploaded documents)
    relevant_chunks = await rag_service.retrieve_relevant_chunks(
        session=session,
        user_id=current_user.id,
        query=question,
        document_id=req.document_id,
        subject_id=req.subject_id,
        top_k=3
    )

    # 4. Generate Answer via Gemini Service
    ai_result = await gemini_service.answer_study_question(
        question=question,
        context_chunks=relevant_chunks
    )

    citations_data = ai_result.get("citations", [])
    citations_json = json.dumps(citations_data) if citations_data else None

    # 5. Record Assistant Message
    assistant_msg = ChatMessage(
        conversation_id=conv.id,
        sender_role="assistant",
        content=ai_result["answer"],
        citations_json=citations_json
    )
    session.add(assistant_msg)
    await session.commit()
    await session.refresh(user_msg)
    await session.refresh(assistant_msg)

    # Format response
    user_resp = ChatMessageResponse(
        id=user_msg.id,
        conversation_id=conv.id,
        sender_role="user",
        content=user_msg.content,
        citations=None,
        created_at=user_msg.created_at
    )

    assistant_citations = [
        CitationItem(
            doc_title=c["doc_title"],
            page_number=c["page_number"],
            snippet=c["snippet"]
        )
        for c in citations_data
    ] if citations_data else None

    assistant_resp = ChatMessageResponse(
        id=assistant_msg.id,
        conversation_id=conv.id,
        sender_role="assistant",
        content=assistant_msg.content,
        citations=assistant_citations,
        created_at=assistant_msg.created_at
    )

    return AssistantAskResponse(
        conversation_id=conv.id,
        user_message=user_resp,
        assistant_message=assistant_resp
    )
