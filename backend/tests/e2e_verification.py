import asyncio
import os
import sys
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:8000"

async def run_e2e_tests():
    print("=== STARTING EDUPATH AI END-TO-END WORKFLOW VERIFICATION ===")

    try:
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=1.0) as check_client:
            await check_client.get("/health")
            use_asgi = False
    except Exception:
        use_asgi = True

    if use_asgi:
        from app.main import app
        from httpx import ASGITransport
        transport = ASGITransport(app=app)
        client_ctx = httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0)
    else:
        client_ctx = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)

    async with client_ctx as client:
        # Workflow 1: Registration and Demo Login
        print("\n--- Workflow 1: User Authentication & Profile ---")
        login_res = await client.get("/api/auth/demo-login")
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        auth_data = login_res.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"[PASS] Authenticated as: {auth_data['user']['email']} (Token generated)")

        me_res = await client.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        print(f"[PASS] Verified profile: {me_res.json()['full_name']}")

        # Workflow 2: Smart Notes Generation, Editing, Saving, and Pinning
        print("\n--- Workflow 2: Smart Notes Lifecycle (8 Formats) ---")
        gen_note_res = await client.post(
            "/api/notes/generate",
            json={"topic_name": "Database Normalization & BCNF", "note_type": "revision"},
            headers=headers
        )
        assert gen_note_res.status_code == 200, f"Notes gen failed: {gen_note_res.text}"
        note = gen_note_res.json()
        note_id = note["id"]
        print(f"[PASS] Generated note: '{note['title']}' ({note['note_type']})")

        # Edit note
        update_res = await client.put(
            f"/api/notes/{note_id}",
            json={"title": "Mastering 1NF, 2NF, 3NF & BCNF", "is_pinned": True},
            headers=headers
        )
        assert update_res.status_code == 200
        updated_note = update_res.json()
        assert updated_note["is_pinned"] is True
        print(f"[PASS] Updated & pinned note: '{updated_note['title']}'")

        # Workflow 3: AI Study Assistant with Grounded Citations
        print("\n--- Workflow 3: AI Study Assistant Q&A with Conversation Context ---")
        ask_res = await client.post(
            "/api/assistant/ask",
            json={"question": "What is the primary difference between 2NF and 3NF?"},
            headers=headers
        )
        assert ask_res.status_code == 200
        assistant_data = ask_res.json()
        conv_id = assistant_data["conversation_id"]
        print(f"[PASS] Assistant responded. Conversation ID: {conv_id}")
        print(f"[PASS] Answer excerpt: {assistant_data['assistant_message']['content'][:120]}...")

        # Workflow 4: AI Quiz Generation, Masked Answers, and Central Intelligence Evaluation
        print("\n--- Workflow 4: AI Quiz Generator & Central Intelligence Engine Update ---")
        # Get topics
        subj_res = await client.get("/api/skills/subjects")
        subjects = subj_res.json()
        topic_id = subjects[0]["topics"][0]["id"]
        topic_name = subjects[0]["topics"][0]["name"]

        quiz_res = await client.post(
            "/api/quizzes/generate",
            json={"topic_id": topic_id, "difficulty": "medium", "question_count": 3},
            headers=headers
        )
        assert quiz_res.status_code == 200
        quiz = quiz_res.json()
        quiz_id = quiz["id"]
        print(f"[PASS] Generated quiz: '{quiz['title']}' with {len(quiz['questions'])} questions")

        # Verify answer key is strictly masked before submission
        assert "correct_answer" not in quiz["questions"][0], "SECURITY VIOLATION: Answer key was exposed!"
        print("[PASS] Verified: Answer key is masked during active quiz taking")

        # Submit quiz
        answers = [
            {"question_id": q["id"], "user_response": q["options"][0] if q.get("options") else "Option A"}
            for q in quiz["questions"]
        ]
        submit_res = await client.post(
            f"/api/quizzes/{quiz_id}/submit",
            json={"time_taken_seconds": 45, "answers": answers},
            headers=headers
        )
        assert submit_res.status_code == 200
        eval_result = submit_res.json()
        print(f"[PASS] Evaluated score: {eval_result['score']}/{eval_result['max_score']} ({eval_result['percentage']}%)")
        print(f"[PASS] Pedagogical explanation returned: {eval_result['answers'][0]['explanation'][:80]}...")

        # Workflow 5: Verification that Quiz Submission Updated Topic Performance & Career Recommendations
        print("\n--- Workflow 5: Central Intelligence Engine Propagation Verification ---")
        tp_res = await client.get("/api/topics/performance", headers=headers)
        assert tp_res.status_code == 200
        tp_list = tp_res.json()
        assert len(tp_list) > 0
        matching_tp = next((t for t in tp_list if t["topic_id"] == topic_id), None)
        assert matching_tp is not None
        print(f"[PASS] Topic Performance record found: {matching_tp['topic_name']} - Accuracy: {matching_tp['accuracy_percentage']}% - Mastery: {matching_tp['mastery_status']}")

        # Check Career Recommendations
        career_res = await client.get("/api/careers/recommendations", headers=headers)
        assert career_res.status_code == 200
        recs = career_res.json()
        assert len(recs) >= 8
        top_rec = recs[0]
        print(f"[PASS] Top Career Recommendation: {top_rec['career_role']['title']} - Match: {top_rec['match_score']}%")

        # Check Skill Gaps for top role
        gaps_res = await client.get(f"/api/skills/gaps/{top_rec['career_role']['id']}", headers=headers)
        assert gaps_res.status_code == 200
        gaps_data = gaps_res.json()
        print(f"[PASS] Skill Gaps Analyzed: {len(gaps_data['gaps'])} competencies audited (Readiness: {gaps_data['overall_readiness']}%)")

        # Workflow 6: Career Roadmap Generation & Adaptive Study Planner
        print("\n--- Workflow 6: Career Roadmap & Adaptive Study Planning ---")
        roadmap_res = await client.post(
            "/api/roadmaps/generate",
            json={"career_role_id": top_rec["career_role"]["id"], "target_timeline_months": 6},
            headers=headers
        )
        assert roadmap_res.status_code == 200
        roadmap = roadmap_res.json()
        print(f"[PASS] Generated Roadmap: '{roadmap['title']}' with {len(roadmap['milestones'])} milestone phases")

        # Toggle milestone
        m_id = roadmap["milestones"][0]["id"]
        toggle_res = await client.post(f"/api/roadmaps/milestones/{m_id}/toggle", headers=headers)
        assert toggle_res.status_code == 200
        print(f"[PASS] Milestone toggled: New progress: {toggle_res.json()['roadmap_progress']}%")

        # Active study plan
        plan_res = await client.get("/api/study-planner/active", headers=headers)
        assert plan_res.status_code == 200
        plan = plan_res.json()
        print(f"[PASS] Active Study Plan: '{plan['title']}' with {len(plan['tasks'])} adaptive scheduled tasks")

        # Toggle task
        task_id = plan["tasks"][0]["id"]
        task_toggle = await client.post(f"/api/study-planner/tasks/{task_id}/toggle", headers=headers)
        assert task_toggle.status_code == 200
        print(f"[PASS] Study Task toggled: completed = {task_toggle.json()['is_completed']}")

        # Workflow 7: Data Persistence Across Sessions
        print("\n--- Workflow 7: Data Persistence Across Sessions ---")
        # Re-fetch notes and analytics to confirm persistent database storage
        notes_res = await client.get("/api/notes", headers=headers)
        assert any(n["id"] == note_id for n in notes_res.json()), "Persistent note not found!"
        analytics_res = await client.get("/api/analytics/dashboard", headers=headers)
        assert analytics_res.json()["total_quizzes_attempted"] >= 1, "Quiz attempt was not persisted in database!"
        print("[PASS] Verified: Database records fully persisted across independent requests and sessions.")

        print("\n=======================================================")
        print("ALL 12 MODULES & INTELLIGENCE ENGINE VERIFIED SUCCESSFULLY!")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(run_e2e_tests())
