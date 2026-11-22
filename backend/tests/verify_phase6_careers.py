import asyncio
import os
import sys
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

async def test_phase6_careers():
    print("=" * 70)
    print("Starting Comprehensive Phase 6: Advanced Career Intelligence System Verification")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=90.0) as client:
        # Step 0: Authenticate demo user
        print("\n[Step 0] Authenticating demo user...")
        login_res = await client.post(f"{BASE_URL}/auth/demo-login")
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  ✓ Authenticated as demo@edupath.ai")

        # Step 1: Student Career Profile Management
        print("\n[Step 1] Testing Student Career Profile Management...")
        # 1.1 GET profile
        profile_res = await client.get(f"{BASE_URL}/profile/student", headers=headers)
        assert profile_res.status_code == 200, f"Profile fetch failed: {profile_res.text}"
        profile_data = profile_res.json()
        print(f"  ✓ Retrieved initial student profile: {profile_data['full_name']}")
        print(f"    - Existing Verified Skills: {len(profile_data.get('verified_skills', []))}")
        print(f"    - Current Preferred Domains: {profile_data.get('preferred_domains', [])}")

        # 1.2 PUT profile update (adding domains, self-reported skills, projects)
        print("\n  Updating student profile with new domains, skills, and projects...")
        update_payload = {
            "interests": ["Distributed Systems", "Cloud Native Computing", "Generative AI", "Cyber Defense"],
            "preferred_domains": ["Cloud Computing", "Artificial Intelligence", "Cybersecurity"],
            "career_goals": "Targeting Principal Cloud Architect or AI Engineer role in 2 years",
            "self_reported_skills": ["Docker", "Kubernetes", "AWS", "FastAPI", "Terraform"],
            "projects_and_experience": [
                {
                    "title": "Cloud Microservices Mesh",
                    "role": "Lead Architect",
                    "description": "Engineered multi-region Kubernetes cluster with Istio mesh and Prometheus monitoring.",
                    "technologies": ["Kubernetes", "Docker", "Prometheus", "Go"],
                    "url": "https://github.com/demo/cloud-mesh"
                },
                {
                    "title": "LLM Document Intelligence Gateway",
                    "role": "Full-Stack AI Developer",
                    "description": "Constructed asynchronous document analysis pipeline with multi-model fallback.",
                    "technologies": ["Python", "FastAPI", "React", "Vector DB"],
                    "url": "https://github.com/demo/llm-gateway"
                }
            ]
        }
        update_res = await client.put(f"{BASE_URL}/profile/student", headers=headers, json=update_payload)
        assert update_res.status_code == 200, f"Profile update failed: {update_res.text}"
        updated_profile = update_res.json()
        print("  ✓ Student profile updated successfully:")
        print(f"    - Interests: {updated_profile.get('interests')}")
        print(f"    - Preferred Domains: {updated_profile.get('preferred_domains')}")
        print(f"    - Self-reported Skills: {updated_profile.get('self_reported_skills')}")
        print(f"    - Projects Count: {len(updated_profile.get('projects_and_experience', []))}")
        assert "Cloud Computing" in updated_profile["preferred_domains"]
        assert "Artificial Intelligence" in updated_profile["preferred_domains"]
        assert len(updated_profile["projects_and_experience"]) == 2

        # Step 2: Career Recommendations & Domain Intelligence
        print("\n[Step 2] Testing Career Recommendations Engine...")
        recs_res = await client.get(f"{BASE_URL}/careers/recommendations", headers=headers)
        assert recs_res.status_code == 200, f"Recommendations fetch failed: {recs_res.text}"
        recs = recs_res.json()
        assert len(recs) > 0, "No career recommendations returned!"
        print(f"  ✓ Received {len(recs)} career recommendations")

        cloud_or_ai_found = False
        for r in recs:
            role_title = r['career_role']['title']
            print(f"\n  • Role: {role_title} [{r.get('domain', 'General')}]")
            print(f"    - Overall Match Score: {r['match_score']}%")
            print(f"    - Demonstrated (Verified) Score: {r.get('demonstrated_match_score', 0.0)}%")
            print(f"    - Self-Reported Match Score: {r.get('self_reported_match_score', 0.0)}%")
            print(f"    - Rationale: {r.get('rationale', 'N/A')}")
            print(f"    - Recommended Projects: {len(r.get('recommended_projects', []))}")
            
            # Assert schema validity
            assert 0.0 <= r["match_score"] <= 100.0
            assert "domain" in r and r["domain"]
            assert "demonstrated_match_score" in r
            assert "self_reported_match_score" in r
            assert "rationale" in r
            assert len(r.get("recommended_projects", [])) >= 1

            if r.get("domain") in ["Cloud Computing", "Artificial Intelligence", "Machine Learning"]:
                cloud_or_ai_found = True

        assert cloud_or_ai_found, "Cloud Computing or AI/ML roles should be recommended given profile preferences!"

        # Step 3: Skill Gap Identification & Prioritization
        print("\n[Step 3] Testing Skill Gap Analysis...")
        target_role_id = recs[0]["career_role"]["id"]
        gaps_res = await client.get(f"{BASE_URL}/skills/gaps/{target_role_id}", headers=headers)
        assert gaps_res.status_code == 200, f"Skill gaps fetch failed: {gaps_res.text}"
        gaps_data = gaps_res.json()
        print(f"  ✓ Skill Gaps for '{gaps_data['career_role']['title']}':")
        all_gaps = gaps_data.get("gaps", [])
        missing_skills = [g for g in all_gaps if g["status"] == "missing"]
        matched_skills = [g for g in all_gaps if g["status"] == "existing"]
        print(f"    - Missing Skills Count: {len(missing_skills)}")
        print(f"    - Matched Skills Count: {len(matched_skills)}")

        # Check gap item attributes
        for skill in missing_skills[:3]:
            print(f"    • Missing: {skill['skill_name']} [Importance: {skill.get('job_market_importance', 'Core')}]")
            print(f"      - Is Verified: {skill.get('is_verified', False)}")
            print(f"      - Learning Resources: {len(skill.get('learning_resources', []))}")
            print(f"      - Suggested Projects: {len(skill.get('suggested_projects', []))}")
            assert "is_verified" in skill
            assert "job_market_importance" in skill
            assert "learning_resources" in skill
            assert "suggested_projects" in skill

        # Step 4: Phased Personalized Career Roadmap
        print("\n[Step 4] Testing Personalized Career Roadmap...")
        # 4.1 Generate roadmap
        roadmap_req = {
            "career_role_id": target_role_id,
            "target_timeline_months": 6
        }
        gen_res = await client.post(f"{BASE_URL}/roadmaps/generate", headers=headers, json=roadmap_req)
        assert gen_res.status_code == 200, f"Roadmap generation failed: {gen_res.text}"
        roadmap_data = gen_res.json()
        print(f"  ✓ Generated Roadmap: {roadmap_data['title']} ({roadmap_data['target_timeline_months']} months)")
        milestones = roadmap_data.get("milestones", [])
        assert len(milestones) >= 4, f"Expected at least 4 milestones, got {len(milestones)}"

        stages_found = set()
        for m in milestones:
            stages_found.add(m.get("stage"))
            print(f"    - Milestone {m['order_index']}: [{m.get('stage', 'N/A').upper()}] {m['title']}")
            print(f"      Resources: {len(m.get('learning_resources', []))}")
            assert "stage" in m and m["stage"] in ["beginner", "intermediate", "advanced", "capstone"]
            assert "learning_resources" in m

        print(f"  ✓ Phased Stages present: {stages_found}")
        assert "beginner" in stages_found or "intermediate" in stages_found
        assert "capstone" in stages_found

        # 4.2 Toggle Milestone Completion
        first_m_id = milestones[0]["id"]
        toggle_res = await client.post(f"{BASE_URL}/roadmaps/milestones/{first_m_id}/toggle", headers=headers)
        assert toggle_res.status_code == 200, f"Milestone toggle failed: {toggle_res.text}"
        toggled = toggle_res.json()
        print(f"  ✓ Toggled Milestone ID '{toggled['milestone_id']}' is_completed={toggled['is_completed']}, roadmap_progress={toggled['roadmap_progress']}%")
        assert toggled["is_completed"] is True

        # Step 5: Academic-to-Industry Skill Mapping
        print("\n[Step 5] Testing Academic-to-Industry Skill Mapping...")
        mapping_res = await client.get(f"{BASE_URL}/skills/mappings")
        assert mapping_res.status_code == 200, f"Skill mappings fetch failed: {mapping_res.text}"
        mappings = mapping_res.json()
        assert len(mappings) > 0, "No skill mappings returned!"
        print(f"  ✓ Retrieved {len(mappings)} Academic-to-Industry Mappings")

        applications_verified = 0
        projects_verified = 0
        for m in mappings:
            assert "subject_name" in m
            assert "topic_name" in m
            assert "competency_name" in m
            assert "skill_name" in m
            assert "career_role_title" in m
            if m.get("industry_application"):
                applications_verified += 1
            if m.get("practical_project_example"):
                projects_verified += 1

        print(f"  ✓ Mappings with explicit Real-World Applications: {applications_verified}/{len(mappings)}")
        print(f"  ✓ Mappings with Practical Project Examples: {projects_verified}/{len(mappings)}")
        assert applications_verified > 0
        assert projects_verified > 0

        # Print example mapping
        sample = next((m for m in mappings if m.get("industry_application")), mappings[0])
        print("\n  Sample Academic-to-Industry Connection:")
        print(f"    • Subject & Topic: {sample['subject_name']} -> {sample['topic_name']}")
        print(f"    • Competency & Skill: {sample['competency_name']} -> {sample['skill_name']}")
        print(f"    • Target Career: {sample['career_role_title']}")
        print(f"    • Production Application: {sample.get('industry_application')}")
        print(f"    • Project Example: {sample.get('practical_project_example')}")

        print("\n" + "=" * 70)
        print("PHASE 6: ADVANCED CAREER INTELLIGENCE SYSTEM VERIFIED SUCCESSFULLY!")
        print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_phase6_careers())
