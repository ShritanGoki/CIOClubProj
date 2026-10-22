from django.test import TestCase

from cios.forms import (
    AnnouncementForm, ApplicationForm, CIOForm, DocumentForm,
    GaugeInterestForm, OfficerForm, PhotoForm, ReviewForm,
)
from testing_utils import make_category, tiny_file, tiny_image


class CIOFormTests(TestCase):
    def test_valid_minimal_data(self):
        category = make_category()
        form = CIOForm(data={
            'name': 'New Club',
            'description': 'A description',
            'category': category.id,
            'membership_type': 'open',
            'time_commitment': 'medium',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_required_name_is_invalid(self):
        form = CIOForm(data={'description': 'No name given'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class AnnouncementFormTests(TestCase):
    def test_valid_data(self):
        form = AnnouncementForm(data={'title': 'Hi', 'content': 'Body text', 'pinned': False})
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_content_is_invalid(self):
        form = AnnouncementForm(data={'title': 'Hi'})
        self.assertFalse(form.is_valid())


class ReviewFormTests(TestCase):
    def test_valid_rating(self):
        form = ReviewForm(data={'rating': 4, 'content': 'Pretty good'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_rating_out_of_range_is_invalid(self):
        form = ReviewForm(data={'rating': 6, 'content': 'Too high'})
        self.assertFalse(form.is_valid())


class DocumentFormTests(TestCase):
    def test_valid_with_file(self):
        form = DocumentForm(data={'title': 'Bylaws'}, files={'file': tiny_file()})
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_file_is_invalid(self):
        form = DocumentForm(data={'title': 'Bylaws'})
        self.assertFalse(form.is_valid())


class PhotoFormTests(TestCase):
    def test_valid_with_image(self):
        form = PhotoForm(data={'caption': 'Retreat'}, files={'image': tiny_image()})
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_image_is_invalid(self):
        form = PhotoForm(data={'caption': 'Retreat'})
        self.assertFalse(form.is_valid())


class ApplicationFormTests(TestCase):
    def test_valid_statement(self):
        form = ApplicationForm(data={'statement': 'Why I want to join'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_statement_is_invalid(self):
        form = ApplicationForm(data={})
        self.assertFalse(form.is_valid())


class GaugeInterestFormTests(TestCase):
    def test_valid_data(self):
        category = make_category()
        form = GaugeInterestForm(data={
            'title': 'Would a chess club work?',
            'description': 'Gauging interest.',
            'category': category.id,
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_title_is_invalid(self):
        form = GaugeInterestForm(data={'description': 'No title'})
        self.assertFalse(form.is_valid())


class OfficerFormTests(TestCase):
    def test_valid_data(self):
        form = OfficerForm(data={'username': 'someuser', 'role': 'treasurer'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_role_choice(self):
        form = OfficerForm(data={'username': 'someuser', 'role': 'not-a-real-role'})
        self.assertFalse(form.is_valid())
