"""
EduPath AI - AI Study Assistant & Conversational Engine.
Handles context-aware multi-turn reasoning, token streaming, 6 explanation levels,
10 multilingual locales, and honest, verified document grounding.

Rules:
- Never generate generic fabricated technical claims (e.g. fake O(log n), fake CAS, fake atomicity) on unrelated questions.
- When an AI provider is unavailable or returns empty, provide an honest, transparent fallback.
- When document context is provided but insufficient, explicitly abstain instead of guessing.
- Never attach citations to claims not derived from those sources.
- Preserve explanation levels, multilingual support, citations, and streaming behavior.
"""

import json
import logging
import asyncio
import re
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator
from app.services.ai.provider import llm_provider
from app.services.ai.prompts import (
    GENERAL_PURPOSE_SYSTEM_PROMPT,
    EXPLANATION_LEVEL_PROMPTS,
    MULTILINGUAL_INSTRUCTIONS,
    PROMPT_INJECTION_DEFENSE_DIRECTIVE
)

logger = logging.getLogger("edupath.ai.assistant")

STOPWORDS = {
    "what", "which", "where", "when", "how", "why", "who", "whom",
    "does", "explain", "describe", "tell", "show", "about", "this",
    "that", "these", "those", "have", "with", "from", "into", "their",
    "could", "would", "should", "some", "more", "please", "can", "you",
    "the", "and", "for", "are", "is", "was", "were"
}


