import os
from typing import Dict, List, Optional
import json
import google.generativeai as genai
import time


class FinancialAgent:
    """
    AI agent for personalized financial planning using Google Gemini API.
    """
    
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

    # Define tools for function calling
    TOOLS = [
        {
            "function_declarations": [
                {
                    "name": "calculate_savings_potential",
                    "description": "Calculate potential savings based on current spending patterns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target_category": {
                                "type": "string",
                                "description": "The spending category to analyze"
                            },
                            "reduction_percent": {
                                "type": "number",
                                "description": "Percentage reduction to simulate"
                            }
                        },
                        "required": ["target_category", "reduction_percent"]
                    }
                },
                {
                    "name": "simulate_loan_impact",
                    "description": "Simulate the impact of taking a loan on monthly budget",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "loan_amount": {
                                "type": "number",
                                "description": "Total loan amount"
                            },
                            "interest_rate": {
                                "type": "number",
                                "description": "Annual interest rate percentage"
                            },
                            "tenure_months": {
                                "type": "number",
                                "description": "Loan tenure in months"
                            }
                        },
                        "required": ["loan_amount", "interest_rate", "tenure_months"]
                    }
                },
                {
                    "name": "check_goal_feasibility",
                    "description": "Check if a financial goal is achievable with current savings rate",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "goal_amount": {
                                "type": "number",
                                "description": "Target amount for the goal"
                            },
                            "target_months": {
                                "type": "number",
                                "description": "Months to achieve the goal"
                            }
                        },
                        "required": ["goal_amount", "target_months"]
                    }
                }
            ]
        }
    ]

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the financial agent with Google Gemini API.
        
        Args:
            api_key: Google API key (will use env var if not provided)
            model: Gemini model to use (default: gemini-2.0-flash-exp for latest)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key not provided. Set GEMINI_API_KEY or GOOGLE_API_KEY")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model with system instruction
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=self.SYSTEM_PROMPT,
            tools=self.TOOLS
        )
        
        self.chat_session = None
        self.context = {}
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
    def initialize_context(self, 
                          profile: Dict,
                          transactions_summary: Dict,
                          budget_plan: Optional[Dict] = None):
        """
        Initialize agent with user's financial context.
        
        Args:
            profile: User's financial profile
            transactions_summary: Summary of transaction analysis
            budget_plan: Optimized budget plan
        """
        self.context = {
            'profile': profile,
            'transactions': transactions_summary,
            'budget': budget_plan
        }
        
        # Create structured context for the agent
        context_msg = self._format_context_structured()
        
        # Start new chat session with context
        initial_message = f"User Financial Context:\n{json.dumps(context_msg, indent=2)}\n\nI'm ready to help with financial planning questions."
        self.chat_session = self.model.start_chat(history=[])
        
        # Send context as first message
        response = self.chat_session.send_message(initial_message)
        
    def chat(self, user_message: str, stream: bool = False) -> str:
        """
        Process user message and generate response with function calling support.
        
        Args:
            user_message: User's question or request
            stream: Whether to stream the response
            
        Returns:
            Agent's response
        """
        if self.chat_session is None:
            # Initialize with empty context if not already done
            self.initialize_context({}, {}, None)
        
        # Generate response with retry logic
        for attempt in range(self.max_retries):
            try:
                if stream:
                    return self._chat_streaming(user_message)
                else:
                    return self._chat_complete(user_message)
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    return f"I apologize, but I encountered an error after {self.max_retries} attempts: {str(e)}"
    
    def _chat_complete(self, user_message: str) -> str:
        """Complete chat without streaming."""
        response = self.chat_session.send_message(user_message)
        
        # Handle function calling
        while response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            function_args = dict(function_call.args)
            
            # Execute the function
            function_response = self._execute_tool(function_name, function_args)
            
            # Send function response back to model
            response = self.chat_session.send_message(
                genai.protos.Content(
                    parts=[genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=function_name,
                            response={"result": function_response}
                        )
                    )]
                )
            )
        
        return response.text
    
    def _chat_streaming(self, user_message: str) -> str:
        """Chat with streaming response."""
        response = self.chat_session.send_message(user_message, stream=True)
        
        full_response = ""
        print("\nAssistant: ", end="", flush=True)
        
        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)
                full_response += chunk.text
        
        print()  # New line after streaming
        
        return full_response
    
    def _execute_tool(self, function_name: str, arguments: Dict) -> Dict:
        """
        Execute a tool function and return results.
        
        Args:
            function_name: Name of the function to execute
            arguments: Function arguments
            
        Returns:
            Function execution results
        """
        if function_name == "calculate_savings_potential":
            return self._calculate_savings_potential(
                arguments.get("target_category"),
                arguments.get("reduction_percent")
            )
        
        elif function_name == "simulate_loan_impact":
            return self._simulate_loan_impact(
                arguments.get("loan_amount"),
                arguments.get("interest_rate"),
                arguments.get("tenure_months")
            )
        
        elif function_name == "check_goal_feasibility":
            return self._check_goal_feasibility(
                arguments.get("goal_amount"),
                arguments.get("target_months")
            )
        
        return {"error": f"Unknown function: {function_name}"}
    
    def _calculate_savings_potential(self, category: str, reduction_percent: float) -> Dict:
        """Calculate savings potential from reducing a category."""
        if not self.context.get('profile'):
            return {"error": "No profile data available"}
        
        categories = self.context['profile'].get('expense_categories', {})
        if category not in categories:
            return {"error": f"Category '{category}' not found"}
        
        current_amount = categories[category]
        reduction_amount = current_amount * (reduction_percent / 100)
        monthly_savings_increase = reduction_amount
        annual_savings_increase = reduction_amount * 12
        
        new_savings_rate = (
            (self.context['profile']['monthly_savings'] + reduction_amount) /
            self.context['profile']['monthly_income'] * 100
        )
        
        return {
            "category": category,
            "current_spending": current_amount,
            "reduction_percent": reduction_percent,
            "monthly_reduction": reduction_amount,
            "annual_savings": annual_savings_increase,
            "new_savings_rate": new_savings_rate,
            "current_savings_rate": self.context['profile']['savings_rate']
        }
    
    def _simulate_loan_impact(self, loan_amount: float, interest_rate: float, 
                             tenure_months: int) -> Dict:
        """Simulate loan EMI impact on budget."""
        if not self.context.get('profile'):
            return {"error": "No profile data available"}
        
        # Calculate EMI
        monthly_rate = interest_rate / 12 / 100
        emi = loan_amount * monthly_rate * (1 + monthly_rate)**tenure_months / (
            ((1 + monthly_rate)**tenure_months - 1)
        )
        
        total_payment = emi * tenure_months
        total_interest = total_payment - loan_amount
        
        # Impact on finances
        profile = self.context['profile']
        new_monthly_savings = profile['monthly_savings'] - emi
        new_savings_rate = (new_monthly_savings / profile['monthly_income']) * 100
        new_debt_to_income = (
            (profile.get('monthly_debt_payment', 0) + emi) / profile['monthly_income']
        )
        
        return {
            "loan_amount": loan_amount,
            "monthly_emi": emi,
            "tenure_months": tenure_months,
            "total_payment": total_payment,
            "total_interest": total_interest,
            "new_monthly_savings": new_monthly_savings,
            "new_savings_rate": new_savings_rate,
            "new_debt_to_income_ratio": new_debt_to_income,
            "feasible": new_savings_rate > 5 and new_debt_to_income < 0.5
        }
    
    def _check_goal_feasibility(self, goal_amount: float, target_months: int) -> Dict:
        """Check if a financial goal is feasible."""
        if not self.context.get('profile'):
            return {"error": "No profile data available"}
        
        profile = self.context['profile']
        monthly_required = goal_amount / target_months
        current_savings = profile['monthly_savings']
        shortfall = monthly_required - current_savings
        
        feasible = shortfall <= 0
        
        if not feasible:
            # Calculate required expense reduction
            expense_reduction_needed = shortfall
            expense_reduction_percent = (
                expense_reduction_needed / profile['monthly_expenses'] * 100
            )
        else:
            expense_reduction_needed = 0
            expense_reduction_percent = 0
        
        return {
            "goal_amount": goal_amount,
            "target_months": target_months,
            "monthly_required": monthly_required,
            "current_monthly_savings": current_savings,
            "monthly_shortfall": max(0, shortfall),
            "feasible": feasible,
            "expense_reduction_needed": expense_reduction_needed,
            "expense_reduction_percent": expense_reduction_percent,
            "alternative_months": int(goal_amount / current_savings) if current_savings > 0 else None
        }
    
    def get_recommendation(self, focus_area: str) -> str:
        """
        Get specific recommendation for a focus area.
        
        Args:
            focus_area: Area to focus on (savings, debt, budget, etc.)
            
        Returns:
            Detailed recommendation
        """
        prompt = f"""Based on the user's financial profile, provide a detailed recommendation for improving their {focus_area}.

Include:
1. Current situation analysis
2. Specific action steps
3. Expected outcomes with numbers
4. Timeline for implementation
5. Potential challenges and how to overcome them

Be specific and actionable."""

        return self.chat(prompt)
    
    def explain_reasoning(self, recommendation: str) -> str:
        """
        Explain the reasoning behind a recommendation.
        
        Args:
            recommendation: The recommendation to explain
            
        Returns:
            Detailed explanation
        """
        prompt = f"""Explain in detail why this recommendation makes sense: "{recommendation}"

Include:
1. Financial principles behind it
2. How it addresses the user's specific situation
3. Expected benefits with calculations
4. Comparison with alternatives
5. Risk assessment"""

        return self.chat(prompt)
    
    def answer_question(self, question: str) -> str:
        """
        Answer a specific financial question.
        
        Args:
            question: User's question
            
        Returns:
            Answer with explanation
        """
        enhanced_question = f"""Answer this question using the user's financial context: {question}

Provide:
1. Direct answer
2. Explanation based on their data
3. Relevant calculations
4. Actionable next steps if applicable"""

        return self.chat(enhanced_question)
    
    def compare_options(self, options: List[str]) -> str:
        """
        Compare multiple financial options.
        
        Args:
            options: List of options to compare
            
        Returns:
            Detailed comparison
        """
        options_str = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""Compare these financial options for the user:\n{options_str}

