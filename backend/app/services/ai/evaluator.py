"""
EduPath AI - Evaluator & Pedagogical Rubric Engine.
Scores student answers across 4 standardized pedagogical dimensions, evaluates quizzes,
and classifies student mistakes into actionable categories.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from app.services.ai.prompts import MISTAKE_CATEGORIES
from app.services.ai.provider import llm_provider

logger = logging.getLogger("edupath.ai.evaluator")

class EvaluatorService:
    async def evaluate_answer_quality(
        self,
        question: str,
        answer: str,
        reference_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a student's open-ended answer against objective pedagogical criteria.
        Scores:
        - relevance_score (0.0 - 10.0)
        - accuracy_score (0.0 - 10.0)
        - clarity_score (0.0 - 10.0)
        - completeness_score (0.0 - 10.0)
        - overall_score (0.0 - 100.0)
        """
        if not answer or not answer.strip():
            return {
                "overall_score": 0.0,
                "relevance_score": 0.0,
                "accuracy_score": 0.0,
                "clarity_score": 0.0,
                "completeness_score": 0.0,
                "strengths": [],
                "areas_for_improvement": ["No answer provided."],
                "actionable_feedback": "Please write an answer to receive pedagogical evaluation.",
                "rubric_breakdown": {
                    "relevance": "Unattempted",
                    "accuracy": "Unattempted",
                    "clarity": "Unattempted",
                    "completeness": "Unattempted"
                }
            }

        # 1. Attempt LLM evaluation if configured
        prompt = (
            f"You are an expert academic evaluator. Evaluate the student's answer to the following question:\n\n"
            f"QUESTION: {question}\n"
            f"STUDENT ANSWER: {answer}\n"
            f"{f'REFERENCE CONTEXT: {reference_context}' if reference_context else ''}\n\n"
            f"Evaluate strictly and return JSON with keys:\n"
            f"- relevance_score (0.0 to 10.0)\n"
            f"- accuracy_score (0.0 to 10.0)\n"
            f"- clarity_score (0.0 to 10.0)\n"
            f"- completeness_score (0.0 to 10.0)\n"
            f"- overall_score (0.0 to 100.0)\n"
            f"- strengths (list of strings)\n"
            f"- areas_for_improvement (list of strings)\n"
            f"- actionable_feedback (detailed string)"
        )

        llm_response = await llm_provider.generate_with_retry(
            prompt=prompt,
            generation_config={"temperature": 0.2, "max_output_tokens": 1024}
        )

        if llm_response:
            try:
                clean_json = re.sub(r"^```json\s*", "", llm_response.strip(), flags=re.MULTILINE)
                clean_json = re.sub(r"\s*```$", "", clean_json, flags=re.MULTILINE)
                parsed = json.loads(clean_json)
                return {
                    "overall_score": float(parsed.get("overall_score", 75.0)),
                    "relevance_score": float(parsed.get("relevance_score", 7.5)),
                    "accuracy_score": float(parsed.get("accuracy_score", 7.5)),
                    "clarity_score": float(parsed.get("clarity_score", 7.5)),
                    "completeness_score": float(parsed.get("completeness_score", 7.5)),
                    "strengths": list(parsed.get("strengths", ["Solid foundational grasp of the concept."])),
                    "areas_for_improvement": list(parsed.get("areas_for_improvement", ["Add more formal technical precision."])),
                    "actionable_feedback": str(parsed.get("actionable_feedback", "Good effort. Review core terminology.")),
                    "rubric_breakdown": {
                        "relevance": f"{parsed.get('relevance_score', 7.5)}/10",
                        "accuracy": f"{parsed.get('accuracy_score', 7.5)}/10",
                        "clarity": f"{parsed.get('clarity_score', 7.5)}/10",
                        "completeness": f"{parsed.get('completeness_score', 7.5)}/10"
                    }
                }
            except Exception as e:
                logger.warning(f"Failed to parse LLM answer evaluation: {e}")

        # 2. Deterministic Pedagogical Rubric Fallback
        return self._evaluate_deterministic(question, answer)

    def _evaluate_deterministic(self, question: str, answer: str) -> Dict[str, Any]:
        q_clean = question.lower().strip()
        ans_clean = answer.lower().strip()
        words = re.findall(r"\b\w{3,}\b", ans_clean)
        q_words = set(re.findall(r"\b\w{3,}\b", q_clean))

        stops = {"what", "how", "why", "the", "and", "for", "with", "that", "this", "from", "are", "can", "you", "does", "which"}
        q_keywords = q_words - stops

        overlap = len(set(words).intersection(q_keywords))
        relevance_ratio = min(1.0, overlap / max(len(q_keywords), 1))
        length_score = min(1.0, len(words) / 30.0)

        has_formatting = any(m in answer for m in ["- ", "* ", "1.", "###", "**", "```"])
        clarity_factor = 0.9 if has_formatting else 0.75

        relevance = round(min(10.0, max(3.0, (relevance_ratio * 6.0) + (length_score * 4.0))), 1)
        accuracy = round(min(10.0, max(4.0, (relevance_ratio * 5.0) + (length_score * 5.0))), 1)
        clarity = round(clarity_factor * 10.0, 1)
        completeness = round(min(10.0, max(3.0, length_score * 10.0)), 1)
        overall = round(((relevance + accuracy + clarity + completeness) / 40.0) * 100.0, 1)

        if overall >= 85:
            level = "Mastery"
        elif overall >= 70:
            level = "Proficient"
        elif overall >= 50:
            level = "Developing"
        else:
            level = "Needs Improvement"

        strengths = []
        improvements = []

        if relevance >= 7.0:
            strengths.append("Directly addresses the core subject matter of the prompt.")
        else:
            improvements.append("Ensure the explanation connects more explicitly with the target terms in the prompt.")

        if completeness >= 7.0:
            strengths.append("Provides substantive depth and elaboration on key mechanics.")
        else:
            improvements.append("Include more granular steps, edge conditions, or concrete examples to enhance completeness.")

        if has_formatting:
            strengths.append("Employs structured formatting for high readability.")
        else:
            improvements.append("Use bullet points or code/equation blocks to visually delineate distinct points.")

        if not strengths:
            strengths.append("Clear conceptual phrasing and direct terminology.")
        if not improvements:
            improvements.append("Consider exploring advanced nuances, performance implications, or comparative trade-offs.")

        feedback = (
            f"The response achieves an overall quality score of {overall}%. "
            f"{'It demonstrates a rigorous grasp of the topic.' if overall >= 75 else 'It captures several correct notions but benefits from further elaboration.'} "
            f"Focus on {'formalizing system boundaries and verifying edge cases' if overall >= 75 else 'grounding definitions with concrete illustrations and clear steps'}."
        )

        return {
            "overall_score": overall,
            "relevance_score": relevance,
            "accuracy_score": accuracy,
            "clarity_score": clarity,
            "completeness_score": completeness,
            "evaluation_level": level,
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "actionable_feedback": feedback,
            "rubric_breakdown": {
                "relevance": f"{relevance}/10",
                "accuracy": f"{accuracy}/10",
                "clarity": f"{clarity}/10",
                "completeness": f"{completeness}/10"
            }
        }

    def classify_mistake(
        self,
        question_text: str,
        user_response: str,
        correct_answer: str,
        explanation: str
    ) -> str:
        """
        Classifies an incorrect quiz answer into one of 6 standardized mistake categories.
        """
        q_lower = question_text.lower()
        if any(w in q_lower for w in ("calculate", "compute", "complexity", "big-o", "time", "space")):
            return "calculation_error"
        if any(w in q_lower for w in ("apply", "implement", "configure", "use", "when to")):
            return "incorrect_application"
        if any(w in q_lower for w in ("except", "not", "incorrect", "false", "least")):
            return "misinterpretation"
        if len(user_response.strip()) == 0:
            return "knowledge_gap"
        return "conceptual_misunderstanding"

evaluator_service = EvaluatorService()
