"""Daily staff-portal job (cron, 06:00):

    python manage.py staff_daily              # scan + notify + document reminders + email digest
    python manage.py staff_daily --scan-only  # used by the "Scan now" button
"""
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from core import tender_intel
from core.emails import _send
from core.models import Notification, SharedDocument, TenderOpportunity, User

REMIND_DAYS = {30, 14, 7, 1, 0}


class Command(BaseCommand):
    help = 'Scan tender & grant sources, then notify staff about good fits and expiring bid documents.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=7, help='How many days of eTenders publications to read')
        parser.add_argument('--scan-only', action='store_true', help='Scan and notify in the portal, but send no email digest')
        parser.add_argument('--release-lock', action='store_true', help=argparse_hidden())

    def handle(self, *args, **opts):
        started = timezone.now()
        try:
            result = tender_intel.run_scan(days_back=opts['days'])
        finally:
            if opts['release_lock']:
                cache.delete('tender-scan-running')
        self.stdout.write(f'Scan: {result.summary()}')
        for err in result.errors:
            self.stderr.write(f'  {err}')

        staff = list(User.objects.filter(role__in=['admin', 'instructor'], is_active=True))
        new_matches = list(TenderOpportunity.objects.filter(created_at__gte=started)
                           .exclude(fit_verdict='low').order_by('-ai_relevance_score')[:25])
        for t in new_matches[:10]:
            for user in staff:
                Notification.objects.create(
                    user=user, title=f'{t.get_fit_verdict_display()}: {t.title[:150]}',
                    message=f'Fit {t.fit_score}/100 · {t.get_eligibility_status_display()}'
                            + (f' · closes {t.closing_date:%d %b %Y}' if t.closing_date else ''),
                    link=t.get_absolute_url())

        today = timezone.localdate()
        expiring = [d for d in SharedDocument.objects.filter(is_current=True, expiry_date__isnull=False,
                                                             expiry_date__lte=today + timedelta(days=30))
                    .exclude(doc_type='other') if d.days_to_expiry in REMIND_DAYS or d.days_to_expiry < 0]
        due_today = [d for d in expiring if d.days_to_expiry in REMIND_DAYS]
        for d in due_today:
            for user in staff:
                if user.role == 'admin' or d.uploaded_by_id == user.pk:
                    Notification.objects.create(
                        user=user, title=f'Renew {d.title}',
                        message=f'Expires {d.expiry_date:%d %b %Y}. Tenders that need it will show "Documents needed".',
                        link=reverse('shared_drive') + f'?type={d.doc_type}')

        if opts['scan_only'] or not (new_matches or due_today):
            return
        sent = _send(f'Staff portal: {len(new_matches)} new opportunities, {len(due_today)} documents to renew',
                     'email/staff_digest.html',
                     {'today': today, 'new_matches': new_matches, 'expiring': expiring, 'errors': result.errors,
                      'portal_url': settings.SITE_URL + reverse('staff_portal')},
                     [settings.CONTACT_EMAIL])
        self.stdout.write('Digest emailed to ' + settings.CONTACT_EMAIL if sent else 'Digest email failed (see log)')


def argparse_hidden():
    import argparse
    return argparse.SUPPRESS
