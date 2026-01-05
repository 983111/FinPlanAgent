import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class SimulationResult:
    """Results from a what-if simulation."""
    
    scenario_name: str
    description: str
    impact_summary: Dict[str, float]
    new_profile: Dict
    recommendations: List[str]
    feasibility_score: float  # 0-100
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'scenario': self.scenario_name,
            'description': self.description,
            'impact': self.impact_summary,
            'new_profile': self.new_profile,
            'recommendations': self.recommendations,
            'feasibility': self.feasibility_score
        }
    
    def summary(self) -> str:
        """Generate text summary."""
        summary = f"\nScenario: {self.scenario_name}\n"
        summary += "=" * 50 + "\n"
        summary += f"{self.description}\n\n"
        summary += "Impact Analysis:\n"
        
        for metric, value in self.impact_summary.items():
            summary += f"  {metric}: {value:+,.2f}\n"
        
        summary += f"\nFeasibility Score: {self.feasibility_score:.1f}/100\n"
        
        if self.recommendations:
            summary += "\nRecommendations:\n"
            for i, rec in enumerate(self.recommendations, 1):
                summary += f"  {i}. {rec}\n"
        
        return summary


class WhatIfSimulator:
    """Simulate financial scenarios and their impacts."""
    
    def __init__(self, profile: Dict):
        """
        Initialize simulator with user's financial profile.
        
        Args:
            profile: User's current financial profile
        """
        self.base_profile = deepcopy(profile)
        
    def simulate_purchase(self,
                         item: str,
                         amount: float,
                         payment_plan: str = 'cash',
                         duration_months: int = 12,
                         interest_rate: float = 12.0) -> SimulationResult:
        """
        Simulate a major purchase scenario.
        
        Args:
            item: What is being purchased
            amount: Purchase amount
            payment_plan: 'cash', 'loan', or 'installment'
            duration_months: Loan/installment duration
            interest_rate: Annual interest rate for loans
            
        Returns:
            SimulationResult with impact analysis
        """
        new_profile = deepcopy(self.base_profile)
        impact = {}
        recommendations = []
        
        if payment_plan == 'cash':
            # Immediate impact on savings
            current_savings = self.base_profile.get('monthly_savings', 0) * 6
            new_savings = current_savings - amount
            
            impact['savings_change'] = new_savings - current_savings
            impact['emergency_fund_change'] = (
                new_savings / new_profile['monthly_expenses']
                - self.base_profile['emergency_fund_months']
            )
            
            new_profile['emergency_fund_months'] = max(0, 
                new_savings / new_profile['monthly_expenses']
            )
            
            if new_savings < 0:
                recommendations.append(
                    "Cash payment would deplete your savings. Consider financing."
                )
                feasibility = 20
            elif new_savings < new_profile['monthly_expenses'] * 3:
                recommendations.append(
                    "This would reduce your emergency fund below 3 months. Risky."
                )
                feasibility = 50
            else:
                recommendations.append(
                    "Cash payment is feasible and saves you interest costs."
                )
                feasibility = 90
                
        elif payment_plan in ['loan', 'installment']:
            # Calculate EMI
            monthly_rate = interest_rate / 12 / 100
            emi = amount * monthly_rate * (1 + monthly_rate)**duration_months / (
                (1 + monthly_rate)**duration_months - 1
            )
            
            total_interest = emi * duration_months - amount
            
            # Impact on monthly finances
            new_monthly_payment = new_profile.get('monthly_debt_payment', 0) + emi
            new_profile['monthly_debt_payment'] = new_monthly_payment
            new_profile['total_debt'] = new_profile.get('total_debt', 0) + amount
            
            # Recalculate debt ratios
            monthly_income = new_profile['monthly_income']
            new_profile['debt_to_income_ratio'] = new_monthly_payment / monthly_income
            
            # Impact on savings
            new_savings = new_profile['monthly_savings'] - emi
            new_profile['monthly_savings'] = new_savings
            new_profile['savings_rate'] = (new_savings / monthly_income) * 100
            
            impact['monthly_emi'] = -emi
            impact['total_interest'] = -total_interest
            impact['debt_increase'] = amount
            impact['savings_rate_change'] = (
                new_profile['savings_rate'] - self.base_profile['savings_rate']
            )
            
            # Feasibility assessment
            if new_profile['debt_to_income_ratio'] > 0.5:
                recommendations.append(
                    "Debt-to-income ratio would exceed 50%. Not recommended."
                )
                feasibility = 20
            elif new_profile['savings_rate'] < 5:
                recommendations.append(
                    "Would leave very little room for savings. Consider shorter duration."
                )
                feasibility = 40
            elif new_profile['debt_to_income_ratio'] > 0.35:
                recommendations.append(
                    "Manageable but tight. Ensure stable income before proceeding."
                )
                feasibility = 60
            else:
                recommendations.append(
                    f"Financing is manageable. EMI of ₹{emi:,.2f} for {duration_months} months."
                )
                recommendations.append(
                    f"Total interest: ₹{total_interest:,.2f}"
                )
                feasibility = 80
        
        description = f"Purchase {item} for ₹{amount:,.2f} via {payment_plan}"
        if payment_plan != 'cash':
            description += f" over {duration_months} months at {interest_rate}% p.a."
        
        return SimulationResult(
            scenario_name=f"Purchase: {item}",
            description=description,
            impact_summary=impact,
            new_profile=new_profile,
            recommendations=recommendations,
            feasibility_score=feasibility
        )
    
    def simulate_income_change(self,
                              change_percent: float,
                              reason: str = "Job change") -> SimulationResult:
        """
        Simulate income increase or decrease.
        
        Args:
            change_percent: Percentage change in income (positive or negative)
            reason: Reason for change
            
        Returns:
            SimulationResult with impact
        """
        new_profile = deepcopy(self.base_profile)
        
        old_income = self.base_profile['monthly_income']
        new_income = old_income * (1 + change_percent / 100)
        income_diff = new_income - old_income
        
        new_profile['monthly_income'] = new_income
        
        # Assume expenses stay same, impact on savings
        new_savings = new_income - new_profile['monthly_expenses']
        new_profile['monthly_savings'] = new_savings
        new_profile['savings_rate'] = (new_savings / new_income) * 100
        
        # Recalculate debt ratio
        new_profile['debt_to_income_ratio'] = (
            new_profile['monthly_debt_payment'] / new_income
        )
        
        impact = {
            'income_change': income_diff,
            'savings_change': new_savings - self.base_profile['monthly_savings'],
            'savings_rate_change': (
                new_profile['savings_rate'] - self.base_profile['savings_rate']
            ),
            'debt_ratio_change': (
                new_profile['debt_to_income_ratio'] - 
                self.base_profile['debt_to_income_ratio']
            )
        }
        
        recommendations = []
        
        if change_percent > 0:
            recommendations.append(
                f"Increased savings of ₹{impact['savings_change']:,.2f}/month"
            )
            recommendations.append(
                "Consider increasing emergency fund or investments"
            )
            feasibility = 95
        else:
            if new_savings < 0:
                recommendations.append(
                    "Critical: Income insufficient for current expenses"
                )
                recommendations.append(
                    f"Need to cut expenses by ₹{abs(new_savings):,.2f}/month"
                )
                feasibility = 30
            else:
                recommendations.append(
                    "Reduce discretionary spending to maintain savings"
                )
                feasibility = 60
        
        return SimulationResult(
            scenario_name="Income Change",
            description=f"{reason}: {change_percent:+.1f}% ({income_diff:+,.2f})",
            impact_summary=impact,
            new_profile=new_profile,
            recommendations=recommendations,
            feasibility_score=feasibility
        )
    
    def simulate_expense_reduction(self,
                                  category: str,
                                  reduction_percent: float) -> SimulationResult:
        """
        Simulate reducing spending in a category.
        
        Args:
            category: Expense category to reduce
            reduction_percent: Percentage to reduce
            
        Returns:
            SimulationResult with impact
        """
        new_profile = deepcopy(self.base_profile)
        
        categories = new_profile.get('expense_categories', {})
        if category not in categories:
            return SimulationResult(
                scenario_name="Expense Reduction",
                description=f"Category '{category}' not found",
                impact_summary={},
                new_profile=new_profile,
                recommendations=["Invalid category"],
                feasibility_score=0
            )
        
        old_amount = categories[category]
        reduction_amount = old_amount * (reduction_percent / 100)
        new_amount = old_amount - reduction_amount
        
        categories[category] = new_amount
        new_profile['expense_categories'] = categories
        
        # Update totals
        new_expenses = sum(categories.values())
        new_profile['monthly_expenses'] = new_expenses
        
        new_savings = new_profile['monthly_income'] - new_expenses
        new_profile['monthly_savings'] = new_savings
        new_profile['savings_rate'] = (
            new_savings / new_profile['monthly_income'] * 100
        )
        
        impact = {
            'expense_reduction': -reduction_amount,
            'savings_increase': reduction_amount,
            'savings_rate_change': (
                new_profile['savings_rate'] - self.base_profile['savings_rate']
            )
        }
        
        recommendations = [
            f"Reducing {category} by {reduction_percent}% saves ₹{reduction_amount:,.2f}/month",
            f"Annual savings: ₹{reduction_amount * 12:,.2f}"
        ]
        
        if new_profile['savings_rate'] > 20:
            recommendations.append("This brings you to a healthy savings rate!")
        
        # Feasibility based on category and reduction amount
        if category in ['housing', 'utilities', 'healthcare']:
            if reduction_percent > 20:
                feasibility = 40  # Hard to reduce essentials significantly
            else:
                feasibility = 70
        else:
            if reduction_percent <= 30:
                feasibility = 90
            else:
                feasibility = 60
        
        return SimulationResult(
            scenario_name="Expense Reduction",
            description=f"Reduce {category} by {reduction_percent}%",
            impact_summary=impact,
            new_profile=new_profile,
            recommendations=recommendations,
            feasibility_score=feasibility
        )
    
    def simulate_goal(self,
                     goal_name: str,
                     target_amount: float,
                     months: int,
                     priority: str = 'medium') -> SimulationResult:
        """
        Simulate saving for a specific goal.
        
        Args:
            goal_name: Name of the goal
            target_amount: Target amount to save
            months: Time horizon in months
            priority: Goal priority (low/medium/high)
            
        Returns:
            SimulationResult with feasibility analysis
        """
        monthly_required = target_amount / months
        current_savings = self.base_profile.get('monthly_savings', 0)
        
        shortfall = monthly_required - current_savings
        
        new_profile = deepcopy(self.base_profile)
        
        impact = {
            'monthly_savings_required': monthly_required,
            'current_monthly_savings': current_savings,
            'monthly_shortfall': shortfall
        }
        
        recommendations = []
        
        if shortfall <= 0:
            recommendations.append(
                f"Goal is achievable! You can already save ₹{monthly_required:,.2f}/month"
            )
            recommendations.append(
                f"On track to reach ₹{target_amount:,.2f} in {months} months"
            )
            feasibility = 95
        else:
            recommendations.append(
                f"Need to save additional ₹{shortfall:,.2f}/month"
            )
            
            # Calculate required expense reduction
            reduction_pct = (shortfall / self.base_profile['monthly_expenses']) * 100
            
            if reduction_pct < 10:
                recommendations.append(
                    f"Reduce expenses by {reduction_pct:.1f}% to achieve goal"
                )
                feasibility = 80
            elif reduction_pct < 20:
                recommendations.append(
                    f"Need {reduction_pct:.1f}% expense reduction. Challenging but doable"
                )
                feasibility = 60
            elif reduction_pct < 30:
                recommendations.append(
                    f"Requires {reduction_pct:.1f}% expense cut. Consider extending timeline"
                )
                feasibility = 40
            else:
                recommendations.append(
                    f"Goal requires {reduction_pct:.1f}% expense reduction. Not feasible"
                )
                recommendations.append(
                    f"Consider: extending to {int(months * 1.5)} months or increasing income"
                )
                feasibility = 20
        
        return SimulationResult(
            scenario_name=f"Goal: {goal_name}",
            description=f"Save ₹{target_amount:,.2f} in {months} months",
            impact_summary=impact,
            new_profile=new_profile,
            recommendations=recommendations,
            feasibility_score=feasibility
        )
    
    def compare_scenarios(self, scenarios: List[SimulationResult]) -> str:
        """
        Compare multiple scenarios side by side.
        
        Args:
            scenarios: List of simulation results to compare
            
        Returns:
            Comparison summary
        """
        comparison = "\nScenario Comparison\n"
        comparison += "=" * 60 + "\n\n"
        
        for i, scenario in enumerate(scenarios, 1):
            comparison += f"{i}. {scenario.scenario_name}\n"
            comparison += f"   Feasibility: {scenario.feasibility_score:.0f}/100\n"
            comparison += f"   Key Impact: "
            
            # Show most significant impact
            if scenario.impact_summary:
                key_impact = max(
                    scenario.impact_summary.items(),
                    key=lambda x: abs(x[1])
                )
                comparison += f"{key_impact[0]}: {key_impact[1]:+,.2f}\n"
            
            comparison += "\n"
        
        # Recommend best option
        best = max(scenarios, key=lambda x: x.feasibility_score)
        comparison += f"\nRecommendation: {best.scenario_name}\n"
        comparison += f"Reason: Highest feasibility at {best.feasibility_score:.0f}/100\n"
        
        return comparison
