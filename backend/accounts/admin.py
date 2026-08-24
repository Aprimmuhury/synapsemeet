from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'role', 'job_title', 'ai_captions_enabled')
    search_fields = ('user__username', 'display_name')
