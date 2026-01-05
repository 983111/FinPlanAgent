# Complete Setup & Testing Guide (Gemini Version)

Step-by-step guide to set up and test FinPlanAgent with Google Gemini Flash 2.5.

## Part 1: Initial Setup

### Step 1: Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"** or **"Get API Key"**
4. Copy the key (starts with `AIza...`)
5. Keep it secure - don't commit to Git!

### Step 2: Clone and Install

```bash
# Clone repository
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

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

Add your Gemini API key:
```bash
GEMINI_API_KEY=AIzaSyC_your_actual_key_here
```

### Step 4: Verify Installation

```python
# Quick test script
python -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content('Hello!')
print('✅ Gemini API is working!')
print('Response:', response.text)
"
```

Expected output:
```
✅ Gemini API is working!
Response: Hello! How can I help you today?
```

## Part 2: Testing Core Functionality

### Test 1: Transaction Parser

```bash
# Create test script
cat > test_parser.py << 'EOF'
from src.parser import TransactionParser

parser = TransactionParser()
df = parser.parse_csv('data/sample_transactions.csv')

print(f"✅ Loaded {len(df)} transactions")
print(f"✅ Date range: {df['date'].min()} to {df['date'].max()}")
print(f"✅ Total income: ₹{df[df['type']=='credit']['amount'].sum():,.2f}")
print(f"✅ Total expenses: ₹{abs(df[df['type']=='debit']['amount'].sum()):,.2f}")
EOF

python test_parser.py
```

Expected output:
```
✅ Loaded 65 transactions
✅ Date range: 2024-01-01 to 2024-04-30
✅ Total income: ₹315,000.00
✅ Total expenses: ₹165,000.00
```

### Test 2: Transaction Analyzer

```bash
cat > test_analyzer.py << 'EOF'
from src.parser import TransactionParser
from src.analyzer import TransactionAnalyzer

parser = TransactionParser()
df = parser.parse_csv('data/sample_transactions.csv')

analyzer = TransactionAnalyzer()
df_categorized = analyzer.categorize(df)

print("✅ Transaction categorization complete")
print("\nCategory distribution:")
print(df_categorized['category'].value_counts())

patterns = analyzer.compute_spending_patterns(df_categorized)
print(f"\n✅ Monthly savings: ₹{patterns['net_savings']:,.2f}")
EOF

python test_analyzer.py
```

### Test 3: Profile Builder

```bash
cat > test_profile.py << 'EOF'
from src.parser import TransactionParser
from src.analyzer import TransactionAnalyzer
from src.profile_builder import ProfileBuilder

parser = TransactionParser()
df = parser.parse_csv('data/sample_transactions.csv')

analyzer = TransactionAnalyzer()
df_categorized = analyzer.categorize(df)

builder = ProfileBuilder()
profile = builder.build(df_categorized, current_savings=50000)

print("✅ Financial profile created")
print(profile.summary())

health = builder.assess_financial_health(profile)
print(f"\n✅ Health Score: {health['overall_score']:.1f}/100")
print(f"✅ Rating: {health['health_rating']}")
EOF

python test_profile.py
```

### Test 4: Budget Optimizer

```bash
cat > test_optimizer.py << 'EOF'
from src.parser import TransactionParser
from src.analyzer import TransactionAnalyzer
from src.profile_builder import ProfileBuilder
from src.optimizer import BudgetOptimizer

# Load and analyze data
parser = TransactionParser()
df = parser.parse_csv('data/sample_transactions.csv')

analyzer = TransactionAnalyzer()
df_categorized = analyzer.categorize(df)

builder = ProfileBuilder()
profile = builder.build(df_categorized, current_savings=50000)

# Optimize budget
optimizer = BudgetOptimizer()
budget = optimizer.optimize(
    income=profile.monthly_income,
    current_spending=profile.expense_categories,
    savings_goal_pct=20
)

print("✅ Budget optimization complete")
print(budget.summary())
EOF

python test_optimizer.py
```

### Test 5: Gemini Agent (Most Important!)

```bash
cat > test_gemini_agent.py << 'EOF'
import os
from dotenv import load_dotenv
from src.parser import TransactionParser
from src.analyzer import TransactionAnalyzer
from src.profile_builder import ProfileBuilder
from src.agent import FinancialAgent

