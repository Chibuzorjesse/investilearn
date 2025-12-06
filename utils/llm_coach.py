"""Local LLM-powered investment education coach using Ollama"""

import logging
from typing import Any

try:
    import ollama

    _OLLAMA_AVAILABLE = True
except ImportError:
    _OLLAMA_AVAILABLE = False
    ollama = None
    logging.warning("Ollama not available. Install with: uv add ollama")

logger = logging.getLogger(__name__)


class InvestmentCoach:
    """AI coach for investment education using local LLM via Ollama"""

    def __init__(self, model: str = "qwen2.5:14b"):
        """
        Initialize the investment coach

        Args:
            model: Ollama model name (default: qwen2.5:14b)
        """
        self.model = model
        self.system_prompt = (
            "You are an investment education coach helping beginners "
            "learn fundamental investing concepts.\\n\\n"
            "Your role:\\n"
            "- Explain financial metrics and ratios in simple terms\\n"
            "- Provide context-specific insights based on company data\\n"
            "- Use analogies and examples to make concepts clear\\n"
            "- Always emphasize you provide education, NOT advice\\n\\n"
            "Guidelines:\\n"
            "- Keep responses concise (2-3 short paragraphs max)\\n"
            "- Use simple language, avoid jargon when possible\\n"
            "- Reference the specific company/data when relevant\\n"
            "- End with a question to encourage learning\\n"
            "- Never recommend buying or selling stocks\\n"
            "- Always remind users to do their own research\\n\\n"
            "Tone: Friendly, educational, encouraging"
        )

    def check_availability(self) -> tuple[bool, str]:
        """
        Check if Ollama and the model are available

        Returns:
            (available, message) tuple
        """
        if not _OLLAMA_AVAILABLE or ollama is None:
            return False, "Ollama library not installed"

        try:
            # Check if Ollama is running and get models
            models_response = ollama.list()

            # Extract model names - response is a dict with 'models' key
            models_list = models_response.get("models", [])
            if not models_list:
                # No models installed
                msg = f"No models found. Run: ollama pull {self.model}"
                return (False, msg)

            # Model names can be in 'name' or 'model' field
            model_names = [m.get("name", m.get("model", "")) for m in models_list]

            if not any(self.model in name for name in model_names):
                msg = f"Model {self.model} not found. Run: ollama pull {self.model}"
                return (False, msg)

            return True, "Ready"

        except ConnectionError as e:
            msg = f"Ollama not running. Start with: ollama serve ({str(e)})"
            return False, msg
        except Exception as e:  # noqa: BLE001
            msg = f"Error checking Ollama: {str(e)}"
            return False, msg

    def ask(
        self,
        question: str,
        context: dict[str, Any] | None = None,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        Ask the coach a question with optional context

        Args:
            question: User's question
            context: Optional context (company data, ratios, etc.)
            conversation_history: Previous messages for context

        Returns:
            Dictionary with response, confidence, and metadata
        """
        available, message = self.check_availability()
        if not available:
            return {
                "response": f"❌ Coach unavailable: {message}",
                "confidence": "unavailable",
                "error": message,
            }

        try:
            # Build context-aware user message
            user_message = self._build_context_message(question, context)

            # Build message history
            messages = [{"role": "system", "content": self.system_prompt}]

            if conversation_history:
                messages.extend(conversation_history[-6:])  # Last 3 exchanges

            messages.append({"role": "user", "content": user_message})

            # Call Ollama with streaming disabled for simplicity
            assert ollama is not None  # Type narrowing  # nosec B101
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.7,  # Balanced creativity/accuracy
                    "top_p": 0.9,
                    "num_predict": 500,  # Max tokens ~2-3 paragraphs
                },
            )

            answer = response["message"]["content"]

            # Calculate confidence based on response characteristics
            confidence = self._estimate_confidence(answer, context)

            return {
                "response": answer,
                "confidence": confidence,
                "model": self.model,
                "context_used": context is not None,
            }

        except ConnectionError as e:
            logger.error("Coach connection error: %s", str(e))
            return {
                "response": f"❌ Cannot connect to Ollama: {str(e)}",
                "confidence": "error",
                "error": str(e),
            }
        except Exception as e:  # noqa: BLE001
            logger.error("Coach error: %s", str(e))
            return {
                "response": f"❌ Error generating response: {str(e)}",
                "confidence": "error",
                "error": str(e),
            }

    def _build_context_message(self, question: str, context: dict[str, Any] | None) -> str:
        """Build user message with relevant context"""
        if not context:
            return question

        parts = [question, "\n\nRelevant context:"]

        # Add company info
        if "company_name" in context:
            parts.append(f"- Company: {context['company_name']}")
        if "ticker" in context:
            parts.append(f"- Ticker: {context['ticker']}")
        if "sector" in context:
            parts.append(f"- Sector: {context['sector']}")

        # Add specific metric if provided
        if "metric_name" in context and "metric_value" in context:
            parts.append(f"- {context['metric_name']}: {context['metric_value']}")

        # Add industry comparison if available
        if "industry_avg" in context:
            parts.append(f"- Industry average: {context['industry_avg']}")

        return "\n".join(parts)

    def _estimate_confidence(self, response: str, context: dict[str, Any] | None) -> str:
        """
        Estimate confidence level based on response characteristics

        Returns: "high", "medium", or "low"
        """
        # Check for uncertainty markers
        uncertainty_words = [
            "might",
            "could be",
            "possibly",
            "unclear",
            "difficult to say",
            "depends on",
        ]
        confidence_words = [
            "generally",
            "typically",
            "usually",
            "indicates",
            "suggests",
        ]

        uncertainty_count = sum(1 for word in uncertainty_words if word in response.lower())
        confidence_count = sum(1 for word in confidence_words if word in response.lower())

        # Factor in context availability
        has_context = context is not None and len(context) > 0

        # Calculate confidence
        if has_context and confidence_count > uncertainty_count:
            return "high"
        elif uncertainty_count > 2:
            return "low"
        else:
            return "medium"


def get_coach(model: str = "qwen2.5:14b") -> InvestmentCoach:
    """
    Get or create an investment coach instance

    Args:
        model: Ollama model name

    Returns:
        InvestmentCoach instance
    """
    return InvestmentCoach(model=model)
