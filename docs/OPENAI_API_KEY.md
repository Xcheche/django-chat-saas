# How to Get an OpenAI API Key

This project **currently uses Ollama (free)**. You do **not** need an OpenAI key to run the app today.

This guide is here because:

- The original tutorial was built for OpenAI's ChatGPT API
- You may want to switch back to OpenAI later for stronger models
- The commented code in `profiles/ai_engine.py` expects an API key

---

## Step 1: Create an OpenAI account

1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Click **Sign up** (or log in with Google/Microsoft)
3. Verify your email and phone number if prompted

---

## Step 2: Add billing (required for API access)

OpenAI API usage is **paid** (not the same as free ChatGPT on the website).

1. Open [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)
2. Click **Add payment method**
3. Add a credit/debit card
4. Optionally set a **usage limit** so you don't overspend (recommended for learning)

Typical cost for `gpt-3.5-turbo` is low for small projects, but **always set a budget limit**.

---

## Step 3: Create an API key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click **Create new secret key**
3. Name it (e.g. `django-chat-dev`)
4. Copy the key immediately — **you won't see it again**

The key looks like:

```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Step 4: Store the key securely

**Never commit API keys to Git.**

### Option A: Environment variable (recommended)

```bash
# In your shell or .env file (add .env to .gitignore)
export OPENAI_API_KEY="sk-proj-your-key-here"
```

Load in Django settings:

```python
import os
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
```

### Option B: `.env` file with python-dotenv

```bash
# .env (do not commit)
OPENAI_API_KEY=sk-proj-your-key-here
```

```python
# settings.py
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

---

## Step 5: Switch the app back to OpenAI (optional)

1. Uncomment the OpenAI code in `profiles/ai_engine.py`
2. Comment out or remove the Ollama block
3. Set your API key in settings or environment
4. Install/verify: `pip install openai`

Example (modern OpenAI SDK):

```python
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generateChatResponse(prompt):
    messages = [
        {"role": "system", "content": "Your name is cheche. You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response.choices[0].message.content
```

---

## Security checklist

- [ ] API key is in `.env` or environment variables, **not** in source code
- [ ] `.env` is listed in `.gitignore`
- [ ] Usage limit set on OpenAI billing dashboard
- [ ] Key rotated if accidentally exposed

---

## Cost-saving tip

If you don't want to pay for OpenAI, **keep using Ollama** — see [SETUP.md](./SETUP.md). The chat UI and AJAX flow are identical; only the backend LLM client changes.
