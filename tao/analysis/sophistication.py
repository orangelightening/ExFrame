"""
Question Sophistication Analysis - Level Classification

Classifies questions into sophistication levels (L1-L4) to measure learning progression.

Levels:
- L1: Novice - Basic "what is" questions, definitions
- L2: Intermediate - "How to" questions, comparisons
- L3: Advanced - System-level thinking, tradeoffs, design
- L4: Expert - Architecture, optimization, complex integration

Used for:
- Learning velocity calculation (L1→L4 over time)
- Tao Index computation (sophistication component)
- Hiring vetting (question depth metric)
"""

import logging
from typing import Dict, Any, Optional, List
import os
import requests
import json

logger = logging.getLogger("tao.analysis.sophistication")


class QuestionClassifier:
    """Classifies question sophistication using LLM."""

    # Sophistication level definitions
    LEVELS = {
        1: {
            "name": "Novice",
            "description": "Basic definitions, 'what is' questions, simple concepts",
            "examples": [
                "What is Python?",
                "What is a variable?",
                "What is AWS?",
                "How do I install packages?"
            ]
        },
        2: {
            "name": "Intermediate",
            "description": "How-to questions, comparisons, practical application",
            "examples": [
                "How do lists compare to tuples?",
                "What's the difference between IaaS and PaaS?",
                "When to use EC2 vs Lambda?",
                "How to handle exceptions properly?"
            ]
        },
        3: {
            "name": "Advanced",
            "description": "System-level thinking, tradeoffs, design patterns",
            "examples": [
                "How does Python's memory management work?",
                "What are the performance implications of decorators?",
                "How to design for high availability?",
                "What's the tradeoff between consistency and availability?"
            ]
        },
        4: {
            "name": "Expert",
            "description": "Architecture, optimization, complex integration, deep understanding",
            "examples": [
                "How does Python's GIL affect multi-threading?",
                "Design a multi-region active-active architecture",
                "How to implement a custom async context manager?",
                "What are the failure modes of eventual consistency?"
            ]
        }
    }

    def __init__(self, llm_config: Optional[Dict[str, str]] = None):
        """
        Initialize classifier with LLM configuration.

        Args:
            llm_config: Optional LLM config (base_url, model, api_key)
                       Falls back to environment variables if not provided
        """
        self.llm_config = llm_config or self._get_default_llm_config()

    def _get_default_llm_config(self) -> Dict[str, str]:
        """Get LLM config from environment variables."""
        return {
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
            "api_key": os.getenv("OPENAI_API_KEY", "")
        }

    def classify_question(
        self,
        question: str,
        domain: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify question sophistication level using LLM.

        Args:
            question: The question text to classify
            domain: Optional domain name (e.g., "python", "cloud")
            context: Optional additional context

        Returns:
            {
                "level": 1-4,
                "confidence": 0.0-1.0,
                "reasoning": "Why this level",
                "label": "Novice/Intermediate/Advanced/Expert"
            }
        """
        try:
            # Build classification prompt
            prompt = self._build_classification_prompt(question, domain, context)

            # Call LLM
            response = self._call_llm(prompt)

            # Parse response
            result = self._parse_classification(response)

            logger.debug(f"Classified question as L{result['level']}: {question[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Failed to classify question: {e}", exc_info=True)
            # Fallback: return L2 (intermediate) as default
            return {
                "level": 2,
                "confidence": 0.5,
                "reasoning": f"Classification failed: {str(e)}",
                "label": "Intermediate"
            }

    def _build_classification_prompt(
        self,
        question: str,
        domain: Optional[str],
        context: Optional[str]
    ) -> str:
        """Build prompt for LLM classification."""

        levels_desc = "\n\n".join([
            f"**Level {level}: {info['name']}**\n"
            f"{info['description']}\n"
            f"Examples:\n" + "\n".join([f"- {ex}" for ex in info['examples']])
            for level, info in self.LEVELS.items()
        ])

        prompt = f"""Classify the sophistication level of this question on a scale of 1-4.

{levels_desc}

Question to classify: "{question}"
"""

        if domain:
            prompt += f"\nDomain: {domain}"

        if context:
            prompt += f"\nContext: {context}"

        prompt += """

Respond in JSON format:
{
  "level": 1-4,
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of why this level"
}

Consider:
- Complexity of concepts involved
- Depth of understanding required
- Whether it asks "what" (basic) vs "how/why" (deeper) vs "design/optimize" (expert)
- System-level thinking vs isolated concepts
"""

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API for classification."""
        try:
            url = f"{self.llm_config['base_url']}/chat/completions"

            headers = {
                "Authorization": f"Bearer {self.llm_config['api_key']}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.llm_config["model"],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert at assessing question sophistication levels. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # Low temperature for consistent classification
                "max_tokens": 200
            }

            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise

    def _parse_classification(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured result."""
        try:
            # Try to extract JSON from response
            # LLM might wrap in markdown code blocks
            response_text = llm_response.strip()

            if "```json" in response_text:
                # Extract from markdown code block
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                # Generic code block
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            # Parse JSON
            data = json.loads(response_text)

            level = int(data.get("level", 2))
            confidence = float(data.get("confidence", 0.7))
            reasoning = data.get("reasoning", "No reasoning provided")

            # Clamp level to valid range
            level = max(1, min(4, level))

            return {
                "level": level,
                "confidence": confidence,
                "reasoning": reasoning,
                "label": self.LEVELS[level]["name"]
            }

        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            logger.debug(f"Raw response: {llm_response}")

            # Fallback: try to extract level from text
            for level in [4, 3, 2, 1]:  # Check highest first
                if f"level {level}" in llm_response.lower() or f"l{level}" in llm_response.lower():
                    return {
                        "level": level,
                        "confidence": 0.6,
                        "reasoning": "Extracted from text response",
                        "label": self.LEVELS[level]["name"]
                    }

            # Ultimate fallback
            return {
                "level": 2,
                "confidence": 0.5,
                "reasoning": "Could not parse response",
                "label": "Intermediate"
            }


def classify_batch(
    questions: List[str],
    domain: Optional[str] = None,
    llm_config: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Classify multiple questions at once.

    Args:
        questions: List of question strings
        domain: Optional domain name
        llm_config: Optional LLM configuration

    Returns:
        List of classification results
    """
    classifier = QuestionClassifier(llm_config)
    results = []

    for question in questions:
        result = classifier.classify_question(question, domain)
        results.append(result)

    return results


def calculate_learning_velocity(
    history: List[Dict],
    domain: Optional[str] = None,
    min_questions: int = 5
) -> Dict[str, Any]:
    """
    Calculate learning velocity from question history.

    Velocity = (final_level - initial_level) / days_elapsed

    Args:
        history: Query history entries (must have classification in metadata)
        domain: Optional domain filter
        min_questions: Minimum questions required for calculation

    Returns:
        {
            "velocity": float,  # Levels per day
            "initial_level": float,  # Average of first 3 questions
            "final_level": float,  # Average of last 3 questions
            "days_elapsed": float,
            "total_questions": int,
            "progression": [  # Level over time
                {"day": 1, "avg_level": 1.2},
                {"day": 2, "avg_level": 2.1},
                ...
            ]
        }
    """
    from datetime import datetime

    if len(history) < min_questions:
        return {
            "velocity": 0.0,
            "error": f"Insufficient questions (need {min_questions}, have {len(history)})"
        }

    try:
        # Extract questions with classification
        classified = []
        for entry in history:
            if "metadata" in entry and "question_level" in entry["metadata"]:
                classified.append({
                    "timestamp": datetime.fromisoformat(entry["timestamp"]),
                    "level": entry["metadata"]["question_level"]
                })

        if len(classified) < min_questions:
            return {
                "velocity": 0.0,
                "error": f"Insufficient classified questions (need {min_questions}, have {len(classified)})"
            }

        # Sort by timestamp
        classified.sort(key=lambda x: x["timestamp"])

        # Calculate initial and final levels
        initial_level = sum([q["level"] for q in classified[:3]]) / min(3, len(classified))
        final_level = sum([q["level"] for q in classified[-3:]]) / min(3, len(classified))

        # Calculate time elapsed
        start_time = classified[0]["timestamp"]
        end_time = classified[-1]["timestamp"]
        days_elapsed = (end_time - start_time).total_seconds() / 86400
        days_elapsed = max(days_elapsed, 0.1)  # Avoid division by zero

        # Calculate velocity
        velocity = (final_level - initial_level) / days_elapsed

        # Build progression timeline
        progression = []
        current_day = 0
        day_questions = []

        for entry in classified:
            day = int((entry["timestamp"] - start_time).total_seconds() / 86400)
            if day != current_day:
                if day_questions:
                    avg_level = sum([q["level"] for q in day_questions]) / len(day_questions)
                    progression.append({
                        "day": current_day + 1,
                        "avg_level": round(avg_level, 2),
                        "question_count": len(day_questions)
                    })
                current_day = day
                day_questions = []
            day_questions.append(entry)

        # Add last day
        if day_questions:
            avg_level = sum([q["level"] for q in day_questions]) / len(day_questions)
            progression.append({
                "day": current_day + 1,
                "avg_level": round(avg_level, 2),
                "question_count": len(day_questions)
            })

        return {
            "velocity": round(velocity, 3),
            "initial_level": round(initial_level, 2),
            "final_level": round(final_level, 2),
            "days_elapsed": round(days_elapsed, 2),
            "total_questions": len(classified),
            "progression": progression,
            "interpretation": _interpret_velocity(velocity)
        }

    except Exception as e:
        logger.error(f"Failed to calculate learning velocity: {e}", exc_info=True)
        return {
            "velocity": 0.0,
            "error": str(e)
        }


def _interpret_velocity(velocity: float) -> str:
    """Interpret learning velocity score."""
    if velocity >= 0.40:
        return "Exceptional (Top 3%)"
    elif velocity >= 0.30:
        return "Excellent (Top 10%)"
    elif velocity >= 0.20:
        return "Good (Above Average)"
    elif velocity >= 0.10:
        return "Average"
    else:
        return "Below Average"
