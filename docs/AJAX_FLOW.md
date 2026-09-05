# AJAX Chat Flow

How the chat works without reloading the page.

---

## Sequence

```
User clicks "Send"
       │
       ▼
jQuery: e.preventDefault()          ← stops normal form POST / page reload
       │
       ▼
Append user bubble to #list-group   ← instant feedback in the UI
       │
       ▼
$.ajax({ type: "POST", url: "/" })
  data: { prompt, csrfmiddlewaretoken }
       │
       ▼
Django: profiles.views.home (POST)
  prompt = request.POST.get("prompt")
  answer = generateChatResponse(prompt)   ← Ollama call
  return JsonResponse({ "answer": answer })
       │
       ▼
jQuery success callback
  append AI bubble with data.answer
       │
       ▼
User sees reply — page never reloaded
```

---

## Frontend (`templates/profiles/index.html`)

### CSRF token

Django requires a CSRF token on POST requests. The template includes:

```django
{% csrf_token %}
```

JavaScript reads it and sends it with every AJAX request:

```javascript
csrfmiddlewaretoken: $("#chat-form input[name=csrfmiddlewaretoken]").val()
```

Without this, Django returns **403 Forbidden**.

### Why jQuery?

The tutorial uses jQuery for simple `$.ajax()`. jQuery is loaded in `base.html`:

```html
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
```

The chat script runs in `{% block extra_js %}` **after** jQuery loads.

### XSS safety

User and AI text is inserted with `.text()`, not `.html()`, so malicious input cannot run scripts.

Line breaks from Ollama use CSS `white-space: pre-wrap` on `.chat-message-text`.

---

## Backend (`profiles/views.py`)

```python
if request.method == "POST":
    prompt = request.POST.get("prompt", "").strip()
    if not prompt:
        return JsonResponse({"answer": "Please enter a message."}, status=400)
    return JsonResponse({"answer": generateChatResponse(prompt)})
```

- Same URL (`/`) for GET (page) and POST (API)
- Returns JSON, not HTML
- Empty prompts rejected with HTTP 400

---

## Testing AJAX manually

### With curl

```bash
# Get CSRF token from a browser session, or use Django test client
curl -X POST http://127.0.0.1:8000/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "prompt=Hello&csrfmiddlewaretoken=YOUR_TOKEN" \
  -b "csrftoken=YOUR_TOKEN; sessionid=YOUR_SESSION"
```

### With Django shell

```python
python manage.py shell
>>> from profiles.ai_engine import generateChatResponse
>>> generateChatResponse("What is 2+2?")
```

### Browser DevTools

1. Open the chat page
2. Press F12 → **Network** tab
3. Send a message
4. Look for POST to `/` — status should be **200**, response `{"answer": "..."}`

---

## Common AJAX issues (fixed in this project)

| Issue | Cause | Fix |
|-------|-------|-----|
| `$ is not defined` | jQuery not loaded | Added jQuery CDN to `base.html` |
| 403 Forbidden | Missing CSRF token | Send `csrfmiddlewaretoken` in POST data |
| Literal `<br>` in replies | Backend used `<br>`, frontend used `.text()` | Return plain text; use CSS `pre-wrap` |
| No reply, no error | No `error` callback | Added `error` handler with helpful message |
| Button spam | No loading state | Disable button + spinner while waiting |

---

## Field name mapping

| HTML input | JS sends | Django reads |
|------------|----------|--------------|
| `name="message"` (unused by JS) | — | — |
| — | `prompt: question` | `request.POST.get("prompt")` |

The input's `name="message"` is ignored; JavaScript explicitly sends `prompt`, which matches the view.
