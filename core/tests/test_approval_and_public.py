"""Tests for the approval workflow, enquiries, public catalogue and POPIA rules."""
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Enquiry, EnrollmentRequest, Lesson, Programme

from .conftest_base import make_admin, make_course, make_enrollment, make_instructor, make_student

User = get_user_model()


def make_pending(username='pending'):
    return User.objects.create_user(username=username, email=f'{username}@test.local', password='TestPass123!',
                                    role='student', is_active=True, is_approved=False, first_name='Thandi')


@override_settings(SITE_URL='https://malitinne.co.za', CONTACT_EMAIL='hello@malitinne.co.za',
                   REGISTRATION_NOTIFY_EMAILS=['hello@malitinne.co.za'])
class ApprovalWorkflowTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_registration_emails_learner_and_hello_address(self):
        self.client.post(reverse('register'), {
            'username': 'newbie', 'email': 'newbie@test.local', 'password': 'TestPass123!', 'password2': 'TestPass123!',
            'full_name': 'New Bie', 'popia_consent': '1',
        })
        user = User.objects.get(username='newbie')
        self.assertFalse(user.is_approved)
        self.assertTrue(user.popia_consent)
        recipients = [addr for m in mail.outbox for addr in m.to]
        self.assertIn('newbie@test.local', recipients)
        self.assertIn('hello@malitinne.co.za', recipients)
        self.assertNotIn('sah.sakhile@gmail.com', recipients)

    def test_registration_requires_popia_consent(self):
        self.client.post(reverse('register'), {
            'username': 'noconsent', 'email': 'nc@test.local', 'password': 'TestPass123!', 'password2': 'TestPass123!',
            'full_name': 'No Consent',
        })
        self.assertFalse(User.objects.filter(username='noconsent').exists())

    def test_weak_password_rejected(self):
        self.client.post(reverse('register'), {
            'username': 'weak', 'email': 'weak@test.local', 'password': '12345678', 'password2': '12345678',
            'full_name': 'Weak', 'popia_consent': '1',
        })
        self.assertFalse(User.objects.filter(username='weak').exists())

    def test_existing_session_of_unapproved_learner_is_ended(self):
        learner = make_pending()
        self.client.force_login(learner)
        response = self.client.get(reverse('student_dashboard'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_admin_approval_sends_absolute_login_link(self):
        admin = make_admin()
        learner = make_pending()
        self.client.force_login(admin)
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(reverse('approve_user', args=[learner.id]))
        self.assertRedirects(response, reverse('pending_approvals'))
        learner.refresh_from_db()
        self.assertTrue(learner.is_approved)
        self.assertIsNotNone(learner.approved_at)
        approved = [m for m in mail.outbox if learner.email in m.to]
        self.assertEqual(len(approved), 1)
        self.assertIn('https://malitinne.co.za/login/', approved[0].body)

    def test_approved_learner_can_log_in(self):
        learner = make_pending()
        learner.is_approved = True
        learner.save()
        response = self.client.post(reverse('login'), {'username': learner.username, 'password': 'TestPass123!'})
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_login_with_email_address(self):
        make_student(username='byemail')
        response = self.client.post(reverse('login'), {'username': 'byemail@test.local', 'password': 'TestPass123!'})
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_non_admin_cannot_approve(self):
        instructor = make_instructor()
        learner = make_pending()
        self.client.force_login(instructor)
        self.client.post(reverse('approve_user', args=[learner.id]))
        learner.refresh_from_db()
        self.assertFalse(learner.is_approved)

    def test_decline_deactivates_and_emails(self):
        admin = make_admin()
        learner = make_pending()
        self.client.force_login(admin)
        self.client.post(reverse('decline_user', args=[learner.id]), {'reason': 'Intake full'})
        learner.refresh_from_db()
        self.assertFalse(learner.is_active)
        self.assertTrue(any('Intake full' in m.body for m in mail.outbox))

    def test_brute_force_lockout(self):
        make_student(username='target')
        for _ in range(5):
            self.client.post(reverse('login'), {'username': 'target', 'password': 'wrong-password'})
        response = self.client.post(reverse('login'), {'username': 'target', 'password': 'TestPass123!'})
        self.assertEqual(response.status_code, 429)
        self.assertNotIn('_auth_user_id', self.client.session)


@override_settings(COURSE_ENROLMENT_REQUIRES_APPROVAL=True)
class EnrolmentTests(TestCase):
    def setUp(self):
        self.instructor = make_instructor()
        self.course = make_course(self.instructor, 'Project Manager')
        Lesson.objects.create(course=self.course, title='KM-01 Introduction', content='SECRET LESSON CONTENT', order=1)
        self.student = make_student()

    def test_unenrolled_learner_sees_outline_not_content(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertContains(response, 'KM-01 Introduction')
        self.assertNotContains(response, 'SECRET LESSON CONTENT')
        self.assertContains(response, 'Request to join')

    def test_enrol_creates_request_not_access(self):
        self.client.force_login(self.student)
        self.client.post(reverse('enroll_course', args=[self.course.id]), {'motivation': 'Employer funded'})
        self.assertFalse(self.course.students.filter(id=self.student.id).exists())
        req = EnrollmentRequest.objects.get(student=self.student, course=self.course)
        self.assertEqual(req.status, 'pending')

    def test_get_does_not_enrol(self):
        self.client.force_login(self.student)
        self.client.get(reverse('enroll_course', args=[self.course.id]))
        self.assertFalse(EnrollmentRequest.objects.exists())

    def test_admin_approves_enrolment(self):
        req = EnrollmentRequest.objects.create(student=self.student, course=self.course)
        self.client.force_login(make_admin())
        self.client.post(reverse('decide_enrollment', args=[req.id]), {'decision': 'approve'})
        self.assertTrue(self.course.students.filter(id=self.student.id).exists())

    def test_students_cannot_see_roster(self):
        make_enrollment(self.student, self.course)
        self.client.force_login(self.student)
        response = self.client.get(reverse('course_roster', args=[self.course.id]))
        self.assertRedirects(response, reverse('course_detail', args=[self.course.id]))

    def test_instructor_roster_and_csv(self):
        make_enrollment(self.student, self.course)
        self.client.force_login(self.instructor)
        response = self.client.get(reverse('course_roster', args=[self.course.id]))
        self.assertContains(response, self.student.email)
        csv_resp = self.client.get(reverse('course_roster', args=[self.course.id]) + '?export=csv')
        self.assertEqual(csv_resp['Content-Type'], 'text/csv')
        self.assertIn(self.student.email, csv_resp.content.decode())

    def test_other_instructor_cannot_open_course(self):
        other = make_instructor('other-instructor')
        self.client.force_login(other)
        response = self.client.get(reverse('course_detail', args=[self.course.id]))
        self.assertRedirects(response, reverse('instructor_dashboard'))


@override_settings(CONTACT_EMAIL='hello@malitinne.co.za')
class PublicSiteTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_public_pages_render(self):
        for name in ['company_home', 'programmes', 'accreditation', 'footprint', 'privacy', 'contact', 'about',
                     'services', 'impact', 'clients', 'login', 'register', 'forgot_password', 'news_list', 'opportunities', 'gallery']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_programme_detail_hides_content(self):
        instructor = make_instructor()
        course = make_course(instructor, 'NVC')
        Lesson.objects.create(course=course, title='Opportunity spotting', content='PRIVATE BODY', order=1)
        prog = Programme.objects.filter(is_published=True).first()
        prog.course = course
        prog.save()
        response = self.client.get(reverse('programme_detail', args=[prog.slug]))
        self.assertContains(response, prog.title)
        self.assertContains(response, 'Opportunity spotting')
        self.assertNotContains(response, 'PRIVATE BODY')

    def test_unpublished_programme_404(self):
        prog = Programme.objects.filter(is_published=False).first()
        response = self.client.get(reverse('programme_detail', args=[prog.slug]))
        self.assertEqual(response.status_code, 404)

    def test_contact_goes_to_hello_and_is_saved(self):
        response = self.client.post(reverse('contact_submit'), {
            'first_name': 'Nokwethemba', 'last_name': 'Sibiya', 'email': 'learner@example.com',
            'organisation': 'Department of Justice', 'client_type': 'Learner',
            'message': 'I need funding for my in-service training <script>alert(1)</script>', 'popia_consent': '1',
        })
        self.assertRedirects(response, reverse('contact'), fetch_redirect_response=False)
        enquiry = Enquiry.objects.get()
        self.assertTrue(enquiry.email_sent)
        notification = [m for m in mail.outbox if 'hello@malitinne.co.za' in m.to][0]
        self.assertEqual(notification.reply_to, ['learner@example.com'])
        html = notification.alternatives[0][0]
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertTrue(any('learner@example.com' in m.to for m in mail.outbox))
        self.assertFalse(any('sah.sakhile@gmail.com' in m.to for m in mail.outbox))

    def test_contact_honeypot_drops_spam(self):
        self.client.post(reverse('contact_submit'), {'name': 'Bot', 'email': 'b@x.com', 'message': 'spam',
                                                     'popia_consent': '1', 'website': 'http://spam'})
        self.assertFalse(Enquiry.objects.exists())

    def test_programme_enquiry_links_programme(self):
        prog = Programme.objects.filter(is_published=True).first()
        self.client.post(reverse('contact_submit'), {'name': 'Municipality', 'email': 'skills@muni.gov.za',
                                                     'message': 'We want 40 learners', 'popia_consent': '1',
                                                     'programme': prog.pk, 'enquiry_type': 'partner',
                                                     'return_to': prog.get_absolute_url()})
        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.programme, prog)
        self.assertEqual(enquiry.enquiry_type, 'partner')

    def test_application_success_not_public(self):
        response = self.client.get(reverse('application_success', args=['APP-12345678']))
        self.assertEqual(response.status_code, 404)

    def test_security_headers(self):
        response = self.client.get(reverse('company_home'))
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn('camera=()', response['Permissions-Policy'])


class GalleryTests(TestCase):
    def test_seeded_photos_show_on_gallery_and_home(self):
        from core.models import GalleryPhoto
        self.assertEqual(GalleryPhoto.objects.count(), 15)
        gallery = self.client.get(reverse('gallery'))
        self.assertContains(gallery, 'images/gallery/leather-products-showcase-sm.jpg')
        home = self.client.get(reverse('company_home'))
        self.assertContains(home, 'Our Work in Action')

    def test_unpublished_photo_hidden(self):
        from core.models import GalleryPhoto
        photo = GalleryPhoto.objects.get(static_path='images/gallery/leather-clutch-product.jpg')
        photo.is_published = False
        photo.save()
        self.assertNotContains(self.client.get(reverse('gallery')), 'leather-clutch-product')
