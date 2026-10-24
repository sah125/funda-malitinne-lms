"""Staff portal: tender intelligence, eligibility, calendar, report, shared drive, URLs."""
import shutil
import tempfile
from datetime import timedelta
from unittest import mock

from django.core import mail, signing
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core import tender_intel
from core.models import (
    BidProfile, Course, CrawlLog, DocumentCategory, ForumTopic, Lesson, Notification, SharedDocument,
    TenderOpportunity, TenderSource,
)
from core.tests.conftest_base import make_admin, make_instructor, make_student

TODAY = timezone.localdate()


def release(ocid, title, desc, days=20, buyer='eThekwini Municipality', **tender_extra):
    end = (TODAY + timedelta(days=days)).isoformat() + 'T11:00:00Z'
    tender = {'id': ocid.split('-')[-1], 'title': title, 'description': desc, 'status': '',
              'mainProcurementCategory': '', 'additionalProcurementCategories': ['consultingServices'],
              'value': {'amount': 0, 'currency': 'ZAR'},
              'documents': [{'url': 'https://www.etenders.gov.za/doc/1.pdf', 'title': 'Tender document.pdf'}],
              'tenderPeriod': {'startDate': TODAY.isoformat() + 'T00:00:00Z', 'endDate': end},
              'procuringEntity': {'name': buyer}, 'procurementMethodDetails': 'Request for Bid(Open-Tender)'}
    tender.update(tender_extra)
    return {'ocid': ocid, 'date': TODAY.isoformat(), 'buyer': {'name': buyer}, 'tender': tender}


TRAINING = release('ocds-9t57fa-1001', 'ETH 12/26',
                   'Appointment of an accredited training provider for a learnership and skills development programme '
                   'for 40 unemployed youth in Durban. Bidders must be registered on CSD and submit a valid tax compliance PIN '
                   'and B-BBEE certificate. QCTO / Services SETA accreditation required.')
CONSTRUCTION = release('ocds-9t57fa-1002', 'BSM 16/27', 'UPGRADING OF THE KLAPMUTS REFUSE TRANSFER STATION. CIDB 6CE or higher.',
                       buyer='Stellenbosch Municipality')
IRRELEVANT = release('ocds-9t57fa-1003', 'X 1/26', 'Supply of diesel fuel to depots', buyer='Transnet')


class FakeResponse:
    def __init__(self, json_data=None, content=b'', url='https://example.org/', status=200):
        self._json, self.content, self.url, self.status_code = json_data, content, url, status

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f'HTTP {self.status_code}')


class FakeSession:
    def __init__(self, routes):
        self.routes = routes

    def get(self, url, params=None, timeout=None):
        for prefix, resp in self.routes.items():
            if url.startswith(prefix):
                if callable(resp):
                    return resp(params)
                return resp
        raise RuntimeError('no route ' + url)


def vault_doc(user, doc_type, days_valid=200, title=None):
    return SharedDocument.objects.create(
        title=title or doc_type, file=SimpleUploadedFile(f'{doc_type}.pdf', b'%PDF-1.4 test'), file_name=f'{doc_type}.pdf',
        doc_type=doc_type, uploaded_by=user, expiry_date=TODAY + timedelta(days=days_valid) if days_valid is not None else None)


class MediaMixin:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._media)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        shutil.rmtree(cls._media, ignore_errors=True)
        super().tearDownClass()


