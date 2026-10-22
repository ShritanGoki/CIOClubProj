from django.test import TestCase

from accounts.forms import UserProfileForm
from testing_utils import make_category, make_user


class UserProfileFormTests(TestCase):
    def setUp(self):
        self.user = make_user(username='formuser', first_name='Old', last_name='Name')
        self.category = make_category()

    def test_valid_minimal_data(self):
        form = UserProfileForm(data={'bio': 'Hello there'}, instance=self.user.profile, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_initial_first_last_name_populated_from_user(self):
        form = UserProfileForm(instance=self.user.profile, user=self.user)
        self.assertEqual(form.fields['first_name'].initial, 'Old')
        self.assertEqual(form.fields['last_name'].initial, 'Name')

    def test_initial_names_blank_without_user_kwarg(self):
        form = UserProfileForm(instance=self.user.profile)
        self.assertIsNone(form.fields['first_name'].initial)

    def test_save_updates_user_first_and_last_name(self):
        form = UserProfileForm(
            data={'bio': 'Updated bio', 'first_name': 'New', 'last_name': 'Surname'},
            instance=self.user.profile,
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'New')
        self.assertEqual(self.user.last_name, 'Surname')
        self.assertEqual(self.user.profile.bio, 'Updated bio')

    def test_save_with_commit_false_does_not_touch_user(self):
        form = UserProfileForm(
            data={'bio': 'Draft', 'first_name': 'Should Not Save'},
            instance=self.user.profile,
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save(commit=False)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Old')

    def test_interests_accepts_categories(self):
        form = UserProfileForm(
            data={'bio': '', 'interests': [self.category.id]},
            instance=self.user.profile,
            user=self.user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertIn(self.category, self.user.profile.interests.all())
