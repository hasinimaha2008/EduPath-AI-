import asyncio
import os
import sys
import time
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

async def test_phase5_analytics():
    print("=" * 70)
    print("Starting Comprehensive Phase 5: Advanced Learning Analytics Verification")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=90.0) as client:
        # Step 0: Authentication
        print("\n[Step 0] Authenticating demo user...")
        login_res = await client.post(f"{BASE_URL}/auth/demo-login")
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  ✓ Authenticated as demo@edupath.ai")

        # Step 1: Fetch Analytics Dashboard
        print("\n[Step 1] Fetching Learning Analytics Dashboard...")
        dash_res = await client.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
        assert dash_res.status_code == 200, f"Dashboard fetch failed: {dash_res.text}"
        data = dash_res.json()
        print("  ✓ Retrieved analytics dashboard successfully")

        # Step 2: Validate Real Metric Computation
        print("\n[Step 2] Validating Metric Calculations (Zero Fabrication)...")
        print(f"  • Total Quizzes Attempted: {data['total_quizzes_attempted']}")
        print(f"  • Average Quiz Score: {data['average_quiz_score']}%")
        print(f"  • Highest Quiz Score: {data.get('highest_quiz_score', 0.0)}%")
        print(f"  • Study Consistency (14d): {data.get('study_consistency_percentage', 0.0)}%")
        print(f"  • Learning Streak: {data['learning_streak_days']} days")
        print(f"  • Total Study Time: {data['total_study_hours']} hrs")

        assert isinstance(data["total_quizzes_attempted"], int) and data["total_quizzes_attempted"] >= 0
        assert 0.0 <= data["average_quiz_score"] <= 100.0
        assert 0.0 <= data.get("highest_quiz_score", 0.0) <= 100.0
        assert 0.0 <= data.get("study_consistency_percentage", 0.0) <= 100.0
        assert isinstance(data["learning_streak_days"], int) and data["learning_streak_days"] >= 0

        if data["total_quizzes_attempted"] > 0:
            assert data["highest_quiz_score"] >= data["average_quiz_score"] or abs(data["highest_quiz_score"] - data["average_quiz_score"]) < 1e-4

        # Step 3: Validate Visualizations Data
        print("\n[Step 3] Validating Visualizations Data...")

        # 3.1 Weekly Learning Activity
        recent_act = data.get("recent_activity", [])
        assert len(recent_act) == 7, f"Expected 7 days in recent_activity, got {len(recent_act)}"
        print(f"  ✓ Weekly Activity: 7 daily tracking intervals found (total questions solved: {sum(d['questions_solved'] for d in recent_act)})")

        # 3.2 Subject-Wise Performance
        subj_perfs = data.get("subject_performances", [])
        print(f"  ✓ Subject-Wise Performances: {len(subj_perfs)} subjects evaluated")
        for sp in subj_perfs:
            assert "subject_name" in sp
            assert "quizzes_count" in sp and sp["quizzes_count"] >= 0
            assert "topics_practiced" in sp and sp["topics_practiced"] >= 0
            assert 0.0 <= sp["average_accuracy"] <= 100.0
            print(f"    - {sp['subject_name']}: {sp['average_accuracy']}% accuracy, {sp['quizzes_count']} quizzes, {sp['topics_practiced']} topics")

        # 3.3 Quiz Score Trends
        score_trends = data.get("quiz_score_trends", [])
        print(f"  ✓ Quiz Score Trends: {len(score_trends)} chronological attempt points")
        for st in score_trends:
            assert "attempt_id" in st
            assert "quiz_title" in st
            assert 0.0 <= st["percentage"] <= 100.0
            assert "completed_at" in st
            assert "score" in st and "max_score" in st

        # 3.4 Topic Mastery Distribution
        top_stats = data.get("topic_completion_stats")
        assert top_stats is not None, "topic_completion_stats missing"
        print(f"  ✓ Topic Mastery Breakdown:")
        print(f"    - Total Practiced: {top_stats['total_practiced']}")
        print(f"    - Mastered: {top_stats['mastered_count']}")
        print(f"    - Proficient: {top_stats['proficient_count']}")
        print(f"    - Developing: {top_stats['developing_count']}")
        print(f"    - Needs Practice: {top_stats['needs_practice_count']}")
        calculated_sum = top_stats['mastered_count'] + top_stats['proficient_count'] + top_stats['developing_count'] + top_stats['needs_practice_count']
        assert calculated_sum == top_stats['total_practiced']

        # 3.5 Strengths and Weaknesses
        strong_topics = data.get("strong_topics", [])
        weak_topics = data.get("weak_topics", [])
        print(f"  ✓ Strengths: {len(strong_topics)} strong topics, Weaknesses: {len(weak_topics)} weak topics")
        for st in strong_topics:
            assert st["accuracy_percentage"] >= 75.0 or st["mastery_status"] in ["proficient", "mastered"]
        for wt in weak_topics:
            assert wt["accuracy_percentage"] < 75.0 or wt["mastery_status"] in ["needs_practice", "developing"]

        # Step 4: Validate Intelligent Insights
        print("\n[Step 4] Validating Intelligent Insights & Diagnostics...")
        insights = data.get("intelligent_insights", [])
        assert len(insights) >= 4, f"Expected at least 4 diagnostic insights, got {len(insights)}"
        categories = {i["category"] for i in insights}
        print(f"  ✓ Insights generated for categories: {categories}")
        assert "attention" in categories, "Missing 'attention' insight"
        assert "improvement" in categories, "Missing 'improvement' insight"
        assert "difficulty" in categories, "Missing 'difficulty' insight"
        assert "revision" in categories, "Missing 'revision' insight"

        for ins in insights:
            print(f"    [{ins['category'].upper()}] {ins['title']}: {ins['message'][:60]}... ({ins['severity']})")

        # Step 5: Validate Personalized Practical Recommendation
        print("\n[Step 5] Validating Personalized Recommendation...")
        pers_rec = data.get("personalized_recommendation")
        assert pers_rec is not None and len(pers_rec.strip()) > 15, "Personalized recommendation must be a substantial string"
        print(f"  ✓ Recommendation: \"{pers_rec}\"")

        # Step 6: Test Empty State Behavior for Brand New User
        print("\n[Step 6] Testing Empty-State Behavior for Fresh Student Account...")
        unique_email = f"fresh_student_{int(time.time())}@edupath.ai"
        reg_res = await client.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": unique_email,
                "password": "Password123!",
                "full_name": "Fresh Student"
            }
        )
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        new_token = reg_res.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        new_dash_res = await client.get(f"{BASE_URL}/analytics/dashboard", headers=new_headers)
        assert new_dash_res.status_code == 200, f"Fresh dashboard fetch failed: {new_dash_res.text}"
        new_data = new_dash_res.json()

        assert new_data["total_quizzes_attempted"] == 0
        assert new_data["average_quiz_score"] == 0.0
        assert new_data["highest_quiz_score"] == 0.0
        assert new_data["study_consistency_percentage"] == 0.0
        assert new_data["strong_topics"] == []
        assert new_data["weak_topics"] == []
        assert new_data["quiz_score_trends"] == []
        assert new_data["topic_completion_stats"]["total_practiced"] == 0
        assert "Welcome to your Learning Analytics Dashboard" in new_data["personalized_recommendation"]
        print("  ✓ Fresh user dashboard returned clean zero-state without errors or fabricated statistics")

        print("\n" + "=" * 70)
        print("ALL PHASE 5 LEARNING ANALYTICS TESTS PASSED SUCCESSFULLY! ✓")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_phase5_analytics())
