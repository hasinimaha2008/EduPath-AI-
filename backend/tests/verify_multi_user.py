import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.models import User
from sqlalchemy import select, delete

async def run_verification():
    print("==================================================")
    print("      EDUPATH AI - MULTI-USER & AUTH VERIFICATION")
    print("==================================================")

    # Use ASGITransport for in-memory testing against FastAPI app
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        # TEST 1: Unauthenticated requests MUST return 401 Unauthorized
        print("\n[TEST 1] Testing unauthenticated access (Strict Security)...")
        r = await client.get("/api/auth/me")
        assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"
        print("  [PASS] /api/auth/me without token -> 401 Unauthorized (No silent demo fallback)")

        r = await client.get("/api/notes")
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print("  [PASS] /api/notes without token -> 401 Unauthorized")

        r = await client.get("/api/analytics/dashboard")
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print("  [PASS] /api/analytics/dashboard without token -> 401 Unauthorized")

        # Clean up any pre-existing test users
        async with AsyncSessionLocal() as session:
            for email in ["sarah.connor@test.com", "thomas.anderson@matrix.org"]:
                existing = await session.execute(select(User).where(User.email == email))
                u = existing.scalar_one_or_none()
                if u:
                    await session.delete(u)
            await session.commit()

        # TEST 2: Register User 1 (Sarah Connor)
        print("\n[TEST 2] Registering User 1 (Sarah Connor)...")
        reg_sarah = await client.post("/api/auth/register", json={
            "full_name": "Sarah Connor",
            "email": "sarah.connor@test.com",
            "password": "Password123!"
        })
        assert reg_sarah.status_code == 200, f"Sarah register failed: {reg_sarah.text}"
        sarah_data = reg_sarah.json()
        sarah_token = sarah_data["access_token"]
        sarah_headers = {"Authorization": f"Bearer {sarah_token}"}
        assert sarah_data["user"]["full_name"] == "Sarah Connor"
        assert sarah_data["user"]["email"] == "sarah.connor@test.com"
        print(f"  [PASS] User 1 registered: {sarah_data['user']['full_name']} ({sarah_data['user']['email']})")

        # Verify User 1 /api/auth/me
        me_sarah = await client.get("/api/auth/me", headers=sarah_headers)
        assert me_sarah.status_code == 200
        assert me_sarah.json()["full_name"] == "Sarah Connor"
        assert me_sarah.json()["email"] == "sarah.connor@test.com"
        print("  [PASS] /api/auth/me correctly returns Sarah Connor's profile details")

        # Sarah creates a note
        note_sarah = await client.post("/api/notes", headers=sarah_headers, json={
            "title": "Sarah's AI Research Notes",
            "content_markdown": "Deep neural architectures for cybernetic systems.",
            "note_type": "detailed"
        })
        assert note_sarah.status_code == 200
        sarah_note_id = note_sarah.json()["id"]
        print(f"  [PASS] Sarah created note ID {sarah_note_id}: 'Sarah's AI Research Notes'")

        # TEST 3: Register User 2 (Thomas Anderson)
        print("\n[TEST 3] Registering User 2 (Thomas Anderson)...")
        reg_thomas = await client.post("/api/auth/register", json={
            "full_name": "Thomas Anderson",
            "email": "thomas.anderson@matrix.org",
            "password": "RedPill2024!"
        })
        assert reg_thomas.status_code == 200, f"Thomas register failed: {reg_thomas.text}"
        thomas_data = reg_thomas.json()
        thomas_token = thomas_data["access_token"]
        thomas_headers = {"Authorization": f"Bearer {thomas_token}"}
        assert thomas_data["user"]["full_name"] == "Thomas Anderson"
        assert thomas_data["user"]["email"] == "thomas.anderson@matrix.org"
        print(f"  [PASS] User 2 registered: {thomas_data['user']['full_name']} ({thomas_data['user']['email']})")

        # Verify User 2 /api/auth/me
        me_thomas = await client.get("/api/auth/me", headers=thomas_headers)
        assert me_thomas.status_code == 200
        assert me_thomas.json()["full_name"] == "Thomas Anderson"
        assert me_thomas.json()["email"] == "thomas.anderson@matrix.org"
        print("  [PASS] /api/auth/me correctly returns Thomas Anderson's profile details")

        # TEST 4: Cross-User Data Isolation Verification
        print("\n[TEST 4] Verifying strict cross-user data isolation...")
        thomas_notes = await client.get("/api/notes", headers=thomas_headers)
        assert thomas_notes.status_code == 200
        thomas_notes_list = thomas_notes.json()
        assert len(thomas_notes_list) == 0, f"Thomas should have 0 notes, found {len(thomas_notes_list)}"
        print("  [PASS] Thomas cannot see Sarah's notes (isolation confirmed, count = 0)")

        # Thomas creates his own note
        note_thomas = await client.post("/api/notes", headers=thomas_headers, json={
            "title": "Thomas's Matrix Notes",
            "content_markdown": "Simulated realities and distributed algorithms.",
            "note_type": "detailed"
        })
        assert note_thomas.status_code == 200
        print("  [PASS] Thomas created his own note: 'Thomas's Matrix Notes'")

        # Sarah checks her notes again
        sarah_notes = await client.get("/api/notes", headers=sarah_headers)
        assert len(sarah_notes.json()) == 1
        assert sarah_notes.json()[0]["title"] == "Sarah's AI Research Notes"
        print("  [PASS] Sarah still only sees her own 1 note, not Thomas's note")

        # TEST 5: Demo Login Test
        print("\n[TEST 5] Verifying 1-Click Demo Login...")
        demo_res = await client.post("/api/auth/demo-login")
        assert demo_res.status_code == 200
        demo_data = demo_res.json()
        demo_token = demo_data["access_token"]
        assert demo_data["user"]["email"] == "demo@edupath.ai"
        assert "Alex Mercer" in demo_data["user"]["full_name"]
        demo_headers = {"Authorization": f"Bearer {demo_token}"}
        me_demo = await client.get("/api/auth/me", headers=demo_headers)
        assert "Alex Mercer" in me_demo.json()["full_name"]
        assert me_demo.json()["email"] == "demo@edupath.ai"
        print("  [PASS] Demo user correctly returns Alex Mercer and demo@edupath.ai ONLY when explicitly requested")

        # TEST 6: Session Login with Password
        print("\n[TEST 6] Testing Login endpoint with User 1 and User 2 credentials...")
        login_sarah = await client.post("/api/auth/login", json={
            "email": "sarah.connor@test.com",
            "password": "Password123!"
        })
        assert login_sarah.status_code == 200
        assert login_sarah.json()["user"]["full_name"] == "Sarah Connor"
        print("  [PASS] Sarah can log in and receives her correct profile")

        login_thomas = await client.post("/api/auth/login", json={
            "email": "thomas.anderson@matrix.org",
            "password": "RedPill2024!"
        })
        assert login_thomas.status_code == 200
        assert login_thomas.json()["user"]["full_name"] == "Thomas Anderson"
        print("  [PASS] Thomas can log in and receives his correct profile")

        # Wrong password
        bad_login = await client.post("/api/auth/login", json={
            "email": "sarah.connor@test.com",
            "password": "WrongPassword!"
        })
        assert bad_login.status_code == 401
        print("  [PASS] Invalid password rejected with 401 Unauthorized")

    print("\n==================================================")
    print("  ALL MULTI-USER & AUTH SECURITY TESTS PASSED!    ")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
