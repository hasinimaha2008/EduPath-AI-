import os
import shutil
import uuid
import logging
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.database import get_db
from app.api.deps import get_current_user
from app.core.security import check_ai_rate_limit, is_safe_upload_path
from app.models.models import User, Document, DocumentChunk
from app.schemas.schemas import DocumentResponse
from app.services.document_parser import DocumentParserService
from app.services.rag_service import rag_service

logger = logging.getLogger("edupath.documents")

router = APIRouter(prefix="/documents", tags=["Documents"])

class DocumentAskRequest(BaseModel):
    question: str
    language: Optional[str] = "auto"

class DocumentExplainRequest(BaseModel):
    topic: str
    depth: Optional[str] = "step_by_step"

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
    allowed_exts = [".pdf", ".docx", ".pptx", ".txt"]
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats: PDF (.pdf), Word (.docx), PowerPoint (.pptx), Text (.txt)."
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

    if bytes_read == 0:
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot upload an empty file (0 bytes)."
        )

    # Validate file signature (magic bytes) to prevent extension spoofing
    def validate_magic_bytes(fpath: str, file_ext: str) -> bool:
        try:
            with open(fpath, "rb") as f:
                header = f.read(512)
            logger.info(f"Magic bytes check: ext={file_ext}, len={len(header)}, header_start={header[:10]}")
            if len(header) == 0:
                return False
            if file_ext == ".pdf":
                return header.startswith(b"%PDF")
            elif file_ext in (".docx", ".pptx"):
                return header.startswith(b"PK\x03\x04")
            elif file_ext == ".txt":
                if b"\x00" in header:
                    return False
                header.decode("utf-8", errors="strict")
                return True
            return False
        except Exception as e:
            logger.error(f"validate_magic_bytes exception: {e}")
            return False

    if not validate_magic_bytes(saved_path, ext):
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Security rejection: file content does not match the declared '{ext}' format signature."
        )

    # Pre-validate archive integrity and decompression bomb protection before database record creation
    if ext in (".docx", ".pptx"):
        try:
            DocumentParserService.check_zip_bomb(saved_path)
        except ValueError as ze:
            if os.path.exists(saved_path):
                os.remove(saved_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security rejection: {str(ze)}"
            )

    doc_title = title.strip() if title and title.strip() else os.path.splitext(file_name)[0]

    # Map file format
    file_type_map = {
        ".pdf": "pdf",
        ".docx": "docx",
        ".pptx": "pptx",
        ".txt": "txt"
    }

    # Create document record
    doc = Document(
        user_id=current_user.id,
        subject_id=subject_id if subject_id and subject_id.strip() else None,
        title=doc_title,
        file_name=file_name,
        file_path=saved_path,
        file_size=bytes_read,
        file_type=file_type_map.get(ext, "txt"),
        status="processing"
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)

    # Process document extraction & indexing
    try:
        pages = DocumentParserService.extract_document_pages(saved_path, ext)
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
        session.add(doc)

        # Trigger Workflow C: Notification that document intelligence is ready
        from app.models.models import Notification
        notif = Notification(
            user_id=current_user.id,
            title=f"Document Ready: {doc.title}",
            message=f"'{doc.title}' ({len(created_chunks)} chunks) is processed and indexed with hybrid search. Summary and self-assessment are ready.",
            notification_type="task_reminder",
            action_url="/dashboard/documents"
        )
        session.add(notif)

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
        raise HTTPException(status_code=404, detail="Document not found or access denied.")

    real_upload_dir = os.path.realpath(settings.UPLOAD_DIR)
    if is_safe_upload_path(real_upload_dir, doc.file_path):
        real_file_path = os.path.realpath(doc.file_path)
        if os.path.exists(real_file_path):
            try:
                os.remove(real_file_path)
            except Exception as e:
                logger.warning(f"Failed to remove physical file {real_file_path} on deletion: {e}")
    else:
        logger.warning(f"Unsafe document path blocked on deletion for doc {doc.id}: {doc.file_path}")

    await session.delete(doc)
    await session.commit()
    return {"message": "Document successfully deleted."}

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Secure document download and export enforcing authenticated user ownership
    and path traversal prevention via os.path.commonpath().
    """
    stmt = select(Document).where(Document.id == document_id, Document.user_id == current_user.id)
    res = await session.execute(stmt)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found or access denied.")

    # Prevent directory traversal attacks using os.path.commonpath()
    real_upload_dir = os.path.realpath(settings.UPLOAD_DIR)
    if not is_safe_upload_path(real_upload_dir, doc.file_path):
        logger.warning(f"Path traversal / unsafe path download attempt blocked: doc_id={doc.id}, path={doc.file_path}")
        raise HTTPException(status_code=400, detail="Invalid document storage path or traversal attempt detected.")

    real_file_path = os.path.realpath(doc.file_path)
    if not os.path.exists(real_file_path):
        raise HTTPException(status_code=404, detail="Requested file does not exist on disk.")

    return FileResponse(
        path=real_file_path,
        filename=doc.file_name,
        media_type="application/octet-stream"
    )

@router.get("/{document_id}/summary")
async def get_document_summary(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _rate: None = Depends(check_ai_rate_limit)
):
    """
    Generates an executive summary and chapter takeaways from the document (Upgrade 4).
    """
    try:
        return await rag_service.summarize_document(session, current_user.id, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{document_id}/concepts")
async def get_document_concepts(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _rate: None = Depends(check_ai_rate_limit)
):
    """
    Extracts key technical concepts and definitions from document notes (Upgrade 4).
    """
    try:
        return await rag_service.extract_concepts(session, current_user.id, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{document_id}/generate-questions")
async def generate_document_questions(
    document_id: str,
    count: int = 5,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _rate: None = Depends(check_ai_rate_limit)
):
    """
    Generates self-assessment questions grounded directly in the uploaded document (Upgrade 4).
    """
    try:
        return await rag_service.generate_key_questions(session, current_user.id, document_id, count=count)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/evaluate-retrieval")
async def evaluate_retrieval_benchmark(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Evaluates hybrid retrieval performance across benchmark queries (Precision@K and MRR).
    """
    test_queries = [
        {"query": "ACID transaction isolation levels", "expected_keywords": ["acid", "transaction", "isolation", "serializable"]},
        {"query": "B-Tree index search complexity", "expected_keywords": ["b-tree", "index", "search", "logarithmic", "o(log n)"]},
        {"query": "Database normalization 3NF and BCNF", "expected_keywords": ["normalization", "normal", "form", "3nf", "bcnf", "redundancy"]}
    ]
    return await rag_service.evaluate_retrieval(session, current_user.id, test_queries)

