from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, Reminder
from testing_utils import make_cio, make_user


def event_payload(**extra):
    now = timezone.now()
    data = {
        'title': 'General Meeting',
        'description': 'Agenda TBD',
        'event_type': 'general',
        'start_time': now + timedelta(days=1),
        'end_time': now + timedelta(days=1, hours=1),
        'location': 'Newcomb Hall',
        'is_public': True,
    }
    data.update(extra)
    return data


class EventCreateViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='eventcreateowner')
        self.cio = make_cio(self.owner, name='Create Event Club', slug='create-event-club')

    def test_non_officer_denied(self):
        outsider = make_user(username='eventoutsider1')
        self.client.force_login(outsider)
        response = self.client.post(reverse('events:create', args=[self.cio.slug]), data=event_payload())
        self.assertRedirects(response, reverse('cios:detail', args=[self.cio.slug]))
        self.assertEqual(Event.objects.count(), 0)

    def test_get_renders_blank_form(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('events:create', args=[self.cio.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['form'].instance.pk)

    def test_officer_can_create_event(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('events:create', args=[self.cio.slug]), data=event_payload())
        self.assertRedirects(response, reverse('cios:detail', args=[self.cio.slug]))
        event = Event.objects.get(cio=self.cio)
        self.assertEqual(event.created_by, self.owner)


class EventEditViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='eventeditowner')
        self.cio = make_cio(self.owner, name='Edit Event Club', slug='edit-event-club')
        self.event = Event.objects.create(cio=self.cio, created_by=self.owner, **event_payload())

    def test_non_officer_denied(self):
        outsider = make_user(username='eventoutsider2')
        self.client.force_login(outsider)
        response = self.client.post(
            reverse('events:edit', args=[self.cio.slug, self.event.id]),
            data=event_payload(title='Hacked Title'),
        )
        self.assertRedirects(response, reverse('cios:detail', args=[self.cio.slug]))
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'General Meeting')

    def test_get_renders_prefilled_form(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('events:edit', args=[self.cio.slug, self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance, self.event)

    def test_officer_can_edit_event(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse('events:edit', args=[self.cio.slug, self.event.id]),
            data=event_payload(title='Updated Title'),
        )
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Title')


class EventDeleteViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='eventdeleteowner')
        self.cio = make_cio(self.owner, name='Delete Event Club', slug='delete-event-club')
        self.event = Event.objects.create(cio=self.cio, created_by=self.owner, **event_payload())

    def test_non_officer_denied(self):
        outsider = make_user(username='eventoutsider3')
        self.client.force_login(outsider)
        self.client.post(reverse('events:delete', args=[self.cio.slug, self.event.id]))
        self.assertTrue(Event.objects.filter(id=self.event.id).exists())

    def test_get_does_not_delete(self):
        self.client.force_login(self.owner)
        self.client.get(reverse('events:delete', args=[self.cio.slug, self.event.id]))
        self.assertTrue(Event.objects.filter(id=self.event.id).exists())

    def test_officer_post_deletes_event(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('events:delete', args=[self.cio.slug, self.event.id]))
        self.assertRedirects(response, reverse('cios:manage', args=[self.cio.slug]))
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())


class ToggleReminderViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='reminderviewowner')
        self.cio = make_cio(self.owner, name='Reminder View Club', slug='reminder-view-club')
        self.event = Event.objects.create(cio=self.cio, created_by=self.owner, **event_payload())
        self.user = make_user(username='reminderviewuser')
        self.client.force_login(self.user)

    def test_toggle_sets_then_removes_reminder(self):
        self.client.post(reverse('events:toggle_reminder', args=[self.event.id]))
        self.assertTrue(Reminder.objects.filter(user=self.user, event=self.event).exists())

        self.client.post(reverse('events:toggle_reminder', args=[self.event.id]))
        self.assertFalse(Reminder.objects.filter(user=self.user, event=self.event).exists())


class MyEventsViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='myeventsowner')
        self.bookmarked_cio = make_cio(self.owner, name='Bookmarked Events Club', slug='bookmarked-events-club')
        self.officer_cio = make_cio(self.owner, name='Officer Events Club', slug='officer-events-club')
        self.unrelated_cio = make_cio(self.owner, name='Unrelated Events Club', slug='unrelated-events-club')

        self.viewer = make_user(username='myeventsviewer')
        self.bookmarked_cio.bookmarks.create(user=self.viewer)
        from cios.models import Officer
        Officer.objects.create(cio=self.officer_cio, user=self.viewer, role='officer')

        now = timezone.now()
        self.bookmarked_event = Event.objects.create(
            cio=self.bookmarked_cio, created_by=self.owner, title='Bookmarked Upcoming',
            start_time=now + timedelta(days=1), end_time=now + timedelta(days=1, hours=1),
        )
        self.officer_event = Event.objects.create(
            cio=self.officer_cio, created_by=self.owner, title='Officer Upcoming',
            start_time=now + timedelta(days=2), end_time=now + timedelta(days=2, hours=1),
        )
        self.unrelated_event = Event.objects.create(
            cio=self.unrelated_cio, created_by=self.owner, title='Unrelated Upcoming',
            start_time=now + timedelta(days=1), end_time=now + timedelta(days=1, hours=1),
        )
        self.client.force_login(self.viewer)

    def test_only_includes_bookmarked_and_officer_cio_events(self):
        response = self.client.get(reverse('events:my_events'))
        upcoming = set(response.context['upcoming_events'])
        self.assertIn(self.bookmarked_event, upcoming)
        self.assertIn(self.officer_event, upcoming)
        self.assertNotIn(self.unrelated_event, upcoming)

    def test_reminder_event_ids_reflects_set_reminders(self):
        Reminder.objects.create(user=self.viewer, event=self.bookmarked_event)
        response = self.client.get(reverse('events:my_events'))
        self.assertIn(self.bookmarked_event.id, response.context['reminder_event_ids'])
