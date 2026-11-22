import asyncio
import io
import os
import sys
import tempfile
import httpx
import docx
from pptx import Presentation

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000/api"

def create_sample_docx(file_path: str):
    doc = docx.Document()
    doc.add_heading("Advanced Database Systems: Concurrency & Recovery", level=1)
    doc.add_paragraph(
        "Concurrency control in database management systems ensures that multiple transactions can execute concurrently "
        "without violating the ACID properties: Atomicity, Consistency, Isolation, and Durability."
    )
    doc.add_heading("Two-Phase Locking (2PL)", level=2)
    doc.add_paragraph(
        "Two-Phase Locking (2PL) is a concurrency control protocol that guarantees serializability. "
        "It consists of two phases: the Growing Phase, during which a transaction may obtain locks but not release any locks, "
        "and the Shrinking Phase, during which a transaction may release locks but not obtain any new locks. "
        "Strict 2PL further avoids cascading aborts by holding all exclusive locks until commit time."
    )
    doc.add_heading("Write-Ahead Logging (WAL)", level=2)
    doc.add_paragraph(
        "Write-Ahead Logging dictates that any modification to a database page must be recorded in stable storage log records "
        "before the corresponding page is flushed to disk. The ARIES recovery algorithm uses analysis, redo, and undo phases."
    )
    doc.save(file_path)

def create_sample_pptx(file_path: str):
    prs = Presentation()
    # Slide 1
    slide1 = prs.slides.add_slide(prs.slide_layouts[0])
    slide1.shapes.title.text = "Computer Architecture: Cache Memory Hierarchy"
    slide1.placeholders[1].text = "L1, L2, and L3 cache organizations and cache coherence protocols."

    # Slide 2
    slide2 = prs.slides.add_slide(prs.slide_layouts[1])
    slide2.shapes.title.text = "MESI Cache Coherence Protocol"
    slide2.placeholders[1].text = (
        "The MESI protocol defines four cache line states:\n"
        "- Modified (M): Cache line is valid, exclusive to this cache, and dirty.\n"
        "- Exclusive (E): Cache line is clean and present ONLY in this cache.\n"
        "- Shared (S): Cache line is clean and may be present in other caches.\n"
        "- Invalid (I): Cache line does not contain valid data."
    )

    # Slide 3
    slide3 = prs.slides.add_slide(prs.slide_layouts[1])
    slide3.shapes.title.text = "Amdahl's Law and Multi-Core Scaling"
    slide3.placeholders[1].text = (
        "Amdahl's Law defines theoretical speedup: Speedup = 1 / ((1 - p) + (p / s)).\n"
        "Even with infinite processors, speedup is bounded by the sequential execution fraction (1 - p)."
    )
    prs.save(file_path)

