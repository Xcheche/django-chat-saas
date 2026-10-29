from celery import shared_task

from .ai_engine import getChatResponse
from .models import Profiles


@shared_task
def generate_chat_response_task(prompt, profile_id):
    profile = Profiles.objects.get(pk=profile_id)
    return getChatResponse(prompt, profile)


#TODO: Fix flower    