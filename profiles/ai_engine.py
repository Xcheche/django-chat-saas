"""
AI engine module for the Cheche chat application.

Handles LLM integration. Originally used OpenAI's ChatGPT API (paid, cloud).
Switched to Ollama for free local inference — no API key or billing required.

See docs/SETUP.md for Ollama installation and docs/OPENAI_API_KEY.md if you
want to switch back to OpenAI later.
"""

# ---------------------------------------------------------------------------
# OpenAI integration (commented out — replaced by Ollama to avoid API costs)
# ---------------------------------------------------------------------------
# import openai
#
# openai.api_key = config.DevelopmentConfig.OPENAI_KEY


import ollama  # Local LLM client; talks to Ollama daemon on localhost:11434


# ---------------------------------------------------------------------------
# Original OpenAI implementation (kept for reference / easy rollback)
# ---------------------------------------------------------------------------
# def generateChatResponse(prompt):
#     """Send a prompt to OpenAI GPT-3.5-turbo and return the assistant reply."""
#     messages = []
#     messages.append({"role": "system", "content": "Your name is cheche. You are a helpful assistant."})
#
#     question = {}
#     question['role'] = 'user'
#     question['content'] = prompt
#     messages.append(question)
#
#     response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
#
#     try:
#         answer = response['choices'][0]['message']['content']
#     except (KeyError, IndexError):
#         answer = 'Oops you beat the AI, try a different question, if the problem persists, come back later.'
#
#     return answer


def generateChatResponse(prompt):
    """
    Generate an AI chat response for the given user prompt.

    Builds a message list (system + user), sends it to the local Ollama model,
    and returns plain text. Newlines are preserved for frontend rendering.

    Args:
        prompt (str): The user's question or message.

    Returns:
        str: The assistant's reply, or a friendly fallback if Ollama is unavailable.
    """
    # Build the conversation payload expected by the Ollama chat API
    messages = []
    messages.append({
        "role": "system",
        "content": "Your name is cheche. You are a helpful assistant.",
    })

    question = {}
    question["role"] = "user"
    question["content"] = prompt
    messages.append(question)

    try:
        # Call local Ollama — model must be pulled first: ollama pull gemma3:270m
        response = ollama.chat(model="gemma3:270m", messages=messages)
        # Return plain text; frontend uses CSS white-space: pre-wrap for line breaks
        answer = response["message"]["content"]
    except Exception:
        # Covers: Ollama not running, model missing, network errors, etc.
        answer = (
            "Oops you beat the AI, try a different question, "
            "if the problem persists, come back later."
        )

    return answer
