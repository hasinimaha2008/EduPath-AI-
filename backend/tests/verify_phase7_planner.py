import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

async def test_phase7_planner():
    print("=" * 70)
    print("Starting Comprehensive Phase 7: Intelligent Adaptive Study Planner Verification")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=90.0) as client:
        # Step 0: Authentication
        print("\n[Step 0] Authenticating demo user...")
        login_res = await client.post(f"{BASE_URL}/auth/demo-login")
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  ✓ Authenticated as demo@edupath.ai")

        # Step 1: Initial Planner Progress Check
        print("\n[Step 1] Fetching Baseline Planner Progress...")
        prog_res = await client.get(f"{BASE_URL}/study-planner/progress", headers=headers)
        assert prog_res.status_code == 200, f"Progress fetch failed: {prog_res.text}"
        prog = prog_res.json()
        print(f"  ✓ Today Date: {prog['today_date']}")
        print(f"  ✓ Learning Streak: {prog['learning_streak_days']} days")
        print(f"  ✓ Week Adherence: {prog['week_adherence_percentage']}%")
        assert "today_date" in prog
        assert "learning_streak_days" in prog

        # Step 2: Generate Adaptive Study Plan with Student Inputs
        print("\n[Step 2] Generating Adaptive Study Plan with Student Inputs...")
        today_date = datetime.now(timezone.utc).date()
        target_exam_date = (today_date + timedelta(days=12)).strftime("%Y-%m-%d")

        gen_payload = {
            "title": "Semester Final Exam Preparation & Mastery Sprint",
            "daily_hours_target": 2.5,
            "days_duration": 14,
            "exam_date": target_exam_date,
            "learning_priority": "weak_topics_first",
            "include_revision": True,
            "include_quizzes": True,
            "focus_weak_topics": True
        }
        gen_res = await client.post(f"{BASE_URL}/study-planner/generate", headers=headers, json=gen_payload)
        assert gen_res.status_code == 200, f"Plan generation failed: {gen_res.text}"
        plan = gen_res.json()
        print(f"  ✓ Plan Generated: '{plan['title']}'")
        print(f"    - Daily Target Hours: {plan['daily_hours_target']} hrs/day")
        print(f"    - Exam Date Target: {plan.get('exam_date')}")
        print(f"    - Learning Priority: {plan.get('learning_priority')}")
        print(f"    - Total Tasks: {plan['total_tasks']}")
        print(f"    - Initial Completed Tasks: {plan['completed_tasks']}")

        assert plan["title"] == gen_payload["title"]
        assert plan["exam_date"] == target_exam_date
        assert plan["learning_priority"] == "weak_topics_first"
        assert len(plan["tasks"]) > 0

        # Step 3: Validate Multi-Type Tasks, Difficulty Allocations & Deep Links
        print("\n[Step 3] Validating Task Types, Difficulty Allocations & Module Integration...")
        task_types_found = set()
        difficulties_found = set()
        action_urls_found = []

        for task in plan["tasks"]:
            t_type = task.get("task_type")
            t_diff = task.get("difficulty_level")
            t_url = task.get("action_url")
            task_types_found.add(t_type)
            difficulties_found.add(t_diff)
            if t_url:
                action_urls_found.append(t_url)

        print(f"  ✓ Task Types Identified: {task_types_found}")
        print(f"  ✓ Difficulty Allocations: {difficulties_found}")
        print(f"  ✓ Connected Integration Deep Links: {len(action_urls_found)} tasks")

        # Verify study, revision, and quiz tasks were synthesized
        assert "study" in task_types_found, "Missing 'study' tasks"
        assert "revision" in task_types_found, "Missing 'revision' tasks"
        assert "quiz" in task_types_found, "Missing 'quiz' tasks"
        assert any("/dashboard/notes" in url for url in action_urls_found), "Smart Notes deep link missing"
        assert any("/dashboard/quiz" in url for url in action_urls_found), "Quiz generator deep link missing"

        # Step 4: Test Task Lifecycle (Toggle, Edit, Reschedule)
        print("\n[Step 4] Testing Task Lifecycle & Editing Operations...")
        first_task = plan["tasks"][0]
        task_id = first_task["id"]

        # 4.1 Toggle Completion
        print(f"  • Toggling completion on task '{first_task['title']}'...")
        toggle_res = await client.post(f"{BASE_URL}/study-planner/tasks/{task_id}/toggle", headers=headers)
        assert toggle_res.status_code == 200, f"Toggle failed: {toggle_res.text}"
        toggle_data = toggle_res.json()
        assert toggle_data["is_completed"] is True
        assert toggle_data["completed_at"] is not None
        print("    ✓ Task marked as completed with timestamp recorded")

        # 4.2 Edit Task
        print("  • Updating task details (PUT /tasks/{id})...")
        edit_payload = {
            "title": "Deep Dive Note Generation & Schema Derivation",
            "duration_minutes": 65,
            "notes": "Student focus: examine 3NF vs BCNF failure edge cases."
        }
        edit_res = await client.put(f"{BASE_URL}/study-planner/tasks/{task_id}", headers=headers, json=edit_payload)
        assert edit_res.status_code == 200, f"Task update failed: {edit_res.text}"
        updated_task = edit_res.json()
        assert updated_task["title"] == edit_payload["title"]
        assert updated_task["duration_minutes"] == 65
        assert updated_task["notes"] == edit_payload["notes"]
        print("    ✓ Task successfully updated and persisted")

        # 4.3 Reschedule Single Task
        print("  • Rescheduling single task to new date...")
        resched_date = (today_date + timedelta(days=5)).strftime("%Y-%m-%d")
        resched_res = await client.post(
            f"{BASE_URL}/study-planner/tasks/{task_id}/reschedule?new_date={resched_date}",
            headers=headers
        )
        assert resched_res.status_code == 200, f"Reschedule failed: {resched_res.text}"
        assert resched_res.json()["new_date"] == resched_date
        print(f"    ✓ Task rescheduled to {resched_date}")

        # Step 5: Test Custom Task Creation & Deletion
        print("\n[Step 5] Testing Custom Task Creation & Deletion...")
        custom_payload = {
            "title": "Custom Practice: Review Distributed Consensus Algorithms",
            "scheduled_date": today_date.strftime("%Y-%m-%d"),
            "duration_minutes": 45,
            "priority": "High",
            "task_type": "study",
            "notes": "Added manually by student for interview prep."
        }
        create_res = await client.post(f"{BASE_URL}/study-planner/tasks", headers=headers, json=custom_payload)
        assert create_res.status_code == 200, f"Task creation failed: {create_res.text}"
        created_task = create_res.json()
        assert created_task["title"] == custom_payload["title"]
        custom_task_id = created_task["id"]
        print(f"  ✓ Created custom task: {created_task['title']} (ID: {custom_task_id})")

        # Delete the custom task
        del_res = await client.delete(f"{BASE_URL}/study-planner/tasks/{custom_task_id}", headers=headers)
        assert del_res.status_code == 200, f"Task deletion failed: {del_res.text}"
        print("  ✓ Custom task deleted cleanly")

        # Step 6: Test Adaptive Overdue Detection & Intelligent Rebalance
        print("\n[Step 6] Testing Intelligent Missed Task Rebalancing...")
        # Create an intentionally overdue task (dated 3 days ago)
        past_date = (today_date - timedelta(days=3)).strftime("%Y-%m-%d")
        overdue_task_payload = {
            "title": "Overdue Reading: Transaction ACID Invariants",
            "scheduled_date": past_date,
            "duration_minutes": 50,
            "priority": "Medium",
            "task_type": "study"
        }
        overdue_create_res = await client.post(f"{BASE_URL}/study-planner/tasks", headers=headers, json=overdue_task_payload)
        assert overdue_create_res.status_code == 200, f"Overdue task creation failed: {overdue_create_res.text}"
        overdue_task = overdue_create_res.json()
        print(f"  • Injected overdue task dated {past_date} (is_overdue={overdue_task['is_overdue']})")

        # Fetch active plan to verify overdue count
        active_plan_res = await client.get(f"{BASE_URL}/study-planner/active", headers=headers)
        active_plan = active_plan_res.json()
        assert active_plan["overdue_tasks"] >= 1, f"Expected at least 1 overdue task, got {active_plan['overdue_tasks']}"
        print(f"  ✓ Active plan identifies {active_plan['overdue_tasks']} overdue task(s)")

        # Call intelligent rebalance
        print("  • Executing POST /api/study-planner/reschedule-missed...")
        rebalance_res = await client.post(f"{BASE_URL}/study-planner/reschedule-missed", headers=headers)
        assert rebalance_res.status_code == 200, f"Rebalance failed: {rebalance_res.text}"
        rebalance_data = rebalance_res.json()
        print(f"  ✓ {rebalance_data['message']}")
        assert rebalance_data["rescheduled_count"] >= 1

        # Step 7: Test Adaptive Performance Recommendations
        print("\n[Step 7] Testing Proactive Adaptive Recommendations...")
        recs_res = await client.get(f"{BASE_URL}/study-planner/adaptive-recommendations", headers=headers)
        assert recs_res.status_code == 200, f"Recommendations fetch failed: {recs_res.text}"
        recs = recs_res.json()
        print(f"  ✓ Retrieved {len(recs)} proactive recommendation(s):")
        for rec in recs:
            print(f"    • [{rec['recommendation_type'].upper()}] {rec['reason']}")
            print(f"      Action: {rec['suggested_action']}")
            assert "recommendation_type" in rec
            assert "suggested_action" in rec

        # Step 8: Validate Updated Progress & Exam Countdown
        print("\n[Step 8] Validating Real-time Adherence & Exam Countdown...")
        final_prog_res = await client.get(f"{BASE_URL}/study-planner/progress", headers=headers)
        assert final_prog_res.status_code == 200, f"Final progress failed: {final_prog_res.text}"
        final_prog = final_prog_res.json()
        print(f"  ✓ Exam Countdown: {final_prog['exam_countdown_days']} days remaining")
        print(f"  ✓ Today Tasks: {final_prog['today_completed_tasks']}/{final_prog['today_total_tasks']} completed")
        print(f"  ✓ Scheduled Today Minutes: {final_prog['today_minutes_scheduled']} mins")
        print(f"  ✓ Weekly Adherence: {final_prog['week_adherence_percentage']}%")

        assert final_prog["exam_countdown_days"] == 12

        print("\n" + "=" * 70)
        print("PHASE 7: INTELLIGENT PERSONALIZED STUDY PLANNER VERIFIED SUCCESSFULLY!")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_phase7_planner())
