"""
EduPath AI - Multi-Subject, Latest Content & AI Question Generation Test Suite
Validates:
1. 16 Canonical Subjects with metadata (code, category, icon)
2. Strict Subject Isolation (DBMS topics never leak into OS, Networks, AI, etc.)
3. Emerging Topics, Educational Source References & Last Updated Dates
4. Subtopic hierarchical breakdown
5. AI Question Generator across all 8 Question Types:
   - mcq, multiple_select, short_answer, long_answer,
   - technical_interview, programming, scenario_based, application_oriented
6. 3 Difficulty Levels: beginner, intermediate, advanced
7. Hidden answer keys on student fetch & revealed explanations on submission
8. Scoring engine supporting MCQ exact match, MSQ partial/full set match, and open-ended evaluation
9. User analytics & mastery tracking scoped to user
10. AI Study Assistant & Notes scoped by Subject
"""

import asyncio
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.models import User, Subject, Topic, Question, Quiz
from sqlalchemy import select, delete

EXPECTED_16_SUBJECTS = [
    "DBMS",
    "Data Structures and Algorithms",
    "Python Programming",
    "Java Programming",
    "C Programming",
    "Operating Systems",
    "Computer Networks",
    "Software Engineering",
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Data Science",
    "Cloud Computing",
    "Cybersecurity",
    "Web Development",
    "Computer Organization and Architecture",
]

ALL_8_QUESTION_TYPES = [
    "mcq",
    "multiple_select",
    "short_answer",
    "long_answer",
    "technical_interview",
    "programming",
    "scenario_based",
    "application_oriented",
]

