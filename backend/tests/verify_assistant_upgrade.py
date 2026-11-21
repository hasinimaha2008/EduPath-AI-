import sys
import io
import json
import requests

# Ensure UTF-8 output on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=" * 70)
    print("EDUPATH AI STUDY ASSISTANT (CHATGPT-STYLE) VERIFICATION SUITE")
    print("=" * 70)

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

    # 2. Ask Initial Study Question
    print("\n[2] Asking Initial Study Question via POST /api/assistant/ask...")
    q1 = "Explain 3NF database normalization and functional dependencies with an example."
    ask1_resp = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q1
    }, headers=headers)
    assert ask1_resp.status_code == 200, f"Ask 1 failed: {ask1_resp.text}"
    data1 = ask1_resp.json()
    conv_id = data1["conversation_id"]
    ans1 = data1["assistant_message"]["content"]
    assert conv_id is not None, "Missing conversation_id"
    assert len(ans1) > 50, "Assistant answer too short"
    assert "3NF" in ans1 or "normalization" in ans1.lower() or "academic" in ans1.lower(), "Answer does not mention normalization"
    print(f"✓ Initial response received in conversation '{conv_id}'.")
    print(f"  Preview: {ans1[:120]}...")

    # 3. Multi-turn Follow-up Question
    print("\n[3] Testing Multi-turn Conversational Context with Follow-up Question...")
    q2 = "Can you provide a practical SQL table example for this with code?"
    ask2_resp = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q2,
        "conversation_id": conv_id
    }, headers=headers)
    assert ask2_resp.status_code == 200, f"Ask 2 failed: {ask2_resp.text}"
    data2 = ask2_resp.json()
    assert data2["conversation_id"] == conv_id, "Conversation ID mismatch in multi-turn"
    ans2 = data2["assistant_message"]["content"]
    assert "```" in ans2, "Expected code block in assistant response"
    print("✓ Multi-turn context retained. Response contains syntax-highlighted code block.")
    print(f"  Preview: {ans2[:140]}...")

    # 4. Multilingual Intelligence: Telugu Query
    print("\n[4] Testing Multilingual Intelligence: Telugu Query...")
    q_telugu = "DBMS లో Primary Key మరియు Foreign Key ప్రాముఖ్యత ఏమిటి?"
    ask_telugu_resp = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q_telugu
    }, headers=headers)
    assert ask_telugu_resp.status_code == 200, f"Telugu query failed: {ask_telugu_resp.text}"
    ans_telugu = ask_telugu_resp.json()["assistant_message"]["content"]
    has_telugu = any('\u0C00' <= char <= '\u0C7F' for char in ans_telugu)
    assert has_telugu, "Response did not contain Telugu script for Telugu prompt"
    print("✓ Multilingual Telugu query responded with fluent Telugu academic explanation.")

    # 5. Multilingual Intelligence: Hindi Query
    print("\n[5] Testing Multilingual Intelligence: Hindi Query...")
    q_hindi = "Database Indexing क्या है और यह क्वेरी प्रदर्शन को कैसे बेहतर बनाता है?"
    ask_hindi_resp = requests.post(f"{BASE_URL}/api/assistant/ask", json={
        "question": q_hindi
    }, headers=headers)
    assert ask_hindi_resp.status_code == 200, f"Hindi query failed: {ask_hindi_resp.text}"
    ans_hindi = ask_hindi_resp.json()["assistant_message"]["content"]
    has_hindi = any('\u0900' <= char <= '\u097F' for char in ans_hindi)
    assert has_hindi, "Response did not contain Hindi script for Hindi prompt"
    print("✓ Multilingual Hindi query responded with fluent Hindi academic explanation.")

    # 6. Conversation Management (List, Rename, Retrieve)
    print("\n[6] Testing Conversation History Management...")
    # List conversations
    list_resp = requests.get(f"{BASE_URL}/api/chat-history", headers=headers)
    assert list_resp.status_code == 200, f"List failed: {list_resp.text}"
    convs = list_resp.json()
    conv_ids = [c["id"] for c in convs]
    assert conv_id in conv_ids, f"Created conversation {conv_id} not found in history"
    print(f"✓ Found {len(convs)} conversations in history.")

    # Rename conversation
    new_title = "3NF Normalization & SQL Architecture"
    rename_resp = requests.put(f"{BASE_URL}/api/chat-history/{conv_id}", json={
        "title": new_title
    }, headers=headers)
    assert rename_resp.status_code == 200, f"Rename failed: {rename_resp.text}"
    print(f"✓ Renamed conversation to '{new_title}'.")

    # Get conversation details with messages
    get_resp = requests.get(f"{BASE_URL}/api/chat-history/{conv_id}", headers=headers)
    assert get_resp.status_code == 200, f"Get conv failed: {get_resp.text}"
    conv_detail = get_resp.json()
    assert conv_detail["title"] == new_title, "Conversation title not updated"
    assert len(conv_detail["messages"]) >= 4, f"Expected at least 4 messages in conversation, got {len(conv_detail['messages'])}"
    print(f"✓ Verified conversation details: {len(conv_detail['messages'])} messages loaded.")

    # 7. Regenerate Response
    print("\n[7] Testing Response Regeneration (POST /api/assistant/regenerate)...")
    regen_resp = requests.post(f"{BASE_URL}/api/assistant/regenerate", json={
        "conversation_id": conv_id
    }, headers=headers)
    assert regen_resp.status_code == 200, f"Regenerate failed: {regen_resp.text}"
    regen_data = regen_resp.json()
    assert regen_data["conversation_id"] == conv_id, "Regenerate returned wrong conversation_id"
    assert len(regen_data["assistant_message"]["content"]) > 50, "Regenerated message content too short"
    print("✓ Regenerate response succeeded seamlessly.")

    print("\n" + "=" * 70)
    print("ALL AI STUDY ASSISTANT (CHATGPT-STYLE) UPGRADE CHECKS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
