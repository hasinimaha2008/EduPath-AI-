"""
EduPath AI - Modular Artificial Intelligence Subsystem.
Exports specialized AI modules:
- provider: LLM provider connection, bounded retries, and quota handling
- prompts: System prompts, explanation levels, and multilingual templates
- embeddings: 768-dimensional vector embeddings and cosine similarity
- assistant: Multi-turn study assistant with 6 explanation levels and streaming
- notes_generator: Structured notes synthesis across 8 pedagogical formats
- quiz_generator: Adaptive assessment generation and distractor synthesis
- evaluator: Pedagogical answer rubric scoring and mistake classification
- career_analyzer: Job description parsing and demonstrated skill gap analysis
"""

from app.services.ai.provider import llm_provider
from app.services.ai.prompts import (
    GENERAL_PURPOSE_SYSTEM_PROMPT,
    EXPLANATION_LEVEL_PROMPTS,
    MULTILINGUAL_INSTRUCTIONS,
    MISTAKE_CATEGORIES
)
from app.services.ai.embeddings import embedding_service, cosine_similarity
from app.services.ai.assistant import assistant_service
from app.services.ai.notes_generator import notes_generator
from app.services.ai.quiz_generator import quiz_generator
from app.services.ai.evaluator import evaluator_service
from app.services.ai.career_analyzer import career_analyzer

class AIServiceFacade:
    """
    Unified facade providing 100% backward compatibility with all legacy calls.
    Delegates to modular underlying services.
    """
    def __init__(self):
        self.provider = llm_provider
        self.embeddings = embedding_service
        self.assistant = assistant_service
        self.notes = notes_generator
        self.quiz = quiz_generator
        self.evaluator = evaluator_service
        self.career = career_analyzer

    @property
    def is_configured(self) -> bool:
        return self.provider.is_configured

    @property
    def model_name(self) -> str:
        return self.provider.model_name

    def configure_api_key(self, new_key: str):
        return self.provider.configure_api_key(new_key)

    def generate_embedding(self, text: str):
        return self.embeddings.generate_embedding(text)

    async def ask_sync(self, *args, **kwargs):
        return await self.assistant.ask_sync(*args, **kwargs)

    async def ask_stream(self, *args, **kwargs):
        async for chunk in self.assistant.ask_stream(*args, **kwargs):
            yield chunk

    async def generate_notes(self, *args, **kwargs):
        return await self.notes.generate_notes(*args, **kwargs)

    async def generate_quiz(self, *args, **kwargs):
        return await self.quiz.generate_quiz(*args, **kwargs)

    async def evaluate_answer_quality(self, *args, **kwargs):
        return await self.evaluator.evaluate_answer_quality(*args, **kwargs)

    def classify_mistake(self, *args, **kwargs):
        return self.evaluator.classify_mistake(*args, **kwargs)

    async def analyze_job_description(self, *args, **kwargs):
        return await self.career.analyze_job_description(*args, **kwargs)

ai_service = AIServiceFacade()
