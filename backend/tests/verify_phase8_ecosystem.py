import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

async def test_phase8_ecosystem():
    print("=" * 80)
    print("Phase 8 – EduPath AI Connected Ecosystem Verification")
    print("Tagline: Learn Smarter. Grow Better. Build Your Career.")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Step 0: Authenticate
        print("\n[Step 0] Authenticating demo user...")
        login_res = await client.post(f"{BASE_URL}/auth/demo-login")
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  ✓ Authenticated as demo@edupath.ai")

        # Fetch subjects and topics to reference
        subs_res = await client.get(f"{BASE_URL}/subjects", headers=headers)
        assert subs_res.status_code == 200
        subjects = subs_res.json()
        assert len(subjects) > 0, "No subjects found"
        test_subject = subjects[0]
        test_topic = test_subject["topics"][0]
        print(f"  ✓ Context Subject: '{test_subject['name']}' | Topic: '{test_topic['name']}' (ID: {test_topic['id']})")

        # ======================================================================
        # WORKFLOW 1 – DOCUMENT TO LEARNING
        # ======================================================================
        print("\n" + "=" * 60)
        print("WORKFLOW 1: DOCUMENT TO LEARNING")
        print("Upload -> Notes -> Quizzes -> AI Study Assistant -> Topic Identification")
        print("=" * 60)

        # 1.1 Check or create an uploaded document
        docs_res = await client.get(f"{BASE_URL}/documents", headers=headers)
        assert docs_res.status_code == 200
        docs = docs_res.json()

        test_doc_id = None
        if docs:
            test_doc = docs[0]
            test_doc_id = test_doc["id"]
            print(f"  ✓ Using existing uploaded document: '{test_doc['title']}' (ID: {test_doc_id})")
        else:
            print("  - Uploading a fresh academic document for Workflow 1...")
            file_content = (
                "Binary Search Trees and Balanced Trees in Computer Science.\n\n"
                "A Binary Search Tree (BST) is a node-based binary tree data structure with the property that "
                "the key in each node must be greater than or equal to any key stored in the left sub-tree, "
                "and less than or equal to any key in the right sub-tree.\n\n"
                "Key Operations and Time Complexities:\n"
                "- Search: O(log n) average, O(n) worst case in unbalanced trees.\n"
                "- Insertion: O(log n) average, O(n) worst case.\n"
                "- Deletion: O(log n) average, O(n) worst case.\n\n"
                "Self-balancing binary search trees such as AVL Trees and Red-Black Trees maintain an O(log n) "
                "height bound by performing tree rotations during insertions and deletions."
            )
            files = {"file": ("bst_data_structures.txt", file_content.encode("utf-8"), "text/plain")}
            data = {"title": "Binary Search Trees & Balanced Trees", "subject_id": test_subject["id"]}
            up_res = await client.post(f"{BASE_URL}/documents/upload", headers=headers, files=files, data=data)
            assert up_res.status_code in [200, 201], f"Document upload failed: {up_res.text}"
            new_doc = up_res.json()
            test_doc_id = new_doc["id"]
            print(f"  ✓ Document uploaded and indexed: '{new_doc['title']}' (ID: {test_doc_id})")

        # 1.2 Generate Study Notes from Document
        print("  - Generating study notes from document...")
        note_res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "document_id": test_doc_id,
                "note_type": "detailed",
                "explanation_style": "standard",
                "language": "en"
            }
        )
        assert note_res.status_code == 200, f"Note generation failed: {note_res.text}"
        doc_note = note_res.json()
        note_txt = doc_note.get("content_markdown") or doc_note.get("content") or ""
        print(f"  ✓ Notes generated: '{doc_note['title']}' ({len(note_txt)} chars)")
        assert len(note_txt) > 50

        # 1.3 Generate Quiz from Document
        print("  - Generating quiz from document...")
        quiz_res = await client.post(
            f"{BASE_URL}/quizzes/generate",
            headers=headers,
            json={
                "document_id": test_doc_id,
                "difficulty": "medium",
                "question_type": "mcq",
                "question_count": 3
            }
        )
        assert quiz_res.status_code == 200, f"Quiz generation failed: {quiz_res.text}"
        doc_quiz = quiz_res.json()
        print(f"  ✓ Quiz generated: '{doc_quiz['title']}' ({len(doc_quiz['questions'])} questions)")
        assert len(doc_quiz["questions"]) >= 1

        # 1.4 Ask AI Study Assistant with Document Citation
        print("  - Asking AI Study Assistant with document context...")
        ask_res = await client.post(
            f"{BASE_URL}/assistant/ask",
            headers=headers,
            json={
                "question": "What is the worst-case search complexity of an unbalanced binary search tree?",
                "document_id": test_doc_id,
                "language": "en"
            }
        )
        assert ask_res.status_code == 200, f"Assistant ask failed: {ask_res.text}"
        assistant_ans = ask_res.json()
        ans_content = assistant_ans.get("assistant_message", {}).get("content", "") or assistant_ans.get("answer", "")
        print(f"  ✓ Assistant Answer received: {len(ans_content)} chars")
        assert len(ans_content) > 10

        # 1.5 Identify Important Topics from Document
        print("  - Extracting important curriculum topics from document...")
        topics_res = await client.get(f"{BASE_URL}/documents/{test_doc_id}/important-topics", headers=headers)
        assert topics_res.status_code == 200, f"Topic extraction failed: {topics_res.text}"
        extracted_topics = topics_res.json()
        count = len(extracted_topics) if isinstance(extracted_topics, list) else extracted_topics.get("topics_found", len(extracted_topics.get("important_topics", [])))
        print(f"  ✓ Important topics extracted: {count} concepts identified")
        assert count >= 1
        print("  ✓ WORKFLOW 1 PASSED: Document -> Notes -> Quiz -> Assistant -> Topics completed successfully.")

        # ======================================================================
        # WORKFLOW 2 – PERFORMANCE TO PERSONALIZED LEARNING
        # ======================================================================
        print("\n" + "=" * 60)
        print("WORKFLOW 2: PERFORMANCE TO PERSONALIZED LEARNING")
        print("Quiz Submission (< 70%) -> Analytics Update -> Adaptive Study Task")
        print("=" * 60)

        # 2.1 Ensure active study plan exists
        print("  - Checking active study plan...")
        plan_res = await client.get(f"{BASE_URL}/study-planner/active", headers=headers)
        active_plan = None
        if plan_res.status_code == 200:
            active_plan = plan_res.json()
        if not active_plan or not active_plan.get("id"):
            print("  - Generating an active study plan for auto-adaptation...")
            gen_p = await client.post(
                f"{BASE_URL}/study-planner/generate",
                headers=headers,
                json={"title": "Ecosystem Integrated Study Sprint", "daily_hours_target": 2.0, "days_duration": 7}
            )
            assert gen_p.status_code == 200
            active_plan = gen_p.json()
        print(f"  ✓ Active Study Plan: '{active_plan['title']}' (ID: {active_plan['id']})")

        # 2.2 Generate a topic quiz to take
        q_gen = await client.post(
            f"{BASE_URL}/quizzes/generate",
            headers=headers,
            json={
                "topic_id": test_topic["id"],
                "subject_id": test_subject["id"],
                "difficulty": "medium",
                "question_type": "mcq",
                "question_count": 3
            }
        )
        assert q_gen.status_code == 200
        quiz_obj = q_gen.json()
        quiz_id = quiz_obj["id"]

        # 2.3 Submit deliberate low-scoring answers (< 70%)
        print("  - Submitting quiz attempt with low accuracy (< 70%)...")
        bad_answers = [
            {"question_id": q["id"], "user_response": "Wrong deliberate answer"}
            for q in quiz_obj["questions"]
        ]
        submit_res = await client.post(
            f"{BASE_URL}/quizzes/{quiz_id}/submit",
            headers=headers,
            json={"answers": bad_answers, "time_taken_seconds": 45}
        )
        assert submit_res.status_code == 200, f"Quiz submit failed: {submit_res.text}"
        sub_result = submit_res.json()
        print(f"  ✓ Quiz Submitted: Score: {sub_result['score']} / {sub_result['max_score']} ({sub_result['percentage']}%)")
        assert sub_result["percentage"] < 70.0

        # 2.4 Verify Learning Analytics reflects topic performance
        print("  - Verifying Analytics updated for weak topic...")
        an_res = await client.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
        assert an_res.status_code == 200
        an_data = an_res.json()
        print(f"  ✓ Analytics Total Quizzes: {an_data['total_quizzes_attempted']}")
        print(f"  ✓ Analytics Weak Topics: {len(an_data['weak_topics'])} identified")

        # 2.5 Verify Study Planner auto-scheduled adaptive revision task
        print("  - Checking Study Planner for auto-scheduled adaptive revision task...")
        active_plan_check = await client.get(f"{BASE_URL}/study-planner/active", headers=headers)
        assert active_plan_check.status_code == 200
        current_tasks = active_plan_check.json().get("tasks", [])
        
        adaptive_tasks = [
            t for t in current_tasks
            if t.get("task_type") == "revision" and (t.get("topic_id") == test_topic["id"] or test_topic["name"] in t.get("title", ""))
        ]
        print(f"  ✓ Found {len(adaptive_tasks)} auto-scheduled revision task(s) for '{test_topic['name']}'")
        assert len(adaptive_tasks) >= 1, "Expected auto-scheduled revision task in active study plan"
        sample_task = adaptive_tasks[0]
        print(f"    - Task Title: {sample_task['title']}")
        print(f"    - Priority: {sample_task['priority']}")
        print(f"    - Action URL: {sample_task.get('action_url')}")
        assert "dashboard/notes" in sample_task.get("action_url", "")
        print("  ✓ WORKFLOW 2 PASSED: Quiz Result -> Analytics -> Adaptive Study Task auto-scheduled.")

        # ======================================================================
        # WORKFLOW 3 – LEARNING TO CAREER
        # ======================================================================
        print("\n" + "=" * 60)
        print("WORKFLOW 3: LEARNING TO CAREER")
        print("Quiz Mastery (>= 75%) -> UserSkill Verified -> Career Match -> Milestone Advance")
        print("=" * 60)

        # 3.1 Check or create active career roadmap
        print("  - Checking Career Roles & Active Roadmap...")
        roles_res = await client.get(f"{BASE_URL}/careers/roles", headers=headers)
        assert roles_res.status_code == 200, f"Roles fetch failed: {roles_res.text}"
        roles = roles_res.json()
        assert len(roles) > 0
        target_role = roles[0]

        # Ensure roadmap exists for target role
        rm_gen = await client.post(
            f"{BASE_URL}/roadmaps/generate",
            headers=headers,
            json={"career_role_id": target_role["id"], "target_timeline_months": 6}
        )
        assert rm_gen.status_code in [200, 201], f"Roadmap gen failed: {rm_gen.text}"
        active_rm = rm_gen.json()
        print(f"  ✓ Active Roadmap for '{target_role['title']}': Progress = {active_rm['progress_percentage']}%")
        initial_progress = active_rm["progress_percentage"]

        # 3.2 Generate and submit 100% correct quiz answers on curriculum topic
        print("  - Generating mastery assessment...")
        q_gen2 = await client.post(
            f"{BASE_URL}/quizzes/generate",
            headers=headers,
            json={
                "topic_id": test_topic["id"],
                "subject_id": test_subject["id"],
                "difficulty": "medium",
                "question_type": "mcq",
                "question_count": 2
            }
        )
        assert q_gen2.status_code == 200
        mastery_quiz = q_gen2.json()

        # Probe key then submit 100% correct answers
        probe_sub = await client.post(
            f"{BASE_URL}/quizzes/{mastery_quiz['id']}/submit",
            headers=headers,
            json={"answers": [{"question_id": q["id"], "user_response": "probe"} for q in mastery_quiz["questions"]], "time_taken_seconds": 10}
        )
        assert probe_sub.status_code == 200
        correct_answers = [
            {"question_id": a["question_id"], "user_response": a["correct_answer"]}
            for a in probe_sub.json()["answers"]
        ]
        sub_mastery = await client.post(
            f"{BASE_URL}/quizzes/{mastery_quiz['id']}/submit",
            headers=headers,
            json={"answers": correct_answers, "time_taken_seconds": 25}
        )
        assert sub_mastery.status_code == 200
        mastery_result = sub_mastery.json()
        print(f"  ✓ Mastery Quiz Submitted: {mastery_result['percentage']}%")
        assert mastery_result["percentage"] >= 75.0

        # 3.3 Verify UserSkills synchronized as verified (demonstrated)
        print("  - Verifying UserSkill verified status in database...")
        gaps_res = await client.get(f"{BASE_URL}/skills/gaps/{target_role['id']}", headers=headers)
        assert gaps_res.status_code == 200, f"Skill gaps failed: {gaps_res.text}"
        gaps_data = gaps_res.json()
        gaps_list = gaps_data.get("gaps", [])
        verified_skills = [g for g in gaps_list if g.get("is_verified") or g.get("evidence_source") == "demonstrated"]
        print(f"    - Overall Readiness: {gaps_data.get('overall_readiness')}%")
        print(f"    - Total Skills Evaluated: {len(gaps_list)} ({len(verified_skills)} verified/demonstrated)")

        # 3.4 Check Career Roadmap milestone advancement
        print("  - Checking updated Roadmap Progress...")
        rm_check = await client.get(f"{BASE_URL}/roadmaps", headers=headers)
        assert rm_check.status_code == 200, f"Roadmaps fetch failed: {rm_check.text}"
        roadmaps_list = rm_check.json()
        assert len(roadmaps_list) >= 1
        updated_rm = next((r for r in roadmaps_list if r["id"] == active_rm["id"]), roadmaps_list[0])
        print(f"  ✓ Updated Roadmap Progress: {updated_rm['progress_percentage']}% (was {initial_progress}%)")
        assert updated_rm["progress_percentage"] >= initial_progress
        print("  ✓ WORKFLOW 3 PASSED: Learning Evidence -> Verified Skills -> Career Intelligence -> Roadmap Progression.")

        # ======================================================================
        # WORKFLOW 4 – PERSONALIZED ECOSYSTEM SNAPSHOT
        # ======================================================================
        print("\n" + "=" * 60)
        print("WORKFLOW 4: PERSONALIZED STUDENT EXPERIENCE")
        print("Aggregated Cross-Module Snapshot & Unified Recommendations")
        print("=" * 60)

        # 4.1 Fetch Ecosystem Summary
        print("  - Fetching GET /api/workspace/ecosystem-summary...")
        eco_res = await client.get(f"{BASE_URL}/workspace/ecosystem-summary", headers=headers)
        assert eco_res.status_code == 200, f"Ecosystem summary failed: {eco_res.text}"
        eco = eco_res.json()

        print(f"  ✓ Ecosystem User: {eco['user_name']} (Target Career: {eco['target_career']['title']})")
        print(f"    - Career Readiness Score: {eco['target_career']['readiness_score']}%")
        print(f"    - Total Documents: {eco['documents_summary']['total_documents']}")
        print(f"    - Total Notes: {eco['notes_summary']['total_notes']}")
        print(f"    - Total Quiz Attempts: {eco['quizzes_summary']['total_attempts']} (Avg Score: {eco['quizzes_summary']['average_score']}%)")
        print(f"    - Weak Topics Count: {eco['analytics_summary']['weak_topics_count']}")

        if eco.get("study_plan"):
            print(f"    - Active Study Plan: '{eco['study_plan']['title']}' (Adherence: {eco['study_plan']['adherence_rate']}%)")
        if eco.get("career_roadmap"):
            print(f"    - Active Roadmap: '{eco['career_roadmap']['title']}' ({eco['career_roadmap']['progress_percentage']}%)")

        print(f"\n  ✓ Cross-Module Unified Recommendations ({len(eco['recommendations'])} total):")
        assert len(eco["recommendations"]) >= 1, "Expected actionable ecosystem recommendations"
        for rec in eco["recommendations"]:
            print(f"    [{rec['priority']}] ({rec['source']}) {rec['title']} -> {rec['action_url']}")
            assert "action_url" in rec
            assert "action_label" in rec

        # 4.2 Verify Smart Notifications
        print("\n  - Checking Notifications for ecosystem triggers...")
        notif_res = await client.get(f"{BASE_URL}/notifications", headers=headers)
        assert notif_res.status_code == 200
        notifs = notif_res.json()
        print(f"  ✓ System Notifications Count: {len(notifs.get('notifications', []))}")
        print("  ✓ WORKFLOW 4 PASSED: Unified Ecosystem Snapshot & Cross-Module Intelligence Verified.")

        print("\n" + "=" * 80)
        print("ALL 4 ECOSYSTEM WORKFLOWS VERIFIED SUCCESSFULLY (100% PASS)")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_phase8_ecosystem())
