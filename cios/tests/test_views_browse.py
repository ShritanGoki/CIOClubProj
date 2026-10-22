from django.test import TestCase
from django.urls import reverse

from cios.models import CIO, ProfileView
from testing_utils import make_category, make_cio, make_user


class CioListViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='listowner')
        self.tech = make_category(name='Technology', slug='technology')
        self.service = make_category(name='Service', slug='service')
        self.alpha = make_cio(
            self.owner, name='Alpha Robotics', slug='alpha-robotics', category=self.tech,
            membership_type='open', time_commitment='low', meeting_day='monday',
        )
        self.beta = make_cio(
            self.owner, name='Beta Volunteers', slug='beta-volunteers', category=self.service,
            membership_type='application', time_commitment='high', meeting_day='friday',
        )

    def test_default_list_returns_all_active_cios(self):
        response = self.client.get(reverse('cios:list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.context['cios']), {self.alpha, self.beta})

    def test_search_by_name(self):
        response = self.client.get(reverse('cios:list'), {'q': 'Robotics'})
        self.assertEqual(list(response.context['cios']), [self.alpha])

    def test_filter_by_category(self):
        response = self.client.get(reverse('cios:list'), {'category': 'service'})
        self.assertEqual(list(response.context['cios']), [self.beta])

    def test_filter_by_membership_type(self):
        response = self.client.get(reverse('cios:list'), {'membership': 'application'})
        self.assertEqual(list(response.context['cios']), [self.beta])

    def test_filter_by_time_commitment(self):
        response = self.client.get(reverse('cios:list'), {'commitment': 'low'})
        self.assertEqual(list(response.context['cios']), [self.alpha])

    def test_filter_by_meeting_day(self):
        response = self.client.get(reverse('cios:list'), {'meeting_day': 'friday'})
        self.assertEqual(list(response.context['cios']), [self.beta])

    def test_inactive_cios_excluded(self):
        self.alpha.is_active = False
        self.alpha.save()
        response = self.client.get(reverse('cios:list'))
        self.assertNotIn(self.alpha, response.context['cios'])

    def test_sort_newest(self):
        response = self.client.get(reverse('cios:list'), {'sort': 'newest'})
        self.assertEqual(list(response.context['cios']), [self.beta, self.alpha])

    def test_sort_popular(self):
        bookmarker = make_user(username='popularitybookmarker')
        self.beta.bookmarks.create(user=bookmarker)
        response = self.client.get(reverse('cios:list'), {'sort': 'popular'})
        self.assertEqual(list(response.context['cios']), [self.beta, self.alpha])

    def test_default_sort_is_by_name(self):
        response = self.client.get(reverse('cios:list'))
        self.assertEqual(list(response.context['cios']), [self.alpha, self.beta])

    def test_bookmarked_ids_empty_for_anonymous(self):
        response = self.client.get(reverse('cios:list'))
        self.assertEqual(response.context['bookmarked_ids'], set())

    def test_bookmarked_ids_populated_for_authenticated_user(self):
        viewer = make_user(username='bookmarkviewer')
        viewer.bookmarks.create(cio=self.alpha)
        self.client.force_login(viewer)
        response = self.client.get(reverse('cios:list'))
        self.assertEqual(response.context['bookmarked_ids'], {self.alpha.id})


class CioDetailViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='detailowner')
        self.cio = make_cio(self.owner, name='Detail Club', slug='detail-club')

    def test_unknown_slug_404s(self):
        response = self.client.get(reverse('cios:detail', args=['does-not-exist']))
        self.assertEqual(response.status_code, 404)

    def test_anonymous_view_does_not_record_profile_view(self):
        self.client.get(reverse('cios:detail', args=[self.cio.slug]))
        self.assertEqual(ProfileView.objects.filter(cio=self.cio).count(), 0)

    def test_authenticated_view_records_profile_view(self):
        viewer = make_user(username='profileviewviewer')
        self.client.force_login(viewer)
        self.client.get(reverse('cios:detail', args=[self.cio.slug]))
        self.assertEqual(ProfileView.objects.filter(cio=self.cio, viewer=viewer).count(), 1)

    def test_context_flags_for_officer(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('cios:detail', args=[self.cio.slug]))
        self.assertTrue(response.context['is_officer'])
        self.assertFalse(response.context['is_bookmarked'])
        self.assertFalse(response.context['has_applied'])

    def test_context_flags_for_bookmarked_non_officer(self):
        viewer = make_user(username='bookmarker2')
        viewer.bookmarks.create(cio=self.cio)
        self.client.force_login(viewer)
        response = self.client.get(reverse('cios:detail', args=[self.cio.slug]))
        self.assertFalse(response.context['is_officer'])
        self.assertTrue(response.context['is_bookmarked'])
