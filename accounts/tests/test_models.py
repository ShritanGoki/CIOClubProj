from django.test import TestCase

from testing_utils import make_user, tiny_image


class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = make_user(username='profileuser', first_name='Jane', last_name='Doe')

    def test_profile_created_automatically(self):
        self.assertTrue(hasattr(self.user, 'profile'))

    def test_default_role_is_prospective(self):
        self.assertEqual(self.user.profile.role, 'prospective')
        self.assertTrue(self.user.profile.is_prospective)
        self.assertFalse(self.user.profile.is_officer)
        self.assertFalse(self.user.profile.is_admin)

    def test_is_officer_property(self):
        self.user.profile.role = 'officer'
        self.user.profile.save()
        self.assertTrue(self.user.profile.is_officer)
        self.assertFalse(self.user.profile.is_prospective)

    def test_is_admin_property(self):
        self.user.profile.role = 'admin'
        self.user.profile.save()
        self.assertTrue(self.user.profile.is_admin)

    def test_str_includes_username_and_role(self):
        self.assertEqual(str(self.user.profile), 'profileuser (Prospective Member)')

    def test_display_name_prefers_full_name(self):
        self.assertEqual(self.user.profile.display_name, 'Jane Doe')

    def test_display_name_falls_back_to_username(self):
        user = make_user(username='nonameuser')
        self.assertEqual(user.profile.display_name, 'nonameuser')

    def test_profile_picture_url_none_when_empty(self):
        self.assertIsNone(self.user.profile.profile_picture_url)

    def test_profile_picture_url_when_set(self):
        self.user.profile.profile_picture = tiny_image()
        self.user.profile.save()
        self.assertIn('.gif', self.user.profile.profile_picture_url)
