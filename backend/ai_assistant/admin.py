from django.contrib import admin
from .models import TranscriptSegment, MeetingSummary


@admin.register(TranscriptSegment)
class TranscriptSegmentAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'speaker', 'start_time_ms', 'end_time_ms')


@admin.register(MeetingSummary)
class MeetingSummaryAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'generated_at')
