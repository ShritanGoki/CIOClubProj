from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event
from testing_utils import make_category, make_cio, make_user


class HomeViewTests(TestCase):
    def test_renders_with_categories_cios_and_events(self):
        owner = make_user(username='homeowner')
        category = make_category(name='Home Category', slug='home-category')
        cio = make_cio(owner, name='Home Club', slug='home-club', category=category)
        now = timezone.now()
        event = Event.objects.create(
            cio=cio, title='Public Event', start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1), created_by=owner, is_public=True,
        )

        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(category, response.context['categories'])
        self.assertIn(cio, response.context['featured_cios'])
        self.assertIn(event, response.context['upcoming_events'])

    def test_excludes_private_events(self):
        owner = make_user(username='homeowner2')
        cio = make_cio(owner, name='Private Event Club', slug='private-event-club')
        now = timezone.now()
        private_event = Event.objects.create(
            cio=cio, title='Private Event', start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=1), created_by=owner, is_public=False,
        )
        response = self.client.get(reverse('home'))
        self.assertNotIn(private_event, response.context['upcoming_events'])