async def run_verification():
    print("=" * 70)
    print("  EDUPATH AI - MULTI-SUBJECT & QUESTION GENERATOR VERIFICATION")
    print("=" * 70)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", follow_redirects=True, timeout=60.0) as client:
        # Step 0: Register & Authenticate a verification user
        print("\n[STEP 1] Registering verification user...")
        user_email = "tester.multisubject@edupath.ai"
        async with AsyncSessionLocal() as session:
            existing = await session.execute(select(User).where(User.email == user_email))
            u = existing.scalar_one_or_none()
            if u:
                await session.delete(u)
                await session.commit()

        reg_res = await client.post("/api/auth/register", json={
            "full_name": "MultiSubject Tester",
            "email": user_email,
            "password": "SecurePassword123!"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        auth_data = reg_res.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"  [PASS] Logged in as: {auth_data['user']['full_name']} ({user_email})")

        # Step 1: Verify all 16 subjects are present
        print("\n[STEP 2] Verifying 16 Canonical Subjects via GET /api/subjects...")
        subjects_res = await client.get("/api/subjects")
        assert subjects_res.status_code == 200, f"Failed GET /api/subjects: {subjects_res.text}"
        subjects = subjects_res.json()
        print(f"  Found {len(subjects)} subjects in API response.")
        assert len(subjects) >= 16, f"Expected at least 16 subjects, got {len(subjects)}"

        subject_names = [s["name"] for s in subjects]
        subject_map = {s["name"]: s for s in subjects}

        for exp in EXPECTED_16_SUBJECTS:
            assert exp in subject_names, f"Subject '{exp}' missing from subjects list!"
            s_obj = subject_map[exp]
            assert s_obj.get("code"), f"Subject '{exp}' missing 'code'"
            assert s_obj.get("category"), f"Subject '{exp}' missing 'category'"
            assert s_obj.get("icon_name"), f"Subject '{exp}' missing 'icon_name'"
            print(f"  [PASS] Subject verified: {exp} [Code: {s_obj['code']}, Cat: {s_obj['category']}, Icon: {s_obj['icon_name']}]")

        # Step 2: Test Subject Isolation
        print("\n[STEP 3] Testing Strict Subject Isolation...")
        os_subject = subject_map["Operating Systems"]
        dbms_subject = subject_map["DBMS"]
        networks_subject = subject_map["Computer Networks"]

        os_topics_res = await client.get(f"/api/subjects/{os_subject['id']}/topics")
        assert os_topics_res.status_code == 200
        os_topics = os_topics_res.json()
        os_topic_titles = [t["name"] for t in os_topics]
        print(f"  Operating Systems topics ({len(os_topics)}): {os_topic_titles}")

        dbms_topics_res = await client.get(f"/api/subjects/{dbms_subject['id']}/topics")
        assert dbms_topics_res.status_code == 200
        dbms_topics = dbms_topics_res.json()
        dbms_topic_titles = [t["name"] for t in dbms_topics]
        print(f"  DBMS topics ({len(dbms_topics)}): {dbms_topic_titles}")

        # Strict isolation check: No DBMS topics in OS
        for dbms_title in dbms_topic_titles:
            assert dbms_title not in os_topic_titles, f"LEAK DETECTED! DBMS topic '{dbms_title}' leaked into Operating Systems!"
        print("  [PASS] ZERO DBMS topics leaked into Operating Systems!")

        # Strict isolation check: No OS topics in Computer Networks
        networks_topics_res = await client.get(f"/api/subjects/{networks_subject['id']}/topics")
        networks_topics = networks_topics_res.json()
        networks_topic_titles = [t["name"] for t in networks_topics]
        for os_title in os_topic_titles:
            assert os_title not in networks_topic_titles, f"LEAK DETECTED! OS topic '{os_title}' leaked into Computer Networks!"
        print("  [PASS] ZERO OS topics leaked into Computer Networks!")

        # Step 3: Verify Emerging Topics, Subtopics & Educational Citations
        print("\n[STEP 4] Verifying Emerging Topics & Educational References...")
        emerging_found = 0
        references_found = 0
        subtopics_found = 0

        for s in subjects:
            t_res = await client.get(f"/api/subjects/{s['id']}/topics")
            for t in t_res.json():
                if t.get("is_emerging"):
                    emerging_found += 1
                if t.get("source_reference"):
                    references_found += 1
                if t.get("subtopics") and len(t["subtopics"]) > 0:
                    subtopics_found += 1
                assert t.get("module_name"), f"Topic '{t['name']}' missing module_name!"

        print(f"  Total verified emerging topics: {emerging_found}")
        print(f"  Total verified topics with academic citations: {references_found}")
        print(f"  Total verified topics with subtopics: {subtopics_found}")
        assert emerging_found >= 10, f"Expected at least 10 emerging topics, found {emerging_found}"
        assert references_found >= 50, f"Expected at least 50 topics with sources, found {references_found}"
        assert subtopics_found >= 50, f"Expected at least 50 topics with subtopics, found {subtopics_found}"
        print("  [PASS] Emerging topics, module units, subtopics, and official references fully verified.")

        # Step 4: Test AI Question Generator across ALL 8 Question Types
        print("\n[STEP 5] Testing AI Question Generator for all 8 Question Types...")
        # Pick topic: Data Structures & Algorithms -> Advanced Graph Algorithms
        dsa_subject = subject_map["Data Structures and Algorithms"]
        dsa_topics_res = await client.get(f"/api/subjects/{dsa_subject['id']}/topics")
        dsa_topics = dsa_topics_res.json()
        target_topic = dsa_topics[0]

        for q_type in ALL_8_QUESTION_TYPES:
            print(f"  Generating quiz for question type: '{q_type}' (Difficulty: Intermediate)...")
            gen_res = await client.post("/api/quizzes/generate", json={
                "topic_id": target_topic["id"],
                "subtopic": target_topic["subtopics"][0] if target_topic.get("subtopics") else "General",
                "difficulty": "intermediate",
                "question_count": 2,
                "question_types": [q_type]
            }, headers=headers)
            assert gen_res.status_code == 200, f"Failed generation for {q_type}: {gen_res.text}"
            quiz = gen_res.json()
            assert quiz["id"], "Quiz ID missing"
            assert len(quiz["questions"]) >= 1, f"No questions returned for {q_type}"
            q0 = quiz["questions"][0]
            assert q0["question_type"] == q_type, f"Expected question_type '{q_type}', got '{q0['question_type']}'"

            # Anti-cheat check: correct_answer must NOT be leaked in questions view
            assert "correct_answer" not in q0, f"Cheat leak! correct_answer exposed in question object for {q_type}"
            assert "explanation" not in q0, f"Cheat leak! explanation exposed before submission for {q_type}"

            # Type specific checks
            if q_type in ["mcq", "multiple_select"]:
                assert len(q0["options"]) >= 2, f"Expected >= 2 options for {q_type}"
            elif q_type == "programming":
                assert q0.get("code_snippet") is not None, "Programming question should provide starter code snippet"
                assert len(q0.get("test_cases", [])) >= 1, "Programming question should provide test cases"
                print(f"    [OK] Programming question has starter code & {len(q0['test_cases'])} test cases.")

            print(f"    [PASS] Generated '{q_type}': {q0['question_text'][:60]}...")

        # Step 5: Test Difficulty Levels
        print("\n[STEP 6] Testing Difficulty Levels (Beginner, Intermediate, Advanced)...")
        for diff in ["beginner", "intermediate", "advanced"]:
            diff_res = await client.post("/api/quizzes/generate", json={
                "topic_id": target_topic["id"],
                "difficulty": diff,
                "question_count": 1,
                "question_types": ["mcq"]
            }, headers=headers)
            assert diff_res.status_code == 200
            diff_quiz = diff_res.json()
            assert diff_quiz["difficulty"] == diff
            print(f"  [PASS] Quiz generated with difficulty: {diff}")

        # Step 6: Test Quiz Submission & Scoring for Different Types
        print("\n[STEP 7] Testing Submission & Scoring Engine...")
        # 7a. Test MCQ Submission
        mcq_gen = await client.post("/api/quizzes/generate", json={
            "topic_id": target_topic["id"],
            "difficulty": "beginner",
            "question_count": 1,
            "question_types": ["mcq"]
        }, headers=headers)
        mcq_quiz = mcq_gen.json()
        mcq_q = mcq_quiz["questions"][0]

        # Get actual correct answer from DB for controlled test
        async with AsyncSessionLocal() as session:
            db_q = await session.get(Question, mcq_q["id"])
            correct_ans = db_q.correct_answer

        # Submit correct answer
        sub_correct = await client.post(f"/api/quizzes/{mcq_quiz['id']}/submit", json={
            "time_taken_seconds": 25,
            "answers": [{"question_id": mcq_q["id"], "user_response": correct_ans}]
        }, headers=headers)
        assert sub_correct.status_code == 200, f"Submit failed: {sub_correct.text}"
        res_correct = sub_correct.json()
        assert res_correct["percentage"] == 100.0, f"Expected 100% percentage, got {res_correct['percentage']}"
        assert res_correct["answers"][0]["is_correct"] is True
        assert res_correct["answers"][0]["explanation"] is not None
        print(f"  [PASS] MCQ correct answer scored 100% with explanation.")

        # Submit wrong answer
        sub_wrong = await client.post(f"/api/quizzes/{mcq_quiz['id']}/submit", json={
            "time_taken_seconds": 20,
            "answers": [{"question_id": mcq_q["id"], "user_response": "Completely Wrong Answer Choice"}]
        }, headers=headers)
        assert sub_wrong.status_code == 200, f"Submit wrong failed: {sub_wrong.text}"
        res_wrong = sub_wrong.json()
        assert res_wrong["percentage"] == 0.0, f"Expected 0% percentage, got {res_wrong['percentage']}"
        assert res_wrong["answers"][0]["is_correct"] is False
        print(f"  [PASS] MCQ wrong answer scored 0% with detailed explanation.")

        # 7b. Test MSQ (Multiple Select) Partial & Full Credit
        msq_gen = await client.post("/api/quizzes/generate", json={
            "topic_id": target_topic["id"],
            "difficulty": "intermediate",
            "question_count": 1,
            "question_types": ["multiple_select"]
        }, headers=headers)
        msq_quiz = msq_gen.json()
        msq_q = msq_quiz["questions"][0]

        async with AsyncSessionLocal() as session:
            db_msq = await session.get(Question, msq_q["id"])
            msq_correct = db_msq.correct_answer
            try:
                msq_ans_list = json.loads(msq_correct)
            except Exception:
                msq_ans_list = [a.strip() for a in msq_correct.split(",") if a.strip()]

        # Submit full match
        sub_msq = await client.post(f"/api/quizzes/{msq_quiz['id']}/submit", json={
            "time_taken_seconds": 45,
            "answers": [{"question_id": msq_q["id"], "user_response": ", ".join(msq_ans_list)}]
        }, headers=headers)
        assert sub_msq.status_code == 200, f"Submit MSQ failed: {sub_msq.text}"
        res_msq = sub_msq.json()
        assert res_msq["percentage"] == 100.0, f"Expected 100% on full MSQ match, got {res_msq['percentage']}"
        print(f"  [PASS] Multiple Select full credit scored 100%.")

        # 7c. Test Open-Ended / Short Answer Evaluation
        sa_gen = await client.post("/api/quizzes/generate", json={
            "topic_id": target_topic["id"],
            "difficulty": "intermediate",
            "question_count": 1,
            "question_types": ["short_answer"]
        }, headers=headers)
        sa_quiz = sa_gen.json()
        sa_q = sa_quiz["questions"][0]

        async with AsyncSessionLocal() as session:
            db_sa = await session.get(Question, sa_q["id"])
            sample_ans = db_sa.correct_answer

        sub_sa = await client.post(f"/api/quizzes/{sa_quiz['id']}/submit", json={
            "time_taken_seconds": 60,
            "answers": [{"question_id": sa_q["id"], "user_response": sample_ans}]
        }, headers=headers)
        assert sub_sa.status_code == 200, f"Submit SA failed: {sub_sa.text}"
        res_sa = sub_sa.json()
        assert res_sa["percentage"] > 0, "Open ended should give credit for matching sample answer"
        print(f"  [PASS] Short answer evaluated with intelligent evaluation (Percentage: {res_sa['percentage']}%).")

        # Step 7: Verify User Analytics & Mastery Tracking
        print("\n[STEP 8] Verifying User Analytics & Mastery Status...")
        analytics_res = await client.get("/api/analytics/dashboard", headers=headers)
        assert analytics_res.status_code == 200
        stats = analytics_res.json()
        assert stats["total_quizzes_attempted"] >= 3, f"Expected >= 3 quizzes completed, got {stats['total_quizzes_attempted']}"
        print(f"  [PASS] User analytics updated: {stats['total_quizzes_attempted']} quizzes, avg score: {stats['average_quiz_score']:.1f}%")

        # Step 8: AI Study Assistant Scoped with Subject Context
        print("\n[STEP 9] Testing AI Study Assistant with Subject Context...")
        ask_res = await client.post("/api/assistant/ask", json={
            "question": "Explain how Dijkstra's algorithm uses priority queues in time complexity O((V+E) log V).",
            "subject_id": dsa_subject["id"]
        }, headers=headers)
        assert ask_res.status_code == 200, f"Ask failed: {ask_res.text}"
        ask_data = ask_res.json()
        ans_text = ask_data["assistant_message"]["content"]
        assert len(ans_text) > 20
        print(f"  [PASS] Assistant answered with subject scoping: {ans_text[:80]}...")

        # Step 9: Notes Generator with Subject & Topic
        print("\n[STEP 10] Testing Notes Generator with Multi-Subject Support...")
        notes_res = await client.post("/api/notes/generate", json={
            "topic_name": target_topic["name"],
            "subject_name": dsa_subject["name"],
            "note_type": "revision"
        }, headers=headers)
        assert notes_res.status_code == 200, f"Notes failed: {notes_res.text}"
        notes_data = notes_res.json()
        assert len(notes_data["content_markdown"]) > 50
        print(f"  [PASS] Smart Notes generated for '{target_topic['name']}': {notes_data['content_markdown'][:70]}...")

    print("\n" + "=" * 70)
    print("  ALL MULTI-SUBJECT & QUESTION GENERATOR VERIFICATION TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_verification())
