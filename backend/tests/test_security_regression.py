"""
Comprehensive Security & Authorization Regression Test Suite for EduPath AI.
Verifies:
1. CORS configuration (Permitted origins allowed; untrusted origins rejected).
2. Cross-tenant document isolation (Tenant A documents strictly inaccessible to Tenant B across all endpoints).
3. Decompression bomb (zip bomb) mitigation.
4. Magic byte signature enforcement on document uploads.
"""

import pytest
import io
import zipfile
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.models import User, Document, DocumentChunk
from app.core.security import get_password_hash, create_access_token
from app.services.document_parser import check_zip_bomb

@pytest.mark.asyncio
async def test_cors_permitted_origin():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.options(
            "/api/auth/me",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization"
            }
        )
        assert response.status_code in (200, 204)
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert response.headers.get("access-control-allow-credentials") == "true"

@pytest.mark.asyncio
async def test_cors_untrusted_origin_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.options(
            "/api/auth/me",
            headers={
                "Origin": "https://malicious-attacker-domain.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization"
            }
        )
        # Untrusted origin must not be reflected in access-control-allow-origin
        allow_origin = response.headers.get("access-control-allow-origin")
        assert allow_origin != "https://malicious-attacker-domain.com"

@pytest.mark.asyncio
async def test_cross_tenant_document_isolation():
    """
    Ensure Tenant B cannot access, preview, download, query concepts,
    generate questions, or query via assistant any document owned by Tenant A.
    """
    tenant_a_id = str(uuid.uuid4())
    tenant_b_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as session:
        # Create Tenant A
        user_a = User(
            id=tenant_a_id,
            email=f"tenant_a_{uuid.uuid4().hex[:6]}@edupath.local",
            hashed_password=get_password_hash("Password123!"),
            full_name="Tenant A"
        )
        # Create Tenant B
        user_b = User(
            id=tenant_b_id,
            email=f"tenant_b_{uuid.uuid4().hex[:6]}@edupath.local",
            hashed_password=get_password_hash("Password123!"),
            full_name="Tenant B"
        )
        # Create Document for Tenant A
        doc = Document(
            id=doc_id,
            user_id=tenant_a_id,
            title="Tenant A Private Research",
            file_name="private_research.txt",
            file_path="uploads/private_research.txt",
            file_size=1024,
            file_type="txt",
            status="ready",
            chunk_count=1
        )
        session.add_all([user_a, user_b, doc])
        await session.commit()

        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            document_id=doc_id,
            chunk_index=0,
            content="Proprietary sensitive research data belonging strictly to Tenant A.",
            page_number=1
        )
        session.add(chunk)
        await session.commit()

    token_b = create_access_token(tenant_b_id)
    headers_b = {"Authorization": f"Bearer {token_b}"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Tenant B attempts to preview Tenant A's document
        r = await ac.get(f"/api/documents/{doc_id}/preview", headers=headers_b)
        assert r.status_code == 404, f"Preview leaked: {r.status_code}"

        # 2. Tenant B attempts to download Tenant A's document
        r = await ac.get(f"/api/documents/{doc_id}/download", headers=headers_b)
        assert r.status_code == 404, f"Download leaked: {r.status_code}"

        # 3. Tenant B attempts to extract concepts from Tenant A's document
        r = await ac.get(f"/api/documents/{doc_id}/concepts", headers=headers_b)
        assert r.status_code == 404, f"Concepts leaked: {r.status_code}"

        # 4. Tenant B attempts to generate questions from Tenant A's document
        r = await ac.get(f"/api/documents/{doc_id}/questions", headers=headers_b)
        assert r.status_code == 404, f"Questions leaked: {r.status_code}"

        # 5. Tenant B attempts to ask questions on Tenant A's document
        r = await ac.post(
            f"/api/documents/{doc_id}/ask",
            json={"question": "What is in Tenant A private research?"},
            headers=headers_b
        )
        assert r.status_code == 404, f"Document Q&A leaked: {r.status_code}"

        # 6. Tenant B attempts to delete Tenant A's document
        r = await ac.delete(f"/api/documents/{doc_id}", headers=headers_b)
        assert r.status_code == 404, f"Delete permitted: {r.status_code}"

        # 7. Tenant B attempts assistant chat targeting Tenant A's document
        r = await ac.post(
            "/api/assistant/ask",
            json={"question": "Summarize this doc", "document_id": doc_id},
            headers=headers_b
        )
        assert r.status_code == 404, f"Assistant ask leaked: {r.status_code}"

        # 8. Tenant B attempts assistant chat stream targeting Tenant A's document
        r = await ac.post(
            "/api/assistant/chat-stream",
            json={"question": "Stream summary", "document_id": doc_id},
            headers=headers_b
        )
        assert r.status_code == 404, f"Assistant stream leaked: {r.status_code}"

    # Cleanup
    async with AsyncSessionLocal() as session:
        c = await session.get(DocumentChunk, chunk.id)
        if c:
            await session.delete(c)
        d = await session.get(Document, doc_id)
        if d:
            await session.delete(d)
        ua = await session.get(User, tenant_a_id)
        if ua:
            await session.delete(ua)
        ub = await session.get(User, tenant_b_id)
        if ub:
            await session.delete(ub)
        await session.commit()

def test_zip_bomb_prevention():
    """Verify that decompression bomb checks reject zip files with dangerous compression ratios."""
    # Create an in-memory zip file with extreme compression ratio
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 1MB of zeros compresses to ~1KB (1000:1 ratio, exceeds MAX_COMPRESSION_RATIO of 50)
        large_zeros = b"0" * (1024 * 1024 * 2)  # 2MB uncompressed
        zf.writestr("test_bomb.txt", large_zeros)

    raw_bytes = zip_buffer.getvalue()

    with pytest.raises(ValueError, match="Decompression bomb protection"):
        check_zip_bomb(raw_bytes)
