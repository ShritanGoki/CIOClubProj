from django.test import TestCase
from django.urls import reverse

from cios.models import Bookmark, GaugeInterest
from testing_utils import make_category, make_cio, make_user


class ToggleBookmarkViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='bookmarktoggleowner')
        self.cio = make_cio(self.owner, name='Bookmark Toggle Club', slug='bookmark-toggle-club')
        self.user = make_user(username='bookmarktoggler')
        self.client.force_login(self.user)

    def test_toggle_adds_then_removes_bookmark(self):
        response = self.client.post(reverse('cios:toggle_bookmark', args=[self.cio.slug]))
        self.assertRedirects(response, reverse('cios:list'))
        self.assertTrue(Bookmark.objects.filter(user=self.user, cio=self.cio).exists())

        self.client.post(reverse('cios:toggle_bookmark', args=[self.cio.slug]))
        self.assertFalse(Bookmark.objects.filter(user=self.user, cio=self.cio).exists())


class BookmarksViewTests(TestCase):
    def test_lists_only_current_users_bookmarks(self):
        owner = make_user(username='bookmarklistowner')
        cio = make_cio(owner, name='Bookmark List Club', slug='bookmark-list-club')
        me = make_user(username='bookmarklistme')
        other = make_user(username='bookmarklistother')
        Bookmark.objects.create(user=me, cio=cio)
        Bookmark.objects.create(user=other, cio=cio)
        self.client.force_login(me)
        response = self.client.get(reverse('cios:bookmarks'))
        self.assertEqual(response.context['bookmarks'].count(), 1)


class RecommendationsViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='recowner')
        self.tech = make_category(name='Tech2', slug='tech2')
        self.service = make_category(name='Service2', slug='service2')
        self.tech_cio = make_cio(self.owner, name='Tech Rec Club', slug='tech-rec-club', category=self.tech)
        self.service_cio = make_cio(self.owner, name='Service Rec Club', slug='service-rec-club', category=self.service)

    def test_anonymous_redirected_to_list(self):
        response = self.client.get(reverse('cios:recommendations'))
        self.assertRedirects(response, reverse('cios:list'))

    def test_recommends_by_interest_category(self):
        viewer = make_user(username='recviewer')
        viewer.profile.interests.add(self.tech)
        self.client.force_login(viewer)
        response = self.client.get(reverse('cios:recommendations'))
        self.assertIn(self.tech_cio, response.context['cios'])
        self.assertNotIn(self.service_cio, response.context['cios'])

    def test_falls_back_to_popular_without_interests(self):
        viewer = make_user(username='recviewer2')
        self.client.force_login(viewer)
        response = self.client.get(reverse('cios:recommendations'))
        self.assertEqual(set(response.context['cios']), {self.tech_cio, self.service_cio})


class GaugeInterestViewTests(TestCase):
    def setUp(self):
        self.creator = make_user(username='gaugecreator')
        self.gauge = GaugeInterest.objects.create(
            title='Would a ski club work?', description='Thoughts?', creator=self.creator,
        )

    def test_list_shows_active_gauges(self):
        response = self.client.get(reverse('cios:gauge_list'))
        self.assertIn(self.gauge, response.context['gauges'])

    def test_create_requires_login(self):
        response = self.client.post(reverse('cios:gauge_create'), data={
            'title': 'New idea', 'description': 'Details',
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_get_request_redirects_without_creating(self):
        user = make_user(username='gaugecreator3')
        self.client.force_login(user)
        response = self.client.get(reverse('cios:gauge_create'))
        self.assertRedirects(response, reverse('cios:gauge_list'))
        self.assertEqual(GaugeInterest.objects.filter(creator=user).count(), 0)

    def test_create_gauge(self):
        user = make_user(username='gaugecreator2')
        self.client.force_login(user)
        self.client.post(reverse('cios:gauge_create'), data={
            'title': 'New idea', 'description': 'Details',
        })
        self.assertTrue(GaugeInterest.objects.filter(title='New idea', creator=user).exists())

    def test_vote_adds_then_removes_vote(self):
        voter = make_user(username='gaugevoter')
        self.client.force_login(voter)
        self.client.post(reverse('cios:gauge_vote', args=[self.gauge.id]))
        self.gauge.refresh_from_db()
        self.assertIn(voter, self.gauge.votes.all())

        self.client.post(reverse('cios:gauge_vote', args=[self.gauge.id]))
        self.gauge.refresh_from_db()
        self.assertNotIn(voter, self.gauge.votes.all())


class StartCioGuideViewTests(TestCase):
    def test_renders_successfully(self):
        response = self.client.get(reverse('cios:start_guide'))
        self.assertEqual(response.status_code, 200)
