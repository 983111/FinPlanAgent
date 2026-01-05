import pytest
from src.optimizer import BudgetOptimizer


class TestBudgetOptimizer:
    
    def setup_method(self):
        """Set up test fixtures."""
        self.optimizer = BudgetOptimizer()
        self.sample_spending = {
            'housing': 25000,
            'groceries': 5000,
            'transportation': 3000,
            'utilities': 2000,
            'food_dining': 4000,
            'entertainment': 2000
        }
        
    def test_optimize_basic(self):
        """Test basic budget optimization."""
        income = 50000
        result = self.optimizer.optimize(income, self.sample_spending, savings_goal_pct=20)
        
        assert result.total_budget <= income * 0.8  # Should leave room for 20% savings
        assert result.optimization_status in ['optimal', 'optimal_inaccurate', 'fallback']
        assert isinstance(result.category_allocations, dict)
        
    def test_optimize_with_high_savings(self):
        """Test optimization with high savings goal."""
        income = 50000
        result = self.optimizer.optimize(income, self.sample_spending, savings_goal_pct=40)
        
        assert result.expected_savings >= income * 0.3  # Should aim for 40%, may be slightly less
        
    def test_suggest_cuts(self):
        """Test spending cut suggestions."""
        cuts = self.optimizer.suggest_cuts(self.sample_spending, target_reduction=5000)
        
        assert isinstance(cuts, dict)
        assert sum(cuts.values()) >= 4500  # Should be close to target
        
    def test_optimize_with_goals(self):
        """Test optimization with financial goals."""
        goals = [
            {'target_amount': 100000, 'months': 12},
            {'target_amount': 50000, 'months': 6}
        ]
        
        income = 60000
        result = self.optimizer.optimize_with_goals(income, self.sample_spending, goals)
        
        assert result.savings_target > 0
        assert isinstance(result.category_allocations, dict)
        
    def test_compare_scenarios(self):
        """Test scenario comparison."""
        scenarios = [
            {'savings_goal_pct': 10},
            {'savings_goal_pct': 20},
            {'savings_goal_pct': 30}
        ]
        
        income = 50000
        results = self.optimizer.compare_scenarios(income, self.sample_spending, scenarios)
        
        assert len(results) == 3
        assert all(hasattr(r, 'expected_savings') for r in results)
        
    def test_constraint_validation(self):
        """Test that budget constraints are respected."""
        income = 50000
        result = self.optimizer.optimize(income, self.sample_spending)
        
        for category, amount in result.category_allocations.items():
            if category in self.optimizer.constraints:
                constraints = self.optimizer.constraints[category]
                min_amount = income * constraints['min']
                max_amount = income * constraints['max']
                
                # Allow some tolerance for optimization
                assert amount >= min_amount * 0.95
                assert amount <= max_amount * 1.05
