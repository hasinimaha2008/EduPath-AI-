import json
import logging
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db, AsyncSessionLocal
from app.api.deps import get_current_user
from app.models.models import User, Conversation, ChatMessage, Document
from app.schemas.schemas import ChatMessageResponse, CitationItem
from app.services.rag_service import rag_service
from app.services.gemini_service import gemini_service

logger = logging.getLogger("edupath.assistant")
router = APIRouter(prefix="/assistant", tags=["General-Purpose AI Assistant"])

class AssistantAskRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    document_id: Optional[str] = None
    subject_id: Optional[str] = None
    language: Optional[str] = "auto"

class AssistantAskResponse(BaseModel):
    conversation_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse

class AssistantRegenerateRequest(BaseModel):
    conversation_id: str

class AssistantRegenerateResponse(BaseModel):
    conversation_id: str
    assistant_message: ChatMessageResponse

class ConfigureKeyRequest(BaseModel):
    api_key: str

@router.get("/status")
async def get_assistant_status():
    """
    Returns current LLM status and active model information.
    """
    return {
        "is_configured": gemini_service.is_configured,
        "model_name": gemini_service.model_name,
        "provider": "Google Gemini (gemini-1.5-flash)" if gemini_service.is_configured else "EduPath Dynamic LLM Engine",
        "streaming_supported": True,
        "multilingual_supported": ["en", "te", "hi", "auto"]
    }

@router.post("/configure-key")
async def configure_api_key(
    req: ConfigureKeyRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Verifies and configures the user's Gemini API key dynamically.
    Persists key to environment and backend configuration.
    """
    res = gemini_service.configure_api_key(req.api_key)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message", "API Key verification failed."))
    return res

@router.post("/ask", response_model=AssistantAskResponse)
async def ask_study_assistant(
    req: AssistantAskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Resolve or create conversation with smart title
    conv = None
    if req.conversation_id:
        stmt = select(Conversation).where(
            Conversation.id == req.conversation_id,
            Conversation.user_id == current_user.id
        )
        res = await session.execute(stmt)
        conv = res.scalar_one_or_none()

    if not conv:
        smart_title = await gemini_service.generate_conversation_title(question)
        conv = Conversation(
            user_id=current_user.id,
            subject_id=req.subject_id,
            document_id=req.document_id,
            title=smart_title
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

    # 3. Query sliding window conversation history for multi-turn context
    history_stmt = select(ChatMessage).where(
        ChatMessage.conversation_id == conv.id,
        ChatMessage.id != user_msg.id
    ).order_by(ChatMessage.created_at.asc())
    history_res = await session.execute(history_stmt)
    history_msgs = history_res.scalars().all()
    conversation_history = [
        {"role": m.sender_role, "content": m.content}
        for m in history_msgs[-10:]
    ]

    # 4. Retrieve relevant chunks from documents via RAG (if attached)
    relevant_chunks = await rag_service.retrieve_relevant_chunks(
        session=session,
        user_id=current_user.id,
        query=question,
        document_id=req.document_id or conv.document_id,
        subject_id=req.subject_id or conv.subject_id,
        top_k=3
    )

    # 5. Generate Answer via Gemini Service with history and context
    ai_result = await gemini_service.answer_study_question(
        question=question,
        context_chunks=relevant_chunks,
        conversation_history=conversation_history,
        language=req.language or "auto"
    )

    citations_data = ai_result.get("citations", [])
    citations_json = json.dumps(citations_data) if citations_data else None

    # 6. Record Assistant Message
    assistant_msg = ChatMessage(
        conversation_id=conv.id,
        sender_role="assistant",
        content=ai_result["answer"],
        citations_json=citations_json
    )
    session.add(assistant_msg)
    conv.updated_at = datetime.utcnow()
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

@router.post("/chat-stream")
async def chat_stream_assistant(
    req: AssistantAskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Real-time response streaming endpoint for ChatGPT-like conversational interaction.
    Emits Server-Sent Events (SSE) token-by-token and persists messages seamlessly.
    """
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
        smart_title = await gemini_service.generate_conversation_title(question)
        conv = Conversation(
            user_id=current_user.id,
            subject_id=req.subject_id,
            document_id=req.document_id,
            title=smart_title
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

    # 3. Retrieve prior context & RAG chunks
    history_stmt = select(ChatMessage).where(
        ChatMessage.conversation_id == conv.id,
        ChatMessage.id != user_msg.id
    ).order_by(ChatMessage.created_at.asc())
    history_res = await session.execute(history_stmt)
    history_msgs = history_res.scalars().all()
    conversation_history = [
        {"role": m.sender_role, "content": m.content}
        for m in history_msgs[-10:]
    ]

    relevant_chunks = await rag_service.retrieve_relevant_chunks(
        session=session,
        user_id=current_user.id,
        query=question,
        document_id=req.document_id or conv.document_id,
        subject_id=req.subject_id or conv.subject_id,
        top_k=3
    )

    citations_data = []
    if relevant_chunks:
        for c in relevant_chunks:
            snippet = c.get("content", "")
            citations_data.append({
                "doc_title": c.get("doc_title", "Document"),
                "page_number": c.get("page_number", 1),
                "snippet": snippet[:200] + "..." if len(snippet) > 200 else snippet
            })

    conv_id = conv.id
    conv_title = conv.title
    user_msg_id = user_msg.id
    user_created = user_msg.created_at.isoformat()
    await session.commit()

    async def event_generator():
        # First event: metadata
        yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conv_id, 'title': conv_title, 'user_message': {'id': user_msg_id, 'conversation_id': conv_id, 'sender_role': 'user', 'content': question, 'created_at': user_created}, 'citations': citations_data})}\n\n"

        full_answer = ""
        try:
            async for token in gemini_service.stream_chat_response(
                question=question,
                context_chunks=relevant_chunks,
                conversation_history=conversation_history,
                language=req.language or "auto"
            ):
                full_answer += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as stream_err:
            logger.error(f"Error during stream generation: {stream_err}")
            if not full_answer:
                full_answer = "I encountered an error while formulating the response. Please try asking again."
                yield f"data: {json.dumps({'type': 'token', 'content': full_answer})}\n\n"

        # Persist assistant message safely with a fresh DB session
        try:
            async with AsyncSessionLocal() as save_session:
                citations_json = json.dumps(citations_data) if citations_data else None
                ass_msg = ChatMessage(
                    conversation_id=conv_id,
                    sender_role="assistant",
                    content=full_answer,
                    citations_json=citations_json
                )
                save_session.add(ass_msg)
                conv_up = await save_session.get(Conversation, conv_id)
                if conv_up:
                    conv_up.updated_at = datetime.utcnow()
                await save_session.commit()
                await save_session.refresh(ass_msg)
                ass_id = ass_msg.id
                created_at = ass_msg.created_at.isoformat()

            yield f"data: {json.dumps({'type': 'done', 'assistant_message': {'id': ass_id, 'conversation_id': conv_id, 'sender_role': 'assistant', 'content': full_answer, 'citations': citations_data, 'created_at': created_at}})}\n\n"
        except Exception as save_err:
            logger.error(f"Failed to persist assistant message after stream: {save_err}")
            yield f"data: {json.dumps({'type': 'done', 'assistant_message': {'id': 'temp-done', 'conversation_id': conv_id, 'sender_role': 'assistant', 'content': full_answer, 'citations': citations_data, 'created_at': datetime.utcnow().isoformat()}})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/regenerate", response_model=AssistantRegenerateResponse)
