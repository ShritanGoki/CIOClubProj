import json

from django.test import TestCase
from django.urls import reverse

from messaging.models import Conversation, Message
from testing_utils import make_user


class InboxViewTests(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse('messaging:inbox'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_only_shows_conversations_the_user_participates_in(self):
        alice = make_user(username='inboxalice')
        bob = make_user(username='inboxbob')
        carol = make_user(username='inboxcarol')

        mine = Conversation.objects.create()
        mine.participants.add(alice, bob)
        Message.objects.create(conversation=mine, sender=bob, body='Hi Alice')

        not_mine = Conversation.objects.create()
        not_mine.participants.add(bob, carol)

        self.client.force_login(alice)
        response = self.client.get(reverse('messaging:inbox'))
        conversations = list(response.context['conversations'])
        self.assertIn(mine, conversations)
        self.assertNotIn(not_mine, conversations)

    def test_unread_count_excludes_own_messages(self):
        alice = make_user(username='inboxalice2')
        bob = make_user(username='inboxbob2')
        conversation = Conversation.objects.create()
        conversation.participants.add(alice, bob)
        Message.objects.create(conversation=conversation, sender=alice, body='From me')
        Message.objects.create(conversation=conversation, sender=bob, body='From bob')

        self.client.force_login(alice)
        response = self.client.get(reverse('messaging:inbox'))
        conv = response.context['conversations'][0]
        self.assertEqual(conv.unread_count, 1)


class ConversationDetailViewTests(TestCase):
    def setUp(self):
        self.alice = make_user(username='convalice')
        self.bob = make_user(username='convbob')
        self.carol = make_user(username='convcarol')
        self.conversation = Conversation.objects.create()
        self.conversation.participants.add(self.alice, self.bob)
        self.message = Message.objects.create(conversation=self.conversation, sender=self.bob, body='Hi Alice')

    def test_non_participant_gets_404(self):
        self.client.force_login(self.carol)
        response = self.client.get(reverse('messaging:conversation', args=[self.conversation.pk]))
        self.assertEqual(response.status_code, 404)

    def test_participant_marks_unread_messages_as_read(self):
        self.client.force_login(self.alice)
        self.client.get(reverse('messaging:conversation', args=[self.conversation.pk]))
        self.message.refresh_from_db()
        self.assertIn(self.alice, self.message.read_by.all())

    def test_post_adds_reply(self):
        self.client.force_login(self.alice)
        response = self.client.post(
            reverse('messaging:conversation', args=[self.conversation.pk]), data={'body': 'Hi Bob!'}
        )
        self.assertRedirects(response, reverse('messaging:conversation', args=[self.conversation.pk]))
        self.assertTrue(self.conversation.messages.filter(sender=self.alice, body='Hi Bob!').exists())


class NewConversationViewTests(TestCase):
    def setUp(self):
        self.alice = make_user(username='newconvalice')
        self.bob = make_user(username='newconvbob')
        self.client.force_login(self.alice)

    def test_get_prefills_recipient_from_query_param(self):
        response = self.client.get(reverse('messaging:new') + '?to=newconvbob')
        self.assertEqual(response.context['form'].initial['recipient'], 'newconvbob')

    def test_post_creates_conversation_and_message(self):
        response = self.client.post(reverse('messaging:new'), data={
            'recipient': 'newconvbob', 'subject': 'Hi', 'body': 'Hello!',
        })
        conversation = Conversation.objects.get(participants=self.alice)
        self.assertRedirects(response, reverse('messaging:conversation', args=[conversation.pk]))
        self.assertIn(self.bob, conversation.participants.all())

    def test_post_reuses_existing_conversation(self):
        existing = Conversation.objects.create()
        existing.participants.add(self.alice, self.bob)
        self.client.post(reverse('messaging:new'), data={
            'recipient': 'newconvbob', 'body': 'Second message',
        })
        self.assertEqual(Conversation.objects.filter(participants=self.alice).count(), 1)
        self.assertEqual(existing.messages.count(), 1)

    def test_cannot_message_self(self):
        response = self.client.post(reverse('messaging:new'), data={
            'recipient': 'newconvalice', 'body': 'Talking to myself',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Conversation.objects.count(), 0)

    def test_unknown_recipient_shows_error(self):
        response = self.client.post(reverse('messaging:new'), data={
            'recipient': 'ghostuser', 'body': 'Hello?',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Conversation.objects.count(), 0)


class UnreadCountViewTests(TestCase):
    def test_requires_login(self):
        response = self.client.get(reverse('messaging:unread_count'))
        self.assertEqual(response.status_code, 302)

    def test_returns_correct_count_as_json(self):
        alice = make_user(username='unreadalice')
        bob = make_user(username='unreadbob')
        conversation = Conversation.objects.create()
        conversation.participants.add(alice, bob)
        Message.objects.create(conversation=conversation, sender=bob, body='Unread 1')
        Message.objects.create(conversation=conversation, sender=bob, body='Unread 2')

        self.client.force_login(alice)
        response = self.client.get(reverse('messaging:unread_count'))
        self.assertEqual(json.loads(response.content), {'count': 2})
