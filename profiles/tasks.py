from celery import shared_task
from datetime import timedelta

from django.utils import timezone

from common.emails import send_chat_retention_email
from .ai_engine import getChatResponse
from .models import ChatRecord, CustomUser, Profiles


@shared_task
def generate_chat_response_task(prompt, profile_id):
    profile = Profiles.objects.get(pk=profile_id)
    return getChatResponse(prompt, profile)


@shared_task
def delete_old_chat_records():
    cutoff = timezone.now() - timedelta(days=60)
    # For testing purposes, you can set a shorter duration, e.g., 1 day:
    # cutoff = timezone.now() - timedelta(minutes=5)
    deleted_count, _ = ChatRecord.objects.filter(
        date_created__lt=cutoff
    ).delete()

    if deleted_count:
        for staff_user in CustomUser.objects.filter(
            is_staff=True,
            is_active=True,
        ).exclude(email=""):
            send_chat_retention_email(
                recipient=staff_user.email,
                deleted_count=deleted_count,
                cutoff=cutoff,
            )

    return deleted_count

