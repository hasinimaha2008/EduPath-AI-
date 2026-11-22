import asyncio
import os
import json
import httpx
import fitz  # PyMuPDF

BASE_URL = "http://127.0.0.1:8000"

async def deep_audit():
    print("=" * 70)
    print("EDUPATH AI: DEEP FEATURE-BY-FEATURE FUNCTIONALITY BACKTESTING")
    print("=" * 70)

    results = {}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=40.0) as client:
        # Auth Preparation
        print("\n[INIT] Authenticating Test Session...")
        login_res = await client.get("/api/auth/demo-login")
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(" -> Session authenticated as demo user.")

        # ---------------------------------------------------------
        # Feature 11: Document Upload & Management (PDF Extraction & RAG)
        # ---------------------------------------------------------
        print("\n--- Testing Feature 11: Document Upload & RAG Indexing ---")
        pdf_path = "test_study_doc.pdf"
        doc = fitz.open()
        page1 = doc.new_page()
        page1.insert_text(
            (50, 72),
            "DATABASE NORMALIZATION AND INTEGRITY RULES\n\n"
            "Page 1 Content:\n"
            "First Normal Form (1NF) mandates that table cells contain atomic values and no repeating groups.\n"
            "Second Normal Form (2NF) eliminates partial dependency, ensuring non-prime attributes depend on candidate key.\n"
            "Third Normal Form (3NF) strictly resolves transitive functional dependencies (X -> Y -> Z)."
        )
        page2 = doc.new_page()
        page2.insert_text(
            (50, 72),
            "CONCURRENCY CONTROL AND ACID PROPERTIES\n\n"
            "Page 2 Content:\n"
            "ACID transactions guarantee Atomicity, Consistency, Isolation, and Durability.\n"
            "Two-Phase Locking (2PL) avoids conflict serializability anomalies.\n"
            "Deadlocks are detected via Wait-For Graphs."
        )
        doc.save(pdf_path)
        doc.close()

        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path, f, "application/pdf")}
            data = {"title": "DBMS Comprehensive Normalization Lecture"}
            up_res = await client.post("/api/documents/upload", files=files, data=data, headers=headers)

        assert up_res.status_code == 200, f"Doc upload failed: {up_res.text}"
        uploaded_doc = up_res.json()
        doc_id = uploaded_doc["id"]
        assert uploaded_doc["status"] == "ready", f"Status expected ready, got {uploaded_doc['status']}"
        assert uploaded_doc["chunk_count"] >= 2, f"Expected chunks >= 2, got {uploaded_doc['chunk_count']}"
        print(f" [PASS] Feature 11: Document parsed, {uploaded_doc['chunk_count']} chunks indexed into vector storage.")
        results["Feature 11 (Document Upload & RAG Indexing)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 1: AI Study Assistant (RAG Q&A with Page Citations)
        # ---------------------------------------------------------
        print("\n--- Testing Feature 1: AI Study Assistant (Cited RAG Q&A) ---")
        ask_res = await client.post(
            "/api/assistant/ask",
            json={
                "question": "What does Third Normal Form (3NF) strictly resolve according to my notes?",
                "document_id": doc_id
            },
            headers=headers
        )
        assert ask_res.status_code == 200, f"Assistant ask failed: {ask_res.text}"
        ask_data = ask_res.json()
        conv_id = ask_data["conversation_id"]
        citations = ask_data["assistant_message"].get("citations")
        assert citations is not None and len(citations) > 0, "No citations returned for grounded document!"
        print(f" [PASS] Feature 1: Study Assistant cited '{citations[0]['doc_title']}' on Page {citations[0]['page_number']}.")
        results["Feature 1 (AI Study Assistant & Citations)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 12: AI Chat History (Sessions & Citations Persistence)
        # ---------------------------------------------------------
        print("\n--- Testing Feature 12: AI Chat History Persistence ---")
        hist_list_res = await client.get("/api/chat-history", headers=headers)
        assert hist_list_res.status_code == 200
        convs = hist_list_res.json()
        assert any(c["id"] == conv_id for c in convs), "Conversation not found in chat history!"
        
        # Rename conversation
        ren_res = await client.put(f"/api/chat-history/{conv_id}", json={"title": "3NF & Concurrency Review"}, headers=headers)
        assert ren_res.status_code == 200
        assert ren_res.json()["title"] == "3NF & Concurrency Review"
        print(f" [PASS] Feature 12: Conversation successfully persisted, retrieved, and renamed.")
        results["Feature 12 (AI Chat History)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 2: Smart Notes Generator (8 Specialized Formats)
        # ---------------------------------------------------------
        print("\n--- Testing Feature 2: Smart Notes Generator (8 Formats) ---")
        note_formats = [
            "short", "detailed", "chapter_wise", "exam_oriented",
            "revision", "definitions", "key_points", "questions"
        ]
        created_note_ids = []
        for fmt in note_formats:
            n_res = await client.post(
                "/api/notes/generate",
                json={"document_id": doc_id, "note_type": fmt},
                headers=headers
            )
            assert n_res.status_code == 200, f"Failed note format: {fmt}"
            note_obj = n_res.json()
            assert fmt in note_obj["note_type"]
            assert len(note_obj["content_markdown"]) > 40
            created_note_ids.append(note_obj["id"])
        
        print(f" [PASS] Feature 2: Generated notes across all 8 formats successfully.")
        
        # Test Note Update & Pin
        pin_res = await client.put(f"/api/notes/{created_note_ids[0]}", json={"is_pinned": True}, headers=headers)
        assert pin_res.status_code == 200 and pin_res.json()["is_pinned"] is True
        print(f" [PASS] Feature 2: Note pinned and updated.")
        results["Feature 2 (Smart Notes Generator - 8 Formats)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 3: AI Quiz Generator & Answer Key Security
        # ---------------------------------------------------------
        print("\n--- Testing Feature 3: AI Quiz Generator & Answer Key Masking ---")
        # Fetch DBMS Subject Topics
        subj_res = await client.get("/api/skills/subjects")
        subjects = subj_res.json()
        dbms_subj = next(s for s in subjects if "DBMS" in s["name"] or "Database" in s["name"])
        sql_topic = next(t for t in dbms_subj["topics"] if "SQL" in t["name"])

        quiz_res = await client.post(
            "/api/quizzes/generate",
            json={
                "topic_id": sql_topic["id"],
                "difficulty": "medium",
                "question_count": 4
            },
            headers=headers
        )
        assert quiz_res.status_code == 200
        quiz = quiz_res.json()
        quiz_id = quiz["id"]
        assert len(quiz["questions"]) == 4

        # CRITICAL SECURITY VERIFICATION: Verify answer keys are strictly hidden
        for q in quiz["questions"]:
            assert "correct_answer" not in q, "SECURITY BREACH: correct_answer was exposed to client!"
            assert "explanation" not in q, "SECURITY BREACH: explanation was exposed to client!"
        print(" [PASS] Feature 3: Answer keys strictly masked during quiz taking.")

        # Submit Quiz
        q1_ans = quiz["questions"][0]["options"][0] if quiz["questions"][0].get("options") else "Option A"
        eval_sub_res = await client.post(
            f"/api/quizzes/{quiz_id}/submit",
            json={
                "time_taken_seconds": 95,
                "answers": [
                    {"question_id": q["id"], "user_response": q["options"][0] if q.get("options") else "Option A"}
                    for q in quiz["questions"]
                ]
            },
            headers=headers
        )
        assert eval_sub_res.status_code == 200, f"Quiz submit failed: {eval_sub_res.status_code} - {eval_sub_res.text}"
        quiz_eval = eval_sub_res.json()
        assert "score" in quiz_eval and "max_score" in quiz_eval
        assert "answers" in quiz_eval
        print(f" [PASS] Feature 3: Quiz submitted and evaluated. Score: {quiz_eval['score']}/{quiz_eval['max_score']} ({quiz_eval['percentage']}%)")
        results["Feature 3 (AI Quiz Generator & Evaluation)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 5: Topic Performance & Repeated Evidence Mastery
        # ---------------------------------------------------------
        print("\n--- Testing Feature 5: Topic Performance & Mastery Evidence Standard ---")
        tp_res = await client.get("/api/topics/performance", headers=headers)
        assert tp_res.status_code == 200
        tp_records = tp_res.json()
        sql_tp = next((t for t in tp_records if t["topic_id"] == sql_topic["id"]), None)
        assert sql_tp is not None
        print(f" -> Current Topic State: Attempts = {sql_tp['total_attempts']}, Accuracy = {sql_tp['accuracy_percentage']}%, Mastery = '{sql_tp['mastery_status']}'")
        
        # Verify single attempt does NOT award 'mastered' (requires repeated evidence >= 3 attempts)
        assert sql_tp["mastery_status"] != "mastered", "Repeated evidence violation: awarded mastered on 1 attempt!"
        print(" [PASS] Feature 5: Repeated evidence rule respected (single attempt cannot award mastery).")
        results["Feature 5 (Topic Performance & Mastery Rules)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 4: Learning Analytics Dashboard (Real Metrics)
        # ---------------------------------------------------------
        print("\n--- Testing Feature 4: Learning Analytics Dashboard ---")
        an_res = await client.get("/api/analytics/dashboard", headers=headers)
        assert an_res.status_code == 200
        an = an_res.json()
        assert an["total_quizzes_attempted"] >= 1
        assert an["average_quiz_score"] > 0
        assert len(an["recent_activity"]) == 7
        assert len(an["revision_recommendations"]) > 0
        print(f" [PASS] Feature 4: Real user analytics computed (Total Quizzes: {an['total_quizzes_attempted']}, Avg Score: {an['average_quiz_score']}%).")
        results["Feature 4 (Learning Analytics Dashboard)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 7: Academic-to-Industry Skill Mapping
        # ---------------------------------------------------------
        print("\n--- Testing Feature 7: Academic-to-Industry Skill Mapping ---")
        map_res = await client.get("/api/skills/mappings")
        assert map_res.status_code == 200
        mappings = map_res.json()
        assert len(mappings) >= 10
        # Check DBMS topic mapping
        dbms_map = next((m for m in mappings if m["subject_name"] in ("DBMS", "Database Management Systems")), None)
        assert dbms_map is not None
        print(f" [PASS] Feature 7: Verified Academic-to-Industry mapping: {dbms_map['subject_name']} -> {dbms_map['topic_name']} -> {dbms_map['competency_name']} -> {dbms_map['skill_name']} -> {dbms_map['career_role_title']}")
        results["Feature 7 (Academic-to-Industry Skill Mapping)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 6: Career Intelligence & Recommendations
        # ---------------------------------------------------------
        print("\n--- Testing Feature 6: Career Intelligence (8 Core Roles) ---")
        car_res = await client.get("/api/careers/recommendations", headers=headers)
        assert car_res.status_code == 200
        recs = car_res.json()
        assert len(recs) >= 8, f"Expected at least 8 career roles, found {len(recs)}"
        
        expected_roles = [
            "Python Developer", "Data Analyst", "Data Scientist", "Web Developer",
            "Backend Developer", "Database Developer", "Machine Learning Engineer", "Cybersecurity Analyst"
        ]
        found_roles = [r["career_role"]["title"] for r in recs]
        for role_name in expected_roles:
            assert role_name in found_roles, f"Missing required career role: {role_name}"
            
        print(" [PASS] Feature 6: All 8 required career roles evaluated with match scores and rationales.")
        results["Feature 6 (Career Intelligence & Recommendations)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 8: Skill Gap Identification
        # ---------------------------------------------------------
        print("\n--- Testing Feature 8: Skill Gap Identification ---")
        db_dev_role = next(r["career_role"] for r in recs if r["career_role"]["title"] == "Database Developer")
        gaps_res = await client.get(f"/api/skills/gaps/{db_dev_role['id']}", headers=headers)
        assert gaps_res.status_code == 200
        gaps_data = gaps_res.json()
        assert len(gaps_data["gaps"]) > 0
        
        # Verify demonstrated vs missing distinction
        demonstrated_items = [g for g in gaps_data["gaps"] if g["evidence_source"] == "demonstrated"]
        missing_items = [g for g in gaps_data["gaps"] if g["status"] == "missing"]
        assert len(demonstrated_items) > 0, "Demonstrated skill from quiz was not recognized!"
        assert len(missing_items) > 0, "Missing required skill was not identified!"
        print(f" [PASS] Feature 8: Identified {len(demonstrated_items)} demonstrated skills and {len(missing_items)} missing skill gaps for {db_dev_role['title']}.")
        results["Feature 8 (Skill Gap Identification)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 9: Personalized Career Roadmap
        # ---------------------------------------------------------
        print("\n--- Testing Feature 9: Personalized Career Roadmap ---")
        rm_res = await client.post(
            "/api/roadmaps/generate",
            json={"career_role_id": db_dev_role["id"], "target_timeline_months": 6},
            headers=headers
        )
        assert rm_res.status_code == 200
        rm_data = rm_res.json()
        assert len(rm_data["milestones"]) >= 4
        m1 = rm_data["milestones"][0]
        assert len(m1["suggested_projects"]) > 0
        assert len(m1["practice_activities"]) > 0
        
        # Toggle milestone
        tog_res = await client.post(f"/api/roadmaps/milestones/{m1['id']}/toggle", headers=headers)
        assert tog_res.status_code == 200
        assert tog_res.json()["is_completed"] is True
        assert tog_res.json()["roadmap_progress"] > 0
        print(f" [PASS] Feature 9: Roadmap generated with 4 milestones; milestone toggle updated progress to {tog_res.json()['roadmap_progress']}%.")
        results["Feature 9 (Personalized Career Roadmap)"] = "PASSED"

        # ---------------------------------------------------------
        # Feature 10: AI Adaptive Study Planner
        # ---------------------------------------------------------
        print("\n--- Testing Feature 10: AI Adaptive Study Planner ---")
        plan_res = await client.get("/api/study-planner/active", headers=headers)
        assert plan_res.status_code == 200
        plan = plan_res.json()
        assert len(plan["tasks"]) > 0
        t1 = plan["tasks"][0]
        
        # Toggle task
        initial_state = t1["is_completed"]
        t_tog = await client.post(f"/api/study-planner/tasks/{t1['id']}/toggle", headers=headers)
        assert t_tog.status_code == 200
        assert t_tog.json()["is_completed"] == (not initial_state)
        
        # Reschedule task
        resched = await client.post(f"/api/study-planner/tasks/{t1['id']}/reschedule?new_date=2026-12-01", headers=headers)
        assert resched.status_code == 200
        assert resched.json()["new_date"] == "2026-12-01"
        print(f" [PASS] Feature 10: Study Planner active ({len(plan['tasks'])} tasks). Task toggled & rescheduled to 2026-12-01.")
        results["Feature 10 (AI Adaptive Study Planner)"] = "PASSED"

    # Cleanup temporary pdf
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    print("\n" + "=" * 70)
    print("BACKTESTING AUDIT SUMMARY - ALL 12 FEATURES:")
    print("=" * 70)
    for feat, status in results.items():
        print(f" -> {feat.ljust(50)}: [{status}]")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(deep_audit())