def create_sample_txt(file_path: str):
    content = """# Operating Systems: Process Scheduling and Virtual Memory

## 1. Process Scheduling Algorithms
In modern multiprogrammed operating systems, the CPU scheduler selects from among the processes in memory that are ready to execute.
Common algorithms include:
- First-Come, First-Served (FCFS): Simple FIFO queue, non-preemptive, suffers from the convoy effect.
- Shortest-Job-First (SJF): Provably optimal average waiting time for given burst lengths.
- Round Robin (RR): Preemptive scheduling using a fixed time quantum. If the quantum is too large, it degrades to FCFS; if too small, context-switch overhead dominates.

## 2. Virtual Memory & Paging
Virtual memory separates user logical memory from physical memory.
Paging divides logical memory into fixed-size blocks called pages, and physical memory into frames.
Address translation is facilitated by the Translation Lookaside Buffer (TLB), an associative cache.
Page faults occur when a referenced page is not resident in physical RAM.
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

async def test_phase2():
    print("=" * 65)
    print("EDUPATH AI - PHASE 2: ADVANCED DOCUMENT INTELLIGENCE VERIFICATION")
    print("=" * 65)

    passed = 0
    total = 0

    async with httpx.AsyncClient(timeout=45.0) as client:
        # Step 1: Authenticate Demo User
        total += 1
        print("\n[TEST 1] Authenticating Demo User...")
        login_res = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "demo@edupath.ai", "password": "EduPath@2026"}
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("  ✓ Authenticated as demo@edupath.ai")
        passed += 1

        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = os.path.join(tmpdir, "database_concurrency.docx")
            pptx_path = os.path.join(tmpdir, "cache_architecture.pptx")
            txt_path = os.path.join(tmpdir, "os_scheduling.txt")

            create_sample_docx(docx_path)
            create_sample_pptx(pptx_path)
            create_sample_txt(txt_path)

            # Step 2: Validate Unsupported Formats Rejected
            total += 1
            print("\n[TEST 2] Testing File Format Validation (Reject unsupported extensions)...")
            fake_file = io.BytesIO(b"malicious script")
            unsupported_res = await client.post(
                f"{BASE_URL}/documents/upload",
                headers=headers,
                files={"file": ("malicious.exe", fake_file, "application/octet-stream")},
                data={"title": "Malicious Test"}
            )
            assert unsupported_res.status_code == 400, "Should reject .exe file"
            print("  ✓ Unsupported file extension (.exe) rejected with HTTP 400.")
            passed += 1

            # Step 3: Test Upload & Extraction of DOCX
            total += 1
            print("\n[TEST 3] Uploading & Processing Word Document (.docx)...")
            with open(docx_path, "rb") as f:
                docx_res = await client.post(
                    f"{BASE_URL}/documents/upload",
                    headers=headers,
                    files={"file": ("database_concurrency.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                    data={"title": "Database Concurrency & 2PL"}
                )
            assert docx_res.status_code == 200, f"DOCX upload failed: {docx_res.text}"
            docx_data = docx_res.json()
            docx_id = docx_data["id"]
            assert docx_data["file_type"] == "docx"
            assert docx_data["status"] == "ready"
            assert docx_data["chunk_count"] > 0
            print(f"  ✓ DOCX uploaded, parsed, and indexed: {docx_data['chunk_count']} chunks.")
            passed += 1

            # Step 4: Test Upload & Extraction of PPTX
            total += 1
            print("\n[TEST 4] Uploading & Processing PowerPoint Presentation (.pptx)...")
            with open(pptx_path, "rb") as f:
                pptx_res = await client.post(
                    f"{BASE_URL}/documents/upload",
                    headers=headers,
                    files={"file": ("cache_architecture.pptx", f, "application/vnd.openxmlformats-officedocument.presentationml.presentation")},
                    data={"title": "Cache Architecture & MESI"}
                )
            assert pptx_res.status_code == 200, f"PPTX upload failed: {pptx_res.text}"
            pptx_data = pptx_res.json()
            pptx_id = pptx_data["id"]
            assert pptx_data["file_type"] == "pptx"
            assert pptx_data["status"] == "ready"
            assert pptx_data["chunk_count"] > 0
            print(f"  ✓ PPTX uploaded, slide texts parsed, and indexed: {pptx_data['chunk_count']} chunks.")
            passed += 1

            # Step 5: Test Upload & Extraction of TXT
            total += 1
            print("\n[TEST 5] Uploading & Processing Text Document (.txt)...")
            with open(txt_path, "rb") as f:
                txt_res = await client.post(
                    f"{BASE_URL}/documents/upload",
                    headers=headers,
                    files={"file": ("os_scheduling.txt", f, "text/plain")},
                    data={"title": "Operating Systems Virtual Memory"}
                )
            assert txt_res.status_code == 200, f"TXT upload failed: {txt_res.text}"
            txt_data = txt_res.json()
            txt_id = txt_data["id"]
            assert txt_data["file_type"] == "txt"
            assert txt_data["status"] == "ready"
            assert txt_data["chunk_count"] > 0
            print(f"  ✓ TXT uploaded, pages chunked, and indexed: {txt_data['chunk_count']} chunks.")
            passed += 1

            # Step 6: Test Document Preview API
            total += 1
            print("\n[TEST 6] Testing Document Preview & Extraction Inspection (GET /preview)...")
            prev_res = await client.get(f"{BASE_URL}/documents/{pptx_id}/preview", headers=headers)
            assert prev_res.status_code == 200, f"Preview failed: {prev_res.text}"
            prev_data = prev_res.json()
            assert prev_data["total_pages"] >= 3
            assert prev_data["total_chunks"] >= 1
            assert len(prev_data["sample_chunks"]) > 0
            print(f"  ✓ Preview verified: {prev_data['total_pages']} slides/pages, {prev_data['total_words']} words.")
            passed += 1

            # Step 7: Test Document Executive Summary
            total += 1
            print("\n[TEST 7] Testing Document Summarization (GET /summary)...")
            sum_res = await client.get(f"{BASE_URL}/documents/{docx_id}/summary", headers=headers)
            assert sum_res.status_code == 200, f"Summary failed: {sum_res.text}"
            sum_data = sum_res.json()
            assert "executive_summary" in sum_data
            assert len(sum_data.get("key_takeaways", [])) > 0
            print(f"  ✓ Executive summary generated: {sum_data['executive_summary'][:100]}...")
            passed += 1

            # Step 8: Test Detailed Study Notes Generation
            total += 1
            print("\n[TEST 8] Testing Detailed Study Notes Generation (GET /notes)...")
            notes_res = await client.get(f"{BASE_URL}/documents/{docx_id}/notes", headers=headers)
            assert notes_res.status_code == 200, f"Notes failed: {notes_res.text}"
            notes_data = notes_res.json()
            assert "modules" in notes_data
            assert len(notes_data["modules"]) > 0
            print(f"  ✓ Generated {len(notes_data['modules'])} study note modules with citations.")
            passed += 1

            # Step 9: Test Exam-Oriented Q&A Preparation
            total += 1
            print("\n[TEST 9] Testing Exam-Oriented Answers & Scoring Rubrics (GET /exam-prep)...")
            exam_res = await client.get(f"{BASE_URL}/documents/{docx_id}/exam-prep", headers=headers)
            assert exam_res.status_code == 200, f"Exam prep failed: {exam_res.text}"
            exam_data = exam_res.json()
            assert "exam_questions" in exam_data
            assert len(exam_data["exam_questions"]) > 0
            print(f"  ✓ Generated {len(exam_data['exam_questions'])} high-yield exam questions with model answers.")
            passed += 1

            # Step 10: Test Grounded Document Q&A with Page Citations
            total += 1
            print("\n[TEST 10] Testing Grounded Document Q&A with Page Citations (POST /ask)...")
            ask_res = await client.post(
                f"{BASE_URL}/documents/{pptx_id}/ask",
                headers=headers,
                json={"question": "What does the Exclusive state mean in MESI?"}
            )
            assert ask_res.status_code == 200, f"Ask failed: {ask_res.text}"
            ask_data = ask_res.json()
            assert ask_data["found_in_document"] is True
            assert len(ask_data["citations"]) > 0
            assert "page_number" in ask_data["citations"][0]
            assert "Page" in ask_data["answer"] or "page" in str(ask_data["citations"])
            print(f"  ✓ Grounded answer verified with page references: {ask_data['answer'][:110]}...")
            passed += 1

            # Step 11: Accuracy Enforcement: Rejecting / Alerting Unrelated Questions
            total += 1
            print("\n[TEST 11] Verifying Accuracy & Non-Hallucination on Irrelevant Query...")
            unrelated_res = await client.post(
                f"{BASE_URL}/documents/{pptx_id}/ask",
                headers=headers,
                json={"question": "How do you bake a sourdough bread with wild yeast?"}
            )
            assert unrelated_res.status_code == 200
            unrelated_data = unrelated_res.json()
            assert unrelated_data["found_in_document"] is False
            assert "does not contain" in unrelated_data["answer"].lower()
            print("  ✓ Correctly identified that document does not contain sourdough information. No hallucination.")
            passed += 1

            # Step 12: Test MCQs and Self-Assessment Generation
            total += 1
            print("\n[TEST 12] Testing MCQs and Self-Assessment Generation (POST /generate-questions)...")
            quiz_res = await client.post(
                f"{BASE_URL}/documents/{txt_id}/generate-questions?count=3",
                headers=headers
            )
            assert quiz_res.status_code == 200, f"Quiz generation failed: {quiz_res.text}"
            quiz_data = quiz_res.json()
            assert len(quiz_data) >= 1
            print(f"  ✓ Generated {len(quiz_data)} self-assessment practice questions.")
            passed += 1

            # Step 13: Test Extraction of Definitions & Formulas
            total += 1
            print("\n[TEST 13] Testing Definitions & Formulas Extraction (GET /definitions-formulas)...")
            form_res = await client.get(f"{BASE_URL}/documents/{pptx_id}/definitions-formulas", headers=headers)
            assert form_res.status_code == 200, f"Formulas failed: {form_res.text}"
            form_data = form_res.json()
            assert "definitions" in form_data
            assert "formulas" in form_data
            print(f"  ✓ Extracted {len(form_data['definitions'])} definitions and {len(form_data['formulas'])} formulas.")
            passed += 1

            # Step 14: Test Important Topics Identification
            total += 1
            print("\n[TEST 14] Testing Important Topics Identification (GET /important-topics)...")
            top_res = await client.get(f"{BASE_URL}/documents/{docx_id}/important-topics", headers=headers)
            assert top_res.status_code == 200, f"Topics failed: {top_res.text}"
            top_data = top_res.json()
            assert len(top_data) > 0
            print(f"  ✓ Identified {len(top_data)} high-yield core topics with exam weightage.")
            passed += 1

            # Step 15: Test Revision Materials Kit
            total += 1
            print("\n[TEST 15] Testing Quick Revision Materials Kit (GET /revision-kit)...")
            rev_res = await client.get(f"{BASE_URL}/documents/{txt_id}/revision-kit", headers=headers)
            assert rev_res.status_code == 200, f"Revision kit failed: {rev_res.text}"
            rev_data = rev_res.json()
            assert "cheat_sheet" in rev_data
            assert "flashcards" in rev_data
            print(f"  ✓ Generated revision cheat sheet and {len(rev_data['flashcards'])} flashcards.")
            passed += 1

            # Step 16: Test Difficult Topic Deep-Dive Explanation
            total += 1
            print("\n[TEST 16] Testing Difficult Topic Deep-Dive Explanation (POST /explain-topic)...")
            exp_res = await client.post(
                f"{BASE_URL}/documents/{docx_id}/explain-topic",
                headers=headers,
                json={"topic": "Two-Phase Locking Protocol"}
            )
            assert exp_res.status_code == 200, f"Explain failed: {exp_res.text}"
            exp_data = exp_res.json()
            assert len(exp_data["explanation"]) > 50
            assert len(exp_data["citations"]) > 0
            print(f"  ✓ Topic explained with first-principles and citations: {exp_data['explanation'][:100]}...")
            passed += 1

            # Step 17: Test Document Deletion & Cleanup
            total += 1
            print("\n[TEST 17] Testing Document Deletion & Storage Cleanup (DELETE /documents/{id})...")
            del_res = await client.delete(f"{BASE_URL}/documents/{txt_id}", headers=headers)
            assert del_res.status_code == 200
            # Verify deleted from list
            list_res = await client.get(f"{BASE_URL}/documents", headers=headers)
            doc_ids = [d["id"] for d in list_res.json()]
            assert txt_id not in doc_ids
            print("  ✓ Document deleted and removed from RAG index.")
            passed += 1

    print("\n" + "=" * 65)
    print(f"PHASE 2 TEST RESULTS: {passed}/{total} SUITES PASSED (100%)")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(test_phase2())
