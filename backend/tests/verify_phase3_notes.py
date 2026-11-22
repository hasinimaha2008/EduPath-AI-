import asyncio
import os
import sys
import tempfile
import httpx
import docx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

def create_sample_docx(file_path: str):
    doc = docx.Document()
    doc.add_heading("Computer Networks: Transport Layer Protocols", level=1)
    doc.add_paragraph(
        "The Transport Layer provides logical communication between application processes running on different hosts. "
        "The two primary transport layer protocols in the Internet protocol suite are TCP (Transmission Control Protocol) "
        "and UDP (User Datagram Protocol)."
    )
    doc.add_heading("Transmission Control Protocol (TCP)", level=2)
    doc.add_paragraph(
        "TCP is connection-oriented, reliable, and provides in-order byte stream delivery. "
        "It uses a 3-way handshake (SYN, SYN-ACK, ACK) for connection establishment and a 4-way handshake for termination. "
        "Key mechanisms include flow control via sliding window and congestion control via Slow Start, Congestion Avoidance, "
        "Fast Retransmit, and Fast Recovery."
    )
    doc.add_heading("User Datagram Protocol (UDP)", level=2)
    doc.add_paragraph(
        "UDP is connectionless, lightweight, and provides best-effort datagram delivery with no guaranteed ordering or reliability. "
        "It is widely used for DNS queries, video streaming (RTP), and online gaming where low latency is critical."
    )
    doc.save(file_path)

