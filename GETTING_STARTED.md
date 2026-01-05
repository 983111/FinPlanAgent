# Getting Started with FinPlanAgent

## Quick Start Guide

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/983111/finplan-agent.git
cd finplan-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### 3. Basic Usage

#### Option A: Using Jupyter Notebook (Recommended for Beginners)

```bash
jupyter notebook notebooks/demo.ipynb
```

Run through the cells to see the complete workflow.

#### Option B: Python Script

Create a file `my_analysis.py`:

```python
from src.parser import TransactionParser
from src.analyzer import TransactionAnalyzer
from src.profile_builder import ProfileBuilder
from src.optimizer import BudgetOptimizer

# Parse transactions
parser = TransactionParser()
df = parser.parse_csv('data/sample_transactions.csv')

# Analyze
analyzer = TransactionAnalyzer()
df_categorized = analyzer.categorize(df)
patterns = analyzer.compute_spending_patterns(df_categorized)

# Build profile
builder = ProfileBuilder()
profile = builder.build(df_categorized, current_savings=50000)

# Optimize budget
optimizer = BudgetOptimizer()
budget = optimizer.optimize(
    income=profile.monthly_income,
    current_spending=profile.expense_categories,
    savings_goal_pct=20
)

# Print results
print(profile.summary())
print("\n" + "="*50 + "\n")
print(budget.summary())
```

Run it:
```bash
python my_analysis.py
```

## Learning Path for Beginners

### Week 1: Data Processing
**Goal:** Understand how to parse and analyze transaction data

1. **Day 1-2:** Study `parser.py`
   - Learn how CSV parsing works
   - Understand data cleaning and validation
   - Practice: Parse your own CSV file

2. **Day 3-4:** Study `analyzer.py`
   - Learn transaction categorization
   - Understand spending pattern analysis
   - Practice: Categorize different types of transactions

3. **Day 5-7:** Experiments
   - Create custom categories
   - Try different data formats
   - Visualize your spending

**Resources to Learn:**
- Pandas basics: https://pandas.pydata.org/docs/getting_started/intro_tutorials/
- Regular expressions: https://docs.python.org/3/howto/regex.html

### Week 2: Financial Profiling
**Goal:** Build comprehensive financial profiles

1. **Day 1-3:** Study `profile_builder.py`
   - Understand financial metrics
   - Learn about dataclasses
   - Practice: Build profiles with different scenarios

2. **Day 4-5:** Study financial health assessment
   - Learn scoring algorithms
   - Understand benchmarks
   - Practice: Calculate your own health score

3. **Day 6-7:** Experiments
   - Compare different profiles
   - Test edge cases
   - Generate reports

**Resources to Learn:**
- Personal finance basics: https://www.investopedia.com/
- Python dataclasses: https://docs.python.org/3/library/dataclasses.html

### Week 3: Optimization
**Goal:** Master budget optimization

1. **Day 1-3:** Study `optimizer.py`
   - Understand linear programming basics
   - Learn CVXPY syntax
   - Practice: Simple optimization problems

2. **Day 4-5:** Advanced optimization
   - Constraints and objectives
   - Multi-scenario optimization
   - Practice: Create custom constraints

3. **Day 6-7:** Integration
   - Connect optimizer with other modules
   - Test different optimization goals
   - Compare results

**Resources to Learn:**
- Linear programming: https://optimization.mccormick.northwestern.edu/
- CVXPY tutorial: https://www.cvxpy.org/tutorial/

### Week 4: AI Agent & Simulation
**Goal:** Implement AI-powered features

1. **Day 1-3:** Study `agent.py`
   - Understand LLM integration
   - Learn prompt engineering
   - Practice: Create custom prompts

2. **Day 4-5:** Study `simulator.py`
   - Learn scenario modeling
   - Understand impact analysis
   - Practice: Create custom scenarios

3. **Day 6-7:** Final integration
   - Run complete pipeline
   - Test with real data
   - Prepare demo

**Resources to Learn:**
- OpenAI API: https://platform.openai.com/docs/
- Prompt engineering: https://www.promptingguide.ai/

## Common Tasks

### Adding a New Category

Edit `src/analyzer.py`:

```python
CATEGORY_KEYWORDS = {
    # ... existing categories ...
    'new_category': ['keyword1', 'keyword2', 'keyword3']
}
```

### Customizing Budget Constraints

Edit `config.yaml`:

```yaml
budget_constraints:
  new_category:
    min: 0.05
    max: 0.15
    recommended: 0.10
```

### Creating Custom Reports

```python
from src.explainer import Explainer

explainer = Explainer()
report = explainer.generate_report(profile, analysis, recommendations)

# Save to file
with open('my_report.txt', 'w') as f:
    f.write(report)
```

### Running Simulations

```python
from src.simulator import WhatIfSimulator

simulator = WhatIfSimulator(profile.to_dict())

# Test different scenarios
scenarios = [
    simulator.simulate_purchase("Laptop", 80000, "cash"),
    simulator.simulate_expense_reduction("dining", 25),
    simulator.simulate_income_change(10, "Promotion")
]

# Compare
comparison = simulator.compare_scenarios(scenarios)
print(comparison)
```

## Testing Your Code

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_parser.py

# Run with coverage
pytest --cov=src tests/
```

## Debugging Tips

1. **Transaction not categorized correctly?**
   - Check `CATEGORY_KEYWORDS` in `analyzer.py`
   - Add more specific keywords
   - Test with `_rule_based_categorize()` directly

2. **Optimization not working?**
   - Check if income > expenses
   - Verify constraints in `config.yaml`
   - Try lower savings goal percentage

3. **API errors?**
   - Verify API key in `.env`
   - Check API rate limits
   - Test with smaller requests first

## Next Steps

Once you're comfortable with the basics:

1. **Add Features:**
   - Investment tracking
   - Multi-currency support
   - Goal progress tracking
   - Automated report generation

2. **Improve Performance:**
   - Cache LLM responses
   - Optimize database queries
   - Parallel processing for large datasets

3. **Build Interface:**
   - Create Streamlit dashboard
   - Build REST API
   - Mobile app integration

4. **Research Extensions:**
   - Compare optimization algorithms
   - User study on explainability
   - Robustness testing
   - Behavioral finance integration

## Getting Help

- Check the documentation in each module
- Review test files for usage examples
- Open an issue on GitHub
- Read the original research paper references

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Additional Resources

- **Financial Planning:** https://www.bogleheads.org/wiki/
- **Python Best Practices:** https://realpython.com/
- **ML in Finance:** https://www.quantstart.com/
- **Optimization:** https://neos-guide.org/

Good luck with your project! 🚀
