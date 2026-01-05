import pandas as pd
import numpy as np
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class FinancialProfile:
    """Data class representing a user's financial profile."""
    
    # Income metrics
    monthly_income: float
    income_stability: float  # 0-1, higher is more stable
    
    # Expense metrics
    monthly_expenses: float
    expense_categories: Dict[str, float]
    essential_expenses: float
    discretionary_expenses: float
    
    # Savings metrics
    monthly_savings: float
    savings_rate: float  # Percentage
    emergency_fund_months: float
    
    # Debt metrics
    total_debt: float
    monthly_debt_payment: float
    debt_to_income_ratio: float
    
    # Risk metrics
    spending_volatility: float
    risk_tolerance: str  # 'low', 'medium', 'high'
    
    # Goals
    financial_goals: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convert profile to dictionary."""
        return asdict(self)
    
    def summary(self) -> str:
        """Generate a text summary of the profile."""
        summary = f"""
Financial Profile Summary:
-------------------------
Income: ₹{self.monthly_income:,.2f}/month (Stability: {self.income_stability:.2%})
Expenses: ₹{self.monthly_expenses:,.2f}/month
  - Essential: ₹{self.essential_expenses:,.2f}
  - Discretionary: ₹{self.discretionary_expenses:,.2f}
Savings: ₹{self.monthly_savings:,.2f}/month ({self.savings_rate:.1f}%)
Emergency Fund: {self.emergency_fund_months:.1f} months

Debt:
  - Total: ₹{self.total_debt:,.2f}
  - Monthly Payment: ₹{self.monthly_debt_payment:,.2f}
  - Debt-to-Income: {self.debt_to_income_ratio:.1%}

