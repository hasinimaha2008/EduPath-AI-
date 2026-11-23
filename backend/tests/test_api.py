import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_root_and_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        root_res = await ac.get("/")
        assert root_res.status_code == 200
        assert "EduPath AI" in root_res.json()["platform"]

@pytest.mark.asyncio
async def test_auth_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Demo login
        res = await ac.get("/api/auth/demo-login")
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "demo@edupath.ai"

        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check /me
        me_res = await ac.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "demo@edupath.ai"

@pytest.mark.asyncio
async def test_skill_mapping_and_careers():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Check career roles
        res = await ac.get("/api/careers/roles")
        assert res.status_code == 200
        roles = res.json()
        assert len(roles) >= 8
        role_titles = [r["title"] for r in roles]
        assert "Python Developer" in role_titles
        assert "Database Developer" in role_titles
        assert "Cybersecurity Analyst" in role_titles

        # Check academic-to-industry mappings
        map_res = await ac.get("/api/skills/mappings")
        assert map_res.status_code == 200
        mappings = map_res.json()
        assert len(mappings) > 0
        dbms_mapping = any(m["subject_name"] in ("DBMS", "Database Management Systems") for m in mappings)
        assert dbms_mapping

@pytest.mark.asyncio
async def test_quiz_generation_and_intelligence_engine():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        auth_res = await ac.get("/api/auth/demo-login")
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Fetch topics
        sub_res = await ac.get("/api/skills/subjects")
        subjects = sub_res.json()
        assert len(subjects) > 0
        topic_id = subjects[0]["topics"][0]["id"]

        # Generate Quiz
        quiz_res = await ac.post(
            "/api/quizzes/generate",
            json={
                "topic_id": topic_id,
                "difficulty": "medium",
                "question_count": 3
            },
            headers=headers
        )
        assert quiz_res.status_code == 200
        quiz_data = quiz_res.json()
        quiz_id = quiz_data["id"]
        assert len(quiz_data["questions"]) > 0

        # Verify answer key is NOT exposed before submission
        assert "correct_answer" not in quiz_data["questions"][0]

        # Submit Quiz
        q1 = quiz_data["questions"][0]
        chosen_opt = q1["options"][0] if q1.get("options") else "Option A"
        submit_res = await ac.post(
            f"/api/quizzes/{quiz_id}/submit",
            json={
                "time_taken_seconds": 60,
                "answers": [{"question_id": q1["id"], "user_response": chosen_opt}]
            },
            headers=headers
        )
        assert submit_res.status_code == 200
        eval_data = submit_res.json()
        assert "percentage" in eval_data
        assert "attempt_id" in eval_data

        # Verify that Learning Analytics and Topic Performance updated
        analytics_res = await ac.get("/api/analytics/dashboard", headers=headers)
        assert analytics_res.status_code == 200
        analytics = analytics_res.json()
        assert analytics["total_quizzes_attempted"] >= 1

        # Check Career Recommendations recalculated
        career_rec_res = await ac.get("/api/careers/recommendations", headers=headers)
        assert career_rec_res.status_code == 200
        recs = career_rec_res.json()
        assert len(recs) > 0

@pytest.mark.asyncio
async def test_notes_and_assistant():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        auth_res = await ac.get("/api/auth/demo-login")
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Ask Assistant
        ask_res = await ac.post(
            "/api/assistant/ask",
            json={"question": "Explain 3NF Normalization in DBMS simply."},
            headers=headers
        )
        assert ask_res.status_code == 200
        res_data = ask_res.json()
        assert "conversation_id" in res_data
        assert "answer" in res_data["assistant_message"]["content"] or len(res_data["assistant_message"]["content"]) > 20

        # Generate Notes
        note_res = await ac.post(
            "/api/notes/generate",
            json={
                "topic_name": "Database Normalization",
                "note_type": "revision"
            },
            headers=headers
        )
        assert note_res.status_code == 200
        note_data = note_res.json()
        assert "Revision" in note_data["title"]
        assert len(note_data["content_markdown"]) > 50

@pytest.mark.asyncio
async def test_security_and_input_validation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Unauthenticated request rejected
        unauth_res = await ac.get("/api/auth/me")
        assert unauth_res.status_code == 401

        # 2. Forged bearer token rejected
        forged_res = await ac.get("/api/auth/me", headers={"Authorization": "Bearer fake.jwt.token"})
        assert forged_res.status_code == 401

        # 3. Missing required fields in login rejected with 422
        val_res = await ac.post("/api/auth/login", json={})
        assert val_res.status_code == 422

        # 4. Non-existent quiz ID returns 404/422
        auth_res = await ac.get("/api/auth/demo-login")
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        not_found_res = await ac.get("/api/quizzes/non-existent-id-12345", headers=headers)
        assert not_found_res.status_code in (404, 422)

@pytest.mark.asyncio
async def test_study_planner_and_roadmaps():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        auth_res = await ac.get("/api/auth/demo-login")
        token = auth_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check Active Study Plan
        plan_res = await ac.get("/api/study-planner/active", headers=headers)
        assert plan_res.status_code in (200, 404)
        if plan_res.status_code == 200:
            plan = plan_res.json()
            assert "tasks" in plan
            assert "adherence_rate" in plan

        # Check Career Roadmaps
        roadmaps_res = await ac.get("/api/roadmaps", headers=headers)
        assert roadmaps_res.status_code == 200
        roadmaps = roadmaps_res.json()
        assert isinstance(roadmaps, list)

