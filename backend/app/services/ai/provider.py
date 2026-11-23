"""
EduPath AI - LLM Provider Integration.
Manages connection, authentication, bounded retries, timeouts, and quota handling
for Google Gemini Large Language Models.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger("edupath.ai.provider")

class LLMProvider:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = "gemini-1.5-flash"
        self.chat_model: Optional[genai.GenerativeModel] = None
        self.is_configured: bool = False
        self._init_model()

    def _init_model(self):
        if bool(self.api_key and len(self.api_key.strip()) > 10):
            try:
                genai.configure(api_key=self.api_key.strip())
                self.chat_model = genai.GenerativeModel(self.model_name)
                self.is_configured = True
                logger.info("Gemini API client successfully configured.")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API client: {e}. Falling back to internal engine.")
                self.is_configured = False
        else:
            logger.info("GEMINI_API_KEY not configured. Running in internal deterministic pedagogical mode.")
            self.is_configured = False

    def configure_api_key(self, new_key: str) -> Dict[str, Any]:
        clean_key = new_key.strip()
        if not clean_key or len(clean_key) < 10:
            return {"success": False, "message": "Invalid API key format."}

        try:
            genai.configure(api_key=clean_key)
            test_model = genai.GenerativeModel(self.model_name)
            res = test_model.generate_content("Ping", generation_config={"max_output_tokens": 5})
            if res:
                self.api_key = clean_key
                self.chat_model = test_model
                self.is_configured = True
                settings.GEMINI_API_KEY = clean_key
                return {
                    "success": True,
                    "message": "Gemini API key verified and updated successfully.",
                    "model": self.model_name
                }
        except Exception as e:
            logger.error(f"API key verification failed: {e}")
            return {"success": False, "message": f"Verification failed: {str(e)}"}
        return {"success": False, "message": "Verification failed."}

    async def generate_with_retry(
        self,
        prompt: str,
        generation_config: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        timeout_seconds: float = 30.0
    ) -> Optional[str]:
        """
        Executes generation with bounded exponential backoff retries and timeouts.
        Handles rate limits and quota boundaries gracefully.
        """
        if not self.is_configured or not self.chat_model:
            return None

        delay = 1.0
        for attempt in range(1, max_retries + 1):
            try:
                loop = asyncio.get_event_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: self.chat_model.generate_content(
                            prompt,
                            generation_config=generation_config
                        )
                    ),
                    timeout=timeout_seconds
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text.strip()
            except asyncio.TimeoutError:
                logger.warning(f"Gemini API timeout on attempt {attempt}/{max_retries}")
            except Exception as e:
                err_str = str(e).lower()
                if "quota" in err_str or "429" in err_str or "resourceexhausted" in err_str:
                    logger.warning(f"Gemini quota exhausted on attempt {attempt}/{max_retries}: {e}")
                else:
                    logger.warning(f"Gemini API error on attempt {attempt}/{max_retries}: {e}")
                
            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay *= 2.0

        return None

llm_provider = LLMProvider()