Risk Profile: {self.risk_tolerance.upper()}
Spending Volatility: {self.spending_volatility:.2f}
        """
        return summary.strip()


class ProfileBuilder:
    """Build comprehensive financial profiles from transaction data."""
    
    ESSENTIAL_CATEGORIES = {
        'housing', 'utilities', 'groceries', 'healthcare', 
        'insurance', 'transportation', 'education'
    }
    
    DISCRETIONARY_CATEGORIES = {
        'food_dining', 'entertainment', 'shopping', 'others'
    }
    
    def __init__(self):
        self.profile = None
        
    def build(self, df: pd.DataFrame, 
              current_savings: float = 0.0,
              current_debt: float = 0.0,
              goals: List[Dict] = None) -> FinancialProfile:
        """
        Build a financial profile from transaction data.
        
        Args:
            df: Categorized transaction DataFrame
            current_savings: Current savings balance
            current_debt: Current total debt
            goals: List of financial goals
            
        Returns:
            FinancialProfile object
        """
        # Calculate income metrics
        income_metrics = self._calculate_income_metrics(df)
        
        # Calculate expense metrics
        expense_metrics = self._calculate_expense_metrics(df)
        
        # Calculate savings metrics
        savings_metrics = self._calculate_savings_metrics(
            df, income_metrics['monthly_income'], 
            expense_metrics['monthly_expenses'], current_savings
        )
        
        # Calculate debt metrics
        debt_metrics = self._calculate_debt_metrics(
            df, income_metrics['monthly_income'], current_debt
        )
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(df, expense_metrics)
        
        # Create profile
        self.profile = FinancialProfile(
            monthly_income=income_metrics['monthly_income'],
            income_stability=income_metrics['stability'],
            monthly_expenses=expense_metrics['monthly_expenses'],
            expense_categories=expense_metrics['by_category'],
            essential_expenses=expense_metrics['essential'],
            discretionary_expenses=expense_metrics['discretionary'],
            monthly_savings=savings_metrics['monthly_savings'],
            savings_rate=savings_metrics['savings_rate'],
            emergency_fund_months=savings_metrics['emergency_fund_months'],
            total_debt=debt_metrics['total_debt'],
            monthly_debt_payment=debt_metrics['monthly_payment'],
            debt_to_income_ratio=debt_metrics['debt_to_income'],
            spending_volatility=risk_metrics['volatility'],
            risk_tolerance=risk_metrics['tolerance'],
            financial_goals=goals or []
        )
        
        return self.profile
    
    def _calculate_income_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate income-related metrics."""
        income_data = df[df['type'] == 'credit']
        
        # Monthly income
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        monthly_income = income_data.groupby('month')['amount'].sum()
        
        avg_monthly_income = monthly_income.mean() if len(monthly_income) > 0 else 0
        
        # Income stability (inverse of coefficient of variation)
        if len(monthly_income) > 1 and avg_monthly_income > 0:
            cv = monthly_income.std() / avg_monthly_income
            stability = max(0, 1 - cv)
        else:
            stability = 0.5  # Default for insufficient data
        
        return {
            'monthly_income': avg_monthly_income,
            'stability': stability
        }
    
    def _calculate_expense_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate expense-related metrics."""
        expense_data = df[df['type'] == 'debit'].copy()
        expense_data['amount'] = expense_data['amount'].abs()
        
        # Monthly expenses
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        monthly_expenses = expense_data.groupby('month')['amount'].sum()
        avg_monthly_expenses = monthly_expenses.mean() if len(monthly_expenses) > 0 else 0
        
        # By category
        by_category = expense_data.groupby('category')['amount'].sum().to_dict()
        
        # Essential vs discretionary
        essential = sum(
            amount for cat, amount in by_category.items() 
            if cat in self.ESSENTIAL_CATEGORIES
        )
        
        discretionary = sum(
            amount for cat, amount in by_category.items() 
            if cat in self.DISCRETIONARY_CATEGORIES
        )
        
        return {
            'monthly_expenses': avg_monthly_expenses,
            'by_category': by_category,
            'essential': essential,
            'discretionary': discretionary
        }
    
    def _calculate_savings_metrics(self, df: pd.DataFrame,
                                   monthly_income: float,
                                   monthly_expenses: float,
                                   current_savings: float) -> Dict:
        """Calculate savings-related metrics."""
        monthly_savings = monthly_income - monthly_expenses
        
        savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
        
        # Emergency fund (how many months of expenses covered)
        emergency_fund_months = (current_savings / monthly_expenses) if monthly_expenses > 0 else 0
        
        return {
            'monthly_savings': monthly_savings,
            'savings_rate': savings_rate,
            'emergency_fund_months': emergency_fund_months
        }
    
    def _calculate_debt_metrics(self, df: pd.DataFrame,
                               monthly_income: float,
                               current_debt: float) -> Dict:
        """Calculate debt-related metrics."""
        # Look for loan/EMI payments in transactions
        debt_keywords = ['emi', 'loan', 'credit card', 'installment']
        debt_payments = df[
            (df['type'] == 'debit') & 
            (df['description'].str.contains('|'.join(debt_keywords), case=False, na=False))
        ]
        
        monthly_payment = debt_payments['amount'].abs().sum() / max(1, df['month'].nunique())
        
        # Debt-to-income ratio
        dti = (monthly_payment / monthly_income) if monthly_income > 0 else 0
        
        return {
            'total_debt': current_debt,
            'monthly_payment': monthly_payment,
            'debt_to_income': dti
        }
    
    def _calculate_risk_metrics(self, df: pd.DataFrame,
                               expense_metrics: Dict) -> Dict:
        """Calculate risk tolerance and volatility metrics."""
        expense_data = df[df['type'] == 'debit'].copy()
        expense_data['amount'] = expense_data['amount'].abs()
        
        # Calculate spending volatility (coefficient of variation)
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        monthly_expenses = expense_data.groupby('month')['amount'].sum()
        
        if len(monthly_expenses) > 1:
            mean_expense = monthly_expenses.mean()
            volatility = monthly_expenses.std() / mean_expense if mean_expense > 0 else 0
        else:
            volatility = 0
        
        # Determine risk tolerance based on profile
        discretionary_ratio = (
            expense_metrics['discretionary'] / 
            expense_metrics['monthly_expenses']
        ) if expense_metrics['monthly_expenses'] > 0 else 0
        
        if volatility < 0.2 and discretionary_ratio < 0.3:
            tolerance = 'low'
        elif volatility > 0.4 or discretionary_ratio > 0.5:
            tolerance = 'high'
        else:
            tolerance = 'medium'
        
        return {
            'volatility': volatility,
            'tolerance': tolerance
        }
    
    def assess_financial_health(self, profile: FinancialProfile = None) -> Dict:
        """
        Assess overall financial health and provide scores.
        
        Args:
            profile: FinancialProfile to assess (uses self.profile if None)
            
        Returns:
            Dictionary with health scores and recommendations
        """
        if profile is None:
            profile = self.profile
        
        if profile is None:
            raise ValueError("No profile available to assess")
        
        scores = {}
        
        # Savings score (0-100)
        if profile.savings_rate >= 20:
            scores['savings'] = 100
        elif profile.savings_rate >= 10:
            scores['savings'] = 50 + (profile.savings_rate - 10) * 5
        else:
            scores['savings'] = max(0, profile.savings_rate * 5)
        
        # Emergency fund score (0-100)
        if profile.emergency_fund_months >= 6:
            scores['emergency_fund'] = 100
        elif profile.emergency_fund_months >= 3:
            scores['emergency_fund'] = 50 + (profile.emergency_fund_months - 3) * 16.67
        else:
            scores['emergency_fund'] = profile.emergency_fund_months * 16.67
        
        # Debt score (0-100, higher is better)
        if profile.debt_to_income_ratio <= 0.2:
            scores['debt'] = 100
        elif profile.debt_to_income_ratio <= 0.4:
            scores['debt'] = 100 - (profile.debt_to_income_ratio - 0.2) * 250
        else:
            scores['debt'] = max(0, 50 - (profile.debt_to_income_ratio - 0.4) * 100)
        
        # Overall health score
        overall = np.mean(list(scores.values()))
        
        # Generate recommendations
        recommendations = []
        
        if scores['savings'] < 50:
            recommendations.append("Increase your savings rate to at least 20% of income")
        
        if scores['emergency_fund'] < 50:
            recommendations.append("Build an emergency fund covering 3-6 months of expenses")
        
        if scores['debt'] < 70:
            recommendations.append("Focus on reducing debt to improve financial stability")
        
        if profile.discretionary_expenses > profile.essential_expenses:
            recommendations.append("Consider reducing discretionary spending")
        
        return {
            'overall_score': overall,
            'category_scores': scores,
            'health_rating': self._get_health_rating(overall),
            'recommendations': recommendations
        }
    
    def _get_health_rating(self, score: float) -> str:
        """Convert numeric score to rating."""
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        else:
            return 'Needs Improvement'
