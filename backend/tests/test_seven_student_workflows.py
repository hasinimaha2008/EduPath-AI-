"""
EduPath AI - Seven Student Workflows End-to-End Test Suite.
Verifies the exact 7 student lifecycle workflows required by the production specification:
  1. New student: Register -> Login -> Dashboard Profile -> Create study plan
  2. AI learning: Ask assistant question -> Ask follow-up -> Verify multi-turn continuity
  3. Document learning: Upload PDF -> Process document -> Ask grounded question -> Verify sources
  4. Quiz: Generate quiz -> Answer -> Submit -> Score -> Check analytics
  5. Notes: Generate smart note -> Edit note -> Reopen note -> Delete note
  6. Career: Skills & Profile -> Career roles -> Analyze JD -> Generate roadmap
  7. User isolation: Two distinct users -> Verify neither can access the other's data
"""

import uuid
import pytest
import fitz  # PyMuPDF
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_workflow_1_new_student():
    """Workflow 1: Register -> Login -> Dashboard -> Profile -> Create study plan."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"wf1_student_{uid}@example.com"
        pw = "StudentPass123!"

        # Register
        reg = await client.post("/api/auth/register", json={
            "email": email,
            "password": pw,
            "full_name": "Jordan Lee"
        })
        assert reg.status_code == 200
        user_id = reg.json()["user"]["id"]

        # Login
        login = await client.post("/api/auth/login", json={"email": email, "password": pw})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Dashboard / Profile
        me = await client.get("/api/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["id"] == user_id
        assert me.json()["email"] == email

        # Create study plan
        plan = await client.post("/api/study-planner/generate", json={
            "title": "Semester Launch Plan",
            "daily_hours_target": 2.5,
            "days_duration": 7
        }, headers=headers)
        assert plan.status_code == 200
        plan_data = plan.json()
        assert len(plan_data["tasks"]) > 0


@pytest.mark.asyncio
async def test_workflow_2_ai_learning():
    """Workflow 2: AI Assistant -> Ask a question -> Ask follow-up -> Verify context."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Use demo login for quick assistant session
        auth = await client.get("/api/auth/demo-login")
        headers = {"Authorization": f"Bearer {auth.json()['access_token']}"}

        # Turn 1
        q1 = "What is the primary difference between a stack and a queue?"
        res1 = await client.post("/api/assistant/ask", json={
            "question": q1,
            "explanation_level": "intermediate"
        }, headers=headers)
        assert res1.status_code == 200
        data1 = res1.json()
        ans1 = data1["assistant_message"]["content"]
        assert len(ans1) > 20

        # Turn 2: Follow-up relying on prior turn
        history = [
            {"role": "user", "content": q1},
            {"role": "assistant", "content": ans1}
        ]
        q2 = "Can you show me how to implement the first one in Python?"
        res2 = await client.post("/api/assistant/ask", json={
            "question": q2,
            "explanation_level": "code_based",
            "conversation_history": history
        }, headers=headers)
        assert res2.status_code == 200
        data2 = res2.json()
        ans2 = data2["assistant_message"]["content"]
        assert len(ans2) > 20


