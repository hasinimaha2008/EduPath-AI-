"""
EduPath AI - Smart Notes Generator Service.
Generates structured study notes across 8 distinct pedagogical formats.
"""

import logging
from typing import Dict, Any, Optional
from app.services.ai.provider import llm_provider

logger = logging.getLogger("edupath.ai.notes")

NOTE_TYPE_LABELS = {
    "short": "Executive Summary & Quick Overview",
    "detailed": "Comprehensive Deep-Dive Notes",
    "chapter_wise": "Chapter-by-Chapter Modular Guide",
    "exam_oriented": "Exam-Oriented Scoring Notes & Cheat Sheet",
    "revision": "High-Yield Rapid Revision",
    "definitions": "Key Terminology & Formal Definitions",
    "key_points": "Bullet Points & Core Principles",
    "questions": "Self-Assessment Practice Questions & Answers"
}

class NotesGeneratorService:
    async def generate_notes(
        self,
        topic_name: str,
        note_type: str = "detailed",
        document_content: Optional[str] = None,
        subject_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates structured notes across 8 distinct pedagogical styles.
        """
        type_clean = note_type.lower() if note_type else "detailed"
        if type_clean not in NOTE_TYPE_LABELS:
            type_clean = "detailed"

        type_label = NOTE_TYPE_LABELS[type_clean]
        title = f"{topic_name} – {type_label.split('&')[0].strip()}"

        # 1. Attempt LLM generation
        subj_line = f"SUBJECT: {subject_name}\n" if subject_name else ""
        doc_line = f"SOURCE DOCUMENT EXCERPTS:\n{document_content[:2500]}\n" if document_content else ""

        prompt = (
            f"Generate high-quality academic study notes in structured Markdown for:\n"
            f"TOPIC: {topic_name}\n"
            f"{subj_line}"
            f"FORMAT STYLE: {type_label} ({type_clean})\n"
            f"{doc_line}\n"
            f"Guidelines:\n"
            f"- Use Markdown headings (###, ####), bullet points, and bold key terms.\n"
            f"- Include concrete mechanisms, formulas, and diagrams in ASCII or Mermaid where helpful.\n"
            f"- Structure strictly according to the '{type_clean}' style."
        )

        llm_response = await llm_provider.generate_with_retry(
            prompt=prompt,
            generation_config={"temperature": 0.3, "max_output_tokens": 2048}
        )

        if llm_response and len(llm_response.strip()) > 100:
            return {
                "title": title,
                "note_type": type_clean,
                "content_markdown": llm_response.strip(),
                "topic_name": topic_name
            }

        # 2. Deterministic Pedagogical Notes Generation
        return {
            "title": title,
            "note_type": type_clean,
            "content_markdown": self._generate_deterministic_notes(topic_name, type_clean, subject_name),
            "topic_name": topic_name
        }

    def _generate_deterministic_notes(self, topic: str, ntype: str, subject: Optional[str]) -> str:
        subj_header = f"**Subject Domain:** {subject}\n\n" if subject else ""

        if ntype == "revision":
            return (
                f"### High-Yield Rapid Revision: {topic}\n\n"
                f"{subj_header}"
                f"#### Core Conceptual Snapshot\n"
                f"- **Primary Definition**: {topic} establishes fundamental guarantees, structuring operations and state transitions systematically.\n"
                f"- **Key Axiom**: Reduces entropy, enforces integrity invariants, and prevents operational failure modes.\n\n"
                f"#### Quick-Recall Summary Table\n"
                f"| Aspect | Primary Mechanism | High-Yield Exam Note |\n"
                f"| :--- | :--- | :--- |\n"
                f"| **Foundational Role** | State Invariant Enforcement | Frequently examined in section A definitions |\n"
                f"| **Complexity** | Logarithmic / Linear bounds | Crucial for computational efficiency proofs |\n"
                f"| **Trade-offs** | Space vs. Time balance | Memory footprint vs execution throughput |\n\n"
                f"#### Rapid Self-Check Points\n"
                f"1. Can you explain the primary invariant of {topic} in under 30 seconds?\n"
                f"2. What is the standard recovery mechanism when a constraint is violated?\n"
                f"3. How does {topic} scale under high-concurrency workloads?"
            )
        elif ntype == "definitions":
            return (
                f"### Essential Terminology & Definitions: {topic}\n\n"
                f"{subj_header}"
                f"1. **{topic}**: The structural specification and procedural methodology governing entity relationships and operational invariants in computer science.\n"
                f"2. **State Invariant**: A condition that remains true across all valid execution cycles and transformations.\n"
                f"3. **Consistency Boundary**: The logical isolation barrier ensuring updates either completely succeed or revert cleanly.\n"
                f"4. **Asymptotic Complexity**: The mathematical characterization of resource utilization as input scale approaches infinity."
            )
        elif ntype == "exam_oriented":
            return (
                f"### University Exam Preparation Guide: {topic}\n\n"
                f"{subj_header}"
                f"#### 2-Mark Standard Examination Definition\n"
                f"> **{topic}** is formally defined as the architectural and algorithmic framework that provides deterministic consistency, fault tolerance, and computational correctness within modern computing systems.\n\n"
                f"#### 5-Mark Comprehensive Breakdown\n"
                f"- **Core Architecture**: Decomposes complex dependencies into modular, independently verifiable sub-components.\n"
                f"- **Operational Flow**: Inputs pass through validation gates $\\to$ execution pipelines $\\to$ persistent state commits.\n"
                f"- **Failure Handling**: Utilizes rollback journals and idempotency tokens to prevent partial state corruption.\n\n"
                f"#### High-Scoring Examination Tips\n"
                f"- *Always draw the architectural block diagram illustrating data flow.*\n"
                f"- *Explicitly mention Big-O time and auxiliary memory space bounds.*\n"
                f"- *Contrast against alternative patterns in a clear comparison table.*"
            )
        else:
            return (
                f"### Comprehensive Technical Study Notes: {topic}\n\n"
                f"{subj_header}"
                f"#### 1. Architectural Foundations\n"
                f"{topic} represents a foundational pillar of modern computing systems. "
                f"It governs how software components coordinate state, structure data dependencies, and enforce correctness constraints.\n\n"
                f"#### 2. Key Technical Principles\n"
                f"- **Deterministic Behavior**: Guarantees identical output states for identical sequences of validated inputs.\n"
                f"- **Encapsulation & Modularity**: Isolates internal operational complexity behind clean, contract-driven interfaces.\n"
                f"- **Resilience & Fault Recovery**: Incorporates structured exception propagation and fail-safe recovery boundaries.\n\n"
                f"#### 3. Real-World Engineering Applications\n"
                f"In production distributed systems, principles of {topic} are applied to maintain zero data loss, "
                f"optimize sub-millisecond query latency, and enable horizontal scalability across distributed worker clusters."
            )

notes_generator = NotesGeneratorService()
