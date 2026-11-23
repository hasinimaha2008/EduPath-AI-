"""
EduPath AI - Gemini Service Facade.
Refactored to delegate to specialized modules in `app.services.ai`:
- `llm_provider`: Gemini client connection, bounded retries, timeouts, and quota handling.
- `embedding_service`: 768-dimensional standardized vector embeddings.
- `assistant_service`: Context-aware multi-turn conversational reasoning and streaming.
- `notes_generator`: Structured notes synthesis across 8 pedagogical formats.
- `quiz_generator`: Adaptive assessment generation and distractor synthesis.
- `evaluator_service`: Multi-metric answer rubric evaluation and mistake classification.
- `career_analyzer`: Job description parsing and demonstrated skill gap analysis.
"""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.services.ai import (
    llm_provider,
    embedding_service,
    assistant_service,
    notes_generator,
    quiz_generator,
    evaluator_service,
    career_analyzer,
    GENERAL_PURPOSE_SYSTEM_PROMPT
)

logger = logging.getLogger("edupath.gemini")

class GeminiService:
    """
    Backward-compatible facade maintaining 100% compatibility with all existing
    API endpoints, tests, and consumers while delegating to decoupled AI modules.
    """
    def __init__(self):
        self.provider = llm_provider
        self.embeddings = embedding_service
        self.assistant = assistant_service
        self.notes = notes_generator
        self.quiz = quiz_generator
        self.evaluator = evaluator_service
        self.career = career_analyzer
        self.model_name = self.provider.model_name

    @property
    def is_configured(self) -> bool:
        return self.provider.is_configured

    @property
    def chat_model(self):
        return self.provider.chat_model

    def configure_api_key(self, new_key: str) -> Dict[str, Any]:
        return self.provider.configure_api_key(new_key)

    async def generate_conversation_title(self, prompt: str) -> str:
        words = prompt.strip().split()[:5]
        return " ".join(words).title() if words else "Academic Consultation"

    def generate_embedding(self, text: str) -> List[float]:
        return self.embeddings.generate_embedding(text)

    async def answer_study_question(
        self,
        question: str,
        context_chunks: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        language: str = "auto",
        explanation_level: Optional[str] = "intermediate",
        context: Optional[str] = None,
        mode: str = "study",
        citations: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        parsed_citations = list(citations) if citations else []
        if context_chunks:
            chunk_text = ""
            for idx, c in enumerate(context_chunks):
                doc_title = c.get("doc_title", "Document")
                page_num = c.get("page_number", 1)
                snippet = c.get("content", "")
                chunk_text += f"\n--- Source [{idx+1}]: {doc_title} (Page {page_num}) ---\n{snippet}\n"
                parsed_citations.append({
                    "doc_title": doc_title,
                    "page_number": page_num,
                    "snippet": snippet[:200] + "..." if len(snippet) > 200 else snippet
                })
            context = (context or "") + "\n" + chunk_text

        res = await self.assistant.ask_sync(
            question=question,
            context=context,
            conversation_history=conversation_history,
            explanation_level=explanation_level or "intermediate",
            language=language or "auto",
            citations=parsed_citations
        )
        return {
            "answer": res["answer"],
            "citations": parsed_citations if (context_chunks or citations) else []
        }

    async def stream_chat_response(
        self,
        question: str,
        context_chunks: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        language: str = "auto",
        explanation_level: Optional[str] = "intermediate",
        context: Optional[str] = None,
        mode: str = "study",
        citations: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        parsed_citations = list(citations) if citations else []
        if context_chunks:
            chunk_text = ""
            for idx, c in enumerate(context_chunks):
                doc_title = c.get("doc_title", "Document")
                page_num = c.get("page_number", 1)
                snippet = c.get("content", "")
                chunk_text += f"\n--- Source [{idx+1}]: {doc_title} (Page {page_num}) ---\n{snippet}\n"
                parsed_citations.append({
                    "doc_title": doc_title,
                    "page_number": page_num,
                    "snippet": snippet[:200] + "..." if len(snippet) > 200 else snippet
                })
            context = (context or "") + "\n" + chunk_text

        # First try LLM streaming if configured
        if self.is_configured and self.provider.chat_model:
            prompt = self.assistant._build_prompt(
                question=question,
                context=context,
                conversation_history=conversation_history,
                explanation_level=explanation_level or "intermediate",
                language=language or "auto"
            )
            try:
                response = self.provider.chat_model.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                logger.error(f"Gemini streaming error: {e}. Falling back to dynamic tokenized generator.")

        # Fallback: tokenized streaming from dynamic assistant
        res = await self.assistant.ask_sync(
            question=question,
            context=context,
            conversation_history=conversation_history,
            explanation_level=explanation_level or "intermediate",
            language=language or "auto",
            citations=parsed_citations
        )
        answer_text = res["answer"]
        tokens = re.findall(r'\S+|\s+', answer_text)
        for t in tokens:
            yield t
            await asyncio.sleep(0.01)

    async def generate_notes(
        self,
        source_text: str = "",
        note_type: str = "detailed",
        topic_name: str = "Topic",
        explanation_style: str = "standard",
        language: str = "en",
        unit_name: Optional[str] = None,
        document_content: Optional[str] = None,
        subject_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        doc_content = document_content or source_text
        res = await self.notes.generate_notes(
            topic_name=topic_name,
            note_type=note_type,
            document_content=doc_content,
            subject_name=subject_name
        )
        content_val = res.get("content_markdown") or res.get("content", "")
        return {
            "title": res.get("title", f"{topic_name} – Study Notes"),
            "note_type": res.get("note_type", note_type),
            "content": content_val,
            "content_markdown": content_val,
            "topic_name": topic_name
        }

    async def generate_quiz(
        self,
        source_text: str = "",
        topic_name: str = "Topic",
        difficulty: str = "medium",
        question_count: int = 5,
        question_types: Optional[List[str]] = None,
        subtopic: Optional[str] = None,
        document_content: Optional[str] = None,
        subject_name: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        doc_content = document_content or source_text
        full_topic = topic_name + (f" - {subtopic}" if subtopic else "")
        return await self.quiz.generate_quiz(
            topic_name=full_topic,
            difficulty=difficulty,
            question_count=question_count,
            document_content=doc_content,
            subject_name=subject_name
        )

    async def evaluate_open_answer(
        self,
        question_text: str,
        question_type: str = "short_answer",
        correct_answer: str = "",
        user_response: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        return await self.evaluator.evaluate_answer_quality(
            question=question_text,
            answer=user_response,
            reference_context=correct_answer
        )

    async def evaluate_answer_quality(
        self,
        question: str,
        answer: str,
        context: Optional[str] = None,
        criteria: Optional[List[str]] = None,
        reference_context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        ref = reference_context or context
        return await self.evaluator.evaluate_answer_quality(
            question=question,
            answer=answer,
            reference_context=ref
        )

    def classify_mistake(
        self,
        question_text: str,
        user_response: str,
        correct_answer: str,
        explanation: str
    ) -> str:
        return self.evaluator.classify_mistake(
            question_text=question_text,
            user_response=user_response,
            correct_answer=correct_answer,
            explanation=explanation
        )

    async def analyze_job_description(
        self,
        job_title: str,
        job_description_text: str,
        user_skills: List[Dict[str, Any]],
        company_name: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.career.analyze_job_description(
            job_title=job_title,
            job_description_text=job_description_text,
            user_skills=user_skills,
            company_name=company_name
        )

gemini_service = GeminiService()
