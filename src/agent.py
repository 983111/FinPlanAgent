import os
from typing import Dict, List, Optional
import json
from openai import OpenAI


class FinancialAgent:
    """
    AI agent for personalized financial planning using LLM.
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

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the financial agent.
        
        Args:
            api_key: OpenAI API key (will use env var if not provided)
            model: LLM model to use
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.conversation_history = []
        self.context = {}
        
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
        
        # Create context summary for the agent
        context_msg = self._format_context()
        self.conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "system", "content": f"User Financial Context:\n{context_msg}"}
        ]
    
    def chat(self, user_message: str) -> str:
        """
        Process user message and generate response.
        
        Args:
            user_message: User's question or request
            
        Returns:
            Agent's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Determine if tool calling is needed
        tools_needed = self._analyze_query(user_message)
        
        # Generate response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
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
    
    def _format_context(self) -> str:
        """Format financial context for the agent."""
        if not self.context:
            return "No financial context loaded."
        
        profile = self.context.get('profile', {})
        trans = self.context.get('transactions', {})
        budget = self.context.get('budget', {})
        
        context_str = f"""
INCOME & SAVINGS:
- Monthly Income: ₹{profile.get('monthly_income', 0):,.2f}
- Monthly Expenses: ₹{profile.get('monthly_expenses', 0):,.2f}
- Savings Rate: {profile.get('savings_rate', 0):.1f}%
- Emergency Fund: {profile.get('emergency_fund_months', 0):.1f} months

DEBT:
- Total Debt: ₹{profile.get('total_debt', 0):,.2f}
- Monthly Payment: ₹{profile.get('monthly_debt_payment', 0):,.2f}
- Debt-to-Income: {profile.get('debt_to_income_ratio', 0):.1%}

SPENDING PATTERNS:
"""
        
        # Add category breakdown
        if 'expense_categories' in profile:
            for cat, amount in profile['expense_categories'].items():
                context_str += f"- {cat}: ₹{amount:,.2f}\n"
        
        context_str += f"""
RISK PROFILE:
- Risk Tolerance: {profile.get('risk_tolerance', 'unknown')}
- Spending Volatility: {profile.get('spending_volatility', 0):.2f}
"""
        
        if budget:
            context_str += "\nOPTIMIZED BUDGET AVAILABLE: Yes"
        
        return context_str
    
    def _analyze_query(self, query: str) -> List[str]:
        """
        Analyze query to determine which tools/data are needed.
        
        Args:
            query: User's query
            
        Returns:
            List of required tool names
        """
        query_lower = query.lower()
        tools = []
        
        # Keywords for different tools
        if any(word in query_lower for word in ['save', 'saving', 'savings']):
            tools.append('savings_analysis')
        
        if any(word in query_lower for word in ['budget', 'spend', 'spending']):
            tools.append('budget_analysis')
        
        if any(word in query_lower for word in ['debt', 'loan', 'emi']):
            tools.append('debt_analysis')
        
        if any(word in query_lower for word in ['invest', 'investment']):
            tools.append('investment_analysis')
        
        if any(word in query_lower for word in ['if i', 'what if', 'scenario']):
            tools.append('scenario_simulation')
        
        return tools
    
    def reset_conversation(self):
        """Reset conversation history while keeping context."""
        context_msg = self._format_context() if self.context else ""
        self.conversation_history = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "system", "content": f"User Financial Context:\n{context_msg}"}
        ]
    
    def export_conversation(self, filepath: str):
        """Export conversation history to file."""
        with open(filepath, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation."""
        if len(self.conversation_history) <= 2:
            return "No conversation yet."
        
        user_messages = [
            msg['content'] for msg in self.conversation_history 
            if msg['role'] == 'user'
        ]
        
        prompt = f"""Summarize this financial planning conversation in 3-4 bullet points:

User asked about:
{chr(10).join([f'- {msg}' for msg in user_messages])}

Focus on key recommendations made and action items."""

        return self.chat(prompt)
