from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from celery.result import AsyncResult
import markdown

from ..tasks import generate_chat_response_task



#================================================
#============Home View=========================
#================================================
@login_required
def home(request):
    """
    Chat page and AJAX endpoint for chat requests.
    """
    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()

        # Guard against empty submissions before calling the LLM
        if not prompt:
            return JsonResponse({"answer": "Please enter a message."}, status=400)

        profile = request.user.profiles
        task = generate_chat_response_task.delay(prompt, profile.pk)
        return JsonResponse({"task_id": task.id}, status=202)

    # GET: render the chat interface
    context = {}
    return render(request, "profiles/index.html", context)




#=============================
#=============Chat Task Status View=============
#=============================
@login_required
def chat_task_status(request, task_id):
    task = AsyncResult(task_id)

    if task.successful():
        return JsonResponse(
            {
                "status": "SUCCESS",
                "answer": markdown.markdown(
                    task.result,
                    extensions=["fenced_code", "codehilite"],
                ),
            }
        )

    if task.failed():
        return JsonResponse(
            {
                "status": "FAILURE",
                "answer": "The AI could not complete your request.",
            },
            status=500,
        )

    return JsonResponse({"status": task.status})
