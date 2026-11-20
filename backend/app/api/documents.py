import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Document, DocumentChunk
from app.schemas.schemas import DocumentResponse
from app.services.document_parser import DocumentParserService
from app.services.rag_service import rag_service

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    subject_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    # Validate extension
    file_name = file.filename or "uploaded_doc"
    ext = os.path.splitext(file_name)[1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF (.pdf) or Word document (.docx)."
        )

    # Prepare upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_name = f"{uuid.uuid4()}{ext}"
    saved_path = os.path.join(settings.UPLOAD_DIR, saved_name)

    # Save file and calculate size
    bytes_read = 0
    with open(saved_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            bytes_read += len(chunk)
            if bytes_read > settings.MAX_UPLOAD_SIZE_BYTES:
                buffer.close()
                if os.path.exists(saved_path):
                    os.remove(saved_path)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)}MB."
                )
            buffer.write(chunk)

    doc_title = title.strip() if title and title.strip() else os.path.splitext(file_name)[0]

    # Create document record
    doc = Document(
        user_id=current_user.id,
        subject_id=subject_id if subject_id and subject_id.strip() else None,
        title=doc_title,
        file_name=file_name,
        file_path=saved_path,
        file_size=bytes_read,
        file_type="pdf" if ext == ".pdf" else "docx",
        status="processing"
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    # Process document extraction & indexing
    try:
        if ext == ".pdf":
            pages = DocumentParserService.extract_text_from_pdf(saved_path)
        else:
            pages = DocumentParserService.extract_text_from_docx(saved_path)

        chunk_data_list = DocumentParserService.chunk_document(pages)
        created_chunks = []

        for c_data in chunk_data_list:
            chunk_obj = DocumentChunk(
                document_id=doc.id,
                chunk_index=c_data["chunk_index"],
                content=c_data["content"],
                page_number=c_data["page_number"],
                token_count=c_data["token_count"]
            )
            session.add(chunk_obj)
            created_chunks.append(chunk_obj)

        await session.commit()
        for c in created_chunks:
            await session.refresh(c)

        # Index vectors
        await rag_service.index_chunks(session, created_chunks)

        doc.chunk_count = len(created_chunks)
        doc.status = "ready"
        await session.commit()
        await session.refresh(doc)

    except Exception as e:
        doc.status = "failed"
        doc.error_message = f"Extraction failed: {str(e)}"
        await session.commit()
        await session.refresh(doc)

    return DocumentResponse.model_validate(doc)

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.user_id == current_user.id).order_by(Document.created_at.desc())
    res = await session.execute(stmt)
    docs = res.scalars().all()
    return [DocumentResponse.model_validate(d) for d in docs]

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    res = await session.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found or access denied.")
    return DocumentResponse.model_validate(doc)

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    res = await session.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception:
            pass

    await session.delete(doc)
    await session.commit()
    return {"message": "Document successfully deleted."}
