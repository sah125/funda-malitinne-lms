"""All outgoing email in one place.

Every message is branded, has a plain-text fallback, and uses absolute links
built from settings.SITE_URL (so links work from any inbox, not just localhost).
Website enquiries go to settings.CONTACT_EMAIL (hello@malitinne.co.za).
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def absolute_url(path_or_name, *args):
    path = path_or_name if path_or_name.startswith('/') else reverse(path_or_name, args=args)
    return f"{settings.SITE_URL}{path}"


def _send(subject, template, context, to, reply_to=None):
    """Render `template` and send it. Returns True on success, never raises."""
    recipients = [addr for addr in (to if isinstance(to, (list, tuple, set)) else [to]) if addr]
    if not recipients:
        return False
    ctx = {
        'site_url': settings.SITE_URL,
        'contact_email': settings.CONTACT_EMAIL,
        'login_url': absolute_url('login'),
        **context,
    }
    html = render_to_string(template, ctx)
    text = strip_tags(html.split('<!--TEXT-->')[-1] if '<!--TEXT-->' in html else html)
    text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
    try:
        msg = EmailMultiAlternatives(
            subject=subject, body=text, from_email=settings.DEFAULT_FROM_EMAIL,
            to=list(recipients), reply_to=reply_to or [settings.CONTACT_EMAIL],
        )
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=False)
        return True
    except Exception as exc:  # email must never crash a page
        logger.warning("Email '%s' to %s failed: %s", subject, recipients, exc)
        return False


# ---------- Registration & approval ----------

def send_registration_received(user):
    return _send('We received your registration — Malitinne', 'email/registration_pending.html',
                 {'user': user}, user.email)


def notify_admins_new_registration(user):
    from .models import User
    admins = set(settings.REGISTRATION_NOTIFY_EMAILS)
    admins.update(User.objects.filter(role='admin', is_active=True).exclude(email='').values_list('email', flat=True))
    return _send(f'New learner waiting for approval: {user.get_full_name() or user.username}',
                 'email/admin_approval_needed.html',
                 {'user': user, 'approvals_url': absolute_url('pending_approvals')}, sorted(admins))


def send_account_approved_email(user):
    return _send('Your Malitinne account is approved — you can now log in', 'email/registration_approved.html',
                 {'user': user}, user.email)


def send_account_declined_email(user, reason=''):
    return _send('Update on your Malitinne registration', 'email/registration_declined.html',
                 {'user': user, 'reason': reason}, user.email)


def send_password_reset_email(user):
    link = absolute_url('reset_password', user.reset_password_token)
    return _send('Reset your Malitinne password', 'email/reset_password.html',
                 {'user': user, 'reset_link': link}, user.email)


def send_enrollment_decision(enrollment_request):
    return _send(f'Enrolment update: {enrollment_request.course.title}', 'email/enrollment_decision.html',
                 {'req': enrollment_request, 'course_url': absolute_url('course_detail', enrollment_request.course_id)},
                 enrollment_request.student.email)


# ---------- Website enquiries ----------

def send_enquiry_notification(enquiry):
    """Deliver a website enquiry to hello@malitinne.co.za. Reply goes straight to the visitor."""
    subject = f"New {enquiry.get_enquiry_type_display().lower()} from {enquiry.name}"
    if enquiry.programme:
        subject += f" — {enquiry.programme.title}"
    return _send(subject, 'email/enquiry_notification.html',
                 {'e': enquiry, 'admin_url': absolute_url(f'/admin/core/enquiry/{enquiry.pk}/change/')},
                 settings.CONTACT_EMAIL, reply_to=[enquiry.email])


def send_enquiry_acknowledgement(enquiry):
    return _send('Thank you for contacting Malitinne', 'email/enquiry_received.html', {'e': enquiry}, enquiry.email)