# Load environment
load_dotenv()

# Prepare data
parser = TransactionParser()
df = parser.parse_csv('data/sample_transactions.csv')

analyzer = TransactionAnalyzer()
df_categorized = analyzer.categorize(df)

builder = ProfileBuilder()
profile = builder.build(df_categorized, current_savings=50000)

patterns = analyzer.compute_spending_patterns(df_categorized)

# Initialize Gemini agent
print("🤖 Initializing Gemini agent...")
agent = FinancialAgent()

# Set context
agent.initialize_context(
    profile=profile.to_dict(),
    transactions_summary=patterns
)
print("✅ Context initialized\n")

# Test conversation
print("Testing basic query...")
response1 = agent.chat("What's my current savings rate?")
print(f"Response: {response1}\n")

print("Testing function calling...")
response2 = agent.chat("If I reduce dining expenses by 25%, how much can I save annually?")
print(f"Response: {response2}\n")

print("Testing contextual follow-up...")
response3 = agent.chat("Is that a good savings rate?")
print(f"Response: {response3}\n")

print("✅ All Gemini agent tests passed!")
EOF

python test_gemini_agent.py
```

Expected output:
```
🤖 Initializing Gemini agent...
✅ Context initialized

Testing basic query...
Response: Your current savings rate is 15.2%. This means...

Testing function calling...
Response: If you reduce dining expenses by 25%, you would save ₹1,200 per month, which amounts to ₹14,400 annually...

Testing contextual follow-up...
Response: A 15.2% savings rate is fair, but financial experts typically recommend...

✅ All Gemini agent tests passed!
```

## Part 3: Full Integration Test

### Run Complete Demo

```bash
# Run the main demo
python main.py --demo
```

This will:
1. ✅ Parse transactions
2. ✅ Analyze spending
3. ✅ Build financial profile
4. ✅ Optimize budget
5. ✅ Generate insights
6. ✅ Run simulations
7. ✅ Initialize Gemini agent (if API key is set)
8. ✅ Generate report

### Interactive Mode

```bash
python main.py --interactive
```

Follow the prompts to:
- Provide your transaction file
- Specify current savings
- Enable/disable Gemini agent
- Get personalized analysis

## Part 4: Testing Gemini-Specific Features

### Test Streaming Responses

```python
from src.agent import FinancialAgent

agent = FinancialAgent()
agent.initialize_context(profile.to_dict(), patterns)

# Enable streaming
response = agent.chat(
    "Give me a detailed 5-step plan to improve my finances",
    stream=True
)
```

### Test Function Calling

```python
# This should automatically trigger calculate_savings_potential
response = agent.chat(
    "Calculate how much I'd save by reducing entertainment by 30%"
)

# This should trigger simulate_loan_impact
response = agent.chat(
    "What if I take a ₹500,000 loan at 9% for 5 years?"
)

# This should trigger check_goal_feasibility
response = agent.chat(
    "Can I save ₹200,000 in 10 months?"
)
```

### Test Conversation Context

```python
# Multi-turn conversation
agent.chat("What's my biggest expense?")
agent.chat("How can I reduce it?")  # Should remember previous context
agent.chat("Show me a 3-month plan")  # Should continue the same topic
```

## Part 5: Performance Testing

### Test Response Time

```bash
cat > test_performance.py << 'EOF'
import time
from src.agent import FinancialAgent

agent = FinancialAgent()
queries = [
    "What's my savings rate?",
    "How can I save more?",
    "Analyze my spending patterns",
]

for query in queries:
    start = time.time()
    response = agent.chat(query)
    elapsed = time.time() - start
    print(f"Query: {query}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Response length: {len(response)} chars\n")
EOF

python test_performance.py
```

Expected results:
- Simple queries: 1-2 seconds
- Complex queries: 2-4 seconds
- With function calls: 3-5 seconds

### Test Rate Limiting

```bash
# Free tier: 15 requests per minute
cat > test_rate_limit.py << 'EOF'
import time
from src.agent import FinancialAgent

agent = FinancialAgent()

