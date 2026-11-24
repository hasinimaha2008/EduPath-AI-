"""
EduPath AI - Centralized Embedding Interface & Vector Operations.
Provides versioned embedding metadata, strict dimension validation, consistent
document vs query task configurations, and transparent lexical fallback labeling.
"""

import abc
import math
import hashlib
import logging
import re
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple
import google.generativeai as genai
from app.services.ai.provider import llm_provider

logger = logging.getLogger("edupath.ai.embeddings")

EMBEDDING_DIMENSION = 768
EMBEDDING_VERSION = "2.0.0"

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)

class BaseEmbeddingProvider(abc.ABC):
    """
    Abstract Base Class for all EduPath AI embedding providers.
    """
    @property
    @abc.abstractmethod
    def model_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def dimension(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def is_semantic(self) -> bool:
        pass

    @abc.abstractmethod
    def embed_document(self, text: str) -> List[float]:
        pass

    @abc.abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass

class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """
    Genuine Semantic Embedding Provider using Google Gemini text-embedding-004.
    Enforces 768-dimensional output, unit normalization, and separate retrieval task types.
    """
    def __init__(self):
        self._model_name = "models/text-embedding-004"
        self._dimension = EMBEDDING_DIMENSION

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def is_semantic(self) -> bool:
        return True

    def embed_document(self, text: str) -> List[float]:
        return self._embed(text, task_type="retrieval_document")

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text, task_type="retrieval_query")

    def _embed(self, text: str, task_type: str) -> List[float]:
        clean_text = text.strip() if text else ""
        if not clean_text:
            return [0.0] * self._dimension

        try:
            result = genai.embed_content(
                model=self._model_name,
                content=clean_text[:2048],
                task_type=task_type
            )
            if result and "embedding" in result:
                emb = result["embedding"]
                if len(emb) == self._dimension:
                    norm = math.sqrt(sum(x * x for x in emb))
                    return [round(x / norm, 6) for x in emb] if norm > 0 else emb
                else:
                    logger.warning(f"Unexpected embedding dimension: got {len(emb)}, expected {self._dimension}")
        except Exception as e:
            logger.warning(f"Gemini {task_type} embedding API error: {e}")
        return []

class LexicalFallbackEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic Lexical-Only Fallback Provider.
    Transparently labeled as non-semantic. Preserves cluster invariants
    for offline testing and guarantees unit-norm dimensional compatibility (768).
    """
    def __init__(self):
        self._model_name = "lexical-bm25-fallback-v1"
        self._dimension = EMBEDDING_DIMENSION

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def is_semantic(self) -> bool:
        return False

    def embed_document(self, text: str) -> List[float]:
        return self._generate_vector(text)

    def embed_query(self, text: str) -> List[float]:
        return self._generate_vector(text)

    def _generate_vector(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self._dimension

        vector = [0.0] * self._dimension
        tokens = re.findall(r'\b[a-zA-Z0-9_\-\+]{2,}\b', text.lower())
        if not tokens:
            return [0.0] * self._dimension

        stop_words = {
            "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of",
            "with", "by", "is", "are", "was", "were", "what", "how", "why", "does",
            "explain", "describe", "compare", "between", "from", "that", "this"
        }
        filtered_tokens = [t for t in tokens if t not in stop_words] or tokens

        # Hashed feature projection (deterministic feature hashing)
        counts = defaultdict(int)
        for t in filtered_tokens:
            counts[t] += 1

        for token, count in counts.items():
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            bucket = h % self._dimension
            sign = 1.0 if ((h >> 16) % 2 == 0) else -1.0
            weight = 1.0 + math.log(count)
            vector[bucket] += sign * weight

        # Normalize to unit Euclidean length
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            return [round(x / norm, 6) for x in vector]
        return [0.0] * self._dimension

class EmbeddingService:
    """
    Centralized Embedding Service managing model dispatch, metadata tracking,
    strict dimension validation, and query vs document task configurations.
    """
    def __init__(self):
        self.gemini_provider = GeminiEmbeddingProvider()
        self.fallback_provider = LexicalFallbackEmbeddingProvider()
        self.dimension = EMBEDDING_DIMENSION
        self.version = EMBEDDING_VERSION

    @property
    def active_provider(self) -> BaseEmbeddingProvider:
        if llm_provider.is_configured:
            return self.gemini_provider
        return self.fallback_provider

    @property
    def model_name(self) -> str:
        return self.active_provider.model_name

    @property
    def is_semantic(self) -> bool:
        return self.active_provider.is_semantic

    def get_metadata(self) -> Dict[str, Any]:
        """
        Returns versioned embedding configuration metadata.
        """
        return {
            "model_name": self.model_name,
            "version": self.version,
            "dimension": self.dimension,
            "is_semantic": self.is_semantic,
            "provider": type(self.active_provider).__name__
        }

    def generate_embedding(self, text: str) -> List[float]:
        """
        Standard document embedding entrypoint maintaining 100% backward compatibility.
        """
        return self.embed_document(text)

    def embed_document_with_metadata(self, text: str) -> Tuple[List[float], Dict[str, Any]]:
        """
        Generates document-level embedding and returns both vector and verified provider metadata.
        Guarantees that metadata accurately reflects whether semantic or lexical fallback was executed.
        """
        if not text or not text.strip():
            fallback_vec = [0.0] * self.dimension
            return fallback_vec, {
                "model_name": self.fallback_provider.model_name,
                "version": self.version,
                "dimension": self.dimension,
                "is_semantic": False,
                "provider": "LexicalFallbackEmbeddingProvider"
            }

        if llm_provider.is_configured:
            try:
                emb = self.gemini_provider.embed_document(text)
                if emb and len(emb) == self.dimension:
                    return emb, {
                        "model_name": self.gemini_provider.model_name,
                        "version": self.version,
                        "dimension": self.dimension,
                        "is_semantic": True,
                        "provider": "GeminiEmbeddingProvider"
                    }
            except Exception as e:
                logger.warning(f"Semantic document embedding failed: {e}. Executing transparent fallback.")

        emb = self.fallback_provider.embed_document(text)
        return emb, {
            "model_name": self.fallback_provider.model_name,
            "version": self.version,
            "dimension": self.dimension,
            "is_semantic": False,
            "provider": "LexicalFallbackEmbeddingProvider"
        }

    def embed_query_with_metadata(self, text: str) -> Tuple[List[float], Dict[str, Any]]:
        """
        Generates query-level embedding and returns both vector and verified provider metadata.
        """
        if not text or not text.strip():
            fallback_vec = [0.0] * self.dimension
            return fallback_vec, {
                "model_name": self.fallback_provider.model_name,
                "version": self.version,
                "dimension": self.dimension,
                "is_semantic": False,
                "provider": "LexicalFallbackEmbeddingProvider"
            }

        if llm_provider.is_configured:
            try:
                emb = self.gemini_provider.embed_query(text)
                if emb and len(emb) == self.dimension:
                    return emb, {
                        "model_name": self.gemini_provider.model_name,
                        "version": self.version,
                        "dimension": self.dimension,
                        "is_semantic": True,
                        "provider": "GeminiEmbeddingProvider"
                    }
            except Exception as e:
                logger.warning(f"Semantic query embedding failed: {e}. Executing transparent fallback.")

        emb = self.fallback_provider.embed_query(text)
        return emb, {
            "model_name": self.fallback_provider.model_name,
            "version": self.version,
            "dimension": self.dimension,
            "is_semantic": False,
            "provider": "LexicalFallbackEmbeddingProvider"
        }

    def embed_document(self, text: str) -> List[float]:
        """
        Generates document-level embedding with retrieval_document task tuning.
        """
        vec, _ = self.embed_document_with_metadata(text)
        return vec

    def embed_query(self, text: str) -> List[float]:
        """
        Generates query-level embedding with retrieval_query task tuning.
        """
        vec, _ = self.embed_query_with_metadata(text)
        return vec

embedding_service = EmbeddingService()
