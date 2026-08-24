"""SynapseMeet user profile model.

We keep Django's built-in auth.User for authentication and extend it with
a one-to-one Profile that stores app-specific fields.
"""
from django.conf import settings
from django.db import models


class Profile(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('org_admin', 'Organization Admin'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    display_name = models.CharField(max_length=120, blank=True)
    avatar = models.ImageField(upload_to='profile_avatars/', blank=True, null=True)
    avatar_color = models.CharField(
        max_length=7,
        default='#7C5CFF',
        help_text='Hex color used for the user\'s generated avatar ring.',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    job_title = models.CharField(max_length=120, blank=True)
    timezone = models.CharField(max_length=64, default='UTC')
    ai_captions_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.user.username