print("Testing rate limits (15 RPM free tier)...")
for i in range(20):
    try:
        start = time.time()
        response = agent.chat(f"Quick test {i+1}")
        elapsed = time.time() - start
        print(f"Request {i+1}: ✅ {elapsed:.2f}s")
    except Exception as e:
        print(f"Request {i+1}: ❌ Rate limited - {e}")
        time.sleep(5)  # Wait before retry
EOF

python test_rate_limit.py
```

## Part 6: Unit Tests

### Run All Tests

```bash
# Run full test suite
pytest tests/ -v

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_parser.py -v
pytest tests/test_analyzer.py -v
pytest tests/test_optimizer.py -v
```

### Expected Results

```
tests/test_parser.py::test_parse_csv_basic PASSED
tests/test_parser.py::test_clean_amount PASSED
tests/test_parser.py::test_validate_data PASSED
tests/test_analyzer.py::test_categorize_transactions PASSED
tests/test_analyzer.py::test_compute_spending_patterns PASSED
tests/test_optimizer.py::test_optimize_basic PASSED
tests/test_optimizer.py::test_suggest_cuts PASSED

========== 15 passed in 2.34s ==========
```

## Part 7: Troubleshooting

### Problem 1: API Key Not Working

```bash
# Test API key directly
python << 'EOF'
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('GEMINI_API_KEY')

if not key:
    print("❌ GEMINI_API_KEY not found in .env")
    exit(1)

print(f"Key starts with: {key[:10]}...")

try:
    genai.configure(api_key=key)
    models = list(genai.list_models())
    print(f"✅ API key valid! Found {len(models)} models")
except Exception as e:
    print(f"❌ API key invalid: {e}")
EOF
```

### Problem 2: Module Import Errors

```bash
# Verify installation
pip list | grep -E "google-generativeai|pandas|cvxpy|numpy"

# Reinstall if needed
pip install --upgrade -r requirements.txt
```

### Problem 3: Model Not Available

```bash
# List available models
python << 'EOF'
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
EOF
```

If `gemini-2.0-flash-exp` is not listed, update agent.py:
```python
# Use stable version instead
agent = FinancialAgent(model="gemini-1.5-flash")
```

### Problem 4: Rate Limiting (Free Tier)

```bash
# Check current usage (approximate)
# Free tier: 15 requests per minute

# Solution: Add delays between requests
import time
time.sleep(5)  # Wait 5 seconds between requests
```

## Part 8: Production Checklist

Before deploying to production:

- [ ] API key is in environment variables (not hardcoded)
- [ ] Error handling is robust
- [ ] Rate limiting is implemented
- [ ] Logging is configured
- [ ] All tests pass
- [ ] Performance is acceptable
- [ ] Cost monitoring is set up
- [ ] Backup/fallback plan exists
- [ ] Documentation is updated
- [ ] Security review completed

## Part 9: Monitoring & Maintenance

### Monitor Usage

```python
# Add to your code
from src.agent import FinancialAgent

agent = FinancialAgent()

# After multiple queries
usage = agent.get_token_usage_estimate()
print(f"Estimated tokens used: {usage['estimated_tokens']}")
print(f"Number of messages: {usage['messages']}")
```

### Export Conversations

```python
# Save conversation history
agent.export_conversation('conversation_log.json')
```

### Reset When Needed

```python
# Reset conversation but keep context
agent.reset_conversation()
```

## Success Criteria

✅ **All systems operational if:**
1. Parser loads 65 transactions without errors
2. Analyzer categorizes transactions correctly
3. Profile builder generates complete profile
4. Optimizer produces feasible budget
5. Gemini agent responds to queries
6. Function calling works automatically
7. Streaming responses work
8. All unit tests pass
9. Demo runs successfully
10. Reports generate correctly

## Next Steps

After successful testing:

1. 📊 Analyze your own transaction data
2. 🎯 Set financial goals
3. 💡 Get personalized recommendations
4. 📈 Track progress over time
5. 🔄 Iterate and improve

## Support

If you encounter issues:

1. Check this guide first
2. Review error messages carefully
3. Test individual components
4. Check API key and permissions
5. Review Gemini documentation
6. Open an issue on GitHub

---

**Setup Time**: 15-30 minutes  
**Testing Time**: 30-60 minutes  
**Total Time**: 1-2 hours  

Good luck! 🚀