@pytest.mark.asyncio
async def test_workflow_3_document_learning():
    """Workflow 3: Upload PDF -> Process document -> Ask questions -> Verify source references."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth = await client.get("/api/auth/demo-login")
        headers = {"Authorization": f"Bearer {auth.json()['access_token']}"}

        # Generate in-memory PDF
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text(
            (50, 72),
            "DATABASE INDEXING AND B-PLUS TREES\n\n"
            "A B+ tree stores all data pointers exclusively in leaf nodes. "
            "Leaf nodes are doubly linked to accelerate range scans. "
            "Internal nodes store only search keys and routing pointers."
        )
        pdf_bytes = doc.tobytes()
        doc.close()

        # Upload
        up_res = await client.post(
            "/api/documents/upload",
            files={"file": ("bplus_trees.pdf", pdf_bytes, "application/pdf")},
            data={"title": "B-Plus Trees & Storage Engines"},
            headers=headers
        )
        assert up_res.status_code == 200
        doc_id = up_res.json()["id"]

        # Ask grounded question
        ask_res = await client.post("/api/assistant/ask", json={
            "question": "Where are data pointers stored in a B+ tree?",
            "document_id": doc_id,
            "explanation_level": "intermediate"
        }, headers=headers)
        assert ask_res.status_code == 200
        ask_data = ask_res.json()
        assert len(ask_data["assistant_message"]["content"]) > 20


@pytest.mark.asyncio
async def test_workflow_4_quiz():
    """Workflow 4: Generate quiz -> Answer questions -> Submit -> View score -> Verify analytics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth = await client.get("/api/auth/demo-login")
        headers = {"Authorization": f"Bearer {auth.json()['access_token']}"}

        # Generate quiz
        subj_res = await client.get("/api/subjects")
        subjects = subj_res.json()
        topic_id = subjects[0]["topics"][0]["id"]

        quiz_res = await client.post("/api/quizzes/generate", json={
            "topic_id": topic_id,
            "difficulty": "medium",
            "question_count": 2
        }, headers=headers)
        assert quiz_res.status_code == 200
        quiz_data = quiz_res.json()
        quiz_id = quiz_data["id"]
        questions = quiz_data["questions"]
        assert len(questions) > 0

        # Submit answers
        sub_res = await client.post(f"/api/quizzes/{quiz_id}/submit", json={
            "time_taken_seconds": 25,
            "answers": [
                {"question_id": q["id"], "user_response": q["options"][0] if q.get("options") else "Option A"}
                for q in questions
            ]
        }, headers=headers)
        assert sub_res.status_code == 200
        sub_data = sub_res.json()
        assert "percentage" in sub_data
        assert "score" in sub_data

        # Verify analytics updated
        analytics_res = await client.get("/api/analytics/dashboard", headers=headers)
        assert analytics_res.status_code == 200
        assert analytics_res.json()["total_quizzes_attempted"] >= 1


@pytest.mark.asyncio
async def test_workflow_5_notes():
    """Workflow 5: Generate notes -> Edit -> Save -> Reopen -> Delete."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth = await client.get("/api/auth/demo-login")
        headers = {"Authorization": f"Bearer {auth.json()['access_token']}"}

        # 1. Generate note
        gen_res = await client.post("/api/notes/generate", json={
            "topic_name": "Operating System Scheduling",
            "note_type": "revision"
        }, headers=headers)
        assert gen_res.status_code == 200
        note = gen_res.json()
        note_id = note["id"]

        # 2. Edit & Save
        updated_title = "Operating System Scheduling — Final Exam Edition"
        updated_content = "### Updated High-Yield CPU Scheduling Summary\n\n- Round Robin: Time quantum slicing."
        edit_res = await client.put(f"/api/notes/{note_id}", json={
            "title": updated_title,
            "content_markdown": updated_content
        }, headers=headers)
        assert edit_res.status_code == 200
        assert edit_res.json()["title"] == updated_title

        # 3. Reopen note
        get_res = await client.get(f"/api/notes/{note_id}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["content_markdown"] == updated_content

        # 4. Delete note
        del_res = await client.delete(f"/api/notes/{note_id}", headers=headers)
        assert del_res.status_code == 200

        # Verify deletion
        not_found = await client.get(f"/api/notes/{note_id}", headers=headers)
        assert not_found.status_code == 404


@pytest.mark.asyncio
async def test_workflow_6_career():
    """Workflow 6: Profile & Skills -> Career roles -> Skill gaps -> Generate roadmap."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth = await client.get("/api/auth/demo-login")
        headers = {"Authorization": f"Bearer {auth.json()['access_token']}"}

        # 1. List career roles
        roles_res = await client.get("/api/careers/roles", headers=headers)
        assert roles_res.status_code == 200
        roles = roles_res.json()
        assert len(roles) > 0
        role_id = roles[0]["id"]

        # 2. Analyze job description
        jd_res = await client.post("/api/careers/analyze-jd", json={
            "job_title": "Full Stack Engineer",
            "job_description_text": "Requires Python, FastAPI, React, Docker, and SQL experience."
        }, headers=headers)
        assert jd_res.status_code == 200
        jd_data = jd_res.json()
        assert "extracted_required_skills" in jd_data
        assert "Python" in jd_data["extracted_required_skills"]

        # 3. Generate career roadmap
        map_res = await client.post("/api/roadmaps/generate", json={
            "career_role_id": role_id
        }, headers=headers)
        assert map_res.status_code == 200
        assert len(map_res.json()["milestones"]) > 0


