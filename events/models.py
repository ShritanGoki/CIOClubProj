from django.conf import settings
from django.db import models
from django.utils import timezone


class Event(models.Model):
    EVENT_TYPES = [
        ('general', 'General Meeting'),
        ('social', 'Social Event'),
        ('info', 'Info Session / Interest Meeting'),
        ('service', 'Service Event'),
        ('fundraiser', 'Fundraiser'),
        ('workshop', 'Workshop'),
        ('other', 'Other'),
    ]

    cio = models.ForeignKey('cios.CIO', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='general')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.cio.name}: {self.title}"

    @property
    def is_upcoming(self):
        return self.start_time > timezone.now()

    @property
    def is_past(self):
        return self.end_time < timezone.now()


class Reminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reminders')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"Reminder: {self.user.username} -> {self.event.title}"
