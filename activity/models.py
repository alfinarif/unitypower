from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ActivityLog(models.Model):

    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('submit', 'Submitted'),
        ('login', 'Logged In'),
        ('logout', 'Logged Out'),
        ('upload', 'Uploaded'),
        ('download', 'Downloaded'),
        ('send', 'Sent'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs'
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )

    description = models.TextField()

    # Track which object was affected
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    object_repr = models.CharField(
        max_length=255,
        blank=True
    )

    # Store changes, without sensitive information
    changes = models.JSONField(
        default=dict,
        blank=True
    )

    # Request information
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        blank=True
    )

    path = models.CharField(
        max_length=500,
        blank=True
    )

    method = models.CharField(
        max_length=10,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"