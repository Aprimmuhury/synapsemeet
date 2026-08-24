"""Models that store the AI assistant's output for a meeting: transcript
segments, the generated summary, and structured key points."""
from django.conf import settings
from django.db import models

from meetings.models import Meeting


class TranscriptSegment(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='transcript_segments')
    speaker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    text = models.TextField()
    start_time_ms = models.PositiveIntegerField(help_text='Offset from meeting start, in ms')
    end_time_ms = models.PositiveIntegerField(help_text='Offset from meeting start, in ms')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time_ms']

    def __str__(self):
        return f"[{self.meeting.room_code}] {self.text[:40]}"


class MeetingSummary(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE, related_name='summary')
    summary_text = models.TextField(blank=True)
    key_points = models.JSONField(default=list, blank=True)
    decisions = models.JSONField(default=list, blank=True)
    generated_action_items = models.JSONField(default=list, blank=True)
    generated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Summary for {self.meeting.title}"
