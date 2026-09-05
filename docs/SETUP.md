# Ollama Setup (Free Local AI)

This project uses **Ollama** instead of OpenAI so you can run AI chat **without paying for API tokens**.

---

## 1. Install Ollama

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### macOS

Download from [https://ollama.com/download](https://ollama.com/download) or:

```bash
brew install ollama
```

### Windows

Download the installer from [https://ollama.com/download](https://ollama.com/download).

---

## 2. Start the Ollama service

```bash
ollama serve
```

By default Ollama listens on **http://127.0.0.1:11434**.

On Linux, Ollama often runs as a systemd service after install — you may not need to run `ollama serve` manually.

Check it is running:

```bash
curl http://127.0.0.1:11434/api/tags
```

You should get JSON listing installed models.

---

## 3. Pull the model used by this project

The app is configured to use **`gemma3:270m`** (small, fast, good for demos):

```bash
ollama pull gemma3:270m
```

Verify:

```bash
ollama list
```

You should see `gemma3:270m` in the list.

---

## 4. Run the Django app

```bash
cd /path/to/django-chat-saas
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and send a test message.

---

## 5. Change the model (optional)

Edit `profiles/ai_engine.py`:

```python
response = ollama.chat(model="your-model-name", messages=messages)
```

Popular free alternatives:

```bash
ollama pull llama3.2
ollama pull mistral
ollama pull phi3
```

Then update the model name in `ai_engine.py`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Connection refused` on port 11434 | Run `ollama serve` or start the Ollama app |
| `model not found` | Run `ollama pull gemma3:270m` |
| Chat shows fallback error message | Check Ollama is running and model is pulled |
| Slow first response | Normal — model loads into memory on first request |
| Out of memory | Use a smaller model like `gemma3:270m` or `phi3:mini` |

---

## Why Ollama vs OpenAI?

| | Ollama | OpenAI |
|---|--------|--------|
| Cost | Free | Pay per token |
| Internet | Works offline | Requires API access |
| Privacy | Data stays local | Sent to OpenAI servers |
| Setup | Install + pull model | API key + billing account |

For learning and development, Ollama is the recommended choice for this project.
