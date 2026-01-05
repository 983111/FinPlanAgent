from typing import Dict, List, Optional
import json


class Explainer:
    """Generate human-readable explanations for financial recommendations."""
    
    EXPLANATION_TEMPLATES = {
        'high_spending': """
You're spending ₹{amount:,.2f}/month on {category}, which is {percent:.1f}% of your income.
This is higher than the recommended {recommended}% for this category.

Why this matters:
- High spending in {category} reduces your ability to save for goals
- You could save ₹{potential_savings:,.2f}/month by optimizing this category
- This impacts your emergency fund and long-term financial security

Recommendation: Aim to reduce {category} spending to ₹{target:,.2f}/month
""",
        
        'low_savings': """
Your current savings rate is {rate:.1f}%, which means you're saving only ₹{amount:,.2f}/month.
Financial experts recommend saving at least 20% of your income.

Why this matters:
- Low savings rate limits your ability to handle emergencies
- Delayed retirement planning and wealth building
- Higher financial stress and limited options

To reach 20% savings:
- You need to save an additional ₹{additional:,.2f}/month
- This could be achieved by reducing discretionary spending by {percent:.1f}%
- Consider automating savings to make it easier
""",
        
        'debt_concern': """
Your debt-to-income ratio is {ratio:.1%}, with monthly payments of ₹{payment:,.2f}.
Experts recommend keeping this below 35% for financial health.

Why this matters:
- High debt payments limit your financial flexibility
- Increases risk if income decreases
- Delays other financial goals

Action plan:
- Focus on paying off highest interest debt first
- Consider debt consolidation if you have multiple loans
- Avoid taking on new debt until ratio improves
""",
        
        'emergency_fund': """
Your emergency fund covers {months:.1f} months of expenses.
Financial advisors recommend 3-6 months for stability.

Why this matters:
- Protects you from unexpected expenses (medical, job loss, repairs)
- Prevents going into debt for emergencies
- Provides peace of mind and financial security

To reach 6 months:
- Need to save ₹{target:,.2f} more
- At current savings rate, this will take {timeline} months
- Consider allocating bonuses or windfalls to emergency fund
"""
    }
    
    def __init__(self):
        self.explanations = []
        
    def explain_budget_recommendation(self,
                                     current_budget: Dict[str, float],
                                     optimized_budget: Dict[str, float],
                                     income: float) -> str:
        """
        Explain why the budget was optimized in a certain way.
        
        Args:
            current_budget: Current spending by category
            optimized_budget: Recommended spending by category
            income: Monthly income
            
        Returns:
            Detailed explanation
        """
        explanation = "Budget Optimization Explanation\n" + "="*50 + "\n\n"
        
        explanation += "I've analyzed your spending and here's what I recommend:\n\n"
        
        changes = []
        for category, opt_amount in optimized_budget.items():
            curr_amount = current_budget.get(category, 0)
            diff = opt_amount - curr_amount
            diff_pct = (diff / curr_amount * 100) if curr_amount > 0 else 0
            
            if abs(diff_pct) > 5:  # Significant change
                changes.append({
                    'category': category,
                    'current': curr_amount,
                    'recommended': opt_amount,
                    'difference': diff,
                    'percent_change': diff_pct
                })
        
        # Sort by absolute change
        changes.sort(key=lambda x: abs(x['difference']), reverse=True)
        
        for change in changes[:5]:  # Top 5 changes
            if change['difference'] < 0:
                explanation += f"✂️ **{change['category'].upper()}**\n"
                explanation += f"   Reduce from ₹{change['current']:,.2f} to ₹{change['recommended']:,.2f}\n"
                explanation += f"   Saving: ₹{abs(change['difference']):,.2f}/month\n"
                explanation += f"   Reason: "
                
                if change['category'] in ['food_dining', 'entertainment', 'shopping']:
                    explanation += "Discretionary category with room for optimization\n"
                else:
                    explanation += "Spending is above recommended limits for this category\n"
            else:
                explanation += f"📈 **{change['category'].upper()}**\n"
                explanation += f"   Increase from ₹{change['current']:,.2f} to ₹{change['recommended']:,.2f}\n"
                explanation += f"   Additional: ₹{change['difference']:,.2f}/month\n"
                explanation += f"   Reason: Essential category that was underfunded\n"
            
            explanation += "\n"
        
        total_saved = sum(c['difference'] for c in changes if c['difference'] < 0)
        if abs(total_saved) > 0:
            explanation += f"💰 Total potential savings: ₹{abs(total_saved):,.2f}/month\n"
            explanation += f"   Annually: ₹{abs(total_saved * 12):,.2f}\n"
        
        return explanation
    
    def explain_metric(self, metric_name: str, value: float, 
                      context: Optional[Dict] = None) -> str:
        """
        Explain a financial metric in simple terms.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            context: Additional context
            
        Returns:
            Plain English explanation
        """
        explanations = {
            'savings_rate': f"""
Your savings rate is {value:.1f}%.

This means for every ₹100 you earn, you save ₹{value:.2f}.

Benchmark:
- Below 10%: Concerning - limited financial security
- 10-19%: Fair - room for improvement
- 20-30%: Good - building wealth steadily
- Above 30%: Excellent - strong financial position

Your status: {'Excellent' if value >= 30 else 'Good' if value >= 20 else 'Fair' if value >= 10 else 'Needs improvement'}
""",
            
            'debt_to_income': f"""
Your debt-to-income ratio is {value:.1%}.

This means {value*100:.1f}% of your monthly income goes toward debt payments.

Guidelines:
- Below 20%: Healthy - good control over debt
- 20-35%: Manageable - monitor closely
- 35-50%: Concerning - difficult to save
- Above 50%: Critical - urgent action needed

Your status: {'Healthy' if value < 0.2 else 'Manageable' if value < 0.35 else 'Concerning' if value < 0.5 else 'Critical'}
""",
            
            'spending_volatility': f"""
Your spending volatility is {value:.2f}.

This measures how much your spending varies month-to-month.

Interpretation:
- Below 0.15: Very stable - predictable spending
- 0.15-0.30: Moderate - some variation
- Above 0.30: High - unpredictable spending

Your status: {'Stable' if value < 0.15 else 'Moderate' if value < 0.30 else 'Volatile'}

{
'Higher volatility makes budgeting harder and indicates less control over spending.' 
if value > 0.30 else 
'Good spending consistency makes it easier to plan and save.'
}
"""
        }
        
        return explanations.get(metric_name, f"{metric_name}: {value}")
    
    def explain_risk_tolerance(self, risk_level: str, 
                              profile: Dict) -> str:
        """
        Explain what the risk tolerance means for investment and planning.
        
        Args:
            risk_level: 'low', 'medium', or 'high'
            profile: Financial profile data
            
        Returns:
            Explanation of risk tolerance
        """
        explanations = {
            'low': """
Your financial profile indicates LOW risk tolerance.

What this means:
- Prefer stable, predictable investments
- Prioritize capital preservation over growth
- Comfortable with lower returns for more security
- Suited for debt funds, FDs, conservative mutual funds

Why you're classified as low risk:
- Low spending volatility (stable expenses)
- Lower discretionary spending ratio
- Preference for financial security

Investment recommendations:
- 70% debt instruments (bonds, FDs)
- 20% balanced funds
- 10% equity for long-term growth
""",
            
            'medium': """
Your financial profile indicates MEDIUM risk tolerance.

What this means:
- Balanced approach to risk and reward
- Can handle some market fluctuations
- Mix of stable and growth investments
- Suited for balanced mutual funds, index funds

Why you're classified as medium risk:
- Moderate spending patterns
- Reasonable emergency fund
- Stable income with some flexibility

Investment recommendations:
- 40% equity funds (diversified)
- 40% debt instruments
- 20% balanced/hybrid funds
""",
            
            'high': """
Your financial profile indicates HIGH risk tolerance.

What this means:
- Comfortable with market volatility
- Focus on long-term growth over stability
- Can absorb temporary losses
- Suited for equity funds, direct stocks

Why you're classified as high risk:
- High discretionary spending indicates flexibility
- Variable spending patterns show adaptability
- Financial cushion to handle volatility

Investment recommendations:
- 60-70% equity (stocks, equity funds)
- 20-30% balanced funds
- 10% debt for stability

⚠️ Important: High risk tolerance still requires diversification
"""
        }
        
        return explanations.get(risk_level, "Risk tolerance not defined")
    
    def generate_report(self, profile: Dict, 
                       analysis: Dict,
                       recommendations: List[str]) -> str:
        """
        Generate a comprehensive explanatory report.
        
        Args:
            profile: Financial profile
            analysis: Analysis results
            recommendations: List of recommendations
            
        Returns:
            Formatted report with explanations
        """
        report = """
╔═══════════════════════════════════════════════════════╗
║       PERSONALIZED FINANCIAL ANALYSIS REPORT          ║
╚═══════════════════════════════════════════════════════╝

"""
        
        # Executive Summary
        report += "EXECUTIVE SUMMARY\n" + "-"*50 + "\n\n"
        
        savings_rate = profile.get('savings_rate', 0)
        debt_ratio = profile.get('debt_to_income_ratio', 0)
        emergency_months = profile.get('emergency_fund_months', 0)
        
        report += f"Monthly Income: ₹{profile.get('monthly_income', 0):,.2f}\n"
        report += f"Monthly Expenses: ₹{profile.get('monthly_expenses', 0):,.2f}\n"
        report += f"Savings Rate: {savings_rate:.1f}%\n"
        report += f"Emergency Fund: {emergency_months:.1f} months\n\n"
        
        # Key Insights
        report += "KEY INSIGHTS\n" + "-"*50 + "\n\n"
        
        insights = []
        
        if savings_rate < 10:
            insights.append("⚠️ Critical: Savings rate below 10% - urgent action needed")
        elif savings_rate < 20:
            insights.append("⚡ Important: Increase savings rate toward 20% target")
        else:
            insights.append("✅ Good: Healthy savings rate")
        
        if emergency_months < 3:
            insights.append("⚠️ Critical: Emergency fund insufficient")
        elif emergency_months < 6:
            insights.append("⚡ Important: Build emergency fund to 6 months")
        else:
            insights.append("✅ Good: Strong emergency fund")
        
        if debt_ratio > 0.35:
            insights.append("⚠️ Critical: High debt burden")
        elif debt_ratio > 0.20:
            insights.append("⚡ Important: Monitor debt levels")
        else:
            insights.append("✅ Good: Manageable debt")
        
        for insight in insights:
            report += f"{insight}\n"
        
        report += "\n"
        
        # Recommendations with Explanations
        report += "RECOMMENDATIONS & EXPLANATIONS\n" + "-"*50 + "\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n\n"
        
        # Action Items
        report += "IMMEDIATE ACTION ITEMS\n" + "-"*50 + "\n\n"
        
        action_items = self._generate_action_items(profile)
        for i, item in enumerate(action_items, 1):
            report += f"[ ] {i}. {item}\n"
        
        report += "\n" + "="*50 + "\n"
        report += "Report generated with explainable AI reasoning\n"
        
        return report
    
    def _generate_action_items(self, profile: Dict) -> List[str]:
        """Generate specific action items based on profile."""
        items = []
        
        if profile.get('savings_rate', 0) < 20:
            shortfall = profile['monthly_income'] * 0.20 - profile['monthly_savings']
            items.append(f"Increase monthly savings by ₹{shortfall:,.2f} to reach 20% target")
        
        if profile.get('emergency_fund_months', 0) < 6:
            needed = profile['monthly_expenses'] * 6
            current = profile.get('emergency_fund_months', 0) * profile['monthly_expenses']
            items.append(f"Build emergency fund by ₹{needed - current:,.2f}")
        
        if profile.get('debt_to_income_ratio', 0) > 0.35:
            items.append("Create debt payoff plan focusing on highest interest loans")
        
        # Category-specific items
        categories = profile.get('expense_categories', {})
        for cat, amount in categories.items():
            if cat in ['food_dining', 'entertainment'] and amount > profile['monthly_income'] * 0.15:
                items.append(f"Reduce {cat} spending by 20-30%")
        
        return items
    
    def explain_comparison(self, option_a: Dict, option_b: Dict, 
                          criteria: List[str]) -> str:
        """
        Explain comparison between two options.
        
        Args:
            option_a: First option data
            option_b: Second option data
            criteria: List of comparison criteria
            
        Returns:
            Comparative explanation
        """
        explanation = "Comparative Analysis\n" + "="*50 + "\n\n"
        
        for criterion in criteria:
            val_a = option_a.get(criterion, 0)
            val_b = option_b.get(criterion, 0)
            
            explanation += f"{criterion.replace('_', ' ').title()}:\n"
            explanation += f"  Option A: {val_a}\n"
            explanation += f"  Option B: {val_b}\n"
            
            if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                if val_a > val_b:
                    explanation += f"  → Option A is better by {val_a - val_b}\n"
                elif val_b > val_a:
                    explanation += f"  → Option B is better by {val_b - val_a}\n"
                else:
                    explanation += "  → Both options are equal\n"
            
            explanation += "\n"
        
        return explanation
