# Migration Guide: OpenAI → Gemini

Complete guide for migrating FinPlanAgent from OpenAI GPT-4 to Google Gemini Flash 2.5.

## Quick Migration (5 minutes)

### Step 1: Update Dependencies

```bash
# Uninstall OpenAI package (optional)
pip uninstall openai

# Install Gemini package
pip install google-generativeai>=0.3.0

# Or update all requirements
pip install -r requirements.txt
```

### Step 2: Update Environment Variables

```bash
# Old .env
OPENAI_API_KEY=sk-...

# New .env  
GEMINI_API_KEY=AIza...
# or
GOOGLE_API_KEY=AIza...
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

### Step 3: Update Config (Optional)

```yaml
# config.yaml
llm:
  provider: "gemini"
  model: "gemini-2.0-flash-exp"  # Latest model
  temperature: 0.7
```

### Step 4: Test the Migration

```bash
python main.py --demo
```

That's it! Your code should work without any changes.

---

## Detailed Migration

### API Changes

#### 1. Initialization

**Before (OpenAI):**
```python
from openai import OpenAI

client = OpenAI(api_key='sk-...')
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**After (Gemini):**
```python
import google.generativeai as genai

genai.configure(api_key='AIza...')
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content("Hello")
```

#### 2. Chat Sessions

**Before (OpenAI):**
```python
messages = [
    {"role": "system", "content": "You are a financial advisor"},
    {"role": "user", "content": "Help me save money"}
]
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)
```

**After (Gemini):**
```python
model = genai.GenerativeModel(
    'gemini-2.0-flash-exp',
    system_instruction="You are a financial advisor"
)
chat = model.start_chat(history=[])
response = chat.send_message("Help me save money")
```

#### 3. Function Calling

**Before (OpenAI):**
```python
tools = [{
    "type": "function",
    "function": {
        "name": "calculate_savings",
        "parameters": {...}
    }
}]

response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools
)
```

**After (Gemini):**
```python
tools = [{
    "function_declarations": [{
        "name": "calculate_savings",
        "parameters": {...}
    }]
}]

model = genai.GenerativeModel('gemini-2.0-flash-exp', tools=tools)
response = model.generate_content("Calculate my savings")
```

#### 4. Streaming

**Before (OpenAI):**
```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**After (Gemini):**
```python
response = model.generate_content("Hello", stream=True)

for chunk in response:
    print(chunk.text, end="")
```

### Feature Comparison

| Feature | OpenAI | Gemini | Notes |
|---------|--------|--------|-------|
| **Models** | GPT-4, GPT-3.5 | Flash 2.5, Pro 1.5 | Gemini Flash ≈ GPT-4 speed |
| **Context** | 128K tokens | 1M tokens | Gemini has 8x more context |
| **Pricing** | $0.03/1K tokens | $0.001/1K tokens | Gemini is 30x cheaper |
| **Free Tier** | ❌ No | ✅ 15 RPM | Gemini has free usage |
| **Speed** | Standard | ⚡ Faster | Flash is optimized |
| **Streaming** | ✅ Yes | ✅ Yes | Both support |
| **Functions** | ✅ Yes | ✅ Yes | Similar capability |
| **Multimodal** | Text + Images | Text + Images + Video | Gemini more capable |

### Code Migration Checklist

- [ ] Replace `openai` import with `google.generativeai`
- [ ] Update API key environment variable
- [ ] Change model initialization
- [ ] Update chat message format
- [ ] Modify function calling structure
- [ ] Adjust streaming implementation
- [ ] Update error handling
- [ ] Test all features

### Error Handling Changes

**Before (OpenAI):**
```python
from openai import OpenAIError

try:
    response = client.chat.completions.create(...)
except OpenAIError as e:
    print(f"Error: {e}")
```

**After (Gemini):**
```python
from google.api_core import exceptions

try:
    response = model.generate_content(...)
except exceptions.GoogleAPIError as e:
    print(f"Error: {e}")
```

### FinPlanAgent-Specific Changes

#### agent.py

The main changes are in `src/agent.py`:

1. **Import changes:**
```python
# OLD
from openai import OpenAI

