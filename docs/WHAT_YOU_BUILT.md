# What You Built

This document explains every major piece of the Cheche chat project and what you implemented.

---

## Overview

You built a **single-page chat application** with Django:

1. User opens the home page and sees a Bootstrap chat card.
2. User types a message and clicks **Send**.
3. **jQuery AJAX** sends the message to Django **without reloading the page**.
4. Django calls **Ollama** (local AI) and returns JSON `{ "answer": "..." }`.
5. JavaScript appends the AI reply to the chat window.

You switched from **OpenAI (paid)** to **Ollama (free/local)** to avoid API costs.

---

## Files you created or modified

### `profiles/ai_engine.py` — AI backend

| What it does |
|--------------|
| Builds a message list: system prompt + user question |
| Sends it to Ollama model `gemma3:270m` |
| Returns the assistant's text (or a fallback error message) |

**Original OpenAI code** is commented out at the top so you can compare or switch back later.

### `profiles/views.py` — HTTP handler

| Method | Behavior |
|--------|----------|
| `GET /` | Renders `templates/profiles/index.html` (chat UI) |
| `POST /` | Reads `prompt` from form data, calls `generateChatResponse()`, returns `JsonResponse` |

Same URL handles both the page and the AJAX API — a common pattern for small apps.

### `templates/profiles/index.html` — Chat UI + AJAX

- Bootstrap card with message list and input form
- Django `{% csrf_token %}` for CSRF protection on POST
- jQuery `$.ajax()` POSTs `prompt` + `csrfmiddlewaretoken` to `/`
- User and AI messages appended as list-group items
- Loading spinner while waiting for Ollama

### `templates/base.html` — Site shell

- Navbar, footer, Bootstrap CSS/JS from CDN
- **jQuery 3.7** loaded before page scripts (required for AJAX)
- `{% block content %}` and `{% block extra_js %}` for child templates

### `profiles/models.py` — User model

- `CustomUser` extends Django's `AbstractUser`
- Registered as `AUTH_USER_MODEL` in settings
- Ready for future SaaS features (accounts, billing, chat history)

### `config/settings.py` — Project configuration

- Django 6, SQLite database, custom user model
- Third-party apps installed for future use (DRF, Celery, debug toolbar)
- Static/media paths configured

---

## What works today

| Feature | Status |
|---------|--------|
| Chat page renders | ✅ |
| AJAX submit (no page reload) | ✅ |
| CSRF protection on POST | ✅ |
| Ollama local AI responses | ✅ (when Ollama is running) |
| Loading spinner | ✅ |
| Error message if Ollama is down | ✅ |
| User accounts / login | ❌ Not yet |
| Chat history saved to database | ❌ Not yet |
| OpenAI integration | ❌ Commented out (use Ollama) |

---

## Architecture diagram

```
Browser (index.html)
    │
    │  jQuery $.ajax POST { prompt, csrfmiddlewaretoken }
    ▼
Django (profiles/views.py → home)
    │
    │  generateChatResponse(prompt)
    ▼
Ollama (localhost:11434)
    │
    │  gemma3:270m model
    ▼
JSON { "answer": "..." }  →  back to browser  →  append to chat
```

---

## Next steps (optional)

- Save messages to a `ChatMessage` model
- Require login before chatting
- Add conversation history so Ollama remembers prior messages
- Deploy with Gunicorn + PostgreSQL