For each option, analyze:
1. Pros and cons
2. Financial impact (with numbers)
3. Suitability for their situation
4. Short-term and long-term effects
5. Risk level

Provide a clear recommendation."""

        return self.chat(prompt)
    
    def generate_action_plan(self, goal: str, timeframe: str) -> str:
        """
        Generate a detailed action plan for a goal.
        
        Args:
            goal: Financial goal description
            timeframe: Time to achieve goal
            
        Returns:
            Step-by-step action plan
        """
        prompt = f"""Create a detailed action plan to achieve this goal: "{goal}" within {timeframe}.

Include:
1. Monthly savings required
2. Budget adjustments needed
3. Week-by-week action steps
4. Milestones to track progress
5. Contingency plans for setbacks
6. Expected outcome with calculations

Make it specific and realistic based on their current financial situation."""

        return self.chat(prompt)
    
    def _format_context_structured(self) -> Dict:
        """Format financial context as structured data."""
        if not self.context:
            return {"message": "No financial context loaded"}
        
        profile = self.context.get('profile', {})
        trans = self.context.get('transactions', {})
        budget = self.context.get('budget', {})
        
        return {
            "income": {
                "monthly_income": profile.get('monthly_income', 0),
                "income_stability": profile.get('income_stability', 0)
            },
            "expenses": {
                "monthly_expenses": profile.get('monthly_expenses', 0),
                "essential_expenses": profile.get('essential_expenses', 0),
                "discretionary_expenses": profile.get('discretionary_expenses', 0),
                "by_category": profile.get('expense_categories', {})
            },
            "savings": {
                "monthly_savings": profile.get('monthly_savings', 0),
                "savings_rate": profile.get('savings_rate', 0),
                "emergency_fund_months": profile.get('emergency_fund_months', 0)
            },
            "debt": {
                "total_debt": profile.get('total_debt', 0),
                "monthly_payment": profile.get('monthly_debt_payment', 0),
                "debt_to_income_ratio": profile.get('debt_to_income_ratio', 0)
            },
            "risk": {
                "risk_tolerance": profile.get('risk_tolerance', 'unknown'),
                "spending_volatility": profile.get('spending_volatility', 0)
            },
            "budget_plan": budget if budget else None
        }
    
    def reset_conversation(self):
        """Reset conversation history while keeping context."""
        context_msg = self._format_context_structured()
        initial_message = f"User Financial Context:\n{json.dumps(context_msg, indent=2)}\n\nI'm ready to help with financial planning questions."
        self.chat_session = self.model.start_chat(history=[])
        self.chat_session.send_message(initial_message)
    
    def export_conversation(self, filepath: str):
        """Export conversation history to file."""
        if self.chat_session:
            history = []
            for message in self.chat_session.history:
                history.append({
                    'role': message.role,
                    'parts': [part.text if hasattr(part, 'text') else str(part) for part in message.parts]
                })
            
            with open(filepath, 'w') as f:
                json.dump(history, f, indent=2)
            print(f"Conversation exported to {filepath}")
        else:
            print("No conversation to export")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation."""
        if not self.chat_session or len(self.chat_session.history) <= 1:
            return "No conversation yet."
        
        user_messages = [
            part.text for msg in self.chat_session.history 
            if msg.role == 'user'
            for part in msg.parts
            if hasattr(part, 'text')
        ]
        
        prompt = f"""Summarize this financial planning conversation in 3-4 bullet points:

User asked about:
{chr(10).join([f'- {msg}' for msg in user_messages])}

Focus on key recommendations made and action items."""

        return self.chat(prompt)
    
    def get_token_usage_estimate(self) -> Dict:
        """Estimate token usage for the current conversation."""
        if not self.chat_session:
            return {
                "messages": 0,
                "estimated_tokens": 0,
                "note": "Gemini API doesn't expose token counts in the same way as OpenAI"
            }
        
        total_chars = sum(
            len(part.text) 
            for msg in self.chat_session.history 
            for part in msg.parts
            if hasattr(part, 'text')
        )
        estimated_tokens = total_chars / 4  # Rough estimate: ~4 chars per token
        
        return {
            "messages": len(self.chat_session.history),
            "estimated_tokens": int(estimated_tokens),
            "note": "This is an estimate. Gemini pricing is different from OpenAI"
        }