@pytest.mark.asyncio
async def test_multi_tenant_data_isolation():
    import time
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register User 1
        u1_email = f"pytest_u1_{int(time.time())}@example.com"
        u1_res = await ac.post("/api/auth/register", json={
            "email": u1_email,
            "password": "Password123!",
            "full_name": "Pytest User 1"
        })
        assert u1_res.status_code == 200
        token_1 = u1_res.json()["access_token"]
        h1 = {"Authorization": f"Bearer {token_1}"}

        # User 1 creates note
        note_res = await ac.post("/api/notes", json={
            "title": "User 1 Secret Notes",
            "content_markdown": "Confidential student data.",
            "note_type": "detailed"
        }, headers=h1)
        assert note_res.status_code == 200
        note_1_id = note_res.json()["id"]

        # Register User 2
        u2_email = f"pytest_u2_{int(time.time())}@example.com"
        u2_res = await ac.post("/api/auth/register", json={
            "email": u2_email,
            "password": "Password123!",
            "full_name": "Pytest User 2"
        })
        assert u2_res.status_code == 200
        token_2 = u2_res.json()["access_token"]
        h2 = {"Authorization": f"Bearer {token_2}"}

        # User 2 cannot see User 1's note in list
        u2_notes = (await ac.get("/api/notes", headers=h2)).json()
        assert not any(n["id"] == note_1_id for n in u2_notes)

        # User 2 cannot access User 1's note directly
        u2_direct = await ac.get(f"/api/notes/{note_1_id}", headers=h2)
        assert u2_direct.status_code in (404, 403)

@pytest.mark.asyncio
async def test_ai_assistant_explanation_levels_and_evaluation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.get("/api/auth/demo-login")
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Verify /status endpoint reports expanded languages and explanation levels
        status_res = await ac.get("/api/assistant/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert "multilingual_supported" in status_data
        assert "ta" in status_data["multilingual_supported"]
        assert "es" in status_data["multilingual_supported"]
        assert "explanation_levels_supported" in status_data
        assert "eli5" in status_data["explanation_levels_supported"]
        assert "advanced" in status_data["explanation_levels_supported"]

        # 2. Test ask with explanation_level='eli5'
        eli5_res = await ac.post("/api/assistant/ask", json={
            "question": "What is a database index?",
            "explanation_level": "eli5"
        }, headers=headers)
        assert eli5_res.status_code == 200
        eli5_answer = eli5_res.json()["assistant_message"]["content"]
        assert len(eli5_answer) > 50
        assert "ELI5" in eli5_answer or "simple" in eli5_answer.lower()

        # 3. Test ask with explanation_level='advanced'
        adv_res = await ac.post("/api/assistant/ask", json={
            "question": "Explain B-Tree indexing concurrency",
            "explanation_level": "advanced"
        }, headers=headers)
        assert adv_res.status_code == 200
        adv_answer = adv_res.json()["assistant_message"]["content"]
        assert len(adv_answer) > 50
        assert "Advanced" in adv_answer or "Complexity" in adv_answer or "Invariants" in adv_answer

        # 4. Test POST /api/assistant/evaluate-answer
        eval_res = await ac.post("/api/assistant/evaluate-answer", json={
            "question": "What are ACID properties in database management systems?",
            "answer": "ACID stands for Atomicity, Consistency, Isolation, and Durability. Atomicity ensures all or nothing. Consistency keeps constraints. Isolation prevents race conditions. Durability writes changes to non-volatile disk logs."
        }, headers=headers)
        assert eval_res.status_code == 200
        eval_data = eval_res.json()
        assert "overall_score" in eval_data
        assert eval_data["overall_score"] >= 60.0
        assert "relevance_score" in eval_data
        assert "accuracy_score" in eval_data
        assert len(eval_data["strengths"]) > 0
        assert "actionable_feedback" in eval_data

@pytest.mark.asyncio
async def test_career_jd_skill_analyzer():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.get("/api/auth/demo-login")
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        jd_text = """
        We are seeking a Backend Software Engineer with strong experience in Python, SQL,
        FastAPI or Django, Docker containerization, PostgreSQL, and Git version control.
        Experience with Kubernetes, CI/CD pipelines, and Microservices is a plus.
        """

        res = await ac.post("/api/careers/analyze-jd", json={
            "job_title": "Senior Backend Software Engineer",
            "company_name": "Tech Innovations Inc.",
            "job_description_text": jd_text
        }, headers=headers)

        assert res.status_code == 200
        data = res.json()
        assert data["job_title"] == "Senior Backend Software Engineer"
        assert len(data["extracted_required_skills"]) >= 4
        assert "Python" in data["extracted_required_skills"]
        assert "SQL" in data["extracted_required_skills"]
        assert "overall_match_percentage" in data
        assert "readiness_status" in data
        assert isinstance(data["recommended_bridge_projects"], list)
        assert len(data["summary_analysis"]) > 20

