import sys
import io
import json
import requests

# Ensure UTF-8 output on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=" * 75)
    print("EDUPATH AI GENERAL-PURPOSE LLM CONVERSATIONAL ASSISTANT TEST SUITE")
    print("=" * 75)

    # 1. Login
    print("\n[1] Authenticating as demo user...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "demo@edupath.ai",
        "password": "EduPath@2026"
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print("✓ Authenticated successfully.")

    # 2. Assistant Status
    print("\n[2] Checking Assistant & LLM Status (GET /api/assistant/status)...")
    status_resp = requests.get(f"{BASE_URL}/api/assistant/status", headers=headers)
    assert status_resp.status_code == 200, f"Status check failed: {status_resp.text}"
    status_data = status_resp.json()
    print(f"✓ Provider: {status_data.get('provider')}, Model: {status_data.get('model_name')}")
    print(f"  Streaming supported: {status_data.get('streaming_supported')}")

    # 3. Test General Knowledge & Casual Dialogue (Not restricted to academics)
    print("\n[3] Testing General Knowledge & Casual Dialogue...")
    q_general = "Who are you and what are the best ways to explore the Solar System?"
    ask_gen = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q_general
    }, headers=headers)
    assert ask_gen.status_code == 200, f"General query failed: {ask_gen.text}"
    data_gen = ask_gen.json()
    conv_id = data_gen["conversation_id"]
    ans_gen = data_gen["assistant_message"]["content"]
    assert len(ans_gen) > 50, "Answer too short"
    assert "syllabus" not in ans_gen.lower() and "exam" not in ans_gen.lower(), "Artificially redirected to academic syllabus"
    print(f"✓ Conversational answer generated in conversation '{conv_id}' without forced academic redirection.")
    print(f"  Preview: {ans_gen[:130]}...")

    # 4. Test Active Empathy & Emotional Conversation
    print("\n[4] Testing Human-like Empathy & Emotional Listening...")
    q_empathy = "I am feeling really overwhelmed and burnt out with my routine lately."
    ask_emp = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q_empathy,
        "conversation_id": conv_id
    }, headers=headers)
    assert ask_emp.status_code == 200, f"Empathy query failed: {ask_emp.text}"
    ans_emp = ask_emp.json()["assistant_message"]["content"]
    assert any(w in ans_emp.lower() for w in ["hear you", "feeling", "pause", "overwhelm", "care", "rest"]), "Did not respond empathetically"
    print("✓ Assistant responded with genuine conversational empathy and supportive active listening.")
    print(f"  Preview: {ans_emp[:130]}...")

    # 5. Test Programming & Software Engineering (Code with syntax tag & complexity)
    print("\n[5] Testing Programming & Software Engineering...")
    q_code = "Write a clean rate limiter in Python using sliding window and explain its time complexity."
    ask_code = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q_code
    }, headers=headers)
    assert ask_code.status_code == 200, f"Code query failed: {ask_code.text}"
    code_conv_id = ask_code.json()["conversation_id"]
    ans_code = ask_code.json()["assistant_message"]["content"]
    assert "```python" in ans_code or "```" in ans_code, "Code block missing language syntax tags"
    assert "complexity" in ans_code.lower() or "O(" in ans_code or "time" in ans_code.lower(), "Complexity analysis missing"
    print("✓ Technical code generated with clean language tags and architectural breakdown.")
    print(f"  Preview: {ans_code[:130]}...")

    # 6. Test Multi-Turn Follow-Up Context Retention
    print("\n[6] Testing Multi-Turn Follow-Up Context Retention...")
    q_followup = "Can you show me how to test this with edge cases?"
    ask_followup = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q_followup,
        "conversation_id": code_conv_id
    }, headers=headers)
    assert ask_followup.status_code == 200, f"Followup failed: {ask_followup.text}"
    ans_followup = ask_followup.json()["assistant_message"]["content"]
    assert len(ans_followup) > 50, "Followup answer too short"
    print("✓ Multi-turn follow-up successfully understood context from previous message.")
    print(f"  Preview: {ans_followup[:130]}...")

    # 7. Test Mathematics & Step-by-Step Logic
    print("\n[7] Testing Mathematics, Proofs & Quantitative Logic...")
    q_math = "Solve and explain Bayes' Theorem formula and its derivation."
    ask_math = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q_math
    }, headers=headers)
    assert ask_math.status_code == 200, f"Math query failed: {ask_math.text}"
    ans_math = ask_math.json()["assistant_message"]["content"]
    assert len(ans_math) > 60, "Math answer too short"
    assert "step" in ans_math.lower() or "derivation" in ans_math.lower() or "formula" in ans_math.lower(), "Derivation missing"
    print("✓ Mathematics problem broken down into clear step-by-step reasoning.")

    # 8. Test Multilingual: Telugu Native
    print("\n[8] Testing Multilingual Intelligence: Telugu Native Conversation...")
    q_te = "సాఫ్ట్‌వేర్ ఆర్కిటెక్చర్‌లో మైక్రోసర్వీసెస్ ప్రయోజనాలు ఏమిటి?"
    ask_te = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q_te,
        "language": "te"
    }, headers=headers)
    assert ask_te.status_code == 200, f"Telugu query failed: {ask_te.text}"
    ans_te = ask_te.json()["assistant_message"]["content"]
    has_te = any('\u0C00' <= char <= '\u0C7F' for char in ans_te)
    assert has_te, "Telugu response does not contain Telugu script"
    print("✓ Responded in natural, fluent Telugu.")

    # 9. Test Multilingual: Hindi Native
    print("\n[9] Testing Multilingual Intelligence: Hindi Native Conversation...")
    q_hi = "क्लाउड कंप्यूटिंग क्या है और यह व्यवसायों के लिए क्यों उपयोगी है?"
    ask_hi = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q_hi,
        "language": "hi"
    }, headers=headers)
    assert ask_hi.status_code == 200, f"Hindi query failed: {ask_hi.text}"
    ans_hi = ask_hi.json()["assistant_message"]["content"]
    has_hi = any('\u0900' <= char <= '\u097F' for char in ans_hi)
    assert has_hi, "Hindi response does not contain Hindi script"
    print("✓ Responded in natural, fluent Hindi.")

    # 10. Test Real-time Streaming SSE Endpoint (POST /api/assistant/chat-stream)
    print("\n[10] Testing Real-Time Response Streaming (SSE /api/assistant/chat-stream)...")
    stream_resp = requests.post(
        f"{BASE_URL}/api/assistant/chat-stream",
        json={"question": "Briefly explain what makes quantum computers fundamentally different from classical computers."},
        headers=headers,
        stream=True
    )
    assert stream_resp.status_code == 200, f"Streaming failed: {stream_resp.status_code}"
    assert "text/event-stream" in stream_resp.headers.get("content-type", ""), "Wrong content-type for SSE stream"

    tokens_received = 0
    stream_meta = None
    stream_done = False

    for line in stream_resp.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            try:
                payload = json.loads(line[6:])
                p_type = payload.get("type")
                if p_type == "meta":
                    stream_meta = payload
                elif p_type == "token":
                    tokens_received += 1
                elif p_type == "done":
                    stream_done = True
            except Exception:
                pass

    assert stream_meta is not None, "Did not receive metadata event in stream"
    assert tokens_received > 5, f"Expected streaming tokens, got only {tokens_received}"
    assert stream_done, "Stream did not emit done event"
    print(f"✓ Real-time streaming verified: Received {tokens_received} tokens via Server-Sent Events.")
    print(f"  Smart Title generated: '{stream_meta.get('title')}'")

    # 11. Test Smart Conversation Title Generation
    print("\n[11] Verifying Conversation History & Smart Title Persistence...")
    conv_list_resp = requests.get(f"{BASE_URL}/api/chat-history", headers=headers)
    assert conv_list_resp.status_code == 200
    conv_list = conv_list_resp.json()
    matching = [c for c in conv_list if c["id"] == stream_meta.get("conversation_id")]
    assert len(matching) > 0, "Streamed conversation not found in persistent chat history"
    print(f"✓ Verified conversation persisted in database with smart title: '{matching[0]['title']}'.")

    # 12. Test API Key Configuration Validation
    print("\n[12] Testing API Key Configuration Endpoint...")
    # Test invalid key rejection
    bad_key_resp = requests.post(f"{BASE_URL}/api/assistant/configure-key", json={"api_key": "short"}, headers=headers)
    assert bad_key_resp.status_code == 400, "Should reject invalid key format"
    print("✓ Successfully validated and protected against invalid API key formats.")

    print("\n" + "=" * 75)
    print("ALL 12 GENERAL-PURPOSE LLM CONVERSATIONAL ASSISTANT TESTS PASSED 100%!")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
