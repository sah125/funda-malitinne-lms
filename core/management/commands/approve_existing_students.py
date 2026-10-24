"""One-off helper after switching on approval-gated login.

Learners who registered before approval was enforced are still marked
"not approved", so they can no longer sign in. Use this to approve the ones
you know are genuine.

  python manage.py approve_existing_students --list
  python manage.py approve_existing_students --enrolled-only      # approve anyone already in a course
  python manage.py approve_existing_students --usernames thandi sipho
  add --notify to also email each learner their login link
"""
from django.core.management.base import BaseCommand

from core.models import User


class Command(BaseCommand):
    help = 'List or approve students who are waiting for approval.'

    def add_arguments(self, parser):
        parser.add_argument('--list', action='store_true', help='Only list waiting students')
        parser.add_argument('--enrolled-only', action='store_true', help='Approve waiting students already enrolled in a course')
        parser.add_argument('--usernames', nargs='*', default=[], help='Approve these usernames')
        parser.add_argument('--notify', action='store_true', help='Email each approved learner their login link')

    def handle(self, *args, **opts):
        waiting = User.objects.filter(role='student', is_approved=False, is_active=True).order_by('date_joined')
        if opts['list'] or not (opts['enrolled_only'] or opts['usernames']):
            for u in waiting:
                courses = u.enrolled_courses.count()
                self.stdout.write(f"{u.username:<25} {u.email:<35} joined {u.date_joined:%Y-%m-%d}  courses={courses}")
            self.stdout.write(self.style.WARNING(f"{waiting.count()} student(s) waiting. Use --enrolled-only or --usernames to approve."))
            return

        targets = waiting
        if opts['usernames']:
            targets = targets.filter(username__in=opts['usernames'])
        if opts['enrolled_only']:
            targets = targets.filter(enrolled_courses__isnull=False).distinct()

        count = 0
        for user in targets:
            user.is_approved = True
            user._skip_approval_email = not opts['notify']
            user.save()
            count += 1
            self.stdout.write(f"approved {user.username}")
        self.stdout.write(self.style.SUCCESS(f"{count} student(s) approved{' (login-link emails sent; failures are listed above)' if opts['notify'] else ''}."))
