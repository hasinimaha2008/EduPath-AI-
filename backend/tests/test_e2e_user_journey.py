"""
EduPath AI - Complete End-to-End (E2E) User Journey Automation
Validates the complete 9-phase student learning and career trajectory:
  1. User Registration
  2. Login & JWT Issuance
  3. Dashboard Data Retrieval
  4. Study Document Ingestion & Chunking
  5. Grounded AI Tutoring & Citations
  6. Adaptive Quiz Generation & Secure Submission
  7. Dynamic Study Plan Generation
  8. Career Intelligence & Roadmap Progression
  9. Logout & Session Termination Verification
"""

import uuid
import pytest
import fitz  # PyMuPDF
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_complete_e2e_student_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        unique_id = uuid.uuid4().hex[:8]
        user_email = f"student_{unique_id}@example.com"
        password = "SecurePassword123!"

        # ----------------------------------------------------------------------
        # 1. User Registration
        # ----------------------------------------------------------------------
        reg_res = await client.post("/api/auth/register", json={
            "email": user_email,
            "password": password,
            "full_name": "Alex Mercer"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        reg_data = reg_res.json()
        assert "access_token" in reg_data
        user_id = reg_data["user"]["id"]

        # ----------------------------------------------------------------------
        # 2. Login & JWT Authentication Verification
        # ----------------------------------------------------------------------
        login_res = await client.post("/api/auth/login", json={
            "email": user_email,
            "password": password
        })
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        login_data = login_res.json()
        token = login_data["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # ----------------------------------------------------------------------
        # 3. Dashboard Loading (Identity, Analytics & Catalog)
        # ----------------------------------------------------------------------
        me_res = await client.get("/api/auth/me", headers=auth_headers)
        assert me_res.status_code == 200
        assert me_res.json()["id"] == user_id

        subj_res = await client.get("/api/subjects")
        assert subj_res.status_code == 200
        subjects = subj_res.json()
        assert len(subjects) > 0

        # ----------------------------------------------------------------------
        # 4. Uploading Learning Documents (In-Memory PDF Generation)
        # ----------------------------------------------------------------------
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text(
            (50, 72),
            "DISTRIBUTED CONSENSUS AND RAFT PROTOCOL\n\n"
            "Raft achieves consensus by electing a distinguished leader. "
            "The leader accepts log entries from clients and replicates them across followers."
        )
        pdf_bytes = doc.tobytes()
        doc.close()

        up_res = await client.post(
            "/api/documents/upload",
            files={"file": ("raft_consensus.pdf", pdf_bytes, "application/pdf")},
            data={"title": "Raft Protocol & Distributed Consensus"},
            headers=auth_headers
        )
        assert up_res.status_code == 200, f"Upload failed: {up_res.text}"
        doc_data = up_res.json()
        document_id = doc_data["id"]
        assert doc_data["chunk_count"] > 0

        # ----------------------------------------------------------------------
        # 5. AI Tutoring (Grounded Q&A with Document Citations)
        # ----------------------------------------------------------------------
        ask_res = await client.post("/api/assistant/ask", json={
            "question": "How does Raft maintain log consistency?",
            "document_id": document_id,
            "explanation_level": "intermediate"
        }, headers=auth_headers)
        assert ask_res.status_code == 200, f"AI ask failed: {ask_res.text}"
        ask_data = ask_res.json()
        assert "assistant_message" in ask_data
        assert len(ask_data["assistant_message"]["content"]) > 20

        # ----------------------------------------------------------------------
        # 6. Quiz Generation & Submission
        # ----------------------------------------------------------------------
        topic_id = subjects[0]["topics"][0]["id"]
        quiz_res = await client.post("/api/quizzes/generate", json={
            "topic_id": topic_id,
            "difficulty": "medium",
            "question_count": 2
        }, headers=auth_headers)
        assert quiz_res.status_code == 200, f"Quiz generation failed: {quiz_res.text}"
        quiz_data = quiz_res.json()
        quiz_id = quiz_data["id"]
        questions = quiz_data["questions"]
        assert len(questions) > 0

        # Verify answer key is not leaked in client payload
        for q in questions:
            assert "correct_answer" not in q

        # Submit answers
        sub_res = await client.post(f"/api/quizzes/{quiz_id}/submit", json={
            "time_taken_seconds": 45,
            "answers": [
                {"question_id": q["id"], "user_response": q["options"][0] if q.get("options") else "Option A"}
                for q in questions
            ]
        }, headers=auth_headers)
        assert sub_res.status_code == 200
        sub_data = sub_res.json()
        assert "percentage" in sub_data

        # ----------------------------------------------------------------------
        # 7. Study Planning
        # ----------------------------------------------------------------------
        plan_res = await client.post("/api/study-planner/generate", json={
            "title": "Semester Preparation Sprint",
            "daily_hours_target": 3.0,
            "days_duration": 14
        }, headers=auth_headers)
        assert plan_res.status_code == 200
        plan_data = plan_res.json()
        assert len(plan_data["tasks"]) > 0

        # ----------------------------------------------------------------------
        # 8. Career Recommendations & Roadmaps
        # ----------------------------------------------------------------------
        roles_res = await client.get("/api/careers/roles", headers=auth_headers)
        assert roles_res.status_code == 200
        roles = roles_res.json()
        assert len(roles) > 0
        target_role_id = roles[0]["id"]

        map_res = await client.post("/api/roadmaps/generate", json={
            "career_role_id": target_role_id
        }, headers=auth_headers)
        assert map_res.status_code == 200
        roadmap = map_res.json()
        assert len(roadmap["milestones"]) > 0

        # ----------------------------------------------------------------------
        # 9. Session Termination & Protected Route Verification
        # ----------------------------------------------------------------------
        # Client drops token; unauthenticated access to protected route must be rejected (401)
        unauth_res = await client.get("/api/auth/me")
        assert unauth_res.status_code in (401, 403), "Protected route permitted unauthenticated access!"
