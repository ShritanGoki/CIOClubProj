from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cios.models import (
    Announcement, Application, CIO, CIODocument, CIOPhoto, Officer, Review,
)
from testing_utils import make_category, make_cio, make_user, tiny_file, tiny_image


class CioCreateViewTests(TestCase):
    def setUp(self):
        self.user = make_user(username='creator2')
        self.category = make_category()
        self.client.force_login(self.user)

    def test_anonymous_redirected_to_login(self):
        self.client.logout()
        response = self.client.get(reverse('cios:create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_get_renders_form(self):
        response = self.client.get(reverse('cios:create'))
        self.assertEqual(response.status_code, 200)

    def test_post_creates_cio_officer_and_promotes_role(self):
        response = self.client.post(reverse('cios:create'), data={
            'name': 'Brand New Club',
            'description': 'Description here',
            'category': self.category.id,
            'membership_type': 'open',
            'time_commitment': 'medium',
        })
        cio = CIO.objects.get(name='Brand New Club')
        self.assertRedirects(response, reverse('cios:detail', args=[cio.slug]))
        officer = Officer.objects.get(cio=cio, user=self.user)
        self.assertTrue(officer.is_primary)
        self.assertEqual(officer.role, 'president')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.role, 'officer')

    def test_duplicate_name_gets_unique_slug(self):
        make_cio(self.user, name='Collision Club', slug='collision-club')
        second_user = make_user(username='creator3')
        self.client.force_login(second_user)
        self.client.post(reverse('cios:create'), data={
            'name': 'Collision Club',
            'description': 'Another one',
            'category': self.category.id,
            'membership_type': 'open',
            'time_commitment': 'medium',
        })
        self.assertTrue(CIO.objects.filter(slug='collision-club-1').exists())


class CioEditViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='editowner')
        self.category = make_category(name='Edit Category', slug='edit-category')
        self.cio = make_cio(self.owner, name='Editable Club', slug='editable-club', category=self.category)

    def test_non_officer_is_denied(self):
        outsider = make_user(username='outsider1')
        self.client.force_login(outsider)
        response = self.client.get(reverse('cios:edit', args=[self.cio.slug]))
        self.assertRedirects(response, reverse('cios:detail', args=[self.cio.slug]))

    def test_officer_get_renders_prefilled_form(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('cios:edit', args=[self.cio.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance, self.cio)

    def test_officer_can_edit(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('cios:edit', args=[self.cio.slug]), data={
            'name': 'Renamed Club',
            'description': self.cio.description,
            'category': self.category.id,
            'membership_type': 'open',
            'time_commitment': 'medium',
        })
        self.cio.refresh_from_db()
        self.assertEqual(self.cio.name, 'Renamed Club')
        self.assertRedirects(response, reverse('cios:detail', args=[self.cio.slug]))


class ToggleApplicationsViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='toggleowner')
        self.cio = make_cio(self.owner, name='Toggle Club', slug='toggle-club')

    def test_non_officer_denied(self):
        outsider = make_user(username='outsider2')
        self.client.force_login(outsider)
        self.client.post(reverse('cios:toggle_applications', args=[self.cio.slug]))
        self.cio.refresh_from_db()
        self.assertFalse(self.cio.applications_open)

    def test_officer_can_toggle_open_and_closed(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('cios:toggle_applications', args=[self.cio.slug]))
        self.cio.refresh_from_db()
        self.assertTrue(self.cio.applications_open)
        self.client.post(reverse('cios:toggle_applications', args=[self.cio.slug]))
        self.cio.refresh_from_db()
        self.assertFalse(self.cio.applications_open)


class ApplyToCioViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='applyowner')
        self.cio = make_cio(self.owner, name='Apply Club', slug='apply-club', applications_open=True)
        self.applicant = make_user(username='applicant3')
        self.client.force_login(self.applicant)

    def test_applications_closed_redirects_with_error(self):
        self.cio.applications_open = False
        self.cio.save()
        response = self.client.post(reverse('cios:apply', args=[self.cio.slug]), data={'statement': 'Pick me'})
        self.assertRedirects(response, reverse('cios:detail', args=[self.cio.slug]))
        self.assertEqual(Application.objects.count(), 0)

    def test_post_creates_application(self):
        response = self.client.post(reverse('cios:apply', args=[self.cio.slug]), data={'statement': 'Pick me'})
        self.assertRedirects(response, reverse('cios:detail', args=[self.cio.slug]))
        self.assertTrue(Application.objects.filter(cio=self.cio, applicant=self.applicant).exists())

    def test_duplicate_application_blocked(self):
        Application.objects.create(cio=self.cio, applicant=self.applicant, statement='First')
        self.client.post(reverse('cios:apply', args=[self.cio.slug]), data={'statement': 'Second'})
        self.assertEqual(Application.objects.filter(cio=self.cio, applicant=self.applicant).count(), 1)

    def test_get_request_redirects_without_creating_application(self):
        response = self.client.get(reverse('cios:apply', args=[self.cio.slug]))
        self.assertRedirects(response, reverse('cios:detail', args=[self.cio.slug]))
        self.assertEqual(Application.objects.count(), 0)


class ManageCioViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='manageowner')
        self.cio = make_cio(self.owner, name='Manage Club', slug='manage-club')

    def test_non_officer_denied(self):
        outsider = make_user(username='outsider3')
        self.client.force_login(outsider)
        response = self.client.get(reverse('cios:manage', args=[self.cio.slug]))
        self.assertRedirects(response, reverse('cios:detail', args=[self.cio.slug]))

    def test_officer_sees_analytics(self):
        viewer = make_user(username='analyticsviewer2')
        self.cio.profile_views.create(viewer=viewer)
        self.client.force_login(self.owner)
        response = self.client.get(reverse('cios:manage', args=[self.cio.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_views'], 1)
        self.assertEqual(response.context['views_this_week'], 1)


class ReviewApplicationViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='reviewowner')
        self.cio = make_cio(self.owner, name='Review App Club', slug='review-app-club')
        self.applicant = make_user(username='applicant4')
        self.application = Application.objects.create(cio=self.cio, applicant=self.applicant, statement='Hi')

    def test_non_officer_denied(self):
        outsider = make_user(username='outsider4')
        self.client.force_login(outsider)
        self.client.post(
            reverse('cios:review_application', args=[self.cio.slug, self.application.id]),
            data={'action': 'accepted'},
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')

    def test_officer_can_accept(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse('cios:review_application', args=[self.cio.slug, self.application.id]),
            data={'action': 'accepted'},
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'accepted')
        self.assertEqual(self.application.reviewed_by, self.owner)
        self.assertIsNotNone(self.application.reviewed_at)

    def test_officer_can_deny(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse('cios:review_application', args=[self.cio.slug, self.application.id]),
            data={'action': 'denied'},
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'denied')

    def test_invalid_action_is_noop(self):
        self.client.force_login(self.owner)
        self.client.post(
            reverse('cios:review_application', args=[self.cio.slug, self.application.id]),
            data={'action': 'bogus'},
        )
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'pending')


class AnnouncementViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='annowner')
        self.cio = make_cio(self.owner, name='Announce Club', slug='announce-club')

    def test_non_officer_cannot_post(self):
        outsider = make_user(username='outsider5')
        self.client.force_login(outsider)
        self.client.post(reverse('cios:add_announcement', args=[self.cio.slug]), data={
            'title': 'Hi', 'content': 'Body',
        })
        self.assertEqual(Announcement.objects.count(), 0)

    def test_officer_can_post_and_delete(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('cios:add_announcement', args=[self.cio.slug]), data={
            'title': 'Hi', 'content': 'Body',
        })
        announcement = Announcement.objects.get(cio=self.cio)
        self.assertEqual(announcement.author, self.owner)

        self.client.post(reverse('cios:delete_announcement', args=[self.cio.slug, announcement.id]))
        self.assertFalse(Announcement.objects.filter(id=announcement.id).exists())

    def test_non_officer_cannot_delete(self):
        announcement = Announcement.objects.create(cio=self.cio, title='Hi', content='Body', author=self.owner)
        outsider = make_user(username='outsider5b')
        self.client.force_login(outsider)
        self.client.post(reverse('cios:delete_announcement', args=[self.cio.slug, announcement.id]))
        self.assertTrue(Announcement.objects.filter(id=announcement.id).exists())


class AddReviewViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='addreviewowner')
        self.cio = make_cio(self.owner, name='AddReview Club', slug='addreview-club')
        self.reviewer = make_user(username='reviewer2')
        self.client.force_login(self.reviewer)

    def test_creates_review(self):
        self.client.post(reverse('cios:add_review', args=[self.cio.slug]), data={
            'rating': 5, 'content': 'Loved it',
        })
        self.assertTrue(Review.objects.filter(cio=self.cio, author=self.reviewer).exists())

    def test_duplicate_review_blocked(self):
        Review.objects.create(cio=self.cio, author=self.reviewer, rating=4, content='First')
        self.client.post(reverse('cios:add_review', args=[self.cio.slug]), data={
            'rating': 1, 'content': 'Second',
        })
        self.assertEqual(Review.objects.filter(cio=self.cio, author=self.reviewer).count(), 1)


class DocumentAndPhotoViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='docphotoowner')
        self.cio = make_cio(self.owner, name='DocPhoto Club', slug='docphoto-club')

    def test_non_officer_cannot_add_document(self):
        outsider = make_user(username='outsider6')
        self.client.force_login(outsider)
        self.client.post(reverse('cios:add_document', args=[self.cio.slug]), data={
            'title': 'Bylaws', 'file': tiny_file(),
        })
        self.assertEqual(CIODocument.objects.count(), 0)

    def test_officer_can_add_and_delete_document(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('cios:add_document', args=[self.cio.slug]), data={
            'title': 'Bylaws', 'file': tiny_file(),
        })
        doc = CIODocument.objects.get(cio=self.cio)
        self.client.post(reverse('cios:delete_document', args=[self.cio.slug, doc.id]))
        self.assertFalse(CIODocument.objects.filter(id=doc.id).exists())

    def test_non_officer_cannot_delete_document(self):
        doc = CIODocument.objects.create(cio=self.cio, title='Bylaws', file='docs/x.txt', uploaded_by=self.owner)
        outsider = make_user(username='outsider6b')
        self.client.force_login(outsider)
        self.client.post(reverse('cios:delete_document', args=[self.cio.slug, doc.id]))
        self.assertTrue(CIODocument.objects.filter(id=doc.id).exists())

    def test_non_officer_cannot_add_photo(self):
        outsider = make_user(username='outsider6c')
        self.client.force_login(outsider)
        self.client.post(reverse('cios:add_photo', args=[self.cio.slug]), data={
            'caption': 'Retreat', 'image': tiny_image(),
        })
        self.assertEqual(CIOPhoto.objects.count(), 0)

    def test_officer_can_add_and_delete_photo(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('cios:add_photo', args=[self.cio.slug]), data={
            'caption': 'Retreat', 'image': tiny_image(),
        })
        photo = CIOPhoto.objects.get(cio=self.cio)
        self.client.post(reverse('cios:delete_photo', args=[self.cio.slug, photo.id]))
        self.assertFalse(CIOPhoto.objects.filter(id=photo.id).exists())

    def test_non_officer_cannot_delete_photo(self):
        photo = CIOPhoto.objects.create(cio=self.cio, image='photos/x.jpg', uploaded_by=self.owner)
        outsider = make_user(username='outsider6d')
        self.client.force_login(outsider)
        self.client.post(reverse('cios:delete_photo', args=[self.cio.slug, photo.id]))
        self.assertTrue(CIOPhoto.objects.filter(id=photo.id).exists())


class OfficerManagementViewTests(TestCase):
    def setUp(self):
        self.owner = make_user(username='officermgmtowner')
        self.cio = make_cio(self.owner, name='OfficerMgmt Club', slug='officermgmt-club')
        self.client.force_login(self.owner)

    def test_non_officer_cannot_add_officer(self):
        outsider = make_user(username='officermgmtoutsider1')
        recruit = make_user(username='recruit1b')
        self.client.force_login(outsider)
        self.client.post(reverse('cios:add_officer', args=[self.cio.slug]), data={
            'username': 'recruit1b', 'role': 'treasurer',
        })
        self.assertFalse(Officer.objects.filter(cio=self.cio, user=recruit).exists())

    def test_add_officer_promotes_prospective_user(self):
        recruit = make_user(username='recruit1')
        self.client.post(reverse('cios:add_officer', args=[self.cio.slug]), data={
            'username': 'recruit1', 'role': 'treasurer',
        })
        officer = Officer.objects.get(cio=self.cio, user=recruit)
        self.assertEqual(officer.role, 'treasurer')
        recruit.profile.refresh_from_db()
        self.assertEqual(recruit.profile.role, 'officer')

    def test_add_officer_updates_existing_officer_role(self):
        recruit = make_user(username='recruit2')
        Officer.objects.create(cio=self.cio, user=recruit, role='officer')
        self.client.post(reverse('cios:add_officer', args=[self.cio.slug]), data={
            'username': 'recruit2', 'role': 'secretary',
        })
        officer = Officer.objects.get(cio=self.cio, user=recruit)
        self.assertEqual(officer.role, 'secretary')

    def test_add_officer_unknown_username_errors_gracefully(self):
        response = self.client.post(reverse('cios:add_officer', args=[self.cio.slug]), data={
            'username': 'ghost', 'role': 'treasurer',
        })
        self.assertRedirects(response, reverse('cios:manage', args=[self.cio.slug]))
        self.assertEqual(Officer.objects.filter(cio=self.cio).count(), 1)

    def test_non_officer_cannot_remove_officer(self):
        recruit = make_user(username='recruit3b')
        officer = Officer.objects.create(cio=self.cio, user=recruit, role='officer')
        outsider = make_user(username='officermgmtoutsider2')
        self.client.force_login(outsider)
        self.client.post(reverse('cios:remove_officer', args=[self.cio.slug, officer.id]))
        self.assertTrue(Officer.objects.filter(id=officer.id).exists())

    def test_remove_officer_protects_primary(self):
        primary = Officer.objects.get(cio=self.cio, user=self.owner)
        self.client.post(reverse('cios:remove_officer', args=[self.cio.slug, primary.id]))
        self.assertTrue(Officer.objects.filter(id=primary.id).exists())

    def test_remove_officer_allows_non_primary(self):
        recruit = make_user(username='recruit3')
        officer = Officer.objects.create(cio=self.cio, user=recruit, role='officer')
        self.client.post(reverse('cios:remove_officer', args=[self.cio.slug, officer.id]))
        self.assertFalse(Officer.objects.filter(id=officer.id).exists())