# NEW
import google.generativeai as genai
```

2. **Initialization:**
```python
# OLD
self.client = OpenAI(api_key=self.api_key)

# NEW
genai.configure(api_key=self.api_key)
self.model = genai.GenerativeModel(model_name=model, system_instruction=self.SYSTEM_PROMPT)
```

3. **Chat sessions:**
```python
# OLD
self.conversation_history = []

# NEW
self.chat_session = self.model.start_chat(history=[])
```

4. **Message sending:**
```python
# OLD
response = self.client.chat.completions.create(
    model=self.model,
    messages=self.conversation_history
)

# NEW
response = self.chat_session.send_message(user_message)
```

### Testing After Migration

Run the test suite:

```bash
# Run all tests
pytest tests/

# Test specific agent functionality
pytest tests/test_agent.py -v

# Test with sample data
python main.py --demo
```

### Performance Comparison

Based on typical usage:

**OpenAI GPT-4:**
- Response time: 2-5 seconds
- Cost: ~$0.06 per query
- Rate limit: Tier-based
- Context: 128K tokens

**Gemini Flash 2.5:**
- Response time: 1-3 seconds (⚡ 40% faster)
- Cost: ~$0.002 per query (💰 97% cheaper)
- Rate limit: 15 RPM free, higher paid
- Context: 1M tokens (📚 8x more)

### Common Issues & Solutions

#### Issue 1: API Key Not Working
```python
# Test your key
import google.generativeai as genai

genai.configure(api_key='your_key')
for model in genai.list_models():
    print(model.name)
```

#### Issue 2: Model Not Available
```python
# Check available models
import google.generativeai as genai
genai.configure(api_key='your_key')

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)
```

Use `gemini-1.5-flash` if `gemini-2.0-flash-exp` is unavailable.

#### Issue 3: Rate Limiting
```python
# Add retry logic (already included in agent.py)
import time

for attempt in range(3):
    try:
        response = model.generate_content(prompt)
        break
    except Exception as e:
        if attempt < 2:
            time.sleep(2 ** attempt)
        else:
            raise
```

#### Issue 4: Function Calling Format
```python
# Gemini format
tools = [{
    "function_declarations": [{  # Note: function_declarations (plural)
        "name": "function_name",
        "description": "What it does",
        "parameters": {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param_name"]
        }
    }]
}]
```

### Rollback Plan

If you need to rollback to OpenAI:

```bash
# 1. Reinstall OpenAI
pip install openai

# 2. Restore old agent.py
git checkout origin/main src/agent.py

# 3. Update .env
OPENAI_API_KEY=sk-...

# 4. Test
python main.py --demo
```

### Advanced Features

#### 1. Using Different Models

```python
# Fast and cheap
agent = FinancialAgent(model="gemini-1.5-flash")

# More powerful
agent = FinancialAgent(model="gemini-1.5-pro")

# Latest experimental
agent = FinancialAgent(model="gemini-2.0-flash-exp")
```

#### 2. Custom Safety Settings

```python
from google.generativeai.types import HarmCategory, HarmBlockThreshold

safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(
    'gemini-2.0-flash-exp',
    safety_settings=safety_settings
)
```

#### 3. Generation Config

```python
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    'gemini-2.0-flash-exp',
    generation_config=generation_config
)
```

### Cost Optimization Tips

1. **Use Flash models** for most queries (30x cheaper than Pro)
2. **Implement caching** for repeated queries
3. **Use free tier** for development (15 RPM)
4. **Batch requests** when possible
5. **Monitor usage** via Google Cloud Console

### Support & Resources

- **Gemini Docs**: https://ai.google.dev/docs
- **API Reference**: https://ai.google.dev/api
- **Community**: https://github.com/google-gemini/cookbook
- **Pricing**: https://ai.google.dev/pricing

### Next Steps

1. ✅ Complete migration
2. ✅ Test all features
3. ✅ Monitor performance
4. 🔄 Optimize prompts for Gemini
5. 🔄 Implement caching
6. 🔄 Add multimodal features (images, PDFs)

---

**Migration Time**: 5-15 minutes  
**Difficulty**: Easy  
**Benefits**: 30x cost reduction, faster responses, larger context  

Happy migrating! 🚀
