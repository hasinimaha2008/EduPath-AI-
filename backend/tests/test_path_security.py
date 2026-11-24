import os
import tempfile
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import is_safe_upload_path, create_access_token
from app.core.database import AsyncSessionLocal
from app.models.models import User, Document

@pytest.mark.asyncio
async def test_is_safe_upload_path_unit_cases():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = os.path.join(tmpdir, "uploads")
        os.makedirs(base_dir, exist_ok=True)

        sibling_dir = os.path.join(tmpdir, "uploads_evil")
        os.makedirs(sibling_dir, exist_ok=True)
        sibling_file = os.path.join(sibling_dir, "secret.txt")
        with open(sibling_file, "w") as f:
            f.write("secret data")

        valid_file = os.path.join(base_dir, "valid.pdf")
        with open(valid_file, "w") as f:
            f.write("valid data")

        valid_subfolder = os.path.join(base_dir, "sub", "doc.pdf")
        os.makedirs(os.path.dirname(valid_subfolder), exist_ok=True)
        with open(valid_subfolder, "w") as f:
            f.write("sub doc")

        # 1. Valid paths inside base_dir
        assert is_safe_upload_path(base_dir, valid_file) is True
        assert is_safe_upload_path(base_dir, valid_subfolder) is True

        # 2. Sibling directory attack (bypasses simple .startswith() if not checking delimiters)
        # Sibling directory has common prefix "uploads", but is NOT inside "uploads"
        assert is_safe_upload_path(base_dir, sibling_file) is False
        assert is_safe_upload_path(base_dir, sibling_dir) is False

        # 3. Directory traversal via ../
        traversal_target = os.path.join(base_dir, "..", "secret.txt")
        assert is_safe_upload_path(base_dir, traversal_target) is False

        deep_traversal = os.path.join(base_dir, "sub", "..", "..", "outside.txt")
        assert is_safe_upload_path(base_dir, deep_traversal) is False

        # 4. Target is the base directory itself
        assert is_safe_upload_path(base_dir, base_dir) is False

        # 5. Empty or None paths
        assert is_safe_upload_path(base_dir, "") is False
        assert is_safe_upload_path("", valid_file) is False
        assert is_safe_upload_path(None, valid_file) is False

        # 6. Symlink pointing outside base_dir (if platform allows symlink creation)
        try:
            symlink_path = os.path.join(base_dir, "symlink_evil.txt")
            os.symlink(sibling_file, symlink_path)
            # Should resolve to sibling_file outside base_dir and be safely rejected
            assert is_safe_upload_path(base_dir, symlink_path) is False
        except (OSError, NotImplementedError):
            pass  # Windows unprivileged environments without SeCreateSymbolicLinkPrivilege

@pytest.mark.asyncio
async def test_download_endpoint_path_traversal_rejection():
    """
    Ensures that /api/documents/{id}/download strictly rejects sibling-directory
    and traversal attempts with HTTP 400.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create test user and token
        user_id = "test-path-sec-user-123"
        token = create_access_token(subject=user_id)
        headers = {"Authorization": f"Bearer {token}"}

        # Create user in db
        async with AsyncSessionLocal() as session:
            existing_user = await session.get(User, user_id)
            if not existing_user:
                new_user = User(
                    id=user_id,
                    email="path_sec_user@example.com",
                    full_name="Path Security Tester",
                    hashed_password="testhash"
                )
                session.add(new_user)
                await session.commit()

            # Create document with sibling directory path
            with tempfile.TemporaryDirectory() as tmpdir:
                sibling_file = os.path.join(tmpdir, "secret_host_data.txt")
                with open(sibling_file, "w") as f:
                    f.write("critical host data")

                doc_id = "malicious-doc-uuid-999"
                existing_doc = await session.get(Document, doc_id)
                if not existing_doc:
                    malicious_doc = Document(
                        id=doc_id,
                        user_id=user_id,
                        title="Malicious Sibling Doc",
                        file_name="secret.txt",
                        file_path=sibling_file,
                        file_size=len("critical host data"),
                        file_type="txt",
                        status="ready"
                    )
                    session.add(malicious_doc)
                    await session.commit()

        # Attempt to download via API
        resp = await client.get(f"/api/documents/{doc_id}/download", headers=headers)
        assert resp.status_code == 400
        assert "Invalid document storage path or traversal attempt detected" in resp.json()["detail"]

@pytest.mark.asyncio
async def test_delete_endpoint_does_not_remove_sibling_file():
    """
    Ensures that /api/documents/{id} does not physically remove files outside
    UPLOAD_DIR even if malicious DB records point to external paths.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        import uuid
        uid = uuid.uuid4().hex[:8]
        user_id = f"test-del-sec-{uid}"
        token = create_access_token(subject=user_id)
        headers = {"Authorization": f"Bearer {token}"}

        with tempfile.TemporaryDirectory() as tmpdir:
            sibling_file = os.path.join(tmpdir, "do_not_delete.txt")
            with open(sibling_file, "w") as f:
                f.write("must remain safe")

            async with AsyncSessionLocal() as session:
                new_user = User(
                    id=user_id,
                    email=f"del_sec_{uid}@example.com",
                    full_name="Delete Security Tester",
                    hashed_password="testhash"
                )
                session.add(new_user)

                doc_id = f"del-doc-{uid}"
                doc = Document(
                    id=doc_id,
                    user_id=user_id,
                    title="External Path Doc",
                    file_name="do_not_delete.txt",
                    file_path=sibling_file,
                    file_size=10,
                    file_type="txt",
                    status="ready"
                )
                session.add(doc)
                await session.commit()

            # Execute delete via API
            resp = await client.delete(f"/api/documents/{doc_id}", headers=headers)
            assert resp.status_code == 200

            # Verify the physical file outside UPLOAD_DIR was NOT deleted!
            assert os.path.exists(sibling_file) is True
            with open(sibling_file, "r") as f:
                assert f.read() == "must remain safe"
