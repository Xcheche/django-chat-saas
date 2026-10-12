from celery import shared_task

from .ai_engine import generateChatResponse


@shared_task
def generate_chat_response_task(prompt):
    return generateChatResponse(prompt)