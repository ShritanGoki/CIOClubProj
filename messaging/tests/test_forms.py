from django.test import TestCase

from messaging.forms import NewMessageForm, ReplyForm


class NewMessageFormTests(TestCase):
    def test_valid_data(self):
        form = NewMessageForm(data={'recipient': 'someone', 'subject': 'Hi', 'body': 'Hello there'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_subject_is_optional(self):
        form = NewMessageForm(data={'recipient': 'someone', 'body': 'Hello there'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_body_is_invalid(self):
        form = NewMessageForm(data={'recipient': 'someone'})
        self.assertFalse(form.is_valid())


class ReplyFormTests(TestCase):
    def test_valid_data(self):
        form = ReplyForm(data={'body': 'A reply'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_body_is_invalid(self):
        form = ReplyForm(data={})
        self.assertFalse(form.is_valid())
