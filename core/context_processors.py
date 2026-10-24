from django.conf import settings


def site(request):
    """Values every template can use (contact details, pending approval count)."""
    ctx = {
        'CONTACT_EMAIL': settings.CONTACT_EMAIL,
        'SITE_URL': settings.SITE_URL,
        'COMPANY_PHONE': '073 931 7923',
        'COMPANY_TEL': '(031) 301 0835',
    }
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') == 'admin'):
        from .models import EnrollmentRequest, User
        ctx['pending_approvals_count'] = User.objects.filter(role='student', is_approved=False, is_active=True).count()
        ctx['pending_enrolments_count'] = EnrollmentRequest.objects.filter(status='pending').count()
    return ctx
