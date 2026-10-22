from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from events.forms import EventForm


class EventFormTests(TestCase):
    def test_valid_data(self):
        now = timezone.now()
        form = EventForm(data={
            'title': 'Info Session',
            'description': 'Come learn more',
            'event_type': 'info',
            'start_time': now + timedelta(days=1),
            'end_time': now + timedelta(days=1, hours=1),
            'location': 'Room 101',
            'is_public': True,
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_title_is_invalid(self):
        now = timezone.now()
        form = EventForm(data={
            'start_time': now,
            'end_time': now + timedelta(hours=1),
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
