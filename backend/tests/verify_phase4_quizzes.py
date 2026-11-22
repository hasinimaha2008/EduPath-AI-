import asyncio
import os
import sys
import tempfile
import httpx
import docx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

def create_sample_docx(file_path: str):
    doc = docx.Document()
    doc.add_heading("Operating Systems: Virtual Memory & Page Replacement", level=1)
    doc.add_paragraph(
        "Virtual memory is a memory management technique that provides an idealized abstraction of storage resources. "
        "The Memory Management Unit (MMU) translates virtual addresses into physical addresses using page tables. "
        "When a requested page is not resident in physical RAM, a page fault exception is raised."
    )
    doc.add_heading("Page Replacement Algorithms", level=2)
    doc.add_paragraph(
        "Common page replacement algorithms include FIFO (First-In, First-Out), LRU (Least Recently Used), and OPT (Optimal). "
        "Belady's Anomaly occurs in FIFO where increasing page frames can paradoxically increase the number of page faults."
    )
    doc.save(file_path)

async def test_phase4_quizzes():
    print("=" * 70)
    print("Starting Comprehensive Phase 4: AI Quiz Generator Verification")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=90.0) as client:
        # Step 0: Authentication
        print("\n[Step 0] Authenticating demo user...")
        login_res = await client.post(f"{BASE_URL}/auth/demo-login")
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  ✓ Authenticated as demo@edupath.ai")

        # Fetch subjects and topics
        subj_res = await client.get(f"{BASE_URL}/subjects", headers=headers)
        subjects = subj_res.json()
        assert len(subjects) > 0, "No subjects found."
        first_subj = subjects[0]
        first_topic = first_subj["topics"][0]
        print(f"  ✓ Context: Subject '{first_subj['name']}', Topic '{first_topic['name']}'")

        # Test 1: Generate Quiz from Curriculum Topic
        print("\n[Test 1] Generating Quiz from Curriculum Topic...")
        q1_res = await client.post(
            f"{BASE_URL}/quizzes/generate",
            headers=headers,
            json={
                "subject_id": first_subj["id"],
                "topic_id": first_topic["id"],
                "difficulty": "medium",
                "question_count": 5,
                "question_types": ["mcq"]
            }
        )
        assert q1_res.status_code == 200, f"Topic quiz generation failed: {q1_res.text}"
        quiz1 = q1_res.json()
        assert quiz1["total_questions"] == 5
        assert len(quiz1["questions"]) == 5
        # Verify correct answers are strictly hidden from student during quiz taking!
        assert "correct_answer" not in quiz1["questions"][0]
        print(f"  ✓ Generated 5-question MCQ quiz: '{quiz1['title']}' (Answers hidden)")

        # Test 2: Generate Quiz from Uploaded Document
        print("\n[Test 2] Generating Quiz from Uploaded Document...")
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tf:
            temp_path = tf.name
        try:
            create_sample_docx(temp_path)
            with open(temp_path, "rb") as f:
                up_res = await client.post(
                    f"{BASE_URL}/documents/upload",
                    headers=headers,
                    files={"file": ("VirtualMemory.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                )
            assert up_res.status_code == 200
            doc_data = up_res.json()
            doc_id = doc_data["id"]

            doc_quiz_res = await client.post(
                f"{BASE_URL}/quizzes/generate",
                headers=headers,
                json={
                    "document_id": doc_id,
                    "difficulty": "hard",
                    "question_count": 3,
                    "question_types": ["mcq"]
                }
            )
            assert doc_quiz_res.status_code == 200
            doc_quiz = doc_quiz_res.json()
            assert doc_quiz["document_id"] == doc_id
            assert len(doc_quiz["questions"]) == 3
            print(f"  ✓ Generated document-grounded quiz for '{doc_data['title']}'")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Test 3: Generate Quiz from Previously Generated Study Note
        print("\n[Test 3] Generating Quiz from Study Note...")
        note_res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "topic_name": "Cache Coherence and MESI Protocol",
                "note_type": "detailed"
            }
        )
        assert note_res.status_code == 200
        note_data = note_res.json()
        note_id = note_data["id"]

        note_quiz_res = await client.post(
            f"{BASE_URL}/quizzes/generate",
            headers=headers,
            json={
                "note_id": note_id,
                "difficulty": "medium",
                "question_count": 4,
                "question_types": ["mcq"]
            }
        )
        assert note_quiz_res.status_code == 200
        note_quiz = note_quiz_res.json()
        assert note_quiz["note_id"] == note_id
        assert len(note_quiz["questions"]) == 4
        print(f"  ✓ Generated note-grounded quiz for note: '{note_data['title']}'")

        # Test 4: Mixed Difficulty Level & Deduplication
        print("\n[Test 4] Generating Mixed Difficulty Quiz & Verifying Deduplication...")
        mixed_res = await client.post(
            f"{BASE_URL}/quizzes/generate",
            headers=headers,
            json={
                "topic_id": first_topic["id"],
                "difficulty": "mixed",
                "question_count": 5,
                "question_types": ["mcq"]
            }
        )
        assert mixed_res.status_code == 200
        mixed_quiz = mixed_res.json()
        assert mixed_quiz["difficulty"] == "mixed"
        # Deduplication check: all question texts must be unique
        q_texts = [q["question_text"].strip() for q in mixed_quiz["questions"]]
        assert len(q_texts) == len(set(q_texts)), "Duplicate questions found in generated quiz!"
        print(f"  ✓ Mixed difficulty quiz verified with {len(q_texts)} strictly unique questions (No duplicates)")

        # Test 5: True/False Question Type
        print("\n[Test 5] Testing True/False Question Generation...")
        tf_res = await client.post(
            f"{BASE_URL}/quizzes/generate",
            headers=headers,
            json={
                "topic_id": first_topic["id"],
                "difficulty": "easy",
                "question_count": 3,
                "question_types": ["true_false"]
            }
        )
        assert tf_res.status_code == 200
        tf_quiz = tf_res.json()
        assert len(tf_quiz["questions"]) == 3
        for q in tf_quiz["questions"]:
            assert q["question_type"] == "true_false"
            assert q["options"] == ["True", "False"]
        print("  ✓ True/False questions verified with binary options ['True', 'False']")

        # Test 6: Fill-in-the-Blank Question Type
        print("\n[Test 6] Testing Fill-in-the-Blank Question Generation...")
        fib_res = await client.post(
            f"{BASE_URL}/quizzes/generate",
            headers=headers,
            json={
                "topic_id": first_topic["id"],
                "difficulty": "medium",
                "question_count": 3,
                "question_types": ["fill_in_the_blank"]
            }
        )
        assert fib_res.status_code == 200
        fib_quiz = fib_res.json()
        assert len(fib_quiz["questions"]) == 3
        for q in fib_quiz["questions"]:
            assert q["question_type"] == "fill_in_the_blank"
            assert "________" in q["question_text"]
        print("  ✓ Fill-in-the-blank questions verified with blank prompt slots")

        # Test 7: Quiz Submission, Scoring & Explanations
        print("\n[Test 7] Submitting Quiz & Evaluating Scoring & Explanations...")
        submission_answers = [
            {"question_id": tf_quiz["questions"][0]["id"], "user_response": "True"},
            {"question_id": tf_quiz["questions"][1]["id"], "user_response": "False"},
            {"question_id": tf_quiz["questions"][2]["id"], "user_response": "True"},
        ]
        sub_res = await client.post(
            f"{BASE_URL}/quizzes/{tf_quiz['id']}/submit",
            headers=headers,
            json={
                "time_taken_seconds": 45,
                "answers": submission_answers
            }
        )
        assert sub_res.status_code == 200, f"Submission failed: {sub_res.text}"
        eval_result = sub_res.json()
        assert "score" in eval_result
        assert "percentage" in eval_result
        assert "answers" in eval_result
        assert len(eval_result["answers"]) == 3
        for a in eval_result["answers"]:
            assert "correct_answer" in a
            assert "is_correct" in a
            assert "explanation" in a
        attempt_id = eval_result["attempt_id"]
        print(f"  ✓ Submission scored: {eval_result['score']}/{eval_result['max_score']} ({eval_result['percentage']}%) in {eval_result['time_taken_seconds']}s")

        # Test 8: Topic-Wise Performance & Recommended Revision Topics
        print("\n[Test 8] Verifying Topic Breakdown & Revision Recommendations...")
        assert "topic_breakdown" in eval_result and eval_result["topic_breakdown"] is not None
        assert "recommended_revision_topics" in eval_result and eval_result["recommended_revision_topics"] is not None
        print(f"  ✓ Topic Breakdown: {eval_result['topic_breakdown']['topic_name']} (Accuracy: {eval_result['topic_breakdown']['accuracy']}%)")
        print(f"  ✓ Recommended Revision Topics: {eval_result['recommended_revision_topics']}")

        # Test 9: Saved Quiz History & Attempt Retrieval
        print("\n[Test 9] Testing History & Attempt Inspection (GET /attempts/{id})...")
        hist_res = await client.get(f"{BASE_URL}/quizzes/history/attempts", headers=headers)
        assert hist_res.status_code == 200
        history = hist_res.json()
        assert len(history) >= 1
        assert any(h["id"] == attempt_id for h in history)
        print(f"  ✓ Attempt saved in persistent history ({len(history)} total attempts)")

        att_res = await client.get(f"{BASE_URL}/quizzes/attempts/{attempt_id}", headers=headers)
        assert att_res.status_code == 200
        saved_att = att_res.json()
        assert saved_att["attempt_id"] == attempt_id
        assert len(saved_att["answers"]) == 3
        print(f"  ✓ Retrieved full attempt detail with answers and rubric")

        # Test 10: Quiz Retake - Reset answers & verify active quiz
        print("\n[Test 10] Testing Quiz Retrieval for Retake (GET /quizzes/{id})...")
        retake_get = await client.get(f"{BASE_URL}/quizzes/{tf_quiz['id']}", headers=headers)
        assert retake_get.status_code == 200
        retake_quiz = retake_get.json()
        assert retake_quiz["id"] == tf_quiz["id"]
        assert len(retake_quiz["questions"]) == 3
        # Answers must remain hidden during retake!
        assert "correct_answer" not in retake_quiz["questions"][0]
        print("  ✓ Quiz successfully retrieved for retake with answers protected")

    print("\n" + "=" * 70)
    print("ALL 10 PHASE 4 AI QUIZ GENERATOR TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_phase4_quizzes())
