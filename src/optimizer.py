import cvxpy as cp
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class BudgetPlan:
    """Data class for optimized budget plan."""
    
    category_allocations: Dict[str, float]
    total_budget: float
    savings_target: float
    expected_savings: float
    optimization_status: str
    constraints_met: Dict[str, bool]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'category_allocations': self.category_allocations,
            'total_budget': self.total_budget,
            'savings_target': self.savings_target,
            'expected_savings': self.expected_savings,
            'status': self.optimization_status,
            'constraints_met': self.constraints_met
        }
    
    def summary(self) -> str:
        """Generate text summary."""
        summary = "Optimized Budget Plan\n" + "="*40 + "\n\n"
        summary += f"Total Budget: ₹{self.total_budget:,.2f}\n"
        summary += f"Savings Target: ₹{self.savings_target:,.2f}\n"
        summary += f"Expected Savings: ₹{self.expected_savings:,.2f}\n\n"
        summary += "Category Allocations:\n"
        
        for category, amount in sorted(
            self.category_allocations.items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
            pct = (amount / self.total_budget * 100) if self.total_budget > 0 else 0
            summary += f"  {category:20s}: ₹{amount:8,.2f} ({pct:5.1f}%)\n"
        
        return summary


class BudgetOptimizer:
    """Optimize budget allocation using linear programming."""
    
    # Default budget constraints (as percentage of income)
    DEFAULT_CONSTRAINTS = {
        'housing': {'min': 0.20, 'max': 0.35},
        'groceries': {'min': 0.10, 'max': 0.20},
        'transportation': {'min': 0.05, 'max': 0.15},
        'utilities': {'min': 0.05, 'max': 0.10},
        'healthcare': {'min': 0.05, 'max': 0.15},
        'food_dining': {'min': 0.00, 'max': 0.10},
        'entertainment': {'min': 0.00, 'max': 0.08},
        'shopping': {'min': 0.00, 'max': 0.10},
        'education': {'min': 0.00, 'max': 0.15},
        'insurance': {'min': 0.05, 'max': 0.10},
        'others': {'min': 0.00, 'max': 0.10}
    }
    
    def __init__(self, custom_constraints: Optional[Dict] = None):
        """
        Initialize optimizer with optional custom constraints.
        
        Args:
            custom_constraints: Dictionary of category constraints
        """
        self.constraints = custom_constraints or self.DEFAULT_CONSTRAINTS
        
    def optimize(self, 
                income: float,
                current_spending: Dict[str, float],
                savings_goal_pct: float = 20.0,
                priorities: Optional[Dict[str, float]] = None) -> BudgetPlan:
        """
        Optimize budget allocation to maximize savings while meeting constraints.
        
        Args:
            income: Monthly income
            current_spending: Current spending by category
            savings_goal_pct: Target savings as percentage of income
            priorities: Optional priority weights for categories (higher = more important)
            
        Returns:
            BudgetPlan with optimized allocations
        """
        categories = list(self.constraints.keys())
        n_categories = len(categories)
        
        # Decision variables: budget allocation per category
        allocations = cp.Variable(n_categories, nonneg=True)
        
        # Target savings
        savings_target = income * (savings_goal_pct / 100)
        
        # Objective: Minimize deviation from current spending while achieving savings
        # Penalize changes from current spending patterns
        current_vector = np.array([
            current_spending.get(cat, 0) for cat in categories
        ])
        
        # Priority weights (default to equal if not specified)
        if priorities is None:
            weights = np.ones(n_categories)
        else:
            weights = np.array([priorities.get(cat, 1.0) for cat in categories])
        
        # Objective: minimize weighted deviation + maximize savings
        objective = cp.Minimize(
            cp.sum_squares(cp.multiply(weights, allocations - current_vector))
            - 0.1 * (income - cp.sum(allocations))  # Encourage savings
        )
        
        # Constraints
        constraints = []
        
        # Total budget constraint (leave room for savings)
        constraints.append(cp.sum(allocations) <= income - savings_target)
        
        # Per-category constraints
        for i, category in enumerate(categories):
            cat_constraints = self.constraints[category]
            
            # Minimum and maximum allocations
            min_alloc = income * cat_constraints['min']
            max_alloc = income * cat_constraints['max']
            
            constraints.append(allocations[i] >= min_alloc)
            constraints.append(allocations[i] <= max_alloc)
        
        # Solve optimization problem
        problem = cp.Problem(objective, constraints)
        
        try:
            problem.solve()
            status = problem.status
            
            if status in ['optimal', 'optimal_inaccurate']:
                # Extract solution
                allocations_dict = {
                    cat: float(allocations.value[i]) 
                    for i, cat in enumerate(categories)
                }
                
                total_allocated = sum(allocations_dict.values())
                expected_savings = income - total_allocated
                
                # Check which constraints are met
                constraints_met = self._check_constraints(
                    allocations_dict, income, savings_target
                )
                
                return BudgetPlan(
                    category_allocations=allocations_dict,
                    total_budget=total_allocated,
                    savings_target=savings_target,
                    expected_savings=expected_savings,
                    optimization_status=status,
                    constraints_met=constraints_met
                )
            else:
                # Optimization failed, return current spending
                return self._create_fallback_plan(
                    income, current_spending, savings_target
                )
                
        except Exception as e:
            print(f"Optimization error: {e}")
            return self._create_fallback_plan(
                income, current_spending, savings_target
            )
    
    def optimize_with_goals(self,
                          income: float,
                          current_spending: Dict[str, float],
                          goals: List[Dict]) -> BudgetPlan:
        """
        Optimize budget considering specific financial goals.
        
        Args:
            income: Monthly income
            current_spending: Current spending by category
            goals: List of financial goals with target amounts and timelines
            
        Returns:
            BudgetPlan optimized for goals
        """
        # Calculate required monthly savings for goals
        total_monthly_required = 0
        
        for goal in goals:
            target_amount = goal.get('target_amount', 0)
            months = goal.get('months', 12)
            monthly_required = target_amount / months
            total_monthly_required += monthly_required
        
        # Calculate savings percentage needed
        savings_pct = (total_monthly_required / income * 100) if income > 0 else 20
        savings_pct = max(10, min(50, savings_pct))  # Clamp between 10-50%
        
        return self.optimize(income, current_spending, savings_pct)
    
    def compare_scenarios(self,
                         income: float,
                         current_spending: Dict[str, float],
                         scenarios: List[Dict]) -> List[BudgetPlan]:
        """
        Compare multiple budget scenarios.
        
        Args:
            income: Monthly income
            current_spending: Current spending by category
            scenarios: List of scenario configurations
            
        Returns:
            List of BudgetPlans for each scenario
        """
        results = []
        
        for scenario in scenarios:
            savings_goal = scenario.get('savings_goal_pct', 20.0)
            priorities = scenario.get('priorities', None)
            
            plan = self.optimize(income, current_spending, savings_goal, priorities)
            results.append(plan)
        
        return results
    
    def suggest_cuts(self,
                    current_spending: Dict[str, float],
                    target_reduction: float) -> Dict[str, float]:
        """
        Suggest spending cuts to achieve target reduction.
        
        Args:
            current_spending: Current spending by category
            target_reduction: Target amount to reduce spending
            
        Returns:
            Dictionary of suggested cuts by category
        """
        # Prioritize cutting discretionary categories
        discretionary = ['food_dining', 'entertainment', 'shopping', 'others']
        
        cuts = {}
        remaining_reduction = target_reduction
        
        # First pass: Cut discretionary by up to 30%
        for category in discretionary:
            if category in current_spending and remaining_reduction > 0:
                current_amount = current_spending[category]
                max_cut = current_amount * 0.3
                actual_cut = min(max_cut, remaining_reduction)
                
                if actual_cut > 0:
                    cuts[category] = actual_cut
                    remaining_reduction -= actual_cut
        
        # Second pass: Cut all categories proportionally if needed
        if remaining_reduction > 0:
            total_spending = sum(current_spending.values())
            
            for category, amount in current_spending.items():
                if category not in cuts:
                    cuts[category] = 0
                
                proportion = amount / total_spending if total_spending > 0 else 0
                additional_cut = remaining_reduction * proportion
                cuts[category] += additional_cut
        
        return cuts
    
    def _check_constraints(self,
                         allocations: Dict[str, float],
                         income: float,
                         savings_target: float) -> Dict[str, bool]:
        """Check if budget meets all constraints."""
        constraints_met = {}
        
        # Check total budget constraint
        total = sum(allocations.values())
        constraints_met['total_budget'] = total <= (income - savings_target * 0.9)
        
        # Check category constraints
        for category, amount in allocations.items():
            if category in self.constraints:
                cat_constraints = self.constraints[category]
                min_alloc = income * cat_constraints['min']
                max_alloc = income * cat_constraints['max']
                
                constraints_met[category] = min_alloc <= amount <= max_alloc
        
        return constraints_met
    
    def _create_fallback_plan(self,
                            income: float,
                            current_spending: Dict[str, float],
                            savings_target: float) -> BudgetPlan:
        """Create a fallback plan when optimization fails."""
        # Scale down current spending proportionally
        total_current = sum(current_spending.values())
        target_budget = income - savings_target
        
        categories = list(self.constraints.keys())
        min_allocations = {
            cat: income * self.constraints[cat]['min'] for cat in categories
        }
        max_allocations = {
            cat: income * self.constraints[cat]['max'] for cat in categories
        }

        allocations = {
            cat: float(np.clip(current_spending.get(cat, min_allocations[cat]),
                              min_allocations[cat],
                              max_allocations[cat]))
            for cat in categories
        }

        current_total = sum(allocations.values())
        if current_total <= 0:
            equal_share = target_budget / len(categories) if categories else 0
            allocations = {
                cat: float(np.clip(equal_share, min_allocations[cat], max_allocations[cat]))
                for cat in categories
            }
            current_total = sum(allocations.values())

        if current_total > 0:
            scale_factor = target_budget / current_total
            allocations = {cat: amount * scale_factor for cat, amount in allocations.items()}

        # Re-clip after scaling and redistribute residual while respecting bounds
        for cat in categories:
            allocations[cat] = float(np.clip(allocations[cat], min_allocations[cat], max_allocations[cat]))

        residual = target_budget - sum(allocations.values())
        if abs(residual) > 1e-6:
            adjustable = categories.copy()
            while adjustable and abs(residual) > 1e-6:
                per_cat = residual / len(adjustable)
                next_adjustable = []

                for cat in adjustable:
                    proposed = allocations[cat] + per_cat
                    bounded = float(np.clip(proposed, min_allocations[cat], max_allocations[cat]))
                    moved = bounded - allocations[cat]
                    allocations[cat] = bounded
                    residual -= moved

                    # keep only categories that can still move in the needed direction
                    if residual > 1e-6 and allocations[cat] < max_allocations[cat]:
                        next_adjustable.append(cat)
                    elif residual < -1e-6 and allocations[cat] > min_allocations[cat]:
                        next_adjustable.append(cat)

                adjustable = next_adjustable
        
        total_allocated = sum(allocations.values())
        
        return BudgetPlan(
            category_allocations=allocations,
            total_budget=total_allocated,
            savings_target=savings_target,
            expected_savings=income - total_allocated,
            optimization_status='fallback',
            constraints_met={}
        )
