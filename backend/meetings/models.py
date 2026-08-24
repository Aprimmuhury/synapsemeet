"""Core meeting domain models for SynapseMeet."""
import random
import string

from django.conf import settings
from django.db import models


def generate_room_code():
    """Generate a short human-friendly room code, e.g. 'kx7-qpz'."""
    chars = string.ascii_lowercase + string.digits
    part = lambda: ''.join(random.choices(chars, k=3))
    return f"{part()}-{part()}"


class Meeting(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hosted_meetings'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    room_code = models.CharField(max_length=16, unique=True, default=generate_room_code)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    is_ai_enabled = models.BooleanField(
        default=True,
        help_text='Turns on live transcription, summaries, and action-item detection.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_start']

    def __str__(self):
        return f"{self.title} ({self.room_code})"


class Participant(models.Model):
    ROLE_CHOICES = [
        ('host', 'Host'),
        ('co_host', 'Co-host'),
        ('guest', 'Guest'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meeting_participations'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_muted = models.BooleanField(default=False)
    is_camera_on = models.BooleanField(default=True)
    is_speaking = models.BooleanField(
        default=False,
        help_text='Toggled by the client while the participant is actively talking; '
                   'drives the animated synapse pulse ring in the UI.',
    )

    class Meta:
        unique_together = ('meeting', 'user')

    def __str__(self):
        return f"{self.user} in {self.meeting}"


class ChatMessage(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender}: {self.content[:30]}"


class ActionItem(models.Model):
    """A follow-up task, either created manually or detected by the AI
    assistant while parsing the meeting transcript."""

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='action_items')
    description = models.CharField(max_length=300)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_action_items',
    )
    is_done = models.BooleanField(default=False)
    created_by_ai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.description
