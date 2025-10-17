"""
AI Service Module for AI-Powered Quiz System

This module handles all interactions with LLM providers for:
- Dynamic quiz question generation
- Intelligent explanations and feedback
- Personalized learning recommendations

Supported providers:
- Deepseek (primary when configured with DEEPSEEK_API_KEY and DEEPSEEK_MODEL)
- OpenAI (fallback or primary when Deepseek not configured)

Supported client versions:
- Deepseek: Via direct HTTP API calls
- OpenAI: Modern client (openai>=1.0.0) and legacy client with fallbacks
"""

import os
import json
import logging
import requests
import httpx
from typing import Dict, List, Optional, Any
from django.conf import settings

# Try to support both the modern OpenAI client and the legacy openai module
try:
    from openai import OpenAI as ModernOpenAI
except Exception:
    ModernOpenAI = None
try:
    import openai as openai_legacy
except Exception:
    openai_legacy = None

logger = logging.getLogger(__name__)


class OpenAIQuizService:
    """Service class for OpenAI-powered quiz functionality"""

    def __init__(self):
        """Initialize OpenAI client with API key from settings"""
        # Load OpenAI API key (if any)
        api_key = getattr(settings, "OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

        # Deepseek support (optional). If DEEPSEEK_API_KEY is present, prefer Deepseek
        self.deepseek_api_key = getattr(settings, "DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY"))
        # Deepseek base URL (assumption): default to example endpoint if not provided
        self.deepseek_base = getattr(
            settings, "DEEPSEEK_API_BASE", os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.ai")
        )
        self.use_deepseek = bool(self.deepseek_api_key)

        # No hard-coded OpenAI model default; use configured model if present.
        self.model = getattr(settings, "OPENAI_MODEL", None)

        # OpenAI client state
        self.use_modern_client = False
        self.client = None
        # If direct HTTP fallback is possible (when client instantiation fails), store the API key for direct REST calls.
        self._http_api_key = api_key

        # Try to initialize modern OpenAI client only if api_key and model are configured
        if ModernOpenAI and api_key and self.model:
            try:
                # modern client: try to construct with a dedicated httpx client that does not inherit environment proxies (trust_env=False).
                try:
                    http_client = httpx.Client(timeout=60.0, trust_env=False)
                    self.client = ModernOpenAI(api_key=api_key, http_client=http_client)
                except Exception:
                    # fallback to passing only api_key
                    self.client = ModernOpenAI(api_key=api_key)
                self.use_modern_client = True
            except Exception as e:
                logger.warning(f"Modern OpenAI client init failed: {e}")
                self.client = None
                self.use_modern_client = False

        # If modern client not available, try legacy module (best-effort).
        if not self.client and openai_legacy and api_key:
            try:
                openai_legacy.api_key = api_key
                self.client = openai_legacy
                self.use_modern_client = False
            except Exception as e:
                logger.warning(f"Legacy openai module init failed: {e}")

        if not self.client and not self.use_deepseek:
            logger.warning(
                "No OpenAI client available and Deepseek not configured; AI features will use fallback methods."
            )

        if self.use_deepseek:
            logger.info("Deepseek provider configured and will be preferred for generation.")

    def generate_quiz_questions(
        self, category: str, difficulty: str = "intermediate", count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for a specific category using OpenAI

        Args:
            category (str): The quiz category (python, web-development, sql, php)
            difficulty (str): Difficulty level (beginner, intermediate, advanced)
            count (int): Number of questions to generate

        Returns:
            List[Dict]: List of generated questions with options and explanations
        """
        try:
            self._ensure_client()
            prompt = self._build_question_generation_prompt(category, difficulty, count)

            response = None

            # Prefer Deepseek if configured
            if self.use_deepseek:
                try:
                    deepseek_resp = self._call_deepseek_via_http(
                        prompt, temperature=0.7, max_tokens=2000
                    )
                    # Extract text from Deepseek response (similar to OpenAI format)
                    ds_text = None
                    if isinstance(deepseek_resp, dict):
                        choices = deepseek_resp.get("choices", [])
                        if choices and len(choices) > 0:
                            if isinstance(choices[0], dict):
                                message = choices[0].get("message", {})
                                if isinstance(message, dict):
                                    ds_text = message.get("content")

                    if ds_text:
                        questions = self._parse_questions_response(ds_text)
                        if questions:
                            logger.info(f"Generated {len(questions)} questions via Deepseek")
                            return questions[:count]
                except Exception as e:
                    logger.warning(f"Deepseek call failed: {e}, falling back to other providers")

            # Call the OpenAI API using the available client
            if self.use_modern_client and self.client:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert educator and quiz creator. Generate high-quality, educational quiz questions with detailed explanations.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.7,
                        max_tokens=2000,
                    )
                except Exception as e:
                    logger.warning(f"Modern client call failed: {e}")
                    response = None

            # If modern client not used or failed, try HTTP fallback
            if response is None and self._http_api_key:
                try:
                    response = self._call_openai_via_http(
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert educator and quiz creator. Generate high-quality, educational quiz questions with detailed explanations.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.7,
                        max_tokens=2000,
                    )
                except Exception as e:
                    logger.warning(f"HTTP OpenAI call failed: {e}")
                    response = None

            # If HTTP fallback not used or failed, attempt legacy client
            if response is None and self.client and not self.use_modern_client:
                try:
                    response = self.client.ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert educator and quiz creator. Generate high-quality, educational quiz questions with detailed explanations.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.7,
                        max_tokens=2000,
                    )
                except Exception as e:
                    logger.warning(f"Legacy openai call failed: {e}")
                    response = None

            # Parse the response and convert to structured format
            questions_text = self._extract_response_content(response) or ""
            questions = self._parse_questions_response(questions_text)

            # If no questions produced, return fallback questions up to 'count'
            if not questions:
                return self._get_fallback_questions(category, count)

            logger.info(f"Generated {len(questions)} questions for category: {category}")
            # Trim or pad to requested count
            if len(questions) >= count:
                return questions[:count]
            else:
                # If fewer returned, append fallback questions to reach count
                extras = self._get_fallback_questions(category, count - len(questions))
                return questions + extras

        except Exception as e:
            logger.error(f"Error generating quiz questions: {str(e)}")
            return self._get_fallback_questions(category, count)

    def generate_explanation(
        self, question: str, user_answer: str, correct_answer: str, is_correct: bool
    ) -> str:
        """
        Generate an explanation for a user's answer to a question.

        Args:
            question (str): The question text
            user_answer (str): The user's answer text
            correct_answer (str): The correct answer
            is_correct (bool): Whether user's answer was correct

        Returns:
            str: AI-generated explanation
        """
        try:
            self._ensure_client()
            prompt = f"""
            Question: {question}
            User's Answer: {user_answer}
            Correct Answer: {correct_answer}
            Result: {"Correct" if is_correct else "Incorrect"}

            Provide a clear, encouraging explanation that:
            1. Explains why the correct answer is right
            2. If incorrect, explains the mistake gently
            3. Provides additional learning context
            4. Encourages continued learning

            Keep it concise but informative (2-3 sentences).
            """

            if self.use_deepseek:
                try:
                    ds_resp = self._call_deepseek_via_http(prompt, temperature=0.6, max_tokens=300)
                    ds_text = None
                    if isinstance(ds_resp, dict):
                        choices = ds_resp.get("choices", [])
                        if choices and len(choices) > 0:
                            if isinstance(choices[0], dict):
                                message = choices[0].get("message", {})
                                if isinstance(message, dict):
                                    ds_text = message.get("content")

                    if ds_text:
                        return ds_text.strip()
                except Exception as e:
                    logger.warning(
                        f"Deepseek explanation call failed: {e}, falling back to other providers"
                    )

            if self.use_modern_client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a supportive AI tutor. Provide clear, encouraging explanations that help students learn from their answers.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.6,
                    max_tokens=300,
                )
            else:
                # Prefer HTTP fallback if available
                if self._http_api_key:
                    try:
                        response = self._call_openai_via_http(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a supportive AI tutor. Provide clear, encouraging explanations that help students learn from their answers.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                            temperature=0.6,
                            max_tokens=300,
                        )
                    except Exception as e:
                        logger.warning(f"HTTP OpenAI call failed: {e}")
                        response = None

                if response is None and self.client:
                    try:
                        response = self.client.ChatCompletion.create(
                            model=self.model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a supportive AI tutor. Provide clear, encouraging explanations that help students learn from their answers.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                            temperature=0.6,
                            max_tokens=300,
                        )
                    except Exception as e:
                        logger.warning(f"Legacy openai explanation call failed: {e}")
                        # fallback explanation
                        if is_correct:
                            return "Excellent work! You demonstrated a solid understanding of this concept."
                        else:
                            return f"The correct answer is '{correct_answer}'. This is a great learning opportunity!"

            return (self._extract_response_content(response) or "").strip()

        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            # fallback explanation
            if is_correct:
                return "Excellent work! You demonstrated a solid understanding of this concept."
            else:
                return f"The correct answer is '{correct_answer}'. This is a great learning opportunity!"

    def generate_performance_assessment(
        self, score: int, total: int, category: str, time_taken: Optional[int] = None
    ) -> str:
        """
        Generate personalized performance assessment and recommendations

        Args:
            score (int): User's score
            total (int): Total possible score
            category (str): Quiz category
            time_taken (int, optional): Time taken in seconds

        Returns:
            str: AI-generated performance assessment
        """
        try:
            self._ensure_client()
            percentage = round((score / total) * 100)
            time_info = f" in {time_taken} seconds" if time_taken else ""

            prompt = f"""
            A student completed a {category} quiz with the following results:
            - Score: {score}/{total} ({percentage}%)
            - Time taken: {time_info if time_info else "Not recorded"}
            
            Provide a personalized assessment that:
            1. Acknowledges their performance level
            2. Gives specific learning recommendations for {category}
            3. Provides encouragement and next steps
            4. Suggests areas for improvement if needed
            
            Keep it motivational and actionable (2-3 sentences).
            """

            if self.use_deepseek:
                try:
                    ds_resp = self._call_deepseek_via_http(prompt, temperature=0.7, max_tokens=250)
                    ds_text = None
                    if isinstance(ds_resp, dict):
                        choices = ds_resp.get("choices", [])
                        if choices and len(choices) > 0:
                            if isinstance(choices[0], dict):
                                message = choices[0].get("message", {})
                                if isinstance(message, dict):
                                    ds_text = message.get("content")

                    if ds_text:
                        return ds_text.strip()
                except Exception as e:
                    logger.warning(
                        f"Deepseek performance assessment call failed: {e}, falling back to other providers"
                    )

            if self.use_modern_client:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an encouraging AI learning coach. Provide personalized, actionable feedback that motivates continued learning.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                    max_tokens=250,
                )
            else:
                # Prefer HTTP fallback if available
                if self._http_api_key:
                    try:
                        response = self._call_openai_via_http(
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are an encouraging AI learning coach. Provide personalized, actionable feedback that motivates continued learning.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                            temperature=0.7,
                            max_tokens=250,
                        )
                    except Exception as e:
                        logger.warning(f"HTTP OpenAI call failed: {e}")
                        response = None

                if response is None and self.client:
                    try:
                        response = self.client.ChatCompletion.create(
                            model=self.model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are an encouraging AI learning coach. Provide personalized, actionable feedback that motivates continued learning.",
                                },
                                {"role": "user", "content": prompt},
                            ],
                            temperature=0.7,
                            max_tokens=250,
                        )
                    except Exception as e:
                        logger.warning(f"Legacy openai performance call failed: {e}")
                        response = None

            return (self._extract_response_content(response) or "").strip()

        except Exception as e:
            logger.error(f"Error generating performance assessment: {str(e)}")
            # Return fallback assessment
            if percentage >= 80:
                return f"Outstanding performance! You've mastered {category} fundamentals. Consider exploring advanced topics next."
            elif percentage >= 60:
                return f"Good progress in {category}! Focus on the areas you missed and try some practice exercises."
            else:
                return f"Keep learning! {category} takes practice. Review the fundamentals and try again."

    def _build_question_generation_prompt(self, category: str, difficulty: str, count: int) -> str:
        """Build the prompt for question generation"""
        category_contexts = {
            "python": "Python programming language concepts, syntax, data structures, and best practices",
            "web-development": "HTML, CSS, JavaScript, DOM manipulation, and web development concepts",
            "sql": "SQL database queries, data manipulation, table relationships, and database management",
            "php": "PHP server-side programming, syntax, functions, and web application development",
        }

        context = category_contexts.get(category, f"{category} programming concepts")

        return f"""
        Generate {count} multiple-choice quiz questions about {context}.
        
        Requirements:
        - Difficulty level: {difficulty}
        - Each question should have 4 options (A, B, C, D)
        - Include detailed explanations for the correct answers
        - Questions should be practical and test real understanding
        - Avoid trick questions, focus on educational value
        
        Format the response as JSON with this structure:
        [
            {{
                "question": "Question text here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 0,
                "explanation": "Detailed explanation of why this answer is correct and educational context."
            }}
        ]
        """

    def _parse_questions_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse OpenAI response into structured question format"""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find("[")
            end_idx = response_text.rfind("]") + 1

            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx]
                questions = json.loads(json_text)
                return questions
            else:
                logger.error("Could not find JSON in OpenAI response")
                return []

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing OpenAI response as JSON: {str(e)}")
            return []

    def _call_openai_via_http(self, messages, temperature=0.7, max_tokens=1000) -> Optional[dict]:
        """
        Minimal HTTP fallback to call the OpenAI chat completions endpoint using requests.
        Returns the parsed JSON response dict or raises on HTTP errors.
        """
        if not self._http_api_key:
            raise RuntimeError("No API key available for HTTP fallback")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._http_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def _call_deepseek_via_http(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000
    ) -> Optional[dict]:
        """
        Deepseek API call implementation. Uses Deepseek's API which is similar to OpenAI's.
        """
        if not self.deepseek_api_key:
            raise RuntimeError("No Deepseek API key configured")

        # Using Deepseek's chat completions endpoint
        url = f"{self.deepseek_base.rstrip('/')}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json",
        }

        # Get the configured Deepseek model or use default
        deepseek_model = getattr(
            settings, "DEEPSEEK_MODEL", os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        )

        # Format the request like OpenAI's chat completion API
        payload = {
            "model": deepseek_model,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def _ensure_client(self) -> bool:
        """Ensure an OpenAI client is available. Returns True if client exists, False otherwise."""
        if not self.client:
            logger.warning("OpenAI client not initialized; using fallback behavior.")
            return False
        return True

    def _extract_response_content(self, response: Any) -> Optional[str]:
        """Normalize different OpenAI response shapes and extract the assistant text content."""
        try:
            # modern client: response.choices[0].message.content
            if hasattr(response, "choices") and len(response.choices) > 0:
                choice0 = response.choices[0]
                # choice may be object with message attribute
                if hasattr(choice0, "message") and hasattr(choice0.message, "content"):
                    return choice0.message.content
                # choice may be dict-like
                if isinstance(choice0, dict):
                    msg = choice0.get("message") or choice0.get("delta") or {}
                    if isinstance(msg, dict):
                        return msg.get("content") or msg.get("text")
                # older style: choice0.text
                if hasattr(choice0, "text"):
                    return choice0.text

            # legacy: response['choices'][0]['message']['content'] or .text
            if isinstance(response, dict):
                choices = response.get("choices")
                if choices and len(choices) > 0:
                    c0 = choices[0]
                    if isinstance(c0, dict):
                        msg = c0.get("message") or c0.get("delta") or {}
                        if isinstance(msg, dict):
                            return msg.get("content") or msg.get("text")
                        return c0.get("text")

        except Exception as e:
            logger.debug(f"Error extracting response content: {e}")
        return None

    def _get_fallback_questions(self, category: str) -> List[Dict[str, Any]]:
        """Return fallback questions if API fails"""

    def _get_fallback_questions(self, category: str, count: int = 1) -> List[Dict[str, Any]]:
        """Return up to `count` fallback questions for the given category.

        The function will cycle a small builtin pool to satisfy the requested count.
        """
        pool = {
            "python": [
                {
                    "question": "What is the correct way to create a list in Python?",
                    "options": ["list = []", "list = ()", "list = {}", "list = ''"],
                    "correct": 0,
                    "explanation": "Lists in Python are created using square brackets []. This creates an empty list that can store multiple items.",
                }
            ],
            "web-development": [
                {
                    "question": "What does HTML stand for?",
                    "options": [
                        "Hyper Text Markup Language",
                        "High Tech Modern Language",
                        "Home Tool Markup Language",
                        "Hyperlink Text Markup Language",
                    ],
                    "correct": 0,
                    "explanation": "HTML stands for HyperText Markup Language, the standard markup language for creating web pages.",
                }
            ],
            "sql": [
                {
                    "question": "Which SQL command is used to retrieve data?",
                    "options": ["GET", "SELECT", "RETRIEVE", "FETCH"],
                    "correct": 1,
                    "explanation": "The SELECT command is the standard SQL statement used to retrieve data from database tables.",
                }
            ],
            "php": [
                {
                    "question": "How do you start a PHP script?",
                    "options": ["<php>", "<?php", "<script>", "<?"],
                    "correct": 1,
                    "explanation": "PHP scripts begin with the opening tag <?php which tells the server to process the following code as PHP.",
                }
            ],
        }
        # Build a simple pool list and repeat/cycle if count > pool size
        items = pool.get(category, [])
        if not items:
            return []
        result = []
        i = 0
        while len(result) < count:
            result.append(items[i % len(items)])
            i += 1
        return result


# Global instance for easy import (lazy initialization)
_openai_quiz_service = None


def get_openai_quiz_service():
    """Get OpenAI quiz service instance with lazy initialization"""
    global _openai_quiz_service
    if _openai_quiz_service is None:
        try:
            _openai_quiz_service = OpenAIQuizService()
        except Exception as e:
            logger.error(f"Failed to create OpenAI service: {str(e)}")
            # Return a mock service that uses fallback methods
            _openai_quiz_service = OpenAIQuizService.__new__(OpenAIQuizService)
            _openai_quiz_service.client = None
            _openai_quiz_service.model = None
    return _openai_quiz_service


# Create a safe default instance for imports
class SafeOpenAIService:
    """Safe wrapper that won't fail on import"""

    def __getattr__(self, name):
        return getattr(get_openai_quiz_service(), name)


openai_quiz_service = SafeOpenAIService()
