# Cheche Django Chat SaaS — Documentation

Educational Django project that builds a chat interface using **AJAX** (no page reload) and a local **Ollama** LLM instead of paid OpenAI API calls.

## Quick start

```bash
# 1. Install Ollama and pull the model (see SETUP.md)
ollama pull gemma3:270m
ollama serve

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run migrations and start Django
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and send a message.

## Documentation index

| Document | Description |
|----------|-------------|
| [WHAT_YOU_BUILT.md](./WHAT_YOU_BUILT.md) | What this project does and how each piece fits together |
| [SETUP.md](./SETUP.md) | Ollama installation and configuration (free, local AI) |
| [OPENAI_API_KEY.md](./OPENAI_API_KEY.md) | How to get an OpenAI API key if you switch back from Ollama |
| [AJAX_FLOW.md](./AJAX_FLOW.md) | How the frontend AJAX chat works end-to-end |

## Project structure

```
django-chat-saas/
├── config/              # Django project settings and root URLs
├── profiles/            # Main app: views, AI engine, user model
│   ├── ai_engine.py     # Ollama LLM integration
│   ├── views.py         # Chat page + AJAX JSON endpoint
│   └── models.py        # CustomUser (extends AbstractUser)
├── templates/
│   ├── base.html        # Layout, navbar, jQuery + Bootstrap CDN
│   └── profiles/
│       └── index.html   # Chat UI + jQuery AJAX script
├── static/              # Local static files (optional; CDN used for now)
└── docs/                # This documentation
```

## Why Ollama instead of OpenAI?

- **Free** — runs on your machine, no per-token billing
- **Private** — messages never leave your computer
- **Good for learning** — same chat UI pattern works with either backend

The original tutorial used OpenAI; that code is preserved (commented out) in `profiles/ai_engine.py`.
