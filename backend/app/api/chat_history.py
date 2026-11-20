import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Conversation, ChatMessage
from app.schemas.schemas import (
    ConversationResponse, ConversationCreate, ConversationUpdate,
    ChatMessageResponse, CitationItem
)

router = APIRouter(prefix="/chat-history", tags=["AI Chat History"])

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Conversation).where(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc())
    res = await session.execute(stmt)
    conversations = res.scalars().all()

    output = []
    for c in conversations:
        output.append(
            ConversationResponse(
                id=c.id,
                title=c.title,
                subject_id=c.subject_id,
                document_id=c.document_id,
                created_at=c.created_at,
                updated_at=c.updated_at,
                messages=[]
            )
        )
    return output

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Conversation).options(
        selectinload(Conversation.messages)
    ).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    res = await session.execute(stmt)
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    formatted_messages = []
    for m in conv.messages:
        citations = None
        if m.citations_json:
            try:
                raw_c = json.loads(m.citations_json)
                citations = [CitationItem(**item) for item in raw_c]
            except Exception:
                citations = None

        formatted_messages.append(
            ChatMessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                sender_role=m.sender_role,
                content=m.content,
                citations=citations,
                created_at=m.created_at
            )
        )

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        subject_id=conv.subject_id,
        document_id=conv.document_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=formatted_messages
    )

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    res = await session.execute(stmt)
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    conv.title = update_data.title.strip()
    await session.commit()
    await session.refresh(conv)

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        subject_id=conv.subject_id,
        document_id=conv.document_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[]
    )

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    )
    res = await session.execute(stmt)
    conv = res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    await session.delete(conv)
    await session.commit()
    return {"message": "Conversation deleted successfully."}
