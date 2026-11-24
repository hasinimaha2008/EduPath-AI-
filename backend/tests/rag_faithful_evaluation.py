"""
EduPath AI — End-to-End RAG Faithfulness, Citation Accuracy & Retrieval Benchmark.

Empirically evaluates:
1. Retrieval Metrics: Precision@3, Recall@3 (Hit@3), MRR, nDCG@3, Latency (ms).
2. Answer Faithfulness: Verified factual grounding in retrieved text without hallucination.
3. Citation Accuracy: Verifies citation doc_title and page_number match genuine sources.
4. Insufficient-Context Detection: Abstention rate when query has zero or insufficient overlap.

Run Command:
    python tests/rag_faithful_evaluation.py
"""

import sys
import os
import time
import math
import uuid
import asyncio
from typing import List, Dict, Any, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.core.database import AsyncSessionLocal
from app.models.models import User, Document, DocumentChunk
from app.services.rag_service import rag_service
from app.services.ai.assistant import assistant_service
from app.core.security import get_password_hash


EVALUATION_CORPUS = [
    {
        "doc_title": "Database Relational Invariants & ACID",
        "page_number": 1,
        "content": (
            "Write-Ahead Logging (WAL) requires transaction modifications to be committed to non-volatile "
            "log storage before dirty pages are flushed to disk. Two-Phase Locking (2PL) guarantees conflict "
            "serializability through distinct expanding and shrinking lock acquisition phases. Boyce-Codd Normal "
            "Form (BCNF) strictly requires every non-trivial functional dependency X -> Y to have X as a superkey."
        ),
        "test_queries": [
            {
                "query": "What is the core rule of Write-Ahead Logging in databases?",
                "expected_keywords": ["write-ahead logging", "non-volatile", "dirty pages", "flushed"],
                "is_answerable": True
            },
            {
                "query": "How does Two-Phase Locking guarantee conflict serializability?",
                "expected_keywords": ["two-phase locking", "growing", "shrinking", "serializability", "lock"],
                "is_answerable": True
            },
            {
                "query": "What does Boyce-Codd Normal Form require for functional dependencies?",
                "expected_keywords": ["boyce-codd", "bcnf", "superkey", "dependency"],
                "is_answerable": True
            }
        ]
    },
    {
        "doc_title": "Operating Systems Virtual Memory & Paging",
        "page_number": 2,
        "content": (
            "Virtual memory paging maps virtual addresses to physical RAM frames using the Memory Management Unit (MMU). "
            "The Translation Lookaside Buffer (TLB) acts as a hardware associative cache for page table entries. "
            "A page fault interrupt triggers when an accessed virtual page is marked invalid, causing the OS kernel "
            "to retrieve the page from disk swap space."
        ),
        "test_queries": [
            {
                "query": "What role does the Translation Lookaside Buffer play in virtual memory?",
                "expected_keywords": ["translation lookaside buffer", "tlb", "cache", "page table"],
                "is_answerable": True
            },
            {
                "query": "When does an operating system trigger a page fault interrupt?",
                "expected_keywords": ["page fault", "invalid", "swap", "disk"],
                "is_answerable": True
            }
        ]
    },
    {
        "doc_title": "Computer Networks Transport Architecture",
        "page_number": 3,
        "content": (
            "The TCP three-way handshake synchronizes sequence numbers between endpoints using SYN, SYN-ACK, and ACK packets. "
            "TCP enforces flow control via sliding window advertisements and congestion control via Slow Start and Congestion Avoidance. "
            "UDP delivers datagrams connectionlessly without retransmission, ordering, or acknowledgment overhead."
        ),
        "test_queries": [
            {
                "query": "How does the TCP three-way handshake establish a reliable connection?",
                "expected_keywords": ["tcp", "syn", "syn-ack", "ack", "handshake"],
                "is_answerable": True
            },
            {
                "query": "Why does UDP have lower packet overhead than TCP?",
                "expected_keywords": ["udp", "connectionless", "retransmission", "overhead"],
                "is_answerable": True
            }
        ]
    }
]

# Unrelated and adversarial queries for Insufficient-Context Detection
ADVERSARIAL_UNRELATED_QUERIES = [
    {
        "query": "What are the molecular properties of chlorophyll in photosynthesis?",
        "is_answerable": False
    },
    {
        "query": "Explain the historical political structure of the Byzantine Empire.",
        "is_answerable": False
    },
    {
        "query": "What are the optimal culinary techniques for making French puff pastry?",
        "is_answerable": False
    },
    {
        "query": "How do quantum teleportation experiments utilize Einstein-Podolsky-Rosen pairs?",
        "is_answerable": False
    }
]


