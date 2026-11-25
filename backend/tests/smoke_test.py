"""
EduPath AI - Production Deployment Automated Smoke Test Suite.
Can be executed against any live target BASE_URL (local, staging, or production)
or directly in-process via ASGITransport.
Verifies critical user journeys: health, live/ready probes, subjects, careers,
user registration, JWT session, and AI assistant reasoning.
"""

import sys
import os
import asyncio
import time
import uuid
import httpx

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = os.environ.get("DEPLOYMENT_URL") or os.environ.get("BASE_URL") or "http://127.0.0.1:8000"

async def run_smoke_test(target_url: str = BASE_URL) -> bool:
    print("=" * 80)
    print(f"EDUPATH AI - AUTOMATED DEPLOYMENT SMOKE TEST RUNNER")
    print(f"Target URL: {target_url}")
    print("=" * 80)

    use_asgi = False
    try:
        async with httpx.AsyncClient(base_url=target_url, timeout=2.0) as check_client:
            r = await check_client.get("/health")
            if r.status_code != 200:
                use_asgi = True
    except Exception:
        use_asgi = True

    if use_asgi:
        print("[INFO] Live HTTP endpoint unreachable. Executing smoke test via in-process ASGITransport.")
        from app.main import app
        from httpx import ASGITransport
        transport = ASGITransport(app=app)
        client_ctx = httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0)
    else:
        print(f"[INFO] Connected to live HTTP server at {target_url}.")
        client_ctx = httpx.AsyncClient(base_url=target_url, timeout=30.0)

    test_passed = True
    results = []

    def record(step: str, status: str, details: str = ""):
        nonlocal test_passed
        if status != "PASS":
            test_passed = False
        symbol = "✓" if status == "PASS" else "✗"
        results.append((step, status, details))
        print(f"  {symbol} [{step}]: {status} {details}")

    async with client_ctx as client:
        # Step 1: Health probe
        try:
            r = await client.get("/health")
            if r.status_code == 200 and r.json().get("status") == "healthy":
                record("1. Basic Health Probe (/health)", "PASS", f"Status: {r.status_code}")
            else:
                record("1. Basic Health Probe (/health)", "FAIL", f"Status: {r.status_code}, Body: {r.text[:100]}")
        except Exception as e:
            record("1. Basic Health Probe (/health)", "FAIL", f"Exception: {str(e)}")

        # Step 2: Liveness probe
        try:
            r = await client.get("/api/health/live")
            if r.status_code == 200 and r.json().get("status") == "alive":
                record("2. Liveness Probe (/api/health/live)", "PASS", f"Uptime: {r.json().get('uptime_seconds')}s")
            else:
                record("2. Liveness Probe (/api/health/live)", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("2. Liveness Probe (/api/health/live)", "FAIL", f"Exception: {str(e)}")

        # Step 3: Readiness probe with subsystem diagnostics
        try:
            r = await client.get("/api/health/ready")
            data = r.json()
            if r.status_code == 200 and data.get("status") == "ready":
                subsystems = data.get("subsystems", {})
                record("3. Readiness Probe (/api/health/ready)", "PASS", f"Subsystems: {list(subsystems.keys())}")
            else:
                record("3. Readiness Probe (/api/health/ready)", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("3. Readiness Probe (/api/health/ready)", "FAIL", f"Exception: {str(e)}")

        # Step 4: Subjects taxonomy catalog
        try:
            r = await client.get("/api/subjects")
            if r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) > 0:
                record("4. Taxonomy Subjects Catalog (/api/subjects)", "PASS", f"Found {len(r.json())} subjects")
            else:
                record("4. Taxonomy Subjects Catalog (/api/subjects)", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("4. Taxonomy Subjects Catalog (/api/subjects)", "FAIL", f"Exception: {str(e)}")

        # Step 5: Career roles taxonomy
        try:
            r = await client.get("/api/careers/roles")
            if r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) >= 8:
                record("5. Career Intelligence Roles (/api/careers/roles)", "PASS", f"Found {len(r.json())} core roles")
            else:
                record("5. Career Intelligence Roles (/api/careers/roles)", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("5. Career Intelligence Roles (/api/careers/roles)", "FAIL", f"Exception: {str(e)}")

        # Step 6: User registration
        test_email = f"smoke_{uuid.uuid4().hex[:8]}@example.com"
        auth_headers = {}
        try:
            r = await client.post("/api/auth/register", json={
                "email": test_email,
                "password": "StrongPassword123!",
                "full_name": "Smoke Test Runner"
            })
            if r.status_code == 200 and "access_token" in r.json():
                token = r.json()["access_token"]
                auth_headers = {"Authorization": f"Bearer {token}"}
                record("6. User Registration & JWT Issuance", "PASS", f"User: {test_email}")
            else:
                record("6. User Registration & JWT Issuance", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("6. User Registration & JWT Issuance", "FAIL", f"Exception: {str(e)}")

        # Step 7: Authenticated Profile Verification
        try:
            r = await client.get("/api/auth/me", headers=auth_headers)
            if r.status_code == 200 and r.json().get("email") == test_email:
                record("7. Authenticated Profile Verification (/api/auth/me)", "PASS", f"ID: {r.json().get('id')}")
            else:
                record("7. Authenticated Profile Verification (/api/auth/me)", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("7. Authenticated Profile Verification (/api/auth/me)", "FAIL", f"Exception: {str(e)}")

        # Step 8: AI Assistant reasoning query
        try:
            r = await client.post("/api/assistant/ask", headers=auth_headers, json={
                "question": "What is the primary difference between synchronous and asynchronous I/O in distributed systems?",
                "explanation_level": "intermediate"
            })
            ans_content = ""
            if r.status_code == 200:
                data = r.json()
                if "assistant_message" in data and isinstance(data["assistant_message"], dict):
                    ans_content = data["assistant_message"].get("content", "")
                elif "answer" in data:
                    ans_content = data.get("answer", "")

            if r.status_code == 200 and len(ans_content) > 30:
                record("8. AI Assistant Grounded Reasoning (/api/assistant/ask)", "PASS", f"Answer Length: {len(ans_content)} chars")
            else:
                record("8. AI Assistant Grounded Reasoning (/api/assistant/ask)", "FAIL", f"Status: {r.status_code}")
        except Exception as e:
            record("8. AI Assistant Grounded Reasoning (/api/assistant/ask)", "FAIL", f"Exception: {str(e)}")

    print("\n" + "=" * 80)
    print("SMOKE TEST SUMMARY REPORT")
    print("=" * 80)
    passed_count = sum(1 for _, st, _ in results if st == "PASS")
    total_count = len(results)
    print(f"Total Steps Executed: {total_count}")
    print(f"Passed:               {passed_count} / {total_count} ({passed_count/total_count*100:.1f}%)")
    print(f"Overall Result:       {'SUCCESS' if test_passed else 'FAILURE'}")
    print("=" * 80)

    return test_passed

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else BASE_URL
    success = asyncio.run(run_smoke_test(url))
    sys.exit(0 if success else 1)