class AssistantService:
    @staticmethod
    def check_context_sufficiency(question: str, context: Optional[str]) -> Tuple[bool, List[str]]:
        """
        Evaluates whether the attached document context contains substantive overlap
        with the user's inquiry. Returns (is_sufficient, matched_keywords).
        """
        if not context or not context.strip():
            return False, []

        q_words = [
            w.lower()
            for w in re.findall(r'[a-zA-Z]{3,}', question)
            if w.lower() not in STOPWORDS
        ]
        if not q_words:
            # Query has no content words (e.g., punctuation or symbols)
            return True, []

        ctx_lower = context.lower()
        matched = [w for w in q_words if w in ctx_lower]
        is_sufficient = len(matched) > 0
        return is_sufficient, matched

    def _extract_relevant_excerpts(self, context: str, keywords: List[str], max_sentences: int = 4) -> str:
        """
        Extracts up to max_sentences sentences from context that contain matched keywords.
        """
        if not context:
            return ""
        sentences = re.split(r'(?<=[.!?])\s+', context.strip())
        matched_sentences = []
        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            s_lower = s_clean.lower()
            if any(k in s_lower for k in keywords):
                matched_sentences.append(s_clean)
                if len(matched_sentences) >= max_sentences:
                    break

        if matched_sentences:
            return " ".join(matched_sentences)
        return context.strip()[:500] + "..." if len(context.strip()) > 500 else context.strip()

    async def ask_sync(
        self,
        question: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        explanation_level: str = "intermediate",
        language: str = "auto",
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes synchronous multi-turn answer generation with contextual grounding.
        """
        q_clean = question.strip()
        doc_name = (
            citations[0].get("doc_title", "uploaded document")
            if (citations and len(citations) > 0)
            else "the referenced document"
        )

        # 1. Inspect Document Context Sufficiency (if document context was attached)
        if context and context.strip():
            is_sufficient, matched_kw = self.check_context_sufficiency(q_clean, context)
            if not is_sufficient:
                # Explicit Abstention: context is insufficient for this question
                abstention_msg = (
                    f"Based on the provided document context in **{doc_name}**, there is insufficient information "
                    f"to answer your question regarding '{q_clean}'. The referenced excerpts do not contain details "
                    f"matching this inquiry. Please consult the full document or provide additional study material."
                )
                return {
                    "answer": abstention_msg,
                    "citations": [],  # Never attach citations to claims not derived from source
                    "explanation_level": explanation_level,
                    "language": language
                }

        # 2. Attempt Live Inference if Provider is Configured
        prompt = self._build_prompt(
            question=q_clean,
            context=context,
            conversation_history=conversation_history,
            explanation_level=explanation_level,
            language=language
        )

        if llm_provider.is_configured:
            try:
                llm_response = await llm_provider.generate_with_retry(
                    prompt=prompt,
                    generation_config={"temperature": 0.4, "max_output_tokens": 2048}
                )
                if llm_response and len(llm_response.strip()) > 30:
                    return {
                        "answer": llm_response.strip(),
                        "citations": citations or [] if context else [],
                        "explanation_level": explanation_level,
                        "language": language
                    }
            except Exception as e:
                logger.warning(f"Live LLM generation failed ({e}); falling back to honest offline response.")

        # 3. Honest, Non-Fabricated Fallback
        fallback_answer, verified_citations = self._generate_honest_fallback(
            question=q_clean,
            context=context,
            explanation_level=explanation_level,
            language=language,
            citations=citations
        )

        return {
            "answer": fallback_answer,
            "citations": verified_citations,
            "explanation_level": explanation_level,
            "language": language
        }

    async def ask_stream(
        self,
        question: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        explanation_level: str = "intermediate",
        language: str = "auto",
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Genuine token-by-token streaming generator.
        Streams live tokens from LLM provider or streams verified fallback response.
        """
        q_clean = question.strip()
        doc_name = (
            citations[0].get("doc_title", "uploaded document")
            if (citations and len(citations) > 0)
            else "the referenced document"
        )

        # 1. Document Context Sufficiency Check
        if context and context.strip():
            is_sufficient, _ = self.check_context_sufficiency(q_clean, context)
            if not is_sufficient:
                abstention_msg = (
                    f"Based on the provided document context in **{doc_name}**, there is insufficient information "
                    f"to answer your question regarding '{q_clean}'. The referenced excerpts do not contain details "
                    f"matching this inquiry. Please consult the full document or provide additional study material."
                )
                tokens = re.findall(r'\S+|\s+', abstention_msg)
                for t in tokens:
                    yield t
                    await asyncio.sleep(0.01)
                return

        # 2. Attempt Live Stream if Provider Configured
        prompt = self._build_prompt(
            question=q_clean,
            context=context,
            conversation_history=conversation_history,
            explanation_level=explanation_level,
            language=language
        )

        streamed_any = False
        if llm_provider.is_configured:
            try:
                async for chunk in llm_provider.generate_stream(
                    prompt=prompt,
                    generation_config={"temperature": 0.4, "max_output_tokens": 2048}
                ):
                    streamed_any = True
                    yield chunk
                if streamed_any:
                    return
            except Exception as e:
                logger.warning(f"Live LLM stream failed ({e}); streaming honest fallback.")

        # 3. Stream Honest Fallback
        fallback_answer, _ = self._generate_honest_fallback(
            question=q_clean,
            context=context,
            explanation_level=explanation_level,
            language=language,
            citations=citations
        )
        tokens = re.findall(r'\S+|\s+', fallback_answer)
        for t in tokens:
            yield t
            await asyncio.sleep(0.01)

    def _build_prompt(
        self,
        question: str,
        context: Optional[str],
        conversation_history: Optional[List[Dict[str, str]]],
        explanation_level: str,
        language: str
    ) -> str:
        level_instruction = EXPLANATION_LEVEL_PROMPTS.get(
            explanation_level.lower(),
            EXPLANATION_LEVEL_PROMPTS["intermediate"]
        )

        lang_instruction = MULTILINGUAL_INSTRUCTIONS.get(
            language.lower(),
            "Respond articulately in clear English or mirror the query language."
        )

        history_block = ""
        if conversation_history:
            recent = conversation_history[-10:]
            history_lines = []
            for msg in recent:
                role = "Student" if msg.get("role") == "user" else "Assistant"
                content = msg.get("content", "").strip()
                history_lines.append(f"{role}: {content}")
            history_block = "PRIOR CONVERSATION CONTEXT:\n" + "\n".join(history_lines) + "\n\n"

        context_block = ""
        if context and context.strip():
            context_block = (
                f"{PROMPT_INJECTION_DEFENSE_DIRECTIVE}\n\n"
                f"GROUNDING & ABSTENTION INSTRUCTION:\n"
                f"You have been provided with validated document context in <document_context>. "
                f"Ground your answer strictly on the facts, concepts, and relationships detailed within the provided context. "
                f"If the user query cannot be reliably answered using the provided context, or if the question refers to concepts completely missing from the document, "
                f"you MUST state explicitly: 'Based on the provided document, there is insufficient information to answer this question accurately.' "
                f"Do NOT fabricate, speculate, or hallucinate outside the retrieved document scope.\n\n"
                f"<document_context>\n{context.strip()[:4000]}\n</document_context>\n\n"
            )

        return (
            f"{GENERAL_PURPOSE_SYSTEM_PROMPT}\n\n"
            f"{level_instruction}\n\n"
            f"LANGUAGE DIRECTIVE: {lang_instruction}\n\n"
            f"{context_block}"
            f"{history_block}"
            f"<user_query>\n{question}\n</user_query>\n\n"
            f"ASSISTANT RESPONSE:"
        )

    def _generate_honest_fallback(
        self,
        question: str,
        context: Optional[str],
        explanation_level: str,
        language: str,
        citations: Optional[List[Dict[str, Any]]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Produces an honest, non-fabricated response when the live LLM provider is unavailable.
        Never generates arbitrary technical claims (e.g. O(log n), CAS, atomicity) on unrelated questions.
        Never attaches citations unless derived from the actual referenced context.
        """
        q_clean = question.strip()
        lvl = explanation_level.lower()

        # CASE 1: Document context is provided and has verified relevant overlap
        if context and context.strip():
            is_suff, matched_kw = self.check_context_sufficiency(q_clean, context)
            doc_name = citations[0].get("doc_title", "Document") if citations else "the referenced document"
            page_num = citations[0].get("page_number", 1) if citations else 1

            mode_tag = ""
            if lvl == "eli5":
                mode_tag = " (ELI5 Mode — Simple Summary)"
            elif lvl == "advanced":
                mode_tag = " (Advanced Architectural Invariants & Complexity Mode)"
            elif lvl == "exam_oriented":
                mode_tag = " (Exam-Oriented Master Notes Mode)"

            if is_suff and matched_kw:
                excerpts = self._extract_relevant_excerpts(context, matched_kw)
                text = (
                    f"### Grounded Document Notes{mode_tag}: {q_clean}\n\n"
                    f"*The AI model reasoning service is currently operating in offline mode. "
                    f"The following verified simple excerpts are extracted directly from your study material (**{doc_name}**):*\n\n"
                    f"> {excerpts}\n\n"
                    f"*Source: {doc_name} (Page {page_num})*"
                )
                return text, citations or []
            else:
                abstention = (
                    f"Based on the provided document context in **{doc_name}**, there is insufficient information "
                    f"to answer your question regarding '{q_clean}'. The referenced excerpts do not contain details "
                    f"matching this inquiry. Please consult the full document or provide additional study material."
                )
                return abstention, []

        # CASE 2: No document context attached (General Academic Query)
        # Check multilingual requests
        has_telugu = (language == "te") or any('\u0c00' <= char <= '\u0c7f' for char in q_clean)
        has_hindi = (language == "hi") or any('\u0900' <= char <= '\u097f' for char in q_clean)

        if has_telugu:
            te_msg = (
                f"### AI స్టడీ అసిస్టెంట్ (ఆఫ్‌లైన్ మోడ్)\n\n"
                f"AI రీజనింగ్ సర్వీస్ ప్రస్తుతం ఆఫ్‌లైన్‌లో ఉంది (యాక్టివ్ LLM ప్రొవైడర్ కనెక్షన్ అందుబాటులో లేదు).\n\n"
                f"- **మీ ప్రశ్న**: *{q_clean}*\n\n"
                f"*ప్రత్యక్ష AI వివరణలను పొందడానికి దయచేసి సిస్టమ్ సెట్టింగ్స్ లో `GEMINI_API_KEY` కాన్ఫిగర్ చేయబడిందో లేదో తనిఖీ చేయండి. "
                f"ప్రత్యామ్నాయంగా, మీరు డాక్యుమెంట్స్ సెక్షన్‌లో స్టడీ మెటీరియల్ (PDF/DOCX) అప్‌లోడ్ చేసి ప్రశ్నలు అడగవచ్చు.*"
            )
            return te_msg, []

        if has_hindi:
            hi_msg = (
                f"### AI अध्ययन सहायक (ऑफ़लाइन मोड)\n\n"
                f"AI रीजनिंग सेवा वर्तमान में ऑफ़लाइन है (सक्रिय LLM प्रदाता कनेक्शन उपलब्ध नहीं है)।\n\n"
                f"- **आपका प्रश्न**: *{q_clean}*\n\n"
                f"*सीधे AI स्पष्टीकरण प्राप्त करने के लिए कृपया सुनिश्चित करें कि आपके पर्यावरण में मान्य `GEMINI_API_KEY` कॉन्फ़िगर है। "
                f"वैकल्पिक रूप से, आप दस्तावेज़ अनुभाग में अध्ययन सामग्री (PDF/DOCX) अपलोड करके सीधे संदर्भ सामग्री से प्रश्न पूछ सकते हैं।*"
            )
            return hi_msg, []

        # English / General responses tailored to requested level without fabricating facts
        if lvl == "eli5":
            eli5_msg = (
                f"### AI Study Assistant (Offline Fallback — ELI5 Mode)\n\n"
                f"The AI reasoning engine is currently running in offline mode because an active AI provider "
                f"(such as Google Gemini) is not configured or reached.\n\n"
                f"- **Question**: *{q_clean}*\n"
                f"- **Requested Mode**: Simple ELI5 (Explain Like I'm 5)\n\n"
                f"*To receive live AI-generated simple explanations, please configure `GEMINI_API_KEY` in your environment settings. "
                f"You can also upload a reference document (PDF/DOCX) in the Documents section to ground answers directly in your study material.*"
            )
            return eli5_msg, []

        elif lvl == "advanced":
            adv_msg = (
                f"### AI Study Assistant (Offline Fallback — Advanced Mode)\n\n"
                f"The AI reasoning engine is currently running in offline mode because an active AI provider "
                f"(such as Google Gemini) is not configured or reached.\n\n"
                f"- **Inquiry**: *{q_clean}*\n"
                f"- **Requested Depth**: Advanced Architectural Analysis & Complexity Bounds\n\n"
                f"*To analyze theoretical complexity bounds and advanced system invariants with live AI inference, "
                f"please ensure a valid `GEMINI_API_KEY` is configured in your environment. Alternatively, upload academic "
                f"papers or lecture slides in Documents for verifiable retrieval.*"
            )
            return adv_msg, []

        elif lvl == "exam_oriented":
            exam_msg = (
                f"### AI Study Assistant (Offline Fallback — Exam-Oriented Mode)\n\n"
                f"The AI reasoning engine is currently running in offline mode because an active AI provider "
                f"(such as Google Gemini) is not configured or reached.\n\n"
                f"- **Inquiry**: *{q_clean}*\n"
                f"- **Target**: Examination Master Notes & Marking Rubrics\n\n"
                f"*To generate structured 2-mark definitions, operational mechanisms, and exam notes, "
                f"please configure a valid `GEMINI_API_KEY` in your environment settings.*"
            )
            return exam_msg, []

        else:
            default_msg = (
                f"### AI Study Assistant (Offline Fallback)\n\n"
                f"The AI reasoning engine is currently running in offline mode because an active AI provider "
                f"(such as Google Gemini) is not connected or reachable.\n\n"
                f"- **Topic**: *{q_clean}*\n"
                f"- **Explanation Level**: {explanation_level.capitalize()}\n\n"
                f"*To unlock real-time contextual explanations, please set a valid `GEMINI_API_KEY` in your environment settings. "
                f"If you upload a course document in the Documents section, EduPath AI can search and extract verified concepts "
                f"directly from your notes.*"
            )
            return default_msg, []

    def _generate_deterministic_answer(
        self,
        question: str,
        context: Optional[str] = None,
        explanation_level: str = "intermediate",
        language: str = "auto",
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Backward compatible alias for honest fallback generation."""
        text, _ = self._generate_honest_fallback(
            question=question,
            context=context,
            explanation_level=explanation_level,
            language=language,
            citations=citations
        )
        return text


assistant_service = AssistantService()