async def regenerate_assistant_response(
    req: AssistantRegenerateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Conversation).where(
        Conversation.id == req.conversation_id,
        Conversation.user_id == current_user.id
    )
    res = await session.execute(stmt)
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # Get all messages
    msg_stmt = select(ChatMessage).where(
        ChatMessage.conversation_id == conv.id
    ).order_by(ChatMessage.created_at.asc())
    msg_res = await session.execute(msg_stmt)
    all_msgs = msg_res.scalars().all()

    # Find the last user message
    last_user_idx = -1
    for idx, m in enumerate(all_msgs):
        if m.sender_role == "user":
            last_user_idx = idx

    if last_user_idx == -1:
        raise HTTPException(status_code=400, detail="No user message found to regenerate.")

    last_user_msg = all_msgs[last_user_idx]
    history_msgs = all_msgs[:last_user_idx]
    conversation_history = [
        {"role": m.sender_role, "content": m.content}
        for m in history_msgs[-10:]
    ]

    # Retrieve chunks
    relevant_chunks = await rag_service.retrieve_relevant_chunks(
        session=session,
        user_id=current_user.id,
        query=last_user_msg.content,
        document_id=conv.document_id,
        subject_id=conv.subject_id,
        top_k=3
    )

    # Regenerate response
    ai_result = await gemini_service.answer_study_question(
        question=last_user_msg.content,
        context_chunks=relevant_chunks,
        conversation_history=conversation_history
    )

    citations_data = ai_result.get("citations", [])
    citations_json = json.dumps(citations_data) if citations_data else None

    # Check if there is an assistant message right after last_user_msg
    target_assistant_msg = None
    if last_user_idx + 1 < len(all_msgs) and all_msgs[last_user_idx + 1].sender_role == "assistant":
        target_assistant_msg = all_msgs[last_user_idx + 1]
        target_assistant_msg.content = ai_result["answer"]
        target_assistant_msg.citations_json = citations_json
    else:
        target_assistant_msg = ChatMessage(
            conversation_id=conv.id,
            sender_role="assistant",
            content=ai_result["answer"],
            citations_json=citations_json
        )
        session.add(target_assistant_msg)

    conv.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(target_assistant_msg)

    assistant_citations = [
        CitationItem(
            doc_title=c["doc_title"],
            page_number=c["page_number"],
            snippet=c["snippet"]
        )
        for c in citations_data
    ] if citations_data else None

    assistant_resp = ChatMessageResponse(
        id=target_assistant_msg.id,
        conversation_id=conv.id,
        sender_role="assistant",
        content=target_assistant_msg.content,
        citations=assistant_citations,
        created_at=target_assistant_msg.created_at
    )

    return AssistantRegenerateResponse(
        conversation_id=conv.id,
        assistant_message=assistant_resp
    )
