import json
import math
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Document, DocumentChunk, DocumentEmbedding
from app.services.gemini_service import gemini_service

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2:
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

class RAGService:
    @staticmethod
    async def index_chunks(session: AsyncSession, chunks: List[DocumentChunk]):
        """
        Generates and saves embeddings for document chunks.
        """
        for chunk in chunks:
            embedding = gemini_service.generate_embedding(chunk.content)
            doc_embedding = DocumentEmbedding(
                chunk_id=chunk.id,
                embedding_json=json.dumps(embedding),
                model_name="gemini-embedding-001"
            )
            session.add(doc_embedding)
        await session.commit()

    @staticmethod
    async def retrieve_relevant_chunks(
        session: AsyncSession,
        user_id: str,
        query: str,
        document_id: Optional[str] = None,
        subject_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant document chunks belonging to user_id.
        Enforces user ownership and security boundaries.
        """
        query_vector = gemini_service.generate_embedding(query)

        # Build query for user documents
        stmt = select(
            DocumentChunk.id,
            DocumentChunk.content,
            DocumentChunk.page_number,
            Document.title,
            DocumentEmbedding.embedding_json
        ).join(
            Document, DocumentChunk.document_id == Document.id
        ).join(
            DocumentEmbedding, DocumentChunk.id == DocumentEmbedding.chunk_id
        ).where(
            Document.user_id == user_id,
            Document.status == "ready"
        )

        if document_id:
            stmt = stmt.where(Document.id == document_id)
        if subject_id:
            stmt = stmt.where(Document.subject_id == subject_id)

        result = await session.execute(stmt)
        rows = result.all()

        scored_chunks = []
        for chunk_id, content, page_num, doc_title, emb_json in rows:
            try:
                emb_vec = json.loads(emb_json)
                score = cosine_similarity(query_vector, emb_vec)
                scored_chunks.append({
                    "chunk_id": chunk_id,
                    "content": content,
                    "page_number": page_num,
                    "doc_title": doc_title,
                    "score": score
                })
            except Exception:
                continue

        # Sort by similarity score descending
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return scored_chunks[:top_k]

rag_service = RAGService()
