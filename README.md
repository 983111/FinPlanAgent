# FinPlanAgent: AI-Driven Personal Financial Advisor

An autonomous AI agent that provides personalized financial planning with explainable recommendations and what-if scenario analysis.

## Features

- **Automatic Transaction Categorization**: ML-powered expense classification
- **Financial Profile Analysis**: Calculate savings rate, debt ratios, and risk metrics
- **Budget Optimization**: Linear programming-based budget allocation
- **What-If Scenarios**: Simulate financial decisions before making them
- **Explainable AI**: Every recommendation comes with clear reasoning
- **Interactive Q&A**: Natural language queries about your finances

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/finplan-agent.git
cd finplan-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

### Basic Usage

```python
from src.parser import TransactionParser
from src.analyzer import TransactionAnalyzer
from src.profile_builder import ProfileBuilder
from src.optimizer import BudgetOptimizer
from src.agent import FinancialAgent

# Parse transactions
parser = TransactionParser()
transactions = parser.parse_csv('data/sample_transactions.csv')

# Analyze spending patterns
analyzer = TransactionAnalyzer()
categorized = analyzer.categorize(transactions)

# Build financial profile
profile_builder = ProfileBuilder()
profile = profile_builder.build(categorized)

# Optimize budget
optimizer = BudgetOptimizer()
optimal_budget = optimizer.optimize(profile)

# Initialize AI agent
agent = FinancialAgent(api_key='your-api-key')
response = agent.chat("How can I save more money?")
print(response)
```

### Running the Demo

```bash
jupyter notebook notebooks/demo.ipynb
```

## Project Structure

```
finplan-agent/
├── src/                    # Core source code
│   ├── parser.py          # CSV/PDF transaction parser
│   ├── analyzer.py        # Transaction categorization
│   ├── profile_builder.py # Financial profile generation
│   ├── optimizer.py       # Budget optimization (CVXPY)
│   ├── agent.py           # LLM-powered agent
│   ├── simulator.py       # What-if scenario engine
│   ├── explainer.py       # Explainability layer
│   └── utils.py           # Helper functions
├── tests/                 # Unit tests
├── data/                  # Sample data
├── notebooks/             # Jupyter notebooks
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration

Edit `config.yaml` to customize:

- Expense categories
- Budget constraints
- Optimization parameters
- LLM settings

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Examples

### What-If Scenario
```python
from src.simulator import WhatIfSimulator

simulator = WhatIfSimulator(profile)
result = simulator.simulate_purchase(
    item="Car",
    amount=800000,
    payment_plan="loan",
    duration_months=60
)
print(result.impact_summary)
```

### Custom Query
```python
agent = FinancialAgent()
response = agent.chat(
    "If I reduce dining out by 30%, how much can I save in 6 months?"
)
```

## Research Components

This project includes research-ready features for academic evaluation:

- **Reasoning Evaluation**: Compare agent recommendations with financial best practices
- **Robustness Testing**: Test with noisy/incomplete data
- **Explainability Metrics**: Measure recommendation transparency
- **Optimization Comparison**: LP vs RL approaches

See `notebooks/analysis.ipynb` for detailed experiments.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Citation

If you use this project in your research, please cite:

```
@software{finplanagent2024,
  title={FinPlanAgent: AI-Driven Personal Financial Advisor},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/finplan-agent}
}
```

## Contact

For questions or feedback, open an issue on GitHub.

## Acknowledgments

- Built for MBZUAI project requirements
- Inspired by modern agentic AI research
- Uses OpenAI GPT models for reasoning
