import os
from typing import Dict, List, Optional
import json
import requests
import time


class FinancialAgent:
    """
    AI agent for personalized financial planning using K2-Think API
    (MBZUAI-IFM/K2-Think-v2) via OpenAI-compatible chat completions endpoint.
    """

    API_URL = "https://api.k2think.ai/v1/chat/completions"
    MODEL = "MBZUAI-IFM/K2-Think-v2"

    SYSTEM_PROMPT = """You are an expert financial advisor AI. Your role is to:
1. Analyze users' financial situations objectively
2. Provide personalized, actionable recommendations
3. Explain your reasoning clearly and transparently
4. Help users understand financial concepts
5. Simulate financial scenarios and their impacts

Always be:
- Clear and concise
- Evidence-based in your recommendations
- Honest about limitations and risks
- Supportive and non-judgmental
- Focused on long-term financial health

When making recommendations:
- Explain WHY each recommendation matters
- Provide specific numbers and calculations
- Consider the user's risk tolerance
- Prioritize emergency funds and debt reduction
- Encourage sustainable habits over quick fixes"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the financial agent with K2-Think API.

        Args:
            api_key: K2-Think API key (will use K2THINK_API_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv("K2THINK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "K2-Think API key not provided. "
                "Set K2THINK_API_KEY environment variable or pass api_key parameter."
            )

        self.conversation_history: List[Dict] = []
        self.context: Dict = {}
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    # ------------------------------------------------------------------
    # Context helpers
    # ------------------------------------------------------------------

    def initialize_context(
        self,
        profile: Dict,
        transactions_summary: Dict,
        budget_plan: Optional[Dict] = None,
    ):
        """
        Initialize agent with the user's financial context.

        Args:
            profile: User's financial profile dict
            transactions_summary: Summary of transaction analysis
            budget_plan: Optimized budget plan (optional)
        """
        self.context = {
            "profile": profile,
            "transactions": transactions_summary,
            "budget": budget_plan,
        }

        # Build structured context message
        context_data = self._format_context_structured()
        context_msg = (
            f"User Financial Context:\n{json.dumps(context_data, indent=2)}\n\n"
            "I'm ready to help with financial planning questions."
        )

        # Reset history and seed with context
        self.conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": context_msg},
            {
                "role": "assistant",
                "content": "I've reviewed your financial profile. How can I help you today?",
            },
        ]

    # ------------------------------------------------------------------
    # Core chat method
    # ------------------------------------------------------------------

    def chat(self, user_message: str, stream: bool = False) -> str:
        """
        Send a message and get a response from K2-Think.

        Args:
            user_message: The user's question or request
            stream: Whether to stream the response (prints tokens live)

        Returns:
            The assistant's full response as a string
        """
        # Ensure system prompt exists
        if not self.conversation_history:
            self.conversation_history = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]

        self.conversation_history.append({"role": "user", "content": user_message})

        for attempt in range(self.max_retries):
            try:
                if stream:
                    response_text = self._call_streaming()
                else:
                    response_text = self._call_complete()

                self.conversation_history.append(
                    {"role": "assistant", "content": response_text}
                )
                return response_text

            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait = self.retry_delay * (attempt + 1)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    error_msg = f"Failed after {self.max_retries} attempts: {e}"
                    print(error_msg)
                    # Remove the user message we added since we couldn't respond
                    self.conversation_history.pop()
                    return f"I'm sorry, I encountered an error: {e}"

    # ------------------------------------------------------------------
    # API call helpers
    # ------------------------------------------------------------------

    def _build_headers(self) -> Dict:
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_payload(self, stream: bool = False) -> Dict:
        return {
            "model": self.MODEL,
            "messages": self.conversation_history,
            "stream": stream,
        }

    def _call_complete(self) -> str:
        """Non-streaming API call."""
        response = requests.post(
            self.API_URL,
            headers=self._build_headers(),
            json=self._build_payload(stream=False),
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_streaming(self) -> str:
        """Streaming API call — prints tokens live and returns full text."""
        response = requests.post(
            self.API_URL,
            headers=self._build_headers(),
            json=self._build_payload(stream=True),
            stream=True,
            timeout=60,
        )
        response.raise_for_status()

        full_text = ""
        print("\nAssistant: ", end="", flush=True)

        for line in response.iter_lines():
            if not line:
                continue
            # SSE lines look like: "data: {...}" or "data: [DONE]"
            decoded = line.decode("utf-8")
            if decoded.startswith("data:"):
                payload = decoded[len("data:"):].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        print(token, end="", flush=True)
                        full_text += token
                except (json.JSONDecodeError, KeyError):
                    continue

        print()  # newline after streaming
        return full_text

    # ------------------------------------------------------------------
    # Higher-level helpers (unchanged interface from Gemini version)
    # ------------------------------------------------------------------

    def get_recommendation(self, focus_area: str) -> str:
        """Get a detailed recommendation for a specific focus area."""
        prompt = (
            f"Based on the user's financial profile, provide a detailed recommendation "
            f"for improving their {focus_area}.\n\n"
            "Include:\n"
            "1. Current situation analysis\n"
            "2. Specific action steps\n"
            "3. Expected outcomes with numbers\n"
            "4. Timeline for implementation\n"
            "5. Potential challenges and how to overcome them\n\n"
            "Be specific and actionable."
        )
        return self.chat(prompt)

    def explain_reasoning(self, recommendation: str) -> str:
        """Explain the reasoning behind a recommendation."""
        prompt = (
            f'Explain in detail why this recommendation makes sense: "{recommendation}"\n\n'
            "Include:\n"
            "1. Financial principles behind it\n"
            "2. How it addresses the user's specific situation\n"
            "3. Expected benefits with calculations\n"
            "4. Comparison with alternatives\n"
            "5. Risk assessment"
        )
        return self.chat(prompt)

    def answer_question(self, question: str) -> str:
        """Answer a specific financial question using the loaded context."""
        prompt = (
            f"Answer this question using the user's financial context: {question}\n\n"
            "Provide:\n"
            "1. Direct answer\n"
            "2. Explanation based on their data\n"
            "3. Relevant calculations\n"
            "4. Actionable next steps if applicable"
        )
        return self.chat(prompt)

    def compare_options(self, options: List[str]) -> str:
        """Compare multiple financial options."""
        options_str = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        prompt = (
            f"Compare these financial options for the user:\n{options_str}\n\n"
            "For each option, analyze:\n"
            "1. Pros and cons\n"
            "2. Financial impact (with numbers)\n"
            "3. Suitability for their situation\n"
            "4. Short-term and long-term effects\n"
            "5. Risk level\n\n"
            "Provide a clear recommendation."
        )
        return self.chat(prompt)

    def generate_action_plan(self, goal: str, timeframe: str) -> str:
        """Generate a step-by-step action plan for a financial goal."""
        prompt = (
            f'Create a detailed action plan to achieve this goal: "{goal}" within {timeframe}.\n\n'
            "Include:\n"
            "1. Monthly savings required\n"
            "2. Budget adjustments needed\n"
            "3. Week-by-week action steps\n"
            "4. Milestones to track progress\n"
            "5. Contingency plans for setbacks\n"
            "6. Expected outcome with calculations\n\n"
            "Make it specific and realistic based on their current financial situation."
        )
        return self.chat(prompt)

    # ------------------------------------------------------------------
    # Conversation management
    # ------------------------------------------------------------------

    def reset_conversation(self):
        """Reset conversation history while keeping context."""
        context_data = self._format_context_structured()
        context_msg = (
            f"User Financial Context:\n{json.dumps(context_data, indent=2)}\n\n"
            "I'm ready to help with financial planning questions."
        )
        self.conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": context_msg},
            {
                "role": "assistant",
                "content": "I've reviewed your financial profile. How can I help you today?",
            },
        ]

    def export_conversation(self, filepath: str):
        """Save conversation history to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.conversation_history, f, indent=2)
        print(f"Conversation exported to {filepath}")

    def get_conversation_summary(self) -> str:
        """Ask the model to summarise the conversation so far."""
        user_messages = [
            m["content"]
            for m in self.conversation_history
            if m["role"] == "user"
        ]
        prompt = (
            "Summarize this financial planning conversation in 3-4 bullet points:\n\n"
            "User asked about:\n"
            + "\n".join(f"- {msg}" for msg in user_messages)
            + "\n\nFocus on key recommendations made and action items."
        )
        return self.chat(prompt)

    def get_token_usage_estimate(self) -> Dict:
        """Rough token-usage estimate based on character count."""
        total_chars = sum(len(m["content"]) for m in self.conversation_history)
        return {
            "messages": len(self.conversation_history),
            "estimated_tokens": int(total_chars / 4),
            "note": "Rough estimate (~4 chars per token).",
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _format_context_structured(self) -> Dict:
        """Return a clean dict of the loaded financial context."""
        if not self.context:
            return {"message": "No financial context loaded"}

        profile = self.context.get("profile", {})
        budget = self.context.get("budget", {})

        return {
            "income": {
                "monthly_income": profile.get("monthly_income", 0),
                "income_stability": profile.get("income_stability", 0),
            },
            "expenses": {
                "monthly_expenses": profile.get("monthly_expenses", 0),
                "essential_expenses": profile.get("essential_expenses", 0),
                "discretionary_expenses": profile.get("discretionary_expenses", 0),
                "by_category": profile.get("expense_categories", {}),
            },
            "savings": {
                "monthly_savings": profile.get("monthly_savings", 0),
                "savings_rate": profile.get("savings_rate", 0),
                "emergency_fund_months": profile.get("emergency_fund_months", 0),
            },
            "debt": {
                "total_debt": profile.get("total_debt", 0),
                "monthly_payment": profile.get("monthly_debt_payment", 0),
                "debt_to_income_ratio": profile.get("debt_to_income_ratio", 0),
            },
            "risk": {
                "risk_tolerance": profile.get("risk_tolerance", "unknown"),
                "spending_volatility": profile.get("spending_volatility", 0),
            },
            "budget_plan": budget or None,
        }
