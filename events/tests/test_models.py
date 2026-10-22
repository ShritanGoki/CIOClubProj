from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from events.models import Event, Reminder
from testing_utils import make_cio, make_user


class EventModelTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='eventowner')
        self.cio = make_cio(self.owner, name='Event Club', slug='event-club')

    def make_event(self, **extra):
        now = timezone.now()
        defaults = {
            'cio': self.cio,
            'title': 'General Meeting',
            'start_time': now + timedelta(days=1),
            'end_time': now + timedelta(days=1, hours=1),
            'created_by': self.owner,
        }
        defaults.update(extra)
        return Event.objects.create(**defaults)

    def test_str_includes_cio_and_title(self):
        event = self.make_event()
        self.assertEqual(str(event), 'Event Club: General Meeting')

    def test_is_upcoming_true_for_future_event(self):
        event = self.make_event()
        self.assertTrue(event.is_upcoming)
        self.assertFalse(event.is_past)

    def test_is_past_true_for_past_event(self):
        now = timezone.now()
        event = self.make_event(start_time=now - timedelta(days=2), end_time=now - timedelta(days=1))
        self.assertFalse(event.is_upcoming)
        self.assertTrue(event.is_past)


class ReminderModelTests(TestCase):
    def test_str_and_unique_together(self):
        owner = make_user(username='reminderowner')
        cio = make_cio(owner, name='Reminder Club', slug='reminder-club')
        now = timezone.now()
        event = Event.objects.create(
            cio=cio, title='Workshop', start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1), created_by=owner,
        )
        user = make_user(username='reminderuser')
        reminder = Reminder.objects.create(user=user, event=event)
        self.assertEqual(str(reminder), 'Reminder: reminderuser -> Workshop')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Reminder.objects.create(user=user, event=event)
