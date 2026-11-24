from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.security import check_ai_rate_limit
from app.models.models import User, Note, Document, Topic
from app.schemas.schemas import NoteCreate, NoteUpdate, NoteResponse, NoteGenerateRequest
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/notes", tags=["Smart Notes"])

@router.post("/generate", response_model=NoteResponse)
async def generate_smart_notes(
    req: NoteGenerateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _rate: None = Depends(check_ai_rate_limit)
):
    source_text = ""
    topic_name = req.topic_name or "Academic Concept"

    # If document_id provided, extract its chunks
    if req.document_id:
        doc_stmt = select(Document).where(Document.id == req.document_id, Document.user_id == current_user.id)
        doc_res = await session.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()
        if doc:
            from app.models.models import DocumentChunk
            chunk_stmt = select(DocumentChunk).where(DocumentChunk.document_id == doc.id).order_by(DocumentChunk.chunk_index)
            c_res = await session.execute(chunk_stmt)
            chunks = c_res.scalars().all()
            source_text = "\n\n".join([c.content for c in chunks[:10]])
            if not req.topic_name:
                topic_name = doc.title

    if not source_text:
        source_text = f"Curriculum overview and foundational knowledge for {topic_name}."

    result = await gemini_service.generate_notes(
        source_text=source_text,
        note_type=req.note_type,
        topic_name=topic_name,
        explanation_style=req.explanation_style or "standard",
        language=req.language or "en",
        unit_name=req.unit_name
    )

    note = Note(
        user_id=current_user.id,
        subject_id=req.subject_id,
        document_id=req.document_id,
        note_type=req.note_type,
        title=result["title"],
        content_markdown=result["content"]
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)

    return NoteResponse.model_validate(note)

@router.post("", response_model=NoteResponse)
async def create_note(
    note_in: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    note = Note(
        user_id=current_user.id,
        title=note_in.title,
        content_markdown=note_in.content_markdown,
        note_type=note_in.note_type,
        subject_id=note_in.subject_id,
        topic_id=note_in.topic_id,
        document_id=note_in.document_id,
        is_pinned=note_in.is_pinned
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return NoteResponse.model_validate(note)

@router.get("", response_model=List[NoteResponse])
async def list_notes(
    note_type: Optional[str] = None,
    subject_id: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.user_id == current_user.id)
    if note_type and note_type != "all":
        stmt = stmt.where(Note.note_type == note_type)
    if subject_id and subject_id != "all":
        stmt = stmt.where(Note.subject_id == subject_id)
    if search and search.strip():
        term = f"%{search.strip()}%"
        stmt = stmt.where((Note.title.ilike(term)) | (Note.content_markdown.ilike(term)))
    stmt = stmt.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
    res = await session.execute(stmt)
    notes = res.scalars().all()
    return [NoteResponse.model_validate(n) for n in notes]

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    res = await session.execute(stmt)
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return NoteResponse.model_validate(note)

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_in: NoteUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    res = await session.execute(stmt)
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    if note_in.title is not None:
        note.title = note_in.title
    if note_in.content_markdown is not None:
        note.content_markdown = note_in.content_markdown
    if note_in.note_type is not None:
        note.note_type = note_in.note_type
    if note_in.is_pinned is not None:
        note.is_pinned = note_in.is_pinned

    await session.commit()
    await session.refresh(note)
    return NoteResponse.model_validate(note)

@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    res = await session.execute(stmt)
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    await session.delete(note)
    await session.commit()
    return {"message": "Note deleted successfully."}