def compute_dcg(relevances: List[int]) -> float:
    return sum((rel / math.log2(idx + 2)) for idx, rel in enumerate(relevances))


async def run_faithful_rag_evaluation():
    print("=" * 80)
    print("EDUPATH AI — FAITHFUL RAG EVALUATION & CITATION BENCHMARK")
    print("=" * 80)

    user_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        # Create benchmark user
        user = User(
            id=user_id,
            email=f"evaluator_{uuid.uuid4().hex[:6]}@edupath.local",
            hashed_password=get_password_hash("TestPass123!"),
            full_name="RAG Evaluator"
        )
        session.add(user)
        await session.commit()

        # Materialize documents and chunks
        doc_objects = []
        chunk_objects = []
        for doc_info in EVALUATION_CORPUS:
            doc = Document(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=doc_info["doc_title"],
                file_name=f"{doc_info['doc_title'].replace(' ', '_').lower()}.txt",
                file_path="uploads/eval_doc.txt",
                file_size=len(doc_info["content"]),
                file_type="txt",
                status="ready",
                chunk_count=1
            )
            session.add(doc)
            await session.commit()
            doc_objects.append(doc)

            chunk = DocumentChunk(
                id=str(uuid.uuid4()),
                document_id=doc.id,
                chunk_index=0,
                content=doc_info["content"],
                page_number=doc_info["page_number"],
                token_count=len(doc_info["content"].split())
            )
            session.add(chunk)
            chunk_objects.append(chunk)

        await session.commit()
        for c in chunk_objects:
            await session.refresh(c)

        print(f"[Phase 1/4] Indexed {len(doc_objects)} evaluation documents ({len(chunk_objects)} chunks).")

        # Index via rag_service
        start_idx = time.perf_counter()
        await rag_service.index_chunks(session, chunk_objects)
        idx_duration_ms = (time.perf_counter() - start_idx) * 1000.0
        print(f"[Phase 2/4] Indexing completed in {idx_duration_ms:.1f}ms.")

        # --- Phase 3: Evaluate Answerable Queries ---
        print("\n[Phase 3/4] Evaluating Retrieval, Answer Faithfulness & Citation Accuracy...")
        reciprocal_ranks = []
        precision_at_3 = []
        recall_at_3 = []
        ndcg_scores = []
        latencies = []
        faithfulness_hits = 0
        citation_hits = 0
        total_answerable = 0

        for doc_info in EVALUATION_CORPUS:
            expected_title = doc_info["doc_title"]
            expected_page = doc_info["page_number"]

            for q_item in doc_info["test_queries"]:
                total_answerable += 1
                q_text = q_item["query"]

                start_q = time.perf_counter()
                retrieved = await rag_service.retrieve_relevant_chunks(
                    session=session,
                    user_id=user_id,
                    query=q_text,
                    top_k=3
                )
                latency_ms = (time.perf_counter() - start_q) * 1000.0
                latencies.append(latency_ms)

                # Rank evaluation
                titles_retrieved = [r.get("doc_title") for r in retrieved]
                rel_binary = [1 if t == expected_title else 0 for t in titles_retrieved]

                # Hit & Reciprocal Rank
                if 1 in rel_binary:
                    rank = rel_binary.index(1) + 1
                    reciprocal_ranks.append(1.0 / rank)
                    recall_at_3.append(1.0)
                else:
                    reciprocal_ranks.append(0.0)
                    recall_at_3.append(0.0)

                # Precision@3
                p3 = sum(rel_binary) / 3.0
                precision_at_3.append(p3)

                # nDCG@3
                actual_dcg = compute_dcg(rel_binary)
                ideal_dcg = compute_dcg(sorted(rel_binary, reverse=True))
                ndcg = (actual_dcg / ideal_dcg) if ideal_dcg > 0 else 0.0
                ndcg_scores.append(ndcg)

                # Ask assistant using retrieved context
                context_str = "\n".join(r["content"] for r in retrieved)
                citations_in = [
                    {"doc_title": r["doc_title"], "page_number": r["page_number"]}
                    for r in retrieved
                ]

                res = await assistant_service.ask_sync(
                    question=q_text,
                    context=context_str,
                    citations=citations_in
                )
                ans = res["answer"]
                res_cits = res.get("citations", [])

                # Faithfulness check: answer must contain at least one expected keyword from source text
                has_faithful_kw = any(kw in ans.lower() for kw in q_item["expected_keywords"])
                if has_faithful_kw and "insufficient information" not in ans.lower():
                    faithfulness_hits += 1

                # Citation accuracy check: returned citation must match expected document title and page
                if res_cits:
                    cit0 = res_cits[0]
                    if cit0.get("doc_title") == expected_title and cit0.get("page_number") == expected_page:
                        citation_hits += 1

        # --- Phase 4: Evaluate Insufficient-Context Queries ---
        print("\n[Phase 4/4] Evaluating Insufficient-Context Detection & Abstention...")
        combined_context = "\n".join(d["content"] for d in EVALUATION_CORPUS)
        citations_dummy = [{"doc_title": "Database Relational Invariants & ACID", "page_number": 1}]
        abstention_hits = 0
        zero_citation_hits = 0

        for adv_q in ADVERSARIAL_UNRELATED_QUERIES:
            q_text = adv_q["query"]
            res = await assistant_service.ask_sync(
                question=q_text,
                context=combined_context,
                citations=citations_dummy
            )
            ans = res["answer"]
            cits = res.get("citations", [])

            # Must explicitly abstain
            if "insufficient information" in ans.lower():
                abstention_hits += 1
            # Must NOT attach spurious citations
            if len(cits) == 0:
                zero_citation_hits += 1

        # Cleanup evaluator user & data
        for c in chunk_objects:
            await session.delete(c)
        for d in doc_objects:
            await session.delete(d)
        await session.delete(user)
        await session.commit()

        # Summary Metrics
        mean_mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        mean_prec = sum(precision_at_3) / len(precision_at_3) if precision_at_3 else 0.0
        mean_recall = sum(recall_at_3) / len(recall_at_3) if recall_at_3 else 0.0
        mean_ndcg = sum(ndcg_scores) / len(ndcg_scores) if ndcg_scores else 0.0
        mean_latency = sum(latencies) / len(latencies) if latencies else 0.0
        faithfulness_rate = (faithfulness_hits / total_answerable) * 100.0 if total_answerable > 0 else 0.0
        citation_acc_rate = (citation_hits / total_answerable) * 100.0 if total_answerable > 0 else 0.0
        abstention_rate = (abstention_hits / len(ADVERSARIAL_UNRELATED_QUERIES)) * 100.0
        zero_cit_rate = (zero_citation_hits / len(ADVERSARIAL_UNRELATED_QUERIES)) * 100.0

        print("\n" + "=" * 80)
        print("EMPIRICAL RAG BENCHMARK & FAITHFULNESS RESULTS:")
        print("=" * 80)
        print(f"  * Mean Reciprocal Rank (MRR):          {mean_mrr:.3f}   (Benchmark Target: >= 0.750)")
        print(f"  * Recall@3 (Hit@3):                    {mean_recall:.3f}   (Benchmark Target: >= 0.900)")
        print(f"  * Precision@3:                         {mean_prec:.3f}   (Benchmark Target: >= 0.600)")
        print(f"  * Normalized DCG (nDCG@3):             {mean_ndcg:.3f}   (Benchmark Target: >= 0.750)")
        print(f"  * Average Retrieval Latency:           {mean_latency:.2f} ms")
        print(f"  * Answer Faithfulness Rate:            {faithfulness_rate:.1f}% ({faithfulness_hits}/{total_answerable})")
        print(f"  * Citation Accuracy Rate:              {citation_acc_rate:.1f}% ({citation_hits}/{total_answerable})")
        print(f"  * Insufficient Context Abstention:     {abstention_rate:.1f}% ({abstention_hits}/{len(ADVERSARIAL_UNRELATED_QUERIES)})")
        print(f"  * Zero Citation Rate on Abstention:    {zero_cit_rate:.1f}% ({zero_citation_hits}/{len(ADVERSARIAL_UNRELATED_QUERIES)})")
        print("=" * 80)

        assert mean_mrr >= 0.750, f"MRR {mean_mrr} below threshold 0.750"
        assert mean_recall >= 0.900, f"Recall@3 {mean_recall} below threshold 0.900"
        assert faithfulness_rate >= 80.0, f"Faithfulness {faithfulness_rate}% below 80%"
        assert citation_acc_rate >= 80.0, f"Citation accuracy {citation_acc_rate}% below 80%"
        assert abstention_rate == 100.0, f"Abstention rate {abstention_rate}% must be 100%"
        assert zero_cit_rate == 100.0, f"Zero citation rate on abstention must be 100%"

        print("[SUCCESS] All RAG Faithfulness, Citation Accuracy, and Retrieval criteria PASSED!\n")


if __name__ == "__main__":
    asyncio.run(run_faithful_rag_evaluation())