class ScoringTests(MediaMixin, TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.profile = BidProfile.load()

    def test_seeded_profile_from_company_profile(self):
        self.assertIn('learnership', self.profile.core_keywords)
        self.assertEqual(self.profile.home_province, 'KwaZulu-Natal')
        self.assertTrue(TenderSource.objects.filter(source_type='ocds', is_active=True).exists())
        self.assertTrue(DocumentCategory.objects.filter(slug='company-compliance').exists())

    def test_parse_swaps_bid_number_and_title(self):
        values = tender_intel.parse_ocds_release(TRAINING)
        self.assertEqual(values['reference'], 'ETH 12/26')
        self.assertTrue(values['title'].startswith('Appointment of an accredited training provider'))
        self.assertEqual(values['closing_date'], TODAY + timedelta(days=20))
        self.assertEqual(values['province'], 'KwaZulu-Natal')  # from "eThekwini" buyer

    def test_training_tender_is_strong_and_lists_missing_documents(self):
        opp = TenderOpportunity(**{k: v for k, v in tender_intel.parse_ocds_release(TRAINING).items()})
        result = tender_intel.assess(opp, self.profile, vault={})
        self.assertEqual(result.verdict, 'strong')
        self.assertEqual(result.eligibility, 'missing_docs')
        labels = {c['label']: c['status'] for c in result.checklist}
        self.assertEqual(labels['Registered on the Central Supplier Database (CSD)'], 'missing')
        self.assertIn('Accreditation (QCTO / SETA)', labels)

    def test_documents_on_file_make_it_eligible_and_expiry_matters(self):
        for t in ('csd_report', 'tax_compliance', 'bbbee', 'accreditation_letter'):
            vault_doc(self.admin, t)
        opp = TenderOpportunity(**tender_intel.parse_ocds_release(TRAINING))
        result = tender_intel.assess(opp, self.profile)
        self.assertEqual(result.eligibility, 'eligible')
        self.assertGreaterEqual(result.score, 80)
        SharedDocument.objects.filter(doc_type='tax_compliance').update(expiry_date=TODAY - timedelta(days=1))
        result = tender_intel.assess(opp, self.profile)
        self.assertEqual(result.eligibility, 'missing_docs')
        tax = [c for c in result.checklist if c.get('doc_type') == 'tax_compliance'][0]
        self.assertIn('expired', tax['detail'])

    def test_construction_needing_cidb_is_low_and_not_eligible(self):
        opp = TenderOpportunity(**tender_intel.parse_ocds_release(CONSTRUCTION))
        result = tender_intel.assess(opp, self.profile, vault={})
        self.assertEqual(result.verdict, 'low')
        self.assertEqual(result.eligibility, 'not_eligible')
        self.assertFalse(result.relevant)

    def test_missed_compulsory_briefing_blocks(self):
        opp = TenderOpportunity(**tender_intel.parse_ocds_release(TRAINING))
        opp.briefing_at = timezone.now() - timedelta(days=2)
        opp.briefing_compulsory = True
        result = tender_intel.assess(opp, self.profile, vault={})
        self.assertEqual(result.eligibility, 'not_eligible')
        self.assertEqual(result.verdict, 'low')

    def test_find_closing_date_prefers_closing_phrase(self):
        text = 'Published 1 March 2026. Applications close on 30 November 2099 at 16:00.'
        self.assertEqual(tender_intel.find_closing_date(text).isoformat(), '2099-11-30')
        self.assertIsNone(tender_intel.find_closing_date('No dates here'))


class ScanTests(MediaMixin, TestCase):
    def setUp(self):
        self.admin = make_admin()
        TenderSource.objects.exclude(source_type='ocds').update(is_active=False)
        self.grant_source = TenderSource.objects.create(name='Test SETA', source_type='watch_page',
                                                        base_url='https://seta.example.org/', default_kind='grant')

    def session(self, pages=(TRAINING, CONSTRUCTION, IRRELEVANT)):
        html = (b'<html><body><ul><li><a href="/dg-2026.pdf">Discretionary grant funding window for skills programmes and '
                b'learnerships now open</a> closing date 15 December 2099</li><li><a href="/about">About us</a></li></ul></body></html>')

        def ocds(params):
            return FakeResponse({'releases': list(pages) if params['PageNumber'] == 1 else []})
        return FakeSession({tender_intel.OCDS_URL: ocds, 'https://seta.example.org/': FakeResponse(content=html, url='https://seta.example.org/')})

    def test_scan_keeps_relevant_scores_and_is_idempotent(self):
        result = tender_intel.run_scan(session=self.session())
        self.assertEqual(result.errors, [])
        self.assertEqual(TenderOpportunity.objects.filter(kind='tender').count(), 1)  # construction & fuel skipped
        grant = TenderOpportunity.objects.get(kind='grant')
        self.assertEqual(grant.closing_date.isoformat(), '2099-12-15')
        self.assertEqual(grant.source_url, 'https://seta.example.org/dg-2026.pdf')
        tender = TenderOpportunity.objects.get(kind='tender')
        self.assertEqual(tender.fit_verdict, 'strong')
        tender.status = 'preparing'
        tender.internal_notes = 'Sibu is writing the methodology'
        tender.save()
        again = tender_intel.run_scan(session=self.session())
        self.assertEqual(again.created, 0)
        tender.refresh_from_db()
        self.assertEqual(tender.status, 'preparing')               # people's work is never overwritten
        self.assertEqual(tender.internal_notes, 'Sibu is writing the methodology')
        self.assertEqual(CrawlLog.objects.filter(status='success').count(), 4)

    def test_failing_source_does_not_stop_others(self):
        sess = self.session()
        sess.routes['https://seta.example.org/'] = FakeResponse(status=503)
        result = tender_intel.run_scan(session=sess)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(TenderOpportunity.objects.count(), 1)
        self.grant_source.refresh_from_db()
        self.assertTrue(self.grant_source.last_result.startswith('Failed'))

    def test_closed_new_tenders_are_expired(self):
        old = TenderOpportunity.objects.create(tender_id='x', title='Old training', description='', closing_date=TODAY - timedelta(days=1))
        tender_intel.run_scan(sources=[])
        old.refresh_from_db()
        self.assertEqual(old.status, 'expired')

    def test_staff_daily_notifies_and_emails_digest(self):
        instructor = make_instructor()
        with mock.patch.object(tender_intel, '_session', return_value=self.session()):
            vault_doc(self.admin, 'tax_compliance', days_valid=7, title='Tax PIN')
            call_command('staff_daily')
        self.assertTrue(Notification.objects.filter(user=instructor, title__startswith='Strong fit').exists())
        self.assertTrue(Notification.objects.filter(user=self.admin, title='Renew Tax PIN').exists())
        digest = [m for m in mail.outbox if m.subject.startswith('Staff portal')]
        self.assertEqual(len(digest), 1)
        self.assertEqual(digest[0].to, ['hello@malitinne.co.za'])


@override_settings(CONTACT_EMAIL='hello@malitinne.co.za')
class StaffViewTests(MediaMixin, TestCase):
    def setUp(self):
        cache.clear()
        self.admin = make_admin()
        self.instructor = make_instructor()
        self.student = make_student()
        self.opp = TenderOpportunity.objects.create(**{**tender_intel.parse_ocds_release(TRAINING), 'tender_id': 'ocds-1'})
        tender_intel.apply_assessment(self.opp, tender_intel.assess(self.opp, BidProfile.load()))
        self.opp.save()

    def test_students_cannot_enter(self):
        self.client.force_login(self.student)
        for name in ['staff_portal', 'tender_dashboard', 'shared_drive', 'tender_calendar', 'tender_report', 'discussions_list']:
            self.assertRedirects(self.client.get(reverse(name)), reverse('student_dashboard'), fetch_redirect_response=False)

    def test_all_pages_render_for_staff_with_tenders_present(self):
        # regression: the dashboard used to crash as soon as one tender existed
        self.client.force_login(self.instructor)
        for url in [reverse('staff_portal'), reverse('tender_dashboard'), reverse('tender_dashboard') + '?view=all&sort=closing',
                    reverse('tender_detail', args=[self.opp.pk]), reverse('tender_create'), reverse('tender_calendar'),
                    reverse('tender_report'), reverse('shared_drive'), reverse('discussions_list'), reverse('notifications')]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_dashboard_project_health_uses_course_link(self):
        course = Course.objects.create(title='NVC', description='d', instructor=self.instructor, project=self.opp)
        course.students.add(self.student)
        self.client.force_login(self.admin)
        response = self.client.get(reverse('staff_portal'))
        self.assertContains(response, 'Projects we are delivering')

    def test_old_urls_redirect(self):
        self.client.force_login(self.instructor)
        for old, new in [('/shared-drive/', reverse('shared_drive')), ('/tender-dashboard/', reverse('tender_dashboard')),
                         (f'/tender/{self.opp.pk}/', reverse('tender_detail', args=[self.opp.pk])),
                         ('/discussions/', reverse('discussions_list'))]:
            response = self.client.get(old)
            self.assertEqual(response.status_code, 301, old)
            self.assertEqual(response['Location'], new)
        self.assertTrue(reverse('staff_portal').startswith('/staff-portal/'))
        self.assertEqual(reverse('shared_drive'), '/staff-portal/shared-drive/')
        self.assertEqual(reverse('tender_dashboard'), '/staff-portal/tender-dashboard/')
        self.assertEqual(reverse('discussions_list'), '/staff-portal/discussions/')

    def test_tender_filters_and_detail_tracking(self):
        self.client.force_login(self.instructor)
        self.assertContains(self.client.get(reverse('tender_dashboard') + '?verdict=strong'), 'accredited training provider')
        self.assertNotContains(self.client.get(reverse('tender_dashboard') + '?verdict=low'), 'accredited training provider')
        detail = self.client.get(reverse('tender_detail', args=[self.opp.pk]))
        self.assertContains(detail, 'Can we bid?')
        self.assertContains(detail, 'Central Supplier Database')
        response = self.client.post(reverse('tender_detail', args=[self.opp.pk]), {
            'action': 'track', 'status': 'preparing', 'assigned_to': self.instructor.pk, 'internal_notes': 'go'})
        self.assertRedirects(response, reverse('tender_detail', args=[self.opp.pk]))
        self.opp.refresh_from_db()
        self.assertEqual((self.opp.status, self.opp.assigned_to), ('preparing', self.instructor))

    def test_manual_opportunity_is_scored(self):
        self.client.force_login(self.instructor)
        response = self.client.post(reverse('tender_create'), {
            'kind': 'grant', 'title': 'LGSETA discretionary grant for councillor development learnerships',
            'department': 'LGSETA', 'province': 'KwaZulu-Natal', 'closing_date': (TODAY + timedelta(days=30)).isoformat(),
            'description': 'Funding window for accredited skills programmes'})
        opp = TenderOpportunity.objects.get(kind='grant')
        self.assertRedirects(response, opp.get_absolute_url())
        self.assertIn(opp.fit_verdict, ('strong', 'possible'))
        self.assertEqual(opp.created_by, self.instructor)

    def test_scan_button_admin_only_and_runs_in_background(self):
        self.client.force_login(self.instructor)
        self.assertEqual(self.client.post(reverse('run_tender_crawl')).status_code, 403)
        self.client.force_login(self.admin)
        with mock.patch('core.staff_views.subprocess.Popen') as popen:
            self.client.post(reverse('run_tender_crawl'))
            self.client.post(reverse('run_tender_crawl'))  # second click while running: not started twice
        self.assertEqual(popen.call_count, 1)
        self.assertIn('staff_daily', popen.call_args[0][0])
        self.assertEqual(self.client.get(reverse('run_tender_crawl')).status_code, 405)

    def test_bid_profile_save_rescored(self):
        self.client.force_login(self.admin)
        profile = BidProfile.load()
        data = {f: getattr(profile, f) or '' for f in ['company_name', 'core_keywords', 'related_keywords', 'exclude_keywords',
                                                     'home_province', 'target_provinces', 'cidb_grade', 'accreditations']}
        data.update({'exclude_keywords': 'learnership\nskills development\ntraining', 'min_days_to_prepare': 5, 'bbbee_level': 1})
        self.client.post(reverse('bid_profile'), data)
        self.opp.refresh_from_db()
        self.assertLess(self.opp.fit_score, 70)

    def test_calendar_and_private_ics_feed(self):
        self.client.force_login(self.instructor)
        page = self.client.get(reverse('tender_calendar') + f'?month={self.opp.closing_date:%Y-%m}')
        self.assertContains(page, 'Closes: Appointment of an accredited')
        token = signing.dumps(self.instructor.pk, salt='staff-portal-calendar')
        self.client.logout()
        feed = self.client.get(reverse('calendar_ics') + f'?token={token}')
        self.assertEqual(feed.status_code, 200)
        body = feed.content.decode()
        self.assertIn('BEGIN:VCALENDAR', body)
        self.assertIn('Closes: Appointment of an', body)
        self.assertTrue(all(len(line.encode()) <= 75 for line in body.split('\r\n')))
        self.assertEqual(self.client.get(reverse('calendar_ics') + '?token=forged').status_code, 404)
        student_token = signing.dumps(self.student.pk, salt='staff-portal-calendar')
        self.assertEqual(self.client.get(reverse('calendar_ics') + f'?token={student_token}').status_code, 404)

    def test_report_and_csv(self):
        self.client.force_login(self.instructor)
        self.assertContains(self.client.get(reverse('tender_report') + '?period=month'), 'Opportunities found')
        csv_resp = self.client.get(reverse('tender_report') + '?period=year&format=csv')
        self.assertEqual(csv_resp['Content-Type'], 'text/csv')
        self.assertIn('accredited training provider', csv_resp.content.decode('utf-8-sig'))


class DriveTests(MediaMixin, TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.instructor = make_instructor()

    def upload(self, user, **extra):
        self.client.force_login(user)
        data = {'file': SimpleUploadedFile(extra.pop('name', 'tax.pdf'), b'%PDF-1.4 x', content_type='application/pdf'),
                'doc_type': 'tax_compliance', 'visibility': 'all_staff', 'title': 'SARS tax PIN',
                'expiry_date': (TODAY + timedelta(days=100)).isoformat()}
        data.update(extra)
        return self.client.post(reverse('upload_document'), data)

    def test_vault_upload_versions_and_rescores_tenders(self):
        opp = TenderOpportunity.objects.create(**{**tender_intel.parse_ocds_release(TRAINING), 'tender_id': 'ocds-1'})
        self.upload(self.instructor)
        first = SharedDocument.objects.get()
        self.assertEqual((first.is_current, first.version), (True, '1.0'))
        self.upload(self.instructor, name='tax-2026.pdf')
        second = SharedDocument.objects.latest('pk')
        first.refresh_from_db()
        self.assertFalse(first.is_current)
        self.assertEqual((second.previous_version, second.version), (first, '2.0'))
        opp.refresh_from_db()
        tax = [c for c in opp.eligibility if c.get('doc_type') == 'tax_compliance'][0]
        self.assertEqual(tax['status'], 'ok')
        page = self.client.get(reverse('shared_drive'))
        self.assertContains(page, 'Valid until')
        # deleting the current version brings the previous one back
        self.client.post(reverse('delete_document', args=[second.pk]))
        first.refresh_from_db()
        self.assertTrue(first.is_current)

    def test_bad_file_type_rejected(self):
        response = self.upload(self.instructor, name='evil.exe')
        self.assertRedirects(response, reverse('shared_drive'), fetch_redirect_response=False)
        self.assertFalse(SharedDocument.objects.exists())

    def test_sensitive_documents_are_management_only(self):
        self.upload(self.admin, doc_type='director_id', title='Director IDs', name='ids.pdf')
        doc = SharedDocument.objects.get()
        self.assertTrue(doc.is_sensitive)
        self.assertEqual(doc.visibility, 'management')
        self.client.get(reverse('shared_drive'))  # admin reads their "uploaded" message
        self.client.force_login(self.instructor)
        self.assertNotContains(self.client.get(reverse('shared_drive')), 'Director IDs')
        self.assertEqual(self.client.get(reverse('download_document', args=[doc.pk])).status_code, 403)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('download_document', args=[doc.pk])).status_code, 200)

    def test_inline_view_and_download_logging(self):
        self.upload(self.instructor)
        doc = SharedDocument.objects.get()
        response = self.client.get(reverse('download_document', args=[doc.pk]) + '?inline=1')
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('inline'))
        self.assertEqual(response['X-Frame-Options'], 'SAMEORIGIN')
        attachment = self.client.get(reverse('download_document', args=[doc.pk]))
        self.assertTrue(attachment['Content-Disposition'].startswith('attachment'))
        doc.refresh_from_db()
        self.assertEqual(doc.download_count, 2)
        self.assertEqual(doc.download_logs.count(), 2)

    def test_only_owner_or_admin_can_delete(self):
        self.upload(self.admin, title='Policy', doc_type='policy')
        doc = SharedDocument.objects.get()
        self.client.force_login(self.instructor)
        self.assertEqual(self.client.post(reverse('delete_document', args=[doc.pk])).status_code, 403)
        self.assertTrue(SharedDocument.objects.filter(pk=doc.pk).exists())

    def test_search_finds_by_reference_number(self):
        self.upload(self.instructor, reference_number='2014/123456/07', doc_type='cipc_registration', title='CIPC CoR14.3')
        self.assertContains(self.client.get(reverse('shared_drive') + '?q=123456'), 'CIPC CoR14.3')


class DiscussionTests(TestCase):
    def test_unanswered_tab(self):
        instructor = make_instructor()
        student = make_student()
        course = Course.objects.create(title='C', description='d', instructor=instructor)
        lesson = Lesson.objects.create(course=course, title='L1', content='x', order=1)
        ForumTopic.objects.create(lesson=lesson, author=student, title='How do I upload my POE?', content='?')
        self.client.force_login(instructor)
        response = self.client.get(reverse('discussions_list') + '?tab=unanswered')
        self.assertContains(response, 'How do I upload my POE?')