@router.get("/{document_id}/preview")
async def preview_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Returns document preview with page count, word count, and extracted text snippets.
    """
    try:
        return await rag_service.get_document_preview(session, current_user.id, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{document_id}/ask")
async def ask_document_content(
    document_id: str,
    req: DocumentAskRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _rate: None = Depends(check_ai_rate_limit)
):
    """
    Asks questions grounded strictly in the document content with exact page references.
    """
    try:
        return await rag_service.ask_document_question(
            session=session,
            user_id=current_user.id,
            document_id=document_id,
            question=req.question.strip(),
            language=req.language or "auto"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{document_id}/notes")
async def get_document_study_notes(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _rate: None = Depends(check_ai_rate_limit)
):
    """
    Generates detailed, structured study notes module-by-module.
    """
    try:
        return await rag_service.generate_study_notes(session, current_user.id, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{document_id}/exam-prep")
async def get_document_exam_prep(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    _rate: None = Depends(check_ai_rate_limit)
):
    """
    Generates high-yield exam questions with model answers, marks, and scoring criteria.
    """
    try:
        return await rag_service.generate_exam_answers(session, current_user.id, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{document_id}/definitions-formulas")
async def get_document_definitions_and_formulas(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Extracts key technical definitions and mathematical/scientific formulas.
    """
    try:
        return await rag_service.extract_definitions_and_formulas(session, current_user.id, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{document_id}/important-topics")
async def get_document_important_topics(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Identifies high-yield topics, importance rating, and estimated exam relevance.
    """
    try:
        return await rag_service.identify_important_topics(session, current_user.id, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{document_id}/revision-kit")
async def get_document_revision_kit(
    document_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Generates rapid revision materials: cheat sheets, flashcards, and common pitfalls.
    """
    try:
        return await rag_service.generate_revision_materials(session, current_user.id, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{document_id}/explain-topic")
async def explain_topic_in_document(
    document_id: str,
    req: DocumentExplainRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Deep-dive explanation of a difficult topic found within the document.
    """
    try:
        return await rag_service.explain_document_topic(
            session=session,
            user_id=current_user.id,
            document_id=document_id,
            topic_name=req.topic.strip()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


