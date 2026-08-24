from django.contrib import admin
from .models import Meeting, Participant, ChatMessage, ActionItem


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'room_code', 'host', 'status', 'scheduled_start', 'is_ai_enabled')
    list_filter = ('status', 'is_ai_enabled')
    search_fields = ('title', 'room_code', 'host__username')


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'user', 'role', 'is_speaking', 'joined_at', 'left_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'sender', 'sent_at')


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'description', 'assigned_to', 'is_done', 'created_by_ai')
    list_filter = ('is_done', 'created_by_ai')
