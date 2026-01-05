import pytest
import pandas as pd
from src.analyzer import TransactionAnalyzer


class TestTransactionAnalyzer:
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = TransactionAnalyzer()
        self.sample_df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'description': [
                'swiggy order', 'dmart groceries', 'uber ride', 
                'netflix subscription', 'salary credit',
                'apollo pharmacy', 'amazon shopping', 'petrol pump',
                'movie tickets', 'rent payment'
            ],
            'amount': [500, -2000, -300, -499, 50000, -850, -1500, -2000, -900, -15000],
            'type': ['debit', 'debit', 'debit', 'debit', 'credit', 
                    'debit', 'debit', 'debit', 'debit', 'debit']
        })
        
    def test_categorize_transactions(self):
        """Test transaction categorization."""
        df = self.analyzer.categorize(self.sample_df)
        
        assert 'category' in df.columns
        assert df[df['description'] == 'swiggy order']['category'].iloc[0] == 'food_dining'
        assert df[df['description'] == 'dmart groceries']['category'].iloc[0] == 'groceries'
        assert df[df['description'] == 'uber ride']['category'].iloc[0] == 'transportation'
        
    def test_rule_based_categorize(self):
        """Test individual categorization."""
        assert self.analyzer._rule_based_categorize('zomato order') == 'food_dining'
        assert self.analyzer._rule_based_categorize('big bazaar') == 'groceries'
        assert self.analyzer._rule_based_categorize('ola cab') == 'transportation'
        assert self.analyzer._rule_based_categorize('random store') == 'others'
        
    def test_compute_spending_patterns(self):
        """Test spending pattern computation."""
        df = self.analyzer.categorize(self.sample_df)
        patterns = self.analyzer.compute_spending_patterns(df)
        
        assert 'by_category' in patterns
        assert 'total_income' in patterns
        assert 'total_expenses' in patterns
        assert patterns['total_income'] == 50000
        assert patterns['total_expenses'] > 0
        
    def test_detect_anomalies(self):
        """Test anomaly detection."""
        df = self.analyzer.categorize(self.sample_df)
        df_with_anomalies = self.analyzer.detect_anomalies(df)
        
        assert 'is_anomaly' in df_with_anomalies.columns
        assert df_with_anomalies['is_anomaly'].dtype == bool
        
    def test_analyze_recurring(self):
        """Test recurring transaction detection."""
        # Add recurring transactions
        recurring_df = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=3, freq='M'),
            'description': ['netflix'] * 3,
            'amount': [-499, -499, -499],
            'type': ['debit'] * 3
        })
        recurring_df = self.analyzer.categorize(recurring_df)
        
        recurring = self.analyzer.analyze_recurring(recurring_df)
        
        assert len(recurring) > 0
        assert recurring[0]['description'] == 'netflix'
        
    def test_generate_insights(self):
        """Test insight generation."""
        df = self.analyzer.categorize(self.sample_df)
        insights = self.analyzer.generate_insights(df)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        assert all(isinstance(insight, str) for insight in insights)