async def test_phase3_smart_notes():
    print("=" * 70)
    print("Starting Comprehensive Phase 3: Smart Notes Generator Verification")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=90.0) as client:
        # 0. Authenticate
        print("\n[Step 0] Authenticating demo user...")
        login_res = await client.post(f"{BASE_URL}/auth/demo-login")
        if login_res.status_code != 200:
            print(f"Demo login failed ({login_res.status_code}): {login_res.text}")
            sys.exit(1)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  -> Authenticated successfully.")

        # Get subjects
        subj_res = await client.get(f"{BASE_URL}/subjects", headers=headers)
        subjects = subj_res.json() if subj_res.status_code == 200 else []
        subject_id = subjects[0]["id"] if subjects else None
        print(f"  -> Context subject: {subjects[0]['name'] if subjects else 'None'}")

        created_note_ids = []

        # Test 1: Short Notes from Topic
        print("\n[Test 1] Generating Short Notes from Topic...")
        res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "topic_name": "Graph Traversal Algorithms: BFS and DFS",
                "note_type": "short",
                "explanation_style": "point_wise",
                "language": "en"
            }
        )
        assert res.status_code == 200, f"Short notes generation failed: {res.text}"
        data = res.json()
        assert data["note_type"] == "short"
        assert len(data["content_markdown"]) > 100
        created_note_ids.append(data["id"])
        print(f"  -> Success: Generated short note '{data['title']}' ({len(data['content_markdown'])} chars)")

        # Test 2: Detailed Notes with Technical Rigor & Formulas
        print("\n[Test 2] Generating Detailed Technical Notes with Formulas...")
        res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "topic_name": "Asymptotic Notation and Master Theorem",
                "note_type": "detailed",
                "explanation_style": "technical",
                "subject_id": subject_id,
                "language": "en"
            }
        )
        assert res.status_code == 200, f"Detailed notes generation failed: {res.text}"
        data = res.json()
        assert data["note_type"] == "detailed"
        assert "Master Theorem" in data["title"] or "Asymptotic" in data["title"] or len(data["content_markdown"]) > 200
        created_note_ids.append(data["id"])
        print(f"  -> Success: Generated detailed technical note '{data['title']}' ({len(data['content_markdown'])} chars)")

        # Test 3: Exam-Oriented Notes with Unit Name
        print("\n[Test 3] Generating Exam-Oriented Notes with Unit Name...")
        res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "topic_name": "Dynamic Programming: Longest Common Subsequence",
                "note_type": "exam_oriented",
                "unit_name": "Unit 4: Advanced Algorithm Design",
                "subject_id": subject_id,
                "language": "en"
            }
        )
        assert res.status_code == 200, f"Exam-oriented notes generation failed: {res.text}"
        data = res.json()
        assert data["note_type"] == "exam_oriented"
        created_note_ids.append(data["id"])
        print(f"  -> Success: Generated exam-oriented note with unit specification '{data['title']}'")

        # Test 4: Comparison Table Note
        print("\n[Test 4] Generating Comparison Tables Note...")
        res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "topic_name": "SQL Relational vs NoSQL Document Databases",
                "note_type": "comparison",
                "explanation_style": "standard",
                "language": "en"
            }
        )
        assert res.status_code == 200, f"Comparison note generation failed: {res.text}"
        data = res.json()
        assert data["note_type"] == "comparison"
        assert "|" in data["content_markdown"], "Comparison notes must contain Markdown tables"
        created_note_ids.append(data["id"])
        print(f"  -> Success: Generated comparison table note '{data['title']}' with structured Markdown table")

        # Test 5: Definitions and Formulas Note
        print("\n[Test 5] Generating Definitions & Formulas Note...")
        res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "topic_name": "Information Theory and Shannon Entropy",
                "note_type": "definitions",
                "language": "en"
            }
        )
        assert res.status_code == 200, f"Definitions note generation failed: {res.text}"
        data = res.json()
        assert data["note_type"] == "definitions"
        created_note_ids.append(data["id"])
        print(f"  -> Success: Generated definitions and formulas note '{data['title']}'")

        # Test 6: Last-Minute Revision Note
        print("\n[Test 6] Generating Last-Minute High-Yield Flash Notes...")
        res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "topic_name": "CPU Scheduling Algorithms: FCFS, SJF, Round Robin",
                "note_type": "last_minute",
                "explanation_style": "point_wise",
                "language": "en"
            }
        )
        assert res.status_code == 200, f"Last minute notes generation failed: {res.text}"
        data = res.json()
        assert data["note_type"] == "last_minute"
        created_note_ids.append(data["id"])
        print(f"  -> Success: Generated last-minute revision note '{data['title']}'")

        # Test 7: Multilingual Generation - Telugu (తెలుగు)
        print("\n[Test 7] Multilingual Generation: Telugu (te)...")
        res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "topic_name": "Binary Search Trees",
                "note_type": "short",
                "language": "te"
            }
        )
        assert res.status_code == 200, f"Telugu notes generation failed: {res.text}"
        data = res.json()
        # Verify Telugu Unicode block (\u0C00 - \u0C7F)
        telugu_chars = [c for c in data["content_markdown"] if "\u0c00" <= c <= "\u0c7f"]
        assert len(telugu_chars) > 20, f"Telugu characters not found in response: {data['content_markdown'][:200]}"
        created_note_ids.append(data["id"])
        print(f"  -> Success: Generated fluent Telugu notes with {len(telugu_chars)} Telugu Unicode characters")

        # Test 8: Multilingual Generation - Hindi (हिन्दी)
        print("\n[Test 8] Multilingual Generation: Hindi (hi)...")
        res = await client.post(
            f"{BASE_URL}/notes/generate",
            headers=headers,
            json={
                "topic_name": "Object Oriented Programming Principles",
                "note_type": "short",
                "language": "hi"
            }
        )
        assert res.status_code == 200, f"Hindi notes generation failed: {res.text}"
        data = res.json()
        # Verify Devanagari Hindi Unicode block (\u0900 - \u097F)
        hindi_chars = [c for c in data["content_markdown"] if "\u0900" <= c <= "\u097f"]
        assert len(hindi_chars) > 20, f"Hindi characters not found in response: {data['content_markdown'][:200]}"
        created_note_ids.append(data["id"])
        print(f"  -> Success: Generated fluent Hindi notes with {len(hindi_chars)} Hindi Unicode characters")

        # Test 9: Notes from Uploaded Document
        print("\n[Test 9] Generating Notes from Uploaded DOCX Document...")
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tf:
            temp_path = tf.name
        try:
            create_sample_docx(temp_path)
            with open(temp_path, "rb") as f:
                upload_res = await client.post(
                    f"{BASE_URL}/documents/upload",
                    headers=headers,
                    files={"file": ("Transport_Protocols.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                )
            assert upload_res.status_code == 200, f"Document upload failed: {upload_res.text}"
            doc_data = upload_res.json()
            doc_id = doc_data["id"]
            print(f"  -> Uploaded test document {doc_id} ('{doc_data['title']}')")

            # Generate notes grounded in this document
            note_res = await client.post(
                f"{BASE_URL}/notes/generate",
                headers=headers,
                json={
                    "document_id": doc_id,
                    "note_type": "detailed",
                    "explanation_style": "standard",
                    "language": "en"
                }
            )
            assert note_res.status_code == 200, f"Doc-grounded note generation failed: {note_res.text}"
            doc_note = note_res.json()
            assert doc_note["document_id"] == doc_id
            assert "TCP" in doc_note["content_markdown"] or "Transport" in doc_note["content_markdown"] or "UDP" in doc_note["content_markdown"]
            created_note_ids.append(doc_note["id"])
            print(f"  -> Success: Generated document-grounded notes for '{doc_data['title']}'")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Test 10: Filtering and Keyword Search
        print("\n[Test 10] Testing Filter by note_type and Keyword Search...")
        comp_filter_res = await client.get(f"{BASE_URL}/notes?note_type=comparison", headers=headers)
        assert comp_filter_res.status_code == 200
        comp_notes = comp_filter_res.json()
        assert all(n["note_type"] == "comparison" for n in comp_notes), "Filter by note_type failed"
        print(f"  -> Filter by note_type=comparison returned {len(comp_notes)} notes")

        search_res = await client.get(f"{BASE_URL}/notes?search=Dynamic", headers=headers)
        assert search_res.status_code == 200
        search_notes = search_res.json()
        assert len(search_notes) >= 1
        assert any("Dynamic" in n["title"] or "Dynamic" in n["content_markdown"] for n in search_notes)
        print(f"  -> Keyword search for 'Dynamic' returned {len(search_notes)} matching notes")

        # Test 11: Edit and Pin Note
        target_note_id = created_note_ids[0]
        print(f"\n[Test 11] Testing Edit & Pin on note {target_note_id}...")
        edit_res = await client.put(
            f"{BASE_URL}/notes/{target_note_id}",
            headers=headers,
            json={
                "title": "UPDATED: Graph Traversal & Topological Ordering",
                "is_pinned": True,
                "content_markdown": "# Graph Traversal Algorithms\n\n- **BFS**: Queue-based Level-order\n- **DFS**: Stack-based Depth exploration"
            }
        )
        assert edit_res.status_code == 200, f"Update note failed: {edit_res.text}"
        updated_data = edit_res.json()
        assert updated_data["title"] == "UPDATED: Graph Traversal & Topological Ordering"
        assert updated_data["is_pinned"] is True
        print("  -> Success: Note edited and pinned to top successfully.")

        # Test 12: Delete Note
        delete_target_id = created_note_ids.pop()
        print(f"\n[Test 12] Testing Delete on note {delete_target_id}...")
        del_res = await client.delete(f"{BASE_URL}/notes/{delete_target_id}", headers=headers)
        assert del_res.status_code == 200, f"Delete note failed: {del_res.text}"
        print("  -> Success: Note deleted cleanly.")

    print("\n" + "=" * 70)
    print("ALL 12 PHASE 3 SMART NOTES TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_phase3_smart_notes())
