from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import UserProfile
from testing_utils import make_admin_user, make_user

MIDDLEWARE_WITHOUT_ADMIN_LOCKDOWN = [
    m for m in settings.MIDDLEWARE if m != 'accounts.middleware.AdminLockdownMiddleware'
]


class ProfileViewTests(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_regular_user_sees_profile_page(self):
        user = make_user(username='viewer1')
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile'], user.profile)

    def test_admin_is_redirected_to_admin_panel(self):
        admin = make_admin_user(username='admin4')
        self.client.force_login(admin)
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, reverse('accounts:user_admin'))

    @override_settings(MIDDLEWARE=MIDDLEWARE_WITHOUT_ADMIN_LOCKDOWN)
    def test_view_itself_redirects_admin_even_without_middleware(self):
        admin = make_admin_user(username='admin4b')
        self.client.force_login(admin)
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, reverse('accounts:user_admin'))


class ProfileEditViewTests(TestCase):
    def setUp(self):
        self.user = make_user(username='editor1')
        self.client.force_login(self.user)

    def test_get_renders_form(self):
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_post_valid_data_updates_profile(self):
        response = self.client.post(reverse('accounts:profile_edit'), data={
            'bio': 'New bio', 'first_name': 'Edited', 'last_name': 'User',
        })
        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'New bio')
        self.assertEqual(self.user.first_name, 'Edited')

    def test_post_invalid_data_rerenders_form_without_saving(self):
        response = self.client.post(reverse('accounts:profile_edit'), data={
            'bio': 'x' * 501,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)


class PublicProfileViewTests(TestCase):
    def setUp(self):
        self.viewer = make_user(username='viewer2')
        self.client.force_login(self.viewer)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('accounts:public_profile', args=['someone']))
        self.assertEqual(response.status_code, 302)

    def test_existing_user_renders(self):
        other = make_user(username='someoneelse')
        response = self.client.get(reverse('accounts:public_profile', args=['someoneelse']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['profile_user'], other)

    def test_nonexistent_user_404s(self):
        response = self.client.get(reverse('accounts:public_profile', args=['nosuchuser']))
        self.assertEqual(response.status_code, 404)


class DeleteAccountViewTests(TestCase):
    def setUp(self):
        self.user = make_user(username='deleteme')
        self.client.force_login(self.user)

    def test_get_renders_confirmation_page(self):
        response = self.client.get(reverse('accounts:delete_account'))
        self.assertEqual(response.status_code, 200)

    def test_post_deletes_account_and_logs_out(self):
        user_id = self.user.id
        response = self.client.post(reverse('accounts:delete_account'))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(User.objects.filter(id=user_id).exists())
        # Confirm we were logged out: a subsequent login-required view redirects to login.
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)


class UserAdminViewTests(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse('accounts:user_admin'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_non_admin_denied(self):
        user = make_user(username='notadmin')
        self.client.force_login(user)
        response = self.client.get(reverse('accounts:user_admin'))
        self.assertRedirects(response, reverse('home'))

    def test_admin_sees_dashboard_excluding_other_admins(self):
        admin = make_admin_user(username='admin5')
        other_admin = make_admin_user(username='admin6')
        regular = make_user(username='regular2')
        self.client.force_login(admin)
        response = self.client.get(reverse('accounts:user_admin'))
        self.assertEqual(response.status_code, 200)
        listed_users = {p.user for p in response.context['users']}
        self.assertIn(regular, listed_users)
        self.assertNotIn(other_admin, listed_users)
        self.assertNotIn(admin, listed_users)


class ChangeUserRoleViewTests(TestCase):
    def setUp(self):
        self.admin = make_admin_user(username='admin7')
        self.target = make_user(username='target1')

    def test_requires_login(self):
        response = self.client.post(reverse('accounts:change_role', args=[self.target.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_non_admin_denied(self):
        user = make_user(username='notadmin2')
        self.client.force_login(user)
        response = self.client.post(
            reverse('accounts:change_role', args=[self.target.id]), data={'role': 'officer'}
        )
        self.assertRedirects(response, reverse('home'))
        self.target.refresh_from_db()
        self.assertEqual(self.target.profile.role, 'prospective')

    def test_admin_can_promote_to_officer(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('accounts:change_role', args=[self.target.id]), data={'role': 'officer'}
        )
        self.assertRedirects(response, reverse('accounts:user_admin'))
        self.target.refresh_from_db()
        self.assertEqual(self.target.profile.role, 'officer')

    def test_admin_cannot_grant_admin_role(self):
        self.client.force_login(self.admin)
        self.client.post(
            reverse('accounts:change_role', args=[self.target.id]), data={'role': 'admin'}
        )
        self.target.refresh_from_db()
        self.assertEqual(self.target.profile.role, 'prospective')

    def test_get_request_does_not_change_role(self):
        self.client.force_login(self.admin)
        self.client.get(reverse('accounts:change_role', args=[self.target.id]))
        self.target.refresh_from_db()
        self.assertEqual(self.target.profile.role, 'prospective')

    def test_nonexistent_user_404s(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('accounts:change_role', args=[999999]), data={'role': 'officer'}
        )
        self.assertEqual(response.status_code, 404)
