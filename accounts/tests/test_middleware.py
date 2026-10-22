from django.test import TestCase
from django.urls import reverse

from testing_utils import make_admin_user, make_user


class AdminLockdownMiddlewareTests(TestCase):
    def test_admin_redirected_away_from_disallowed_path(self):
        admin = make_admin_user(username='admin1')
        self.client.force_login(admin)
        response = self.client.get(reverse('cios:list'))
        self.assertRedirects(response, reverse('accounts:user_admin'))

    def test_admin_can_reach_allowed_admin_panel_path(self):
        admin = make_admin_user(username='admin2')
        self.client.force_login(admin)
        response = self.client.get(reverse('accounts:user_admin'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_reach_django_admin_site(self):
        admin = make_admin_user(username='admin3', is_staff=True, is_superuser=True)
        self.client.force_login(admin)
        response = self.client.get('/admin/')
        self.assertNotEqual(response.status_code, 302)

    def test_non_admin_is_not_redirected(self):
        user = make_user(username='regular1')
        self.client.force_login(user)
        response = self.client.get(reverse('cios:list'))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_not_redirected(self):
        response = self.client.get(reverse('cios:list'))
        self.assertEqual(response.status_code, 200)
