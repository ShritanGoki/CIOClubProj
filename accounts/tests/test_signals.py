from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import UserProfile


class UserProfileSignalTests(TestCase):
    def test_creating_a_user_creates_a_profile(self):
        user = User.objects.create_user(username='newsignal', password='testpass123')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_saving_an_existing_user_does_not_duplicate_profile(self):
        user = User.objects.create_user(username='resave', password='testpass123')
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)
        user.first_name = 'Updated'
        user.save()
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)
