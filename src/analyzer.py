import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import re


class TransactionAnalyzer:
    """Analyze and categorize financial transactions."""
    
    # Category keywords for rule-based classification
    CATEGORY_KEYWORDS = {
        'food_dining': ['restaurant', 'cafe', 'food', 'pizza', 'burger', 'dining',
                        'zomato', 'swiggy', 'uber eats', 'mcdonald', 'subway'],
        'groceries': ['supermarket', 'grocery', 'walmart', 'target', 'costco',
                     'big bazaar', 'dmart', 'reliance fresh', 'market'],
        'transportation': ['uber', 'lyft', 'taxi', 'gas', 'fuel', 'metro', 'train',
                          'ola', 'rapido', 'petrol', 'parking', 'toll'],
        'utilities': ['electricity', 'water', 'gas bill', 'internet', 'phone',
                     'mobile recharge', 'broadband', 'wifi'],
        'entertainment': ['movie', 'netflix', 'spotify', 'prime', 'theater',
                         'concert', 'game', 'xbox', 'playstation', 'hotstar'],
        'shopping': ['amazon', 'flipkart', 'myntra', 'mall', 'shop',
                    'clothing', 'shoes', 'fashion'],
        'healthcare': ['hospital', 'doctor', 'pharmacy', 'medical', 'clinic',
                      'medicine', 'health', 'dental', 'apollo', 'max healthcare'],
        'education': ['school', 'college', 'university', 'course', 'books',
                     'tuition', 'fees', 'udemy', 'coursera'],
        'housing': ['rent', 'mortgage', 'maintenance', 'repairs', 'furniture',
                   'apartment', 'society'],
        'insurance': ['insurance', 'premium', 'lic', 'policy'],
        'investment': ['mutual fund', 'stock', 'bond', 'sip', 'investment',
                      'zerodha', 'groww', 'upstox'],
        'salary': ['salary', 'wages', 'payroll', 'income', 'bonus'],
        'transfer': ['transfer', 'sent to', 'received from', 'upi', 'neft', 'imps'],
        'others': []
    }
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.fitted = False
        
    def categorize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categorize transactions using rule-based and ML approaches.
        
        Args:
            df: DataFrame with transaction data
            
        Returns:
            DataFrame with added 'category' column
        """
        df = df.copy()
        
        # Rule-based categorization
        df['category'] = df['description'].apply(self._rule_based_categorize)
        
        # Mark uncategorized for potential ML classification
        uncategorized_mask = df['category'] == 'others'
        if uncategorized_mask.sum() > 0:
            # Could add ML-based categorization here for 'others'
            pass
        
        return df
    
    def _rule_based_categorize(self, description: str) -> str:
        """
        Categorize a transaction based on keywords.
        
        Args:
            description: Transaction description
            
        Returns:
            Category name
        """
        description = description.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in description:
                    return category
        
        return 'others'
    
    def compute_spending_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analyze spending patterns across categories and time.
        
        Args:
            df: Categorized transaction DataFrame
            
        Returns:
            Dictionary with spending insights
        """
        patterns = {}
        
        # Spending by category
        spending_by_category = df[df['type'] == 'debit'].groupby('category')['amount'].agg([
            ('total', lambda x: abs(x.sum())),
            ('count', 'count'),
            ('average', lambda x: abs(x.mean()))
        ]).to_dict('index')
        
        patterns['by_category'] = spending_by_category
        
        # Monthly spending trend
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        monthly = df[df['type'] == 'debit'].groupby('month')['amount'].agg(
            lambda x: abs(x.sum())
        )
        patterns['monthly_trend'] = monthly.to_dict()
        
        # Income vs expenses
        total_income = df[df['type'] == 'credit']['amount'].sum()
        total_expenses = abs(df[df['type'] == 'debit']['amount'].sum())
        patterns['total_income'] = total_income
        patterns['total_expenses'] = total_expenses
        patterns['net_savings'] = total_income - total_expenses
        
        # Top spending categories
        top_categories = sorted(
            spending_by_category.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:5]
        patterns['top_spending'] = [
            {'category': cat, **values} for cat, values in top_categories
        ]
        
        # Spending volatility
        monthly_std = monthly.std()
        patterns['spending_volatility'] = monthly_std
        
        return patterns
    
    def detect_anomalies(self, df: pd.DataFrame, threshold: float = 2.5) -> pd.DataFrame:
        """
        Detect unusual transactions using statistical methods.
        
        Args:
            df: Transaction DataFrame
            threshold: Number of standard deviations for anomaly detection
            
        Returns:
            DataFrame with anomalies flagged
        """
        df = df.copy()
        df['is_anomaly'] = False
        
        # Calculate Z-scores for amounts within each category
        df['amount_abs'] = df['amount'].abs()
        
        for category in df['category'].unique():
            mask = df['category'] == category
            amounts = df.loc[mask, 'amount_abs']
            
            if len(amounts) > 3:  # Need enough data points
                mean = amounts.mean()
                std = amounts.std()
                
                if std > 0:
                    z_scores = (amounts - mean) / std
                    df.loc[mask, 'is_anomaly'] = z_scores.abs() > threshold
        
        # Fill NaN anomaly flags with False
        df['is_anomaly'] = df['is_anomaly'].fillna(False)
        
        return df
    
    def analyze_recurring(self, df: pd.DataFrame, 
                         similarity_threshold: float = 0.8) -> List[Dict]:
        """
        Identify recurring transactions (subscriptions, bills, etc.).
        
        Args:
            df: Transaction DataFrame
            similarity_threshold: Threshold for description similarity
            
        Returns:
            List of recurring transaction groups
        """
        df = df.copy()
        df = df.sort_values('date')
        
        recurring = []
        grouped = df.groupby('description')
        
        for desc, group in grouped:
            if len(group) < 2:
                continue
            
            # Check if amounts are similar
            amount_std = group['amount'].std()
            amount_mean = group['amount'].mean()
            
            if amount_std / abs(amount_mean) < 0.1:  # Low variation
                # Check time intervals
                dates = pd.to_datetime(group['date'])
                intervals = dates.diff().dt.days.dropna()
                
                if len(intervals) > 0:
                    avg_interval = intervals.mean()
                    interval_std = intervals.std()
                    
                    # Regular intervals (within 20% variation)
                    if interval_std / avg_interval < 0.2:
                        recurring.append({
                            'description': desc,
                            'category': group['category'].iloc[0],
                            'amount': group['amount'].mean(),
                            'frequency_days': avg_interval,
                            'count': len(group),
                            'last_date': group['date'].max()
                        })
        
        return recurring
    
    def calculate_category_trends(self, df: pd.DataFrame, 
                                  months: int = 3) -> Dict:
        """
        Calculate spending trends for each category over time.
        
        Args:
            df: Transaction DataFrame
            months: Number of recent months to analyze
            
        Returns:
            Dictionary with trend information
        """
        df = df.copy()
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        
        # Filter recent months
        recent_months = df['month'].unique()[-months:]
        df_recent = df[df['month'].isin(recent_months)]
        
        trends = {}
        
        for category in df_recent['category'].unique():
            cat_data = df_recent[
                (df_recent['category'] == category) & 
                (df_recent['type'] == 'debit')
            ]
            
            monthly_spending = cat_data.groupby('month')['amount'].agg(
                lambda x: abs(x.sum())
            )
            
            if len(monthly_spending) >= 2:
                # Simple linear trend
                values = monthly_spending.values
                trend = 'increasing' if values[-1] > values[0] else 'decreasing'
                change_pct = ((values[-1] - values[0]) / abs(values[0])) * 100 if values[0] != 0 else 0
                
                trends[category] = {
                    'trend': trend,
                    'change_percent': change_pct,
                    'recent_avg': monthly_spending.mean(),
                    'months_analyzed': len(monthly_spending)
                }
        
        return trends
    
    def generate_insights(self, df: pd.DataFrame) -> List[str]:
        """
        Generate human-readable insights from transaction data.
        
        Args:
            df: Analyzed transaction DataFrame
            
        Returns:
            List of insight strings
        """
        insights = []
        
        patterns = self.compute_spending_patterns(df)
        
        # High spending categories
        if patterns['top_spending']:
            top_cat = patterns['top_spending'][0]
            insights.append(
                f"Your highest spending category is {top_cat['category']} "
                f"at ₹{top_cat['total']:.2f} ({top_cat['count']} transactions)"
            )
        
        # Savings rate
        if patterns['total_income'] > 0:
            savings_rate = (patterns['net_savings'] / patterns['total_income']) * 100
            if savings_rate > 20:
                insights.append(f"Great job! You're saving {savings_rate:.1f}% of your income")
            elif savings_rate > 0:
                insights.append(f"You're saving {savings_rate:.1f}% of income. Consider increasing this to 20%+")
            else:
                insights.append("Warning: You're spending more than you earn")
        
        # Volatility
        if patterns.get('spending_volatility', 0) > patterns['total_expenses'] * 0.3:
            insights.append("Your spending varies significantly month-to-month. Consider budgeting.")
        
        # Recurring transactions
        recurring = self.analyze_recurring(df)
        if len(recurring) >= 3:
            total_recurring = sum(abs(r['amount']) for r in recurring)
            insights.append(
                f"You have {len(recurring)} recurring expenses totaling ₹{total_recurring:.2f}/month"
            )
        
        return insights
