"""
Views for the profiles app.

The home view serves two roles:
  - GET  → render the chat page (Bootstrap UI + jQuery AJAX form)
  - POST → accept AJAX chat requests and return JSON { "answer": "..." }
"""

from django.http import JsonResponse
from django.shortcuts import render

from .ai_engine import generateChatResponse


def home(request):
    """
    Chat page and AJAX endpoint.

    POST expects form field ``prompt`` (sent by jQuery in index.html).
    Returns JsonResponse with key ``answer`` on success, or an error message
    when the prompt is empty.
    """
    if request.method == "POST":
        # Read the user's message from the AJAX POST body
        prompt = request.POST.get("prompt", "").strip()

        # Guard against empty submissions before calling the LLM
        if not prompt:
            return JsonResponse({"answer": "Please enter a message."}, status=400)

        response = {}
        response["answer"] = generateChatResponse(prompt)
        return JsonResponse(response)

    # GET: render the chat interface
    context = {}
    return render(request, "profiles/index.html", context)