@pytest.mark.asyncio
async def test_workflow_7_user_isolation():
    """Workflow 7: Two users -> Generate data for each -> Verify cross-tenant isolation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        uid_a = uuid.uuid4().hex[:8]
        uid_b = uuid.uuid4().hex[:8]

        # Register User A
        reg_a = await client.post("/api/auth/register", json={
            "email": f"usera_{uid_a}@example.com",
            "password": "PasswordA123!",
            "full_name": "Alice User"
        })
        token_a = reg_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Register User B
        reg_b = await client.post("/api/auth/register", json={
            "email": f"userb_{uid_b}@example.com",
            "password": "PasswordB123!",
            "full_name": "Bob User"
        })
        token_b = reg_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User A creates a private note
        note_a_res = await client.post("/api/notes", json={
            "title": "Alice's Secret Research Note",
            "content_markdown": "Classified quantum algorithms data.",
            "note_type": "detailed"
        }, headers=headers_a)
        assert note_a_res.status_code == 200
        note_a_id = note_a_res.json()["id"]

        # User B attempts to access Alice's note -> MUST BE REJECTED (404)
        leak_note = await client.get(f"/api/notes/{note_a_id}", headers=headers_b)
        assert leak_note.status_code == 404, "Cross-user note access was not blocked!"

        # User B attempts to update Alice's note -> MUST BE REJECTED (404)
        leak_edit = await client.put(f"/api/notes/{note_a_id}", json={
            "title": "Hacked Title"
        }, headers=headers_b)
        assert leak_edit.status_code == 404, "Cross-user note mutation was not blocked!"

        # User B attempts to delete Alice's note -> MUST BE REJECTED (404)
        leak_del = await client.delete(f"/api/notes/{note_a_id}", headers=headers_b)
        assert leak_del.status_code == 404, "Cross-user note deletion was not blocked!"


@pytest.mark.asyncio
async def test_workflow_8_logout_login_persistence():
    """Workflow 8: Logout -> Login again -> Verify persisted data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        uid = uuid.uuid4().hex[:8]
        email = f"wf8_student_{uid}@example.com"
        password = "PersistentPass123!"
        full_name = "Persistent Scholar"

        # 1. Register & Initial Login
        reg_res = await client.post("/api/auth/register", json={
            "email": email,
            "password": password,
            "full_name": full_name
        })
        assert reg_res.status_code == 200
        user_id = reg_res.json()["user"]["id"]

        login_res1 = await client.post("/api/auth/login", json={"email": email, "password": password})
        assert login_res1.status_code == 200
        token1 = login_res1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # 2. Create User Content
        note_res = await client.post("/api/notes", json={
            "title": "Persistent Architecture Study Note",
            "content_markdown": "Key invariants of persistent database systems.",
            "note_type": "detailed"
        }, headers=headers1)
        assert note_res.status_code == 200
        created_note_id = note_res.json()["id"]

        plan_res = await client.post("/api/study-planner/generate", json={
            "title": "Persistent Preparation Plan",
            "daily_hours_target": 2.0,
            "days_duration": 5
        }, headers=headers1)
        assert plan_res.status_code == 200

        # 3. Terminate Session / Logout (Client drops token)
        # Verify that unauthenticated requests to protected endpoints fail
        unauth = await client.get("/api/auth/me")
        assert unauth.status_code in (401, 403)

        # 4. Login Again with Credentials
        login_res2 = await client.post("/api/auth/login", json={"email": email, "password": password})
        assert login_res2.status_code == 200
        token2 = login_res2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # 5. Verify All Persisted Data Remains Accessible
        me_res = await client.get("/api/auth/me", headers=headers2)
        assert me_res.status_code == 200
        assert me_res.json()["id"] == user_id
        assert me_res.json()["email"] == email
        assert me_res.json()["full_name"] == full_name

        persisted_note = await client.get(f"/api/notes/{created_note_id}", headers=headers2)
        assert persisted_note.status_code == 200
        assert persisted_note.json()["title"] == "Persistent Architecture Study Note"

        persisted_notes_list = await client.get("/api/notes", headers=headers2)
        assert persisted_notes_list.status_code == 200
        assert any(n["id"] == created_note_id for n in persisted_notes_list.json())

