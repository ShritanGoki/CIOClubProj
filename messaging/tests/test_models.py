from django.test import TestCase

from messaging.models import Conversation, Message
from testing_utils import make_user


class ConversationModelTests(TestCase):
    def setUp(self):
        self.alice = make_user(username='alice1')
        self.bob = make_user(username='bob1')
        self.conversation = Conversation.objects.create(subject='Hello')
        self.conversation.participants.add(self.alice, self.bob)

    def test_str_lists_participant_usernames(self):
        self.assertIn('alice1', str(self.conversation))
        self.assertIn('bob1', str(self.conversation))

    def test_last_message_returns_most_recent(self):
        self.assertIsNone(self.conversation.last_message)
        first = Message.objects.create(conversation=self.conversation, sender=self.alice, body='Hi')
        second = Message.objects.create(conversation=self.conversation, sender=self.bob, body='Hey')
        self.assertEqual(self.conversation.last_message, second)
        self.assertNotEqual(self.conversation.last_message, first)

    def test_other_participants_excludes_given_user(self):
        others = self.conversation.other_participants(self.alice)
        self.assertEqual(list(others), [self.bob])


class MessageModelTests(TestCase):
    def test_str_truncates_body(self):
        alice = make_user(username='alice2')
        conversation = Conversation.objects.create()
        conversation.participants.add(alice)
        message = Message.objects.create(conversation=conversation, sender=alice, body='x' * 80)
        self.assertTrue(str(message).startswith('alice2: '))
        self.assertLessEqual(len(str(message)), len('alice2: ') + 50)
