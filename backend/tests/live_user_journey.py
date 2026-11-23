"""
EduPath AI - Live Real User Journey Execution Test
Simulates an end-to-end user workflow across the complete platform lifecycle.
"""

import asyncio
import os
import sys
import time
import fitz  # PyMuPDF
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

async def run_live_user_journey():
    print("=" * 80)
    print("EDUPATH AI - LIVE REAL END-TO-END USER JOURNEY EXECUTION")
    print("=" * 80)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=45.0) as client:
        ts = int(time.time() * 1000)
        user_email = f"learner_{ts}@example.com"
        password = "SecurePassword123!"

        # Step 1: User Registration
        print("\n[Step 1/11] Registering fresh student user...")
        reg_res = await client.post("/api/auth/register", json={
            "email": user_email,
            "password": password,
            "full_name": "Maya Lin"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        auth_data = reg_res.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f" -> Successfully registered: {user_email} (User ID: {auth_data['user']['id']})")

        # Step 2: Fetch and Update Profile
        print("\n[Step 2/11] Checking profile & onboarding settings...")
        me_res = await client.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        print(f" -> Verified user identity: {me_res.json()['full_name']}")

        # Step 3: Document Upload & Hybrid RAG Chunking
        print("\n[Step 3/11] Generating & uploading academic study document (PDF)...")
        pdf_path = f"study_doc_{ts}.pdf"
        doc = fitz.open()
        p1 = doc.new_page()
        p1.insert_text((50, 72), "DISTRIBUTED DATABASE CONCURRENCY & REPLICATION\n\nACID properties provide transaction safety. Two-Phase Commit (2PC) guarantees distributed atomicity across replicas.")
        p2 = doc.new_page()
        p2.insert_text((50, 72), "RAFT CONSENSUS AND LEADER ELECTION\n\nRaft divides time into terms. Leaders manage log replication and heartbeat pings to avoid election timeouts.")
        doc.save(pdf_path)
        doc.close()

        with open(pdf_path, "rb") as f:
            up_res = await client.post(
                "/api/documents/upload",
                files={"file": (pdf_path, f, "application/pdf")},
                data={"title": "Distributed Systems & Raft Consensus"},
                headers=headers
            )
        assert up_res.status_code == 200, f"Upload failed: {up_res.text}"
        doc_data = up_res.json()
        doc_id = doc_data["id"]
        print(f" -> Uploaded document ID: {doc_id} (Status: {doc_data['status']}, Chunks: {doc_data['chunk_count']})")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # Step 4: AI Study Assistant Grounded Q&A with Citations
        print("\n[Step 4/11] Querying AI Study Assistant with document groundings...")
        ask_res = await client.post("/api/assistant/ask", json={
            "question": "What is the role of Two-Phase Commit according to my document?",
            "document_id": doc_id,
            "explanation_level": "intermediate"
        }, headers=headers)
        assert ask_res.status_code == 200, f"Ask failed: {ask_res.text}"
        ask_data = ask_res.json()
        conv_id = ask_data["conversation_id"]
        answer = ask_data["assistant_message"]["content"]
        citations = ask_data["assistant_message"].get("citations", [])
        print(f" -> Assistant answered (Conv ID: {conv_id})")
        print(f" -> Citations returned: {len(citations)} source citations grounded.")
        assert len(citations) > 0, "Expected grounded citations!"

        # Step 5: Answer Quality Evaluator
        print("\n[Step 5/11] Evaluating student answer quality with pedagogical rubric...")
        eval_res = await client.post("/api/assistant/evaluate-answer", json={
            "question": "Explain 2PC in distributed transactions.",
            "answer": "Two-Phase Commit coordinates prepare and commit phases across distributed participants to guarantee atomicity."
        }, headers=headers)
        assert eval_res.status_code == 200
        eval_score = eval_res.json()
        print(f" -> Answer score: {eval_score['overall_score']}/100 (Relevance: {eval_score['relevance_score']}/10)")

        # Step 6: Smart Notes Generation
        print("\n[Step 6/11] Generating revision study notes...")
        note_res = await client.post("/api/notes/generate", json={
            "topic_name": "Distributed Transactions",
            "note_type": "revision"
        }, headers=headers)
        assert note_res.status_code == 200
        note = note_res.json()
        print(f" -> Note generated: '{note['title']}' ({len(note['content_markdown'])} chars)")

        # Step 7: AI Quiz Generation, Masked Key Verification & Submission
        print("\n[Step 7/11] Generating adaptive quiz from catalog topic...")
        subj_res = await client.get("/api/skills/subjects")
        subjects = subj_res.json()
        topic_id = subjects[0]["topics"][0]["id"]
        topic_name = subjects[0]["topics"][0]["name"]

        quiz_res = await client.post("/api/quizzes/generate", json={
            "topic_id": topic_id,
            "difficulty": "medium",
            "question_count": 3
        }, headers=headers)
        assert quiz_res.status_code == 200
        quiz = quiz_res.json()
        quiz_id = quiz["id"]
        assert "correct_answer" not in quiz["questions"][0], "SECURITY VIOLATION: Answer key was leaked!"
        print(f" -> Quiz generated: '{quiz['title']}' (Answer keys securely masked)")

        # Submit quiz
        answers = [
            {"question_id": q["id"], "user_response": q["options"][0] if q.get("options") else "Option A"}
            for q in quiz["questions"]
        ]
        submit_res = await client.post(f"/api/quizzes/{quiz_id}/submit", json={
            "time_taken_seconds": 50,
            "answers": answers
        }, headers=headers)
        assert submit_res.status_code == 200
        sub_eval = submit_res.json()
        print(f" -> Submitted quiz. Evaluated score: {sub_eval['score']}/{sub_eval['max_score']} ({sub_eval['percentage']}%)")

        # Step 8: Topic Performance & Central Engine Propagation
        print("\n[Step 8/11] Verifying topic performance mastery tracking...")
        tp_res = await client.get("/api/topics/performance", headers=headers)
        assert tp_res.status_code == 200
        tp_items = tp_res.json()
        assert len(tp_items) > 0
        print(f" -> Topic Performance logged for '{tp_items[0]['topic_name']}': Mastery='{tp_items[0]['mastery_status']}'")

        # Step 9: Live Job Description Skill Analysis
        print("\n[Step 9/11] Running Live Job Description Skill Extraction...")
        jd_text = """
        Cloud Infrastructure Engineer wanted. Requirements: Python, Docker, Kubernetes,
        PostgreSQL, CI/CD pipelines, AWS or GCP, Microservices, and Linux fundamentals.
        """
        jd_res = await client.post("/api/careers/analyze-jd", json={
            "job_title": "Cloud Infrastructure Engineer",
            "company_name": "NextGen Scale Inc.",
            "job_description_text": jd_text
        }, headers=headers)
        assert jd_res.status_code == 200
        jd_data = jd_res.json()
        print(f" -> Extracted {len(jd_data['extracted_required_skills'])} skills: {', '.join(jd_data['extracted_required_skills'][:5])}...")
        print(f" -> Readiness: {jd_data['readiness_status']} (Overall Match: {jd_data['overall_match_percentage']}%)")

        # Step 10: Personalized Career Roadmaps
        print("\n[Step 10/11] Generating personalized career pathway roadmap...")
        roles_res = await client.get("/api/careers/roles", headers=headers)
        assert roles_res.status_code == 200
        roles = roles_res.json()
        assert len(roles) > 0
        role_id = roles[0]["id"]
        role_title = roles[0]["title"]

        rm_res = await client.post("/api/roadmaps/generate", json={"career_role_id": role_id}, headers=headers)
        assert rm_res.status_code == 200, f"Roadmap failed: {rm_res.text}"
        roadmap = rm_res.json()
        print(f" -> Generated roadmap: '{roadmap['title']}' with {len(roadmap['milestones'])} milestone phases")

        # Step 11: Adaptive Study Planner
        print("\n[Step 11/11] Generating adaptive study schedule...")
        plan_res = await client.post("/api/study-planner/generate", json={
            "title": "Sprint Preparation",
            "daily_hours_target": 2.0,
            "days_duration": 7
        }, headers=headers)
        assert plan_res.status_code == 200, f"Planner failed: {plan_res.text}"
        plan = plan_res.json()
        print(f" -> Study Plan active: '{plan['title']}' with {len(plan['tasks'])} scheduled tasks")

        print("\n" + "=" * 80)
        print("[SUCCESS] ALL 11 REAL USER WORKFLOW STEPS EXECUTED & PASSED PERFECTLY!")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_live_user_journey())
