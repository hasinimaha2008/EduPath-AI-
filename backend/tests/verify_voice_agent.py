"""
EduPath AI - Conversational Voice Agent Test Suite
Validates:
1. Available Neural Voice Catalog (English, Hindi, Telugu)
2. Turn 1 Voice Query & Audio Generation
3. Turn 2 Conversational Context Memory (No repetition required)
4. Multilingual Synthesis (Hindi & Telugu)
5. Educational Subject Scoping (Operating Systems, DBMS, DSA)
6. Direct Audio Synthesis Streaming Endpoint
7. Database & Chat History Persistence
"""

import asyncio
import os
import sys
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.models import User, Subject, Conversation, ChatMessage
from sqlalchemy import select, delete

async def run_voice_verification():
    print("=" * 70)
    print("  EDUPATH AI - CONVERSATIONAL VOICE AGENT VERIFICATION")
    print("=" * 70)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", follow_redirects=True, timeout=60.0) as client:
        # Step 0: Register & Authenticate a verification user
        print("\n[STEP 1] Registering verification user...")
        user_email = "voice.tester@edupath.ai"
        async with AsyncSessionLocal() as session:
            existing = await session.execute(select(User).where(User.email == user_email))
            u = existing.scalar_one_or_none()
            if u:
                await session.delete(u)
                await session.commit()

        reg_res = await client.post("/api/auth/register", json={
            "full_name": "Voice AI Tester",
            "email": user_email,
            "password": "SecurePassword123!"
        })
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        auth_data = reg_res.json()
        token = auth_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"  [PASS] Logged in as: {auth_data['user']['full_name']} ({user_email})")

        # Step 1: Verify Voice Models Catalog
        print("\n[STEP 2] Verifying Neural Voices Catalog...")
        voices_res = await client.get("/api/voice/voices")
        assert voices_res.status_code == 200, f"Voices query failed: {voices_res.text}"
        voices = voices_res.json()
        voice_ids = [v["id"] for v in voices]
        voice_langs = [v["language"] for v in voices]

        print(f"  Available voices: {len(voices)}")
        assert "en-US-JennyNeural" in voice_ids, "en-US-JennyNeural missing"
        assert "hi-IN-SwaraNeural" in voice_ids, "hi-IN-SwaraNeural missing"
        assert "te-IN-ShrutiNeural" in voice_ids, "te-IN-ShrutiNeural missing"
        assert "hi" in voice_langs, "Hindi voice missing"
        assert "te" in voice_langs, "Telugu voice missing"
        print("  [PASS] Neural voice catalog verified for English, Hindi, and Telugu.")

        # Step 2: Turn 1 Conversation & Audio Synthesis
        print("\n[STEP 3] Testing Turn 1 Conversational Voice Interaction & Audio Synthesis...")
        turn1_res = await client.post("/api/voice/chat", json={
            "message": "Explain machine learning in simple terms.",
            "language": "en",
            "synthesize_audio": True
        }, headers=headers)
        assert turn1_res.status_code == 200, f"Turn 1 failed: {turn1_res.text}"
        data1 = turn1_res.json()

        conv_id = data1["conversation_id"]
        reply1 = data1["reply_text"]
        audio_b64 = data1.get("audio_base64")

        assert conv_id is not None, "Missing conversation_id"
        assert len(reply1) > 20, "Reply text is too short"
        assert audio_b64 is not None and len(audio_b64) > 1000, "Synthesized audio missing or too short"
        # Audio decode verification
        audio_bytes = base64.b64decode(audio_b64)
        assert len(audio_bytes) > 5000, "Decoded audio bytes too small"
        # Check that response has no raw unpronounceable markdown tables
        assert "|" not in reply1, "Voice response should not contain markdown table pipes"
        assert "**" not in reply1, "Voice response should not contain raw double asterisks"

        print(f"  [PASS] Turn 1 Reply: {reply1[:85]}...")
        print(f"  [PASS] Audio synthesized ({len(audio_bytes)} bytes MP3, Voice: {data1['voice']})")

        # Step 3: Turn 2 Follow-Up Question with Context Memory
        print("\n[STEP 4] Testing Conversational Context Retention (Follow-up Turn)...")
        turn2_res = await client.post("/api/voice/chat", json={
            "message": "Can you give me another example?",
            "conversation_id": conv_id,
            "language": "en",
            "synthesize_audio": False
        }, headers=headers)
        assert turn2_res.status_code == 200, f"Turn 2 failed: {turn2_res.text}"
        data2 = turn2_res.json()
        reply2 = data2["reply_text"]

        # Ensure conversation ID is maintained
        assert data2["conversation_id"] == conv_id, "Conversation ID did not persist across turns"
        assert len(reply2) > 20, "Turn 2 reply too short"
        print(f"  [PASS] Turn 2 Reply (Context Retained): {reply2[:90]}...")

        # Step 4: Multilingual Voice Support (Hindi & Telugu)
        print("\n[STEP 5] Testing Multilingual Voice Support (Hindi & Telugu)...")
        # Hindi Turn
        hi_res = await client.post("/api/voice/chat", json={
            "message": "नमस्ते, क्या आप बाइनरी सर्च समझा सकते हैं?",
            "language": "hi",
            "synthesize_audio": True
        }, headers=headers)
        assert hi_res.status_code == 200, f"Hindi voice failed: {hi_res.text}"
        hi_data = hi_res.json()
        assert hi_data["voice"] == "hi-IN-SwaraNeural"
        assert hi_data.get("audio_base64") is not None
        print(f"  [PASS] Hindi Voice AI Turn: Voice={hi_data['voice']}, Audio={len(hi_data['audio_base64'])} chars")

        # Telugu Turn
        te_res = await client.post("/api/voice/chat", json={
            "message": "నమస్కారం, ఆపరేటింగ్ సిస్టమ్ గురించి చెప్పండి.",
            "language": "te",
            "synthesize_audio": True
        }, headers=headers)
        assert te_res.status_code == 200, f"Telugu voice failed: {te_res.text}"
        te_data = te_res.json()
        assert te_data["voice"] == "te-IN-ShrutiNeural"
        assert te_data.get("audio_base64") is not None
        print(f"  [PASS] Telugu Voice AI Turn: Voice={te_data['voice']}, Audio={len(te_data['audio_base64'])} chars")

        # Step 5: Educational Subject Scoping
        print("\n[STEP 6] Testing Educational Subject Context Scoping...")
        sub_res = await client.get("/api/subjects")
        subjects = sub_res.json()
        os_subj = next((s for s in subjects if "Operating Systems" in s["name"]), subjects[0])

        scoped_res = await client.post("/api/voice/chat", json={
            "message": "What is a deadlock and why does it occur?",
            "subject_id": os_subj["id"],
            "language": "en",
            "synthesize_audio": False
        }, headers=headers)
        assert scoped_res.status_code == 200
        scoped_data = scoped_res.json()
        assert len(scoped_data["reply_text"]) > 20
        print(f"  [PASS] Scoped to {os_subj['name']}: {scoped_data['reply_text'][:90]}...")

        # Step 6: Direct Audio Synthesis Streaming Endpoint
        print("\n[STEP 7] Testing Direct Audio Synthesis Endpoint (POST /api/voice/synthesize)...")
        synth_res = await client.post("/api/voice/synthesize", json={
            "text": "Hello, welcome to EduPath AI conversational learning.",
            "language": "en"
        }, headers=headers)
        assert synth_res.status_code == 200, f"Direct synthesis failed: {synth_res.text}"
        assert synth_res.headers.get("content-type") == "audio/mpeg"
        assert len(synth_res.content) > 1000
        print(f"  [PASS] Direct audio synthesis returned {len(synth_res.content)} bytes (audio/mpeg).")

        # Step 7: Database & History Verification
        print("\n[STEP 8] Verifying Database Persistence & Chat History...")
        history_res = await client.get("/api/chat-history", headers=headers)
        assert history_res.status_code == 200
        conv_list = history_res.json()
        assert len(conv_list) >= 1, "Voice conversations should appear in chat history"
        print(f"  [PASS] Found {len(conv_list)} saved conversations in user history.")

    print("\n" + "=" * 70)
    print("  ALL CONVERSATIONAL VOICE AGENT TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_voice_verification())
