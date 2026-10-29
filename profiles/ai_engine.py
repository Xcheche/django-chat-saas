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


# import ollama  # Local LLM client; talks to Ollama daemon on localhost:11434
from google import genai

import profiles
from .models import *
import time

# =================================================
# ChatgPT Integration (OpenAI API)
# ================================================
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

# =================================================
# Ollama integration (local LLM inference)
# ================================================
# def generateChatResponse(prompt):
#     """
#     Generate an AI chat response for the given user prompt.

#     Builds a message list (system + user), sends it to the local Ollama model,
#     and returns plain text. Newlines are preserved for frontend rendering.

#     Args:
#         prompt (str): The user's question or message.

#     Returns:
#         str: The assistant's reply, or a friendly fallback if Ollama is unavailable.
#     """
#     # Build the conversation payload expected by the Ollama chat API
#     messages = []
#     messages.append({
#         "role": "system",
#         "content": "Your name is cheche. You are a helpful assistant.",
#     })

#     question = {}
#     question["role"] = "user"
#     question["content"] = prompt
#     messages.append(question)

#     try:
#         # Call local Ollama — model must be pulled first: ollama pull gemma3:270m
#         response = ollama.chat(model="gemma3:270m", messages=messages)
#         print("Ollama response:", response)  # Debugging: log the raw response
#         # Return plain text; frontend uses CSS white-space: pre-wrap for line breaks
#         answer = response["message"]["content"]
#     except Exception:
#         # Covers: Ollama not running, model missing, network errors, etc.
#         answer = (
#             "Oops you beat the AI, try a different question, "
#             "if the problem persists, come back later."
#         )

#     return answer


# =================================================
# Gemini API integration (Google's LLM service)
# ================================================

import os
import logging

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)
AI_ERROR = "AI_ERROR"

#=============================================
# Generate Chat Response
#=============================================
def generateChatResponse(prompt,messages):
    """
    Generate an AI chat response using the Gemini API.

    Args:
        prompt (str): The user's question or message.

    Returns:
        str: The assistant's reply or a friendly fallback.
    """

    try:
        # Read the Gemini API key from the environment
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        # Create the Gemini client
        client = genai.Client(api_key=api_key)

        # Send the conversation history and the current prompt.
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=messages,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Your name is Cheche. " "You are a helpful assistant."
                )
            ),
        )

        # print("Gemini response:", response)

        return response.text or "Sorry, I could not generate a response."

    except Exception:
        logger.exception("Gemini request failed")
        return AI_ERROR

#=============================================
# Get Chat Response
#=============================================
def getChatResponse(prompt, profile):
    """
    Generate a chat response based on the user's prompt and profile.

    Args:
        prompt (str): The user's question or message.
        profile (Profile): The user's profile object.
        """

    ## Step 1 =  collect Conversation
    records = list(
        ChatRecord.objects.filter(
            profiles=profile,
            prompt__isnull=False,
        )
        .order_by("-date_created")[:20]
    )
    records.reverse()



    ## Append and Create Messages [] list
    messages = []


    for record in records:
        role = "user" if record.userGenerated else "model"
        messages.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=record.prompt)],
            )
        )

    ## Append the current question to the messages list  
    messages.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        )
    )


    ## Call the API for a response
    res = generateChatResponse(prompt, messages)


    ## Save the prompt and response to the database.
    if res != AI_ERROR:
        ChatRecord.objects.create(
            profiles=profile,
            prompt=prompt,
            userGenerated=True,
        )
        # Save the AI's response to the database as well
        ChatRecord.objects.create(
            profiles=profile,
            prompt=res,
            userGenerated=False,
        )
    


      


   ## Resturn the response to the user
    if res == AI_ERROR:
        return (
            "The AI service is temporarily unavailable because its request "
            "limit has been reached. Please try again later."
        )

    return res