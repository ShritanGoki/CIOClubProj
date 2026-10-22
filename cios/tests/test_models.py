from django.db import IntegrityError, transaction
from django.test import TestCase

from cios.models import (
    Announcement, Application, Bookmark, CIO, CIODocument, CIOPhoto,
    Category, GaugeInterest, Officer, ProfileView, Review,
)
from testing_utils import make_category, make_cio, make_user


class CategoryModelTests(TestCase):
    def test_str_returns_name(self):
        category = make_category(name='Service')
        self.assertEqual(str(category), 'Service')


class CIOModelTests(TestCase):
    def setUp(self):
        self.officer_user = make_user(username='founder1')
        self.category = make_category()
        self.cio = make_cio(self.officer_user, name='HooHacks', slug='hoohacks', category=self.category)

    def test_str_returns_name(self):
        self.assertEqual(str(self.cio), 'HooHacks')

    def test_officer_count(self):
        self.assertEqual(self.cio.officer_count, 1)
        Officer.objects.create(cio=self.cio, user=make_user(), role='officer')
        self.assertEqual(self.cio.officer_count, 2)

    def test_bookmark_count(self):
        self.assertEqual(self.cio.bookmark_count, 0)
        Bookmark.objects.create(user=make_user(), cio=self.cio)
        self.assertEqual(self.cio.bookmark_count, 1)

    def test_get_officers_returns_officer_queryset(self):
        officers = self.cio.get_officers()
        self.assertEqual(list(officers), [Officer.objects.get(cio=self.cio, user=self.officer_user)])


class OfficerModelTests(TestCase):
    def test_str_includes_role_and_cio_name(self):
        user = make_user(username='prez')
        cio = make_cio(user, name='Book Club', slug='book-club')
        officer = Officer.objects.get(cio=cio, user=user)
        self.assertEqual(str(officer), 'prez - President of Book Club')

    def test_unique_together_cio_user(self):
        user = make_user(username='dupofficer')
        cio = make_cio(user, name='Dup CIO', slug='dup-cio')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Officer.objects.create(cio=cio, user=user, role='treasurer')


class BookmarkModelTests(TestCase):
    def test_str_and_uniqueness(self):
        owner = make_user(username='owner1')
        cio = make_cio(owner, name='Chess Club', slug='chess-club')
        bookmarker = make_user(username='bookmarker1')
        bookmark = Bookmark.objects.create(user=bookmarker, cio=cio)
        self.assertEqual(str(bookmark), 'bookmarker1 -> Chess Club')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Bookmark.objects.create(user=bookmarker, cio=cio)


class ApplicationModelTests(TestCase):
    def test_str_and_default_status(self):
        owner = make_user(username='owner2')
        cio = make_cio(owner, name='Robotics', slug='robotics')
        applicant = make_user(username='applicant1')
        application = Application.objects.create(cio=cio, applicant=applicant, statement='Pick me!')
        self.assertEqual(application.status, 'pending')
        self.assertEqual(str(application), 'applicant1 -> Robotics (pending)')

    def test_unique_together_cio_applicant(self):
        owner = make_user(username='owner3')
        cio = make_cio(owner, name='Dance Team', slug='dance-team')
        applicant = make_user(username='applicant2')
        Application.objects.create(cio=cio, applicant=applicant, statement='First try')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Application.objects.create(cio=cio, applicant=applicant, statement='Second try')


class AnnouncementModelTests(TestCase):
    def test_str_and_pinned_ordering(self):
        owner = make_user(username='owner4')
        cio = make_cio(owner, name='Newsletter CIO', slug='newsletter-cio')
        normal = Announcement.objects.create(cio=cio, title='Normal', content='...', author=owner)
        pinned = Announcement.objects.create(cio=cio, title='Pinned', content='...', author=owner, pinned=True)
        self.assertEqual(str(normal), 'Newsletter CIO: Normal')
        self.assertEqual(list(cio.announcements.all()), [pinned, normal])


class ReviewModelTests(TestCase):
    def test_str_and_unique_together(self):
        owner = make_user(username='owner5')
        cio = make_cio(owner, name='Review CIO', slug='review-cio')
        reviewer = make_user(username='reviewer1')
        review = Review.objects.create(cio=cio, author=reviewer, rating=5, content='Great club')
        self.assertEqual(str(review), 'Review of Review CIO by reviewer1')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(cio=cio, author=reviewer, rating=3, content='Again')


class CIODocumentAndPhotoModelTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='owner6')
        self.cio = make_cio(self.owner, name='Docs CIO', slug='docs-cio')

    def test_document_str(self):
        doc = CIODocument.objects.create(cio=self.cio, title='Bylaws', file='docs/bylaws.pdf', uploaded_by=self.owner)
        self.assertEqual(str(doc), 'Docs CIO: Bylaws')

    def test_photo_str_with_caption(self):
        photo = CIOPhoto.objects.create(cio=self.cio, image='photos/a.jpg', caption='Retreat', uploaded_by=self.owner)
        self.assertEqual(str(photo), 'Docs CIO photo: Retreat')

    def test_photo_str_without_caption(self):
        photo = CIOPhoto.objects.create(cio=self.cio, image='photos/b.jpg', uploaded_by=self.owner)
        self.assertEqual(str(photo), 'Docs CIO photo: No caption')


class ProfileViewModelTests(TestCase):
    def test_profile_view_created(self):
        owner = make_user(username='owner7')
        cio = make_cio(owner, name='Analytics CIO', slug='analytics-cio')
        viewer = make_user(username='analyticsviewer')
        ProfileView.objects.create(cio=cio, viewer=viewer)
        self.assertEqual(cio.profile_views.count(), 1)


class GaugeInterestModelTests(TestCase):
    def test_str_and_vote_count(self):
        creator = make_user(username='creator1')
        gauge = GaugeInterest.objects.create(title='New Film Club', description='Would you join?', creator=creator)
        self.assertEqual(str(gauge), 'New Film Club')
        self.assertEqual(gauge.vote_count, 0)
        voter = make_user(username='voter1')
        gauge.votes.add(voter)
        self.assertEqual(gauge.vote_count, 1)
