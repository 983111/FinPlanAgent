# FinPlanAgent: AI-Driven Personal Financial Advisor (Gemini Edition)

An autonomous AI agent powered by **Google Gemini Flash 2.5** that provides personalized financial planning with explainable recommendations and what-if scenario analysis.

## 🚀 What's New - Gemini Integration

This version uses **Google's Gemini 2.0 Flash** (the latest 2025 model) instead of OpenAI's GPT. Benefits include:

- ✅ **Free tier available** - 15 RPM free usage
- ✅ **Faster responses** - Optimized for speed
- ✅ **Multimodal capabilities** - Ready for future image/PDF analysis
- ✅ **Function calling** - Native tool integration
- ✅ **Long context** - Handle more financial data
- ✅ **Cost-effective** - Lower pricing for production use

## Features

- **Automatic Transaction Categorization**: ML-powered expense classification
- **Financial Profile Analysis**: Calculate savings rate, debt ratios, and risk metrics
- **Budget Optimization**: Linear programming-based budget allocation
- **What-If Scenarios**: Simulate financial decisions before making them
- **Explainable AI**: Every recommendation comes with clear reasoning
- **Interactive Q&A**: Natural language queries about your finances powered by Gemini

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Google API Key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Setup

1. Clone the repository:
```bash
git clone https://github.com/983111/finplan-agent.git
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
# Edit .env and add your Google/Gemini API key
```

### Getting Your Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file:
```
GEMINI_API_KEY=your_api_key_here
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

# Initialize AI agent with Gemini
agent = FinancialAgent(api_key='your-gemini-api-key')
response = agent.chat("How can I save more money?")
print(response)
```

### Running the Demo

```bash
# Interactive mode
python main.py --interactive

# Demo with sample data
python main.py --demo

# Jupyter notebook
jupyter notebook notebooks/demo.ipynb
```

## Gemini-Specific Features

### Function Calling
The Gemini agent can automatically call financial calculation functions:

```python
agent = FinancialAgent()
agent.initialize_context(profile, transactions, budget)

# Gemini will automatically use tools when needed
response = agent.chat("If I reduce dining expenses by 30%, how much can I save?")
# Automatically calls calculate_savings_potential()
```

### Streaming Responses
```python
# Get real-time streaming responses
response = agent.chat("Analyze my spending", stream=True)
```

### Context Management
```python
# Gemini maintains conversation context automatically
agent.chat("What's my current savings rate?")
agent.chat("How can I improve it?")  # Gemini remembers previous context
agent.chat("Show me a step-by-step plan")  # Continues the conversation
```

## Project Structure

```
finplan-agent/
├── src/                    # Core source code
│   ├── agent.py           # Gemini-powered AI agent
│   ├── parser.py          # CSV/PDF transaction parser
│   ├── analyzer.py        # Transaction categorization
│   ├── profile_builder.py # Financial profile generation
│   ├── optimizer.py       # Budget optimization (CVXPY)
│   ├── simulator.py       # What-if scenario engine
│   ├── explainer.py       # Explainability layer
│   └── utils.py           # Helper functions
├── tests/                 # Unit tests
├── data/                  # Sample data
├── notebooks/             # Jupyter notebooks
├── requirements.txt       # Python dependencies (Gemini version)
└── README.md             # This file
```

## Configuration

Edit `config.yaml` to customize:

- Gemini model selection (Flash 2.5, Pro, etc.)
- Expense categories
- Budget constraints
- Optimization parameters
- Temperature and generation settings

### Available Gemini Models

```yaml
llm:
  model: "gemini-2.0-flash-exp"    # Latest Flash 2.5 (recommended)
  # model: "gemini-1.5-pro"         # More powerful, slower
  # model: "gemini-1.5-flash"       # Fast, cost-effective
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

## Gemini API Pricing (as of 2025)

- **Free tier**: 15 requests per minute
- **Paid tier**: Extremely cost-effective
  - Input: Much cheaper than GPT-4
  - Output: Significantly lower costs
  - See [Google AI pricing](https://ai.google.dev/pricing) for current rates

## Migration from OpenAI

If you're migrating from the OpenAI version:

1. Install new requirements: `pip install -r requirements.txt`
2. Update `.env` file with `GEMINI_API_KEY`
3. The API is fully compatible - no code changes needed!
4. Optional: Adjust model in `config.yaml`

## Key Differences from OpenAI Version

| Feature | OpenAI GPT-4 | Gemini Flash 2.5 |
|---------|--------------|------------------|
| Speed | Standard | ⚡ **Faster** |
| Cost | Higher | 💰 **Lower** |
| Free Tier | No | ✅ **Yes (15 RPM)** |
| Context Window | 128K | 📚 **1M tokens** |
| Function Calling | ✅ Yes | ✅ Yes |
| Streaming | ✅ Yes | ✅ Yes |
| Multimodal | Limited | 🎨 **Better** |

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

### Custom Query with Gemini
```python
agent = FinancialAgent()
response = agent.chat(
    "If I reduce dining out by 30%, how much can I save in 6 months?"
)
# Gemini automatically calls calculate_savings_potential() 
# and provides detailed analysis
```

## Troubleshooting

### API Key Issues
```python
# Check if your API key is working
import google.generativeai as genai
genai.configure(api_key='your_key')
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content("Hello")
print(response.text)
```

### Rate Limiting
- Free tier: 15 requests/minute
- If you hit limits, the agent will automatically retry with backoff
- Consider upgrading to paid tier for production use

### Model Availability
If `gemini-2.0-flash-exp` is not available in your region:
- Use `gemini-1.5-flash` instead
- Update `config.yaml` or pass model name to `FinancialAgent(model='gemini-1.5-flash')`

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Powered by **Google Gemini** (Flash 2.5)
- Built for MBZUAI project requirements
- Inspired by modern agentic AI research
- Uses CVXPY for budget optimization

## Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Google AI Studio](https://makersuite.google.com/)
- [Gemini Cookbook](https://github.com/google-gemini/cookbook)
- [Project Documentation](docs/)

## Contact

For questions or feedback, open an issue on GitHub.

---

**Powered by Google Gemini Flash 2.5 | Production-Ready | Research-Grade | Cost-Effective** 🚀
