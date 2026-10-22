import io

from django.core.management import call_command
from django.test import TestCase

from cios.models import CIO, Category


class SeedDataCommandTests(TestCase):
    def test_runs_without_error_and_creates_data(self):
        call_command('seed_data', stdout=io.StringIO())
        self.assertTrue(Category.objects.exists())
        self.assertTrue(CIO.objects.exists())

    def test_running_twice_does_not_duplicate_categories(self):
        call_command('seed_data', stdout=io.StringIO())
        first_count = Category.objects.count()
        call_command('seed_data', stdout=io.StringIO())
        self.assertEqual(Category.objects.count(), first_count)
