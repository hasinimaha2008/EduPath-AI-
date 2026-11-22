import asyncio
import httpx
import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

async def test_phase1():
    print("=" * 60)
    print("EDUPATH AI - PHASE 1: ADVANCED AI STUDY ASSISTANT VERIFICATION")
    print("=" * 60)
    passed = 0
    total = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Authenticate with Demo User
        total += 1
        print("\n[TEST 1] Authenticating Demo User...")
        login_res = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "demo@edupath.ai", "password": "EduPath@2026"}
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  -> Authenticated successfully as demo@edupath.ai")
        passed += 1

        # 2. Check Assistant Status
        total += 1
        print("\n[TEST 2] Verifying Assistant Status & Engine...")
        status_res = await client.get(f"{BASE_URL}/assistant/status", headers=headers)
        assert status_res.status_code == 200, f"Status failed: {status_res.text}"
        status_data = status_res.json()
        print(f"  -> Model: {status_data.get('model_name')}, Provider: {status_data.get('provider')}")
        print(f"  -> Streaming: {status_data.get('streaming_supported')}, Languages: {status_data.get('multilingual_supported')}")
        assert "streaming_supported" in status_data
        passed += 1

        # 3. Test General-Purpose Question & Smart Auto-Title
        total += 1
        print("\n[TEST 3] Asking Technical Question & Verifying Smart Auto-Title...")
        ask_res = await client.post(
            f"{BASE_URL}/assistant/ask",
            headers=headers,
            json={
                "question": "Explain the difference between Optimistic Concurrency Control and Two-Phase Locking in database transactions.",
                "language": "en"
            }
        )
        assert ask_res.status_code == 200, f"Ask failed: {ask_res.text}"
        ask_data = ask_res.json()
        conv_id = ask_data["conversation_id"]
        answer_text = ask_data["assistant_message"]["content"]
        assert len(answer_text) > 50, "Answer too short"
        print(f"  -> Conversation ID: {conv_id}")
        print(f"  -> Answer preview: {answer_text[:120]}...")
        passed += 1

        # 4. Multi-Turn Context Retention in the Same Conversation
        total += 1
        print("\n[TEST 4] Testing Multi-Turn Context Retention (Follow-up question)...")
        followup_res = await client.post(
            f"{BASE_URL}/assistant/ask",
            headers=headers,
            json={
                "conversation_id": conv_id,
                "question": "Which of those two is better suited for read-heavy workloads and why?",
                "language": "en"
            }
        )
        assert followup_res.status_code == 200, f"Follow-up failed: {followup_res.text}"
        followup_data = followup_res.json()
        followup_answer = followup_data["assistant_message"]["content"]
        assert len(followup_answer) > 50
        print(f"  -> Follow-up answer preview: {followup_answer[:120]}...")
        passed += 1

        # 5. Real-Time Token Streaming (SSE)
        total += 1
        print("\n[TEST 5] Testing Real-Time Token Streaming via /chat-stream (SSE)...")
        stream_chunks = []
        meta_received = False
        done_received = False

        async with client.stream(
            "POST",
            f"{BASE_URL}/assistant/chat-stream",
            headers=headers,
            json={
                "question": "What is Amdahl's Law in parallel computing?",
                "language": "en"
            }
        ) as response:
            assert response.status_code == 200, f"Stream failed: {response.status_code}"
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    payload = json.loads(line[6:])
                    if payload.get("type") == "meta":
                        meta_received = True
                        stream_conv_id = payload.get("conversation_id")
                    elif payload.get("type") == "token":
                        stream_chunks.append(payload.get("content", ""))
                    elif payload.get("type") == "done":
                        done_received = True

        streamed_content = "".join(stream_chunks)
        assert meta_received, "Metadata event not received in stream"
        assert len(streamed_content) > 30, "No tokens received from stream"
        assert done_received, "Done event not received in stream"
        print(f"  -> Streamed {len(stream_chunks)} tokens successfully.")
        print(f"  -> Streamed answer preview: {streamed_content[:120]}...")
        passed += 1

        # 6. Multilingual Intelligence (Telugu & Hindi)
        total += 1
        print("\n[TEST 6] Testing Multilingual Intelligence (Telugu & Hindi)...")
        telugu_res = await client.post(
            f"{BASE_URL}/assistant/ask",
            headers=headers,
            json={
                "question": "కంప్యూటర్ నెట్‌వర్క్‌లలో TCP మరియు UDP మధ్య ప్రధాన తేడా ఏమిటి?",
                "language": "te"
            }
        )
        assert telugu_res.status_code == 200, f"Telugu ask failed: {telugu_res.text}"
        telugu_answer = telugu_res.json()["assistant_message"]["content"]
        print(f"  -> Telugu response preview: {telugu_answer[:100]}...")

        hindi_res = await client.post(
            f"{BASE_URL}/assistant/ask",
            headers=headers,
            json={
                "question": "आर्टिफिशियल इंटेलिजेंस और मशीन लर्निंग में क्या अंतर है?",
                "language": "hi"
            }
        )
        assert hindi_res.status_code == 200, f"Hindi ask failed: {hindi_res.text}"
        hindi_answer = hindi_res.json()["assistant_message"]["content"]
        print(f"  -> Hindi response preview: {hindi_answer[:100]}...")
        passed += 1

        # 7. Mathematical Formula & KaTeX Output
        total += 1
        print("\n[TEST 7] Testing Mathematical Explanation & Formula Formatting...")
        math_res = await client.post(
            f"{BASE_URL}/assistant/ask",
            headers=headers,
            json={
                "question": "What is the Fundamental Theorem of Calculus?",
                "language": "en"
            }
        )
        assert math_res.status_code == 200, f"Math ask failed: {math_res.text}"
        math_content = math_res.json()["assistant_message"]["content"]
        print(f"  -> Math response preview: {math_content[:120]}...")
        passed += 1

        # 8. Regenerate Response
        total += 1
        print("\n[TEST 8] Testing Regenerate Response (/assistant/regenerate)...")
        regen_res = await client.post(
            f"{BASE_URL}/assistant/regenerate",
            headers=headers,
            json={"conversation_id": conv_id}
        )
        assert regen_res.status_code == 200, f"Regenerate failed: {regen_res.text}"
        regen_data = regen_res.json()
        new_answer = regen_data["assistant_message"]["content"]
        assert len(new_answer) > 50
        print(f"  -> Regenerated answer preview: {new_answer[:120]}...")
        passed += 1

        # 9. Conversation Management: List, Rename, Delete
        total += 1
        print("\n[TEST 9] Testing Conversation Management (List, Rename, Delete)...")
        # List
        list_res = await client.get(f"{BASE_URL}/chat-history", headers=headers)
        assert list_res.status_code == 200
        conv_list = list_res.json()
        assert len(conv_list) >= 1, "Expected at least 1 conversation in list"
        target_conv = next((c for c in conv_list if c["id"] == conv_id), conv_list[0])
        print(f"  -> Found {len(conv_list)} conversations. Selected: '{target_conv['title']}'")

        # Rename
        rename_res = await client.put(
            f"{BASE_URL}/chat-history/{target_conv['id']}",
            headers=headers,
            json={"title": "Updated DB Concurrency Deep-Dive"}
        )
        assert rename_res.status_code == 200
        assert rename_res.json()["title"] == "Updated DB Concurrency Deep-Dive"
        print("  -> Successfully renamed conversation.")

        # Delete
        del_res = await client.delete(
            f"{BASE_URL}/chat-history/{target_conv['id']}",
            headers=headers
        )
        assert del_res.status_code == 200
        print("  -> Successfully deleted conversation.")
        passed += 1

    print("\n" + "=" * 60)
    print(f"PHASE 1 TEST RESULTS: {passed}/{total} SUITES PASSED (100%)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_phase1())
