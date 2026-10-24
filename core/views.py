# ==================== IMPORTS ====================
import csv
import io
import json
import logging
import mimetypes
import os
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.validators import validate_email
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.text import get_valid_filename
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from .ai_assistant import AIAdminAssistant
from .emails import (
    notify_admins_new_registration,
    send_account_declined_email,
    send_enquiry_acknowledgement,
    send_enquiry_notification,
    send_enrollment_decision,
    send_registration_received,
)
from .ai_recommendations import get_course_recommendations
from .models import (
    Announcement,
    Application,
    AssessorSignOff,
    Assignment,
    Attendance,
    AuditLog,
    BackupLog,
    Badge,
    Certificate,
    Course,
    DailyStreak,
    DocumentCategory,
    DocumentDownloadLog,
    Enquiry,
    EnrollmentRequest,
    ForumPost,
    ForumTopic,
    LearnerDocument,
    LearnerProfile,
    LearningModule,
    Lesson,
    LessonInteraction,
    LessonModule,
    LogbookEntry,
    LoginAttempt,
    Meeting,
    ModuleEvidence,
    NewsPost,
    Notification,
    ObservationChecklistItem,
    Opportunity,
    PortfolioOfEvidence,
    Programme,
    Progress,
    Quiz,
    QuizAttempt,
    QuizQuestion,
    SharedDocument,
    StaffAnnouncement,
    StudentChecklistResult,
    GalleryPhoto,
    ServiceLocation,
    Submission,
    SummativeAssessment,
    SummativeAssessmentSubmission,
    Task,
    TenderOpportunity,
    User,
    UserBadge,
    UserModuleProgress,
)
from .permissions import is_admin, is_instructor
from .portal_helpers import (
    calculate_project_health,
    get_overall_stats,
    get_urgent_actions,
)

logger = logging.getLogger(__name__)

# ==================== HELPER FUNCTIONS ====================

def send_notification(user, title, message, link=None):
    Notification.objects.create(user=user, title=title, message=message, link=link)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_for_badges(user):
    streak, _ = DailyStreak.objects.get_or_create(user=user)

    if streak.total_xp >= 100 and not UserBadge.objects.filter(user=user, badge__name='Rookie').exists():
        badge, _ = Badge.objects.get_or_create(name='Rookie', defaults={'description': 'Earned 100 XP', 'icon': 'fa-seedling', 'points_required': 100})
        UserBadge.objects.get_or_create(user=user, badge=badge)

    if streak.total_xp >= 500 and not UserBadge.objects.filter(user=user, badge__name='Apprentice').exists():
        badge, _ = Badge.objects.get_or_create(name='Apprentice', defaults={'description': 'Earned 500 XP', 'icon': 'fa-graduation-cap', 'points_required': 500})
        UserBadge.objects.get_or_create(user=user, badge=badge)

    if streak.total_xp >= 1000 and not UserBadge.objects.filter(user=user, badge__name='Master').exists():
        badge, _ = Badge.objects.get_or_create(name='Master', defaults={'description': 'Earned 1000 XP', 'icon': 'fa-crown', 'points_required': 1000})
        UserBadge.objects.get_or_create(user=user, badge=badge)

    if streak.current_streak >= 7 and not UserBadge.objects.filter(user=user, badge__name='Weekly Warrior').exists():
        badge, _ = Badge.objects.get_or_create(name='Weekly Warrior', defaults={'description': 'Logged in for 7 days in a row', 'icon': 'fa-calendar-check', 'lessons_completed': 7})
        UserBadge.objects.get_or_create(user=user, badge=badge)


# ==================== PUBLIC PAGE VIEWS ====================

PROGRAMME_CATEGORY_ICONS = Programme.ICONS


def programmes_page(request):
    """Public catalogue — shows what we offer, never the learning content."""
    programmes = Programme.objects.filter(is_published=True)
    category = request.GET.get('category') or ''
    status = request.GET.get('status') or ''
    query = (request.GET.get('q') or '').strip()
    if category:
        programmes = programmes.filter(category=category)
    if status:
        programmes = programmes.filter(status=status)
    if query:
        programmes = programmes.filter(Q(title__icontains=query) | Q(summary__icontains=query) | Q(code__icontains=query))
    published = Programme.objects.filter(is_published=True)
    return render(request, 'malitinne/programmes.html', {
        'programmes': programmes,
        'categories': [(key, label, PROGRAMME_CATEGORY_ICONS.get(key, 'fa-book')) for key, label in Programme.CATEGORY_CHOICES
                       if published.filter(category=key).exists()],
        'active_category': category, 'active_status': status, 'query': query,
        'accredited_count': published.filter(status='accredited').count(),
        'in_progress_count': published.filter(status='in_progress').count(),
        'icons': PROGRAMME_CATEGORY_ICONS,
    })


def programme_detail(request, slug):
    programme = get_object_or_404(Programme, slug=slug, is_published=True)
    related = Programme.objects.filter(is_published=True, category=programme.category).exclude(pk=programme.pk)[:3]
    return render(request, 'malitinne/programme_detail.html', {
        'programme': programme, 'related': related,
        'icon': PROGRAMME_CATEGORY_ICONS.get(programme.category, 'fa-book'),
        'enquiry_types': Enquiry.TYPE_CHOICES,
    })


def accreditation_page(request):
    programmes = Programme.objects.filter(is_published=True)
    return render(request, 'malitinne/accreditation.html', {
        'accredited': programmes.filter(status='accredited'),
        'in_progress': programmes.filter(status='in_progress'),
        'icons': PROGRAMME_CATEGORY_ICONS,
    })


def footprint_page(request):
    locations = list(ServiceLocation.objects.filter(is_published=True))
    total = sum(loc.beneficiaries or 0 for loc in locations)
    return render(request, 'malitinne/footprint.html', {
        'locations': locations, 'total_beneficiaries': total,
        'map_points': _map_points(locations),
    })


def _map_points(locations=None):
    if locations is None:
        locations = ServiceLocation.objects.filter(is_published=True)
    return [{
        'name': loc.name, 'kind': loc.kind, 'town': loc.town, 'province': loc.province,
        'lat': float(loc.latitude), 'lng': float(loc.longitude),
        'programmes': loc.programmes_list()[:6], 'beneficiaries': loc.beneficiaries, 'period': loc.period,
    } for loc in locations]


def privacy_page(request):
    return render(request, 'malitinne/privacy.html')


def clients_page(request):
    return render(request, 'malitinne/clients.html')


def about_page(request):
    return render(request, 'malitinne/about.html')


def services_page(request):
    return render(request, 'malitinne/services.html')


def impact_page(request):
    return render(request, 'malitinne/impact.html', {
        'gallery_photos': GalleryPhoto.objects.filter(is_published=True, show_on_home=True)[:6],
    })


def gallery_page(request):
    photos = GalleryPhoto.objects.filter(is_published=True)
    categories = [(key, label) for key, label in GalleryPhoto.CATEGORY_CHOICES
                  if any(p.category == key for p in photos)]
    return render(request, 'malitinne/gallery.html', {'photos': photos, 'categories': categories})


def contact_page(request):
    return render(request, 'malitinne/contact.html')


def news_list(request):
    posts = NewsPost.objects.filter(is_published=True)
    return render(request, 'malitinne/news_list.html', {'posts': posts})


def news_detail(request, slug):
    post = get_object_or_404(NewsPost, slug=slug, is_published=True)
    return render(request, 'malitinne/news_detail.html', {'post': post})


# ==================== STAFF PORTAL ====================

@login_required
def staff_portal(request):
    if request.user.role not in ['admin', 'instructor']:
        messages.error(request, 'You do not have access to the staff portal.')
        return redirect('student_dashboard')

    now = timezone.now()

    my_tasks = Task.objects.filter(assigned_to=request.user).exclude(status='done').order_by('due_date')[:8]
    upcoming_meetings = Meeting.objects.filter(
        Q(organizer=request.user) | Q(attendees=request.user),
        start_time__gte=now
    ).distinct().order_by('start_time')[:5]
    notifications = request.user.notifications.filter(is_read=False)[:5]
    announcements = StaffAnnouncement.objects.all()[:5]

    projects = TenderOpportunity.objects.filter(status__in=['new', 'viewed', 'active'])
    projects_health = []
    for project in projects:
        health = calculate_project_health(project)
        if health['learners'] > 0:
            projects_health.append(health)

    risk_order = {'high': 0, 'medium': 1, 'low': 2}
    projects_health.sort(key=lambda x: risk_order.get(x['risk'], 3))

    urgent_actions = get_urgent_actions()
    stats = get_overall_stats()

    ai_queries_today = AuditLog.objects.filter(action='ai_query', timestamp__date=now.date()).count()

    try:
        profile = LearnerProfile.objects.get(user=request.user)
        has_popia_consent = profile.popia_consent
    except LearnerProfile.DoesNotExist:
        has_popia_consent = False

    context = {
        'my_tasks': my_tasks,
        'upcoming_meetings': upcoming_meetings,
        'notifications': notifications,
        'notification_count': notifications.count(),
        'announcements': announcements,
        'active_learners': User.objects.filter(role='student', is_approved=True).count(),
        'total_courses': Course.objects.filter(status='published').count(),
        'pending_gradings': Submission.objects.filter(grade__isnull=True).count(),
        'active_opportunities': Opportunity.objects.filter(status='published').count(),
        'applications_this_month': Application.objects.filter(
            submitted_at__year=now.year, submitted_at__month=now.month
        ).count(),
        'projects_health': projects_health,
        'urgent_actions': urgent_actions,
        'stats': stats,
        'ai_queries_today': ai_queries_today,
        'has_popia_consent': has_popia_consent,
        'show_popica_banner': not has_popia_consent and request.user.role == 'student',
    }
    return render(request, 'staff_portal.html', context)


# ==================== TENDER MANAGEMENT ====================

@login_required
def tender_dashboard(request):
    if request.user.role not in ['instructor', 'admin']:
        return redirect('student_dashboard')

    tenders = TenderOpportunity.objects.filter(
        Q(status='new') | Q(status='viewed'),
        closing_date__gte=timezone.now().date()
    ).order_by('closing_date', '-ai_relevance_score')

    total = tenders.count()
    urgent = tenders.filter(closing_date__lte=timezone.now().date() + timedelta(days=7)).count()
    upcoming = tenders.filter(
        closing_date__gt=timezone.now().date() + timedelta(days=7),
        closing_date__lte=timezone.now().date() + timedelta(days=30)
    ).count()
    ongoing = tenders.filter(closing_date__gt=timezone.now().date() + timedelta(days=30)).count()

    return render(request, 'tender_dashboard.html', {
        'tenders': tenders[:20],
        'total': total,
        'urgent': urgent,
        'upcoming': upcoming,
        'ongoing': ongoing,
        'today': timezone.now().date(),
    })


@login_required
def run_tender_crawl(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Admin access required'}, status=403)
    return JsonResponse({'error': 'not_implemented'}, status=501)


@login_required
def tender_detail(request, tender_id):
    tender = get_object_or_404(TenderOpportunity, id=tender_id)

    if request.user.role not in ['instructor', 'admin']:
        return redirect('student_dashboard')

    if request.method == 'POST':
        tender.status = request.POST.get('status')
        tender.internal_notes = request.POST.get('notes', '')
        tender.follow_up_date = request.POST.get('follow_up_date') or None
        tender.follow_up_notes = request.POST.get('follow_up_notes', '')

        if request.FILES.get('document'):
            tender.local_document = request.FILES['document']

        tender.save()
        messages.success(request, 'Tender updated successfully')

    return render(request, 'tender_detail.html', {'tender': tender})


# ==================== SHARED DOCUMENT DRIVE ====================

@login_required
def shared_drive(request):
    if request.user.role not in ['instructor', 'admin']:
        return redirect('student_dashboard')

    documents = SharedDocument.objects.filter(
        Q(visibility='all_staff') |
        Q(visibility='management', uploaded_by__role='admin') |
        Q(visibility='private', uploaded_by=request.user)
    ).distinct().order_by('-uploaded_at')

    category = request.GET.get('category')
    if category:
        documents = documents.filter(category__slug=category)

    search = request.GET.get('search')
    if search:
        documents = documents.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__icontains=search)
        )

    categories = DocumentCategory.objects.all()

    return render(request, 'shared_drive.html', {
        'documents': documents,
        'categories': categories,
        'current_category': category,
        'search_query': search,
    })


@login_required
def upload_document(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if request.user.role not in ['instructor', 'admin']:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    title = request.POST.get('title')
    description = request.POST.get('description', '')
    category_id = request.POST.get('category')
    visibility = request.POST.get('visibility', 'all_staff')
    tags = request.POST.get('tags', '')

    if not title or not request.FILES.get('file'):
        return JsonResponse({'error': 'Title and file required'}, status=400)

    file = request.FILES['file']

    doc = SharedDocument.objects.create(
        title=title,
        description=description,
        file=file,
        file_name=file.name,
        file_size=file.size,
        mime_type=file.content_type,
        visibility=visibility,
        tags=tags,
        uploaded_by=request.user,
        category_id=category_id if category_id else None
    )

    staff_users = User.objects.filter(role__in=['instructor', 'admin'])
    for staff in staff_users:
        send_notification(
            staff,
            f'New Document: {title}',
            f'{request.user.username} shared "{title}" in the document drive.',
            '/shared-drive/'
        )

    return JsonResponse({
        'success': True,
        'document': {
            'id': doc.id,
            'title': doc.title,
            'file_url': doc.file.url,
            'file_name': doc.file_name,
            'uploaded_at': doc.uploaded_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@login_required
def download_document(request, doc_id):
    doc = get_object_or_404(SharedDocument, id=doc_id)

    if doc.visibility == 'all_staff':
        pass
    elif doc.visibility == 'management' and request.user.role != 'admin':
        return HttpResponseForbidden("You don't have permission to download this document")
    elif doc.visibility == 'private' and doc.uploaded_by != request.user:
        return HttpResponseForbidden("This document is private")

    DocumentDownloadLog.objects.create(document=doc, user=request.user, ip_address=get_client_ip(request))
    doc.download_count += 1
    doc.save()

    if doc.file and os.path.isfile(doc.file.path):
        return FileResponse(open(doc.file.path, 'rb'), as_attachment=True, filename=doc.file_name)

    raise Http404("File not found")


@login_required
def delete_document(request, doc_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    doc = get_object_or_404(SharedDocument, id=doc_id)

    if request.user.role != 'admin' and doc.uploaded_by != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if doc.file and os.path.isfile(doc.file.path):
        os.remove(doc.file.path)

    doc.delete()
    return JsonResponse({'success': True})


# ==================== AI COMMAND API ====================

@login_required
def ai_command_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    if request.user.role not in ['admin', 'instructor']:
        return JsonResponse({'error': 'Staff access required'}, status=403)

    try:
        data = json.loads(request.body)
        query = data.get('query', '')

        if not query:
            return JsonResponse({'error': 'No query provided'}, status=400)

        from .ai_assistant import process_operation_query
        response = process_operation_query(query, request.user)

        AuditLog.objects.create(
            user=request.user,
            action='ai_query',
            details={'query': query[:200], 'response_type': response.get('type', 'general')},
            ip_address=get_client_ip(request)
        )

        return JsonResponse(response)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def popia_consent_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        consent = data.get('consent', False)

        if not consent:
            return JsonResponse({'error': 'Consent must be true'}, status=400)

        profile, _created = LearnerProfile.objects.get_or_create(user=request.user)
        profile.popia_consent = True
        profile.popia_consent_date = timezone.now()
        profile.save()

        AuditLog.objects.create(
            user=request.user,
            action='popia_consent',
            details={'consent_given': True},
            ip_address=get_client_ip(request)
        )

        return JsonResponse({'success': True, 'message': 'POPIA consent recorded'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== DISCUSSION REPLIES ====================

@login_required
def delete_reply(request, reply_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        reply = get_object_or_404(ForumPost, id=reply_id)
        topic = reply.topic
        lesson = topic.lesson

        if request.user.role == 'instructor':
            if lesson.course.instructor != request.user:
                return JsonResponse({'error': 'You do not have permission to delete this reply'}, status=403)
        elif request.user.role != 'admin':
            return JsonResponse({'error': 'Permission denied'}, status=403)

        reply.delete()
        return JsonResponse({'success': True, 'message': 'Reply deleted successfully'})

    except ForumPost.DoesNotExist:
        return JsonResponse({'error': 'Reply not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def like_reply(request, reply_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        reply = get_object_or_404(ForumPost, id=reply_id)

        if request.user in reply.liked_by.all():
            reply.liked_by.remove(request.user)
            reply.likes_count = max(0, reply.likes_count - 1)
            liked = False
        else:
            reply.liked_by.add(request.user)
            reply.likes_count += 1
            liked = True

        reply.save(update_fields=['likes_count'])

        return JsonResponse({'success': True, 'liked': liked, 'likes_count': reply.likes_count})

    except ForumPost.DoesNotExist:
        return JsonResponse({'error': 'Reply not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== AUTHENTICATION ====================

def _login_cache_keys(request, username):
    ip = get_client_ip(request) or 'unknown'
    return f"login-fail:ip:{ip}", f"login-fail:user:{(username or '').lower()[:150]}"


def _is_locked_out(request, username):
    limit = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 5)
    return any((cache.get(key) or 0) >= limit for key in _login_cache_keys(request, username))


def _record_failed_login(request, username):
    timeout = getattr(settings, 'LOGIN_LOCKOUT_SECONDS', 900)
    for key in _login_cache_keys(request, username):
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout)


def _log_attempt(request, username, user=None, successful=False, reason=''):
    try:
        LoginAttempt.objects.create(
            username=(username or '')[:150], ip_address=get_client_ip(request) or '0.0.0.0',
            user_agent=f"{reason} | {request.META.get('HTTP_USER_AGENT', '')}"[:500], attempt_type='web', success=successful)
    except Exception as exc:
        logger.warning("Could not record login attempt: %s", exc)


def _dashboard_for(user):
    if user.role == 'student':
        return 'student_dashboard'
    if user.role == 'instructor':
        return 'instructor_dashboard'
    return 'admin_dashboard'


def user_login(request):
    if request.user.is_authenticated:
        return redirect(_dashboard_for(request.user))

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        password = request.POST.get('password') or ''

        if _is_locked_out(request, username):
            minutes = getattr(settings, 'LOGIN_LOCKOUT_SECONDS', 900) // 60
            _log_attempt(request, username, reason='locked_out')
            messages.error(request, f'Too many failed sign-in attempts. For your security, please wait {minutes} minutes and try again, or reset your password.')
            return render(request, 'login.html', status=429)

        # Allow signing in with either username or email address
        lookup = username
        if '@' in username:
            match = User.objects.filter(email__iexact=username).values_list('username', flat=True).first()
            lookup = match or username

        user = authenticate(request, username=lookup, password=password)

        if user is None:
            # Was it a correct password for a learner who is not approved yet?
            pending = User.objects.filter(username=lookup, is_active=True, role='student', is_approved=False).first()
            if pending and pending.check_password(password):
                _log_attempt(request, username, user=pending, reason='awaiting_approval')
                messages.warning(request, 'Your registration is still waiting for approval. We will email you a login link as soon as it is approved.')
                return render(request, 'login.html', {'pending_approval': True})
            _record_failed_login(request, username)
            _log_attempt(request, username, reason='bad_credentials')
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')

        if getattr(user, 'needs_approval', False):
            _log_attempt(request, username, user=user, reason='awaiting_approval')
            messages.warning(request, 'Your registration is still waiting for approval. We will email you a login link as soon as it is approved.')
            return render(request, 'login.html', {'pending_approval': True})

        for key in _login_cache_keys(request, username):
            cache.delete(key)
        login(request, user)
        _log_attempt(request, username, user=user, successful=True)
        messages.success(request, f'Welcome back, {user.first_name or user.username}!')
        next_url = request.POST.get('next') or request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect(_dashboard_for(user))

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been signed out securely.')
    return redirect('login')


def register(request):
    if request.user.is_authenticated:
        return redirect(_dashboard_for(request.user))

    form_data = {}
    if request.method == 'POST':
        form_data = request.POST
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''
        password2 = request.POST.get('password2') or ''

        full_name = (request.POST.get('full_name') or '').strip().split(' ', 1)
        first_name = full_name[0] if full_name else ''
        last_name = full_name[1] if len(full_name) > 1 else ''

        errors = []
        if not username or not email or not password:
            errors.append('Please complete all required fields.')
        if password != password2:
            errors.append('Passwords do not match.')
        if username and User.objects.filter(username__iexact=username).exists():
            errors.append('Username already exists.')
        if email and User.objects.filter(email__iexact=email).exists():
            errors.append('Email already exists.')
        if not request.POST.get('popia_consent'):
            errors.append('Please confirm that you consent to Malitinne processing your personal information (POPIA).')
        if password and password == password2:
            try:
                validate_password(password, User(username=username, email=email, first_name=first_name, last_name=last_name))
            except ValidationError as exc:
                errors.extend(exc.messages)

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'register.html', {'form_data': form_data})

        date_of_birth = None
        if request.POST.get('date_of_birth'):
            try:
                date_of_birth = datetime.strptime(request.POST['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                date_of_birth = None

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name,
            role='student', is_active=True, is_approved=False,
            id_number=(request.POST.get('id_number') or '').strip()[:20] or None,
            date_of_birth=date_of_birth,
            gender=request.POST.get('gender') or None,
            nationality=request.POST.get('nationality') or None,
            contact_number=(request.POST.get('contact_number') or '').strip()[:20] or None,
            disability=request.POST.get('disability') or None,
            preferred_language=request.POST.get('preferred_language') or 'English',
            popia_consent=True, popia_consent_at=timezone.now(),
        )

        send_registration_received(user)
        notify_admins_new_registration(user)

        messages.success(request, 'Thank you for registering! Your account is now waiting for approval. We will email you a login link as soon as it is approved.')
        return redirect('login')

    return render(request, 'register.html', {'form_data': form_data})


def forgot_password(request):
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            user.send_reset_email()
        # Same message either way so nobody can find out which emails are registered
        messages.success(request, 'If an account exists, a password reset link has been sent.')

    return render(request, 'forgot_password.html')


def reset_password(request, token):
    user = User.objects.filter(reset_password_token=token, reset_password_expires__gt=timezone.now()).first() if token else None
    valid = user is not None

    if request.method == 'POST' and valid:
        password = request.POST.get('password') or ''
        password2 = request.POST.get('password2') or ''

        if password != password2:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                validate_password(password, user)
            except ValidationError as exc:
                for err in exc.messages:
                    messages.error(request, err)
            else:
                user.set_password(password)
                user.reset_password_token = None
                user.reset_password_expires = None
                user.save()
                messages.success(request, 'Password reset successful! You can now log in.')
                return redirect('login')

    return render(request, 'reset_password.html', {'valid': valid, 'user': user})


# ==================== HOME ====================

def home(request):
    courses = Course.objects.filter(status='published')[:6]
    return render(request, 'home.html', {'courses': courses})


def company_home(request):
    latest_news = NewsPost.objects.filter(is_published=True).order_by('-published_date')[:3]
    return render(request, 'malitinne/home.html', {
        'latest_news': latest_news,
        'featured_programmes': Programme.objects.filter(is_published=True, status='accredited').order_by('-is_featured', 'order')[:6],
        'map_points': _map_points(),
        'gallery_photos': GalleryPhoto.objects.filter(is_published=True, show_on_home=True)[:6],
    })


def lms_portal(request):
    if request.user.is_authenticated:
        if request.user.role == 'student':
            return redirect('student_dashboard')
        elif request.user.role == 'instructor':
            return redirect('instructor_dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_dashboard')
    return redirect('login')


# ==================== STUDENT VIEWS ====================

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('instructor_dashboard')

    enrolled_courses = request.user.enrolled_courses.all()
    available_courses = Course.objects.filter(status='published').exclude(id__in=enrolled_courses)

    course_progress = {}
    courses_in_progress = 0
    total_progress_sum = 0

    for course in enrolled_courses:
        progress, _ = Progress.objects.get_or_create(student=request.user, course=course)
        progress_percent = progress.progress_percentage
        course_progress[course.id] = progress_percent
        total_progress_sum += progress_percent
        if 0 < progress_percent < 100:
            courses_in_progress += 1

    average_progress = int(total_progress_sum / len(enrolled_courses)) if enrolled_courses else 0
    certificates_count = Certificate.objects.filter(student=request.user).count()
    notifications = request.user.notifications.filter(is_read=False)[:5]

    request_status = dict(EnrollmentRequest.objects.filter(student=request.user).values_list('course_id', 'status'))

    return render(request, 'student_dashboard.html', {
        'request_status': request_status,
        'requires_approval': settings.COURSE_ENROLMENT_REQUIRES_APPROVAL,
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses,
        'course_progress': course_progress,
        'average_progress': average_progress,
        'courses_in_progress': courses_in_progress,
        'certificates_count': certificates_count,
        'notifications': notifications,
        'notification_count': notifications.count()
    })


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course.objects.select_related('instructor'), id=course_id)
    user = request.user

    if user.role == 'instructor' and course.instructor_id != user.id and not user.is_superuser:
        messages.error(request, 'You can only open courses that you facilitate.')
        return redirect('instructor_dashboard')

    lessons = course.lessons.all().order_by('order')
    is_enrolled = user.role != 'student' or course.students.filter(id=user.id).exists()

    if user.role == 'student' and not is_enrolled:
        # Not enrolled: show the outline only (lesson titles) — never the content.
        if course.status != 'published':
            raise Http404("Course not available")
        enrollment_request = EnrollmentRequest.objects.filter(student=user, course=course).first()
        return render(request, 'course_detail.html', {
            'course': course,
            'lessons': lessons,
            'is_enrolled': False,
            'enrollment_request': enrollment_request,
            'requires_approval': settings.COURSE_ENROLMENT_REQUIRES_APPROVAL,
        })

    progress = None
    completed_ids = set()
    if user.role == 'student':
        progress, _created = Progress.objects.get_or_create(student=user, course=course)
        completed_ids = set(progress.completed_lessons.values_list('id', flat=True))

    quizzes = []
    for lesson in lessons.select_related('quiz'):
        if hasattr(lesson, 'quiz'):
            attempt = QuizAttempt.objects.filter(quiz=lesson.quiz, student=user).first() if user.role == 'student' else None
            quizzes.append({'quiz': lesson.quiz, 'attempt': attempt, 'lesson': lesson})

    # Sequential unlocking: a lesson opens once the previous one is completed
    lesson_rows = []
    previous_done = True
    for index, lesson in enumerate(lessons, start=1):
        done = lesson.id in completed_ids
        if user.role != 'student':
            state = 'open'
        elif done:
            state = 'completed'
        elif previous_done:
            state = 'current'
        else:
            state = 'locked'
        lesson_rows.append({'lesson': lesson, 'number': index, 'state': state})
        previous_done = done

    return render(request, 'course_detail.html', {
        'course': course,
        'lessons': lessons,
        'lesson_rows': lesson_rows,
        'assignments': course.assignments.all(),
        'quizzes': quizzes,
        'progress': progress,
        'is_enrolled': True,
        'is_staff_view': user.role != 'student',
        'announcements': course.announcements.all()[:3],
    })


@login_required
def enroll_course(request, course_id):
    if request.user.role != 'student':
        messages.error(request, 'Only learners can join courses.')
        return redirect('lms_portal')

    course = get_object_or_404(Course, id=course_id, status='published')
    if request.method != 'POST':
        return redirect('course_detail', course_id=course.id)

    if course.students.filter(id=request.user.id).exists():
        messages.info(request, f'You are already enrolled in {course.title}.')
        return redirect('course_detail', course_id=course.id)

    if not settings.COURSE_ENROLMENT_REQUIRES_APPROVAL:
        course.students.add(request.user)
        Progress.objects.get_or_create(student=request.user, course=course)
        send_notification(request.user, 'Course Enrolled', f'You have successfully enrolled in {course.title}', f'/course/{course.id}/')
        messages.success(request, f'Successfully enrolled in {course.title}!')
        return redirect('course_detail', course_id=course.id)

    req, created = EnrollmentRequest.objects.get_or_create(
        student=request.user, course=course,
        defaults={'motivation': (request.POST.get('motivation') or '')[:2000]},
    )
    if not created and req.status == 'declined':
        req.status = 'pending'
        req.motivation = (request.POST.get('motivation') or req.motivation)[:2000]
        req.decided_at = None
        req.save()
        created = True
    if created:
        messages.success(request, f'Your request to join {course.title} has been sent. We will notify you once it is approved.')
    else:
        messages.info(request, 'Your request for this course is already being reviewed.')
    return redirect('course_detail', course_id=course.id)


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    if request.user.role != 'student':
        return redirect('instructor_dashboard')

    if request.user not in course.students.all():
        messages.warning(request, 'You need to enroll in this course first.')
        return redirect('course_detail', course_id=course.id)

    progress, _created = Progress.objects.get_or_create(student=request.user, course=course)

    quiz_attempt = None
    if hasattr(lesson, 'quiz'):
        quiz_attempt = QuizAttempt.objects.filter(quiz=lesson.quiz, student=request.user).first()

    if request.method == 'POST' and 'complete' in request.POST:
        if lesson not in progress.completed_lessons.all():
            progress.completed_lessons.add(lesson)
            messages.success(request, f'Lesson "{lesson.title}" marked as complete!')
            if progress.progress_percentage == 100:
                _certificate, cert_created = Certificate.objects.get_or_create(student=request.user, course=course)
                if cert_created:
                    messages.success(request, 'CONGRATULATIONS! You have completed the course!')
        else:
            messages.info(request, 'Lesson already completed')

        return redirect('course_detail', course_id=course.id)

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'course': course,
        'progress': progress,
        'quiz_attempt': quiz_attempt,
    })


@login_required
def view_document(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.user.role == 'student' and request.user not in lesson.course.students.all():
        return HttpResponseForbidden("You are not enrolled in this course.")

    if not lesson.document:
        raise Http404("No document available.")

    file_path = lesson.document.path
    if not os.path.exists(file_path):
        raise Http404("Document file not found.")

    with open(file_path, 'rb') as f:
        file_data = f.read()

    if file_path.endswith('.pdf'):
        response = HttpResponse(file_data, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
    else:
        mime_type, _encoding = mimetypes.guess_type(file_path)
        response = HttpResponse(file_data, content_type=mime_type or 'application/octet-stream')
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'

    return response


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    lesson = quiz.lesson
    course = lesson.course

    if request.user.role != 'student' or request.user not in course.students.all():
        messages.error(request, 'You need to be enrolled to take this quiz.')
        return redirect('course_detail', course_id=course.id)

    existing_attempt = QuizAttempt.objects.filter(quiz=quiz, student=request.user).first()
    if existing_attempt and existing_attempt.completed_at:
        messages.warning(request, 'You have already completed this quiz.')
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        answers = {}
        score = 0
        total_points = 0

        for question in quiz.questions.all():
            total_points += question.points
            user_answer = request.POST.get(f'question_{question.id}')
            if user_answer:
                answers[str(question.id)] = user_answer
                if user_answer.upper() == question.correct_answer:
                    score += question.points

        percentage = (score / total_points) * 100 if total_points > 0 else 0
        passed = percentage >= quiz.passing_score

        QuizAttempt.objects.create(
            quiz=quiz, student=request.user, score=score, percentage=percentage,
            passed=passed, answers=answers, completed_at=timezone.now()
        )

        progress, _ = Progress.objects.get_or_create(student=request.user, course=course)
        if lesson not in progress.completed_lessons.all():
            progress.completed_lessons.add(lesson)

        if passed:
            messages.success(request, f'Quiz completed! Score: {score}/{total_points} ({percentage:.0f}%) - PASSED!')
        else:
            messages.warning(request, f'Quiz completed! Score: {score}/{total_points} ({percentage:.0f}%) - Failed.')

        return redirect('course_detail', course_id=course.id)

    questions = quiz.questions.all().order_by('order')
    return render(request, 'take_quiz.html', {'quiz': quiz, 'lesson': lesson, 'questions': questions})


@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.user.role != 'student':
        return HttpResponseForbidden()

    existing = Submission.objects.filter(assignment=assignment, student=request.user).first()

    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        if existing:
            existing.file_upload = file
            existing.submitted_at = timezone.now()
            existing.grade = None
            existing.feedback = None
            existing.save()
            submission_id = existing.id
        else:
            submission = Submission.objects.create(assignment=assignment, student=request.user, file_upload=file)
            submission_id = submission.id

        send_notification(assignment.course.instructor, 'New Submission', f'{request.user.username} submitted {assignment.title}', f'/instructor/grade/{submission_id}/')
        messages.success(request, 'Assignment submitted successfully!')
        return redirect('course_detail', course_id=assignment.course.id)

    return render(request, 'submit_assignment.html', {'assignment': assignment, 'submission': existing})


@login_required
def certificates(request):
    if request.user.role != 'student':
        return redirect('instructor_dashboard')

    certificates = Certificate.objects.filter(student=request.user).select_related('course')
    return render(request, 'certificates.html', {'certificates': certificates})


@login_required
def debug_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    progress, _created = Progress.objects.get_or_create(student=request.user, course=course)

    return JsonResponse({
        'course_title': course.title,
        'total_lessons': course.lessons.count(),
        'completed_lessons': list(progress.completed_lessons.values_list('title', flat=True)),
        'completed_count': progress.completed_lessons.count(),
        'progress_percentage': progress.progress_percentage,
        'is_complete': progress.progress_percentage == 100
    })


@login_required
def download_certificate(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    progress = get_object_or_404(Progress, student=request.user, course=course)

    if progress.progress_percentage < 100:
        messages.error(request, 'You must complete 100% of the course to get a certificate.')
        return redirect('course_detail', course_id=course.id)

    certificate, _created = Certificate.objects.get_or_create(student=request.user, course=course)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    p.setStrokeColorRGB(0.4, 0.2, 0.6)
    p.setLineWidth(5)
    p.rect(30, 30, width - 60, height - 60)

    p.setFillColorRGB(0.4, 0.2, 0.6)
    p.setFont("Helvetica-Bold", 32)
    p.drawCentredString(width/2, height - 120, "CERTIFICATE OF COMPLETION")

    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(width/2, height - 160, "This certificate is proudly presented to")

    p.setFont("Helvetica-Bold", 28)
    p.setFillColorRGB(0.4, 0.2, 0.6)
    name = request.user.get_full_name() or request.user.username
    p.drawCentredString(width/2, height - 220, name.upper())

    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(width/2, height - 270, "For successfully completing the course")

    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.4, 0.2, 0.6)
    p.drawCentredString(width/2, height - 310, course.title)

    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.drawCentredString(width/2, height - 380, f"Issued on: {certificate.issued_at.strftime('%B %d, %Y')}")
    p.drawCentredString(width/2, height - 400, f"Certificate Number: {certificate.certificate_number}")

    p.line(width/2 - 100, height - 450, width/2 + 100, height - 450)
    p.setFont("Helvetica", 10)
    p.drawCentredString(width/2, height - 470, "Authorized Signature")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'certificate_{course.slug}.pdf')


# ==================== INSTRUCTOR VIEWS ====================

@login_required
def instructor_dashboard(request):
    if request.user.role != 'instructor':
        return redirect('student_dashboard')

    courses = Course.objects.filter(instructor=request.user)
    total_students = sum(course.students.count() for course in courses)
    total_lessons = sum(course.lessons.count() for course in courses)
    pending_grading = Submission.objects.filter(assignment__course__instructor=request.user, grade__isnull=True).count()

    all_students = []
    for course in courses:
        for student in course.students.all():
            progress, _ = Progress.objects.get_or_create(student=student, course=course)
            enrollment_date = student.date_joined.date() if student.date_joined else None
            if not any(s['student'].id == student.id for s in all_students):
                all_students.append({
                    'student': student, 'course': course,
                    'progress': progress.progress_percentage,
                    'enrollment_date': enrollment_date,
                })

    return render(request, 'instructor_dashboard.html', {
        'courses': courses,
        'total_courses': courses.count(),
        'total_students': total_students,
        'total_lessons': total_lessons,
        'pending_grading': pending_grading,
        'all_students': all_students,
    })


@login_required
@user_passes_test(is_instructor)
def create_course(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        level = request.POST.get('level', 'beginner')
        price = request.POST.get('price', 0)

        if title:
            course = Course.objects.create(
                title=title, description=description, instructor=request.user,
                level=level, price=price, status='published'
            )
            messages.success(request, f'Course "{title}" created successfully!')
            return redirect('manage_course', course_id=course.id)
        else:
            messages.error(request, 'Course title is required')

    return render(request, 'instructor/create_course.html')


@login_required
def import_learner_guide_view(request, course_id):
    """Convert a face-to-face Word learner guide into online lessons for this course."""
    from .importers import import_into_course

    course = get_object_or_404(Course, id=course_id)
    if not (request.user.is_superuser or request.user.role == 'admin' or
            (request.user.role == 'instructor' and course.instructor_id == request.user.id)):
        messages.error(request, 'Only the course facilitator or an administrator can import material.')
        return redirect('lms_portal')

    if request.method == 'POST':
        guide = request.FILES.get('guide')
        assessment = request.FILES.get('assessment')
        problems = []
        for f in filter(None, [guide, assessment]):
            if not f.name.lower().endswith('.docx'):
                problems.append(f'{f.name}: please upload a Word .docx file.')
            elif f.size > 25 * 1024 * 1024:
                problems.append(f'{f.name}: file is larger than 25 MB.')
        if not guide:
            problems.append('Please choose the learner guide (.docx).')
        if problems:
            for p in problems:
                messages.error(request, p)
        else:
            try:
                result = import_into_course(course, guide, assessment,
                                            module_title=(request.POST.get('module_title') or '').strip()[:200],
                                            replace=bool(request.POST.get('replace')))
            except Exception as exc:
                logger.exception('Learner guide import failed')
                messages.error(request, f'Could not import that document: {exc}')
            else:
                AuditLog.objects.create(user=request.user, action='create', resource_type='learner_guide_import',
                                        resource_id=course.id, ip_address=get_client_ip(request), details=result)
                messages.success(request, f"Done! {result['lessons']} online lessons (about {result['minutes']} minutes of reading) "
                                          f"and {result['assignments']} assessment activities were added to {course.title}.")
                return redirect('course_detail', course_id=course.id)

    return render(request, 'instructor/import_guide.html', {
        'course': course, 'modules': course.learning_modules.all(),
    })


@login_required
@user_passes_test(is_instructor)
def manage_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lessons = course.lessons.all().order_by('order')
    assignments = course.assignments.all()
    students = course.students.all()

    return render(request, 'instructor/manage_course.html', {
        'course': course, 'lessons': lessons, 'assignments': assignments, 'students': students
    })


@login_required
@user_passes_test(is_instructor)
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        video_url = request.POST.get('video_url')
        duration = request.POST.get('duration', 0)
        order = request.POST.get('order', 0)
        document = request.FILES.get('document')

        if title:
            lesson = Lesson.objects.create(
                course=course, title=title, content=content,
                video_url=video_url, duration=duration, order=order
            )
            if document:
                lesson.document = document
                lesson.save()

            messages.success(request, f'Lesson "{title}" added successfully!')
            return redirect('manage_course', course_id=course.id)
        else:
            messages.error(request, 'Lesson title is required')

    return render(request, 'instructor/add_lesson.html', {'course': course})


@login_required
@user_passes_test(is_instructor)
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if lesson.course.instructor != request.user:
        messages.error(request, 'You do not have permission to edit this lesson.')
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        lesson.title = request.POST.get('title')
        lesson.content = request.POST.get('content')
        lesson.video_url = request.POST.get('video_url')
        lesson.duration = request.POST.get('duration', 0)
        lesson.order = request.POST.get('order', 0)

        if request.FILES.get('document'):
            lesson.document = request.FILES['document']

        lesson.save()
        messages.success(request, f'Lesson "{lesson.title}" updated successfully!')
        return redirect('manage_course', course_id=lesson.course.id)

    return render(request, 'instructor/edit_lesson.html', {'lesson': lesson})


@login_required
@user_passes_test(is_instructor)
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if lesson.course.instructor != request.user:
        messages.error(request, 'You cannot delete this lesson.')
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        course_id = lesson.course.id
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully!')
        return redirect('manage_course', course_id=course_id)

    return render(request, 'instructor/delete_lesson.html', {'lesson': lesson})


@login_required
@user_passes_test(is_instructor)
def add_quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if lesson.course.instructor != request.user:
        messages.error(request, 'You cannot add a quiz to this lesson.')
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        quiz, _created = Quiz.objects.get_or_create(lesson=lesson)
        quiz.title = request.POST.get('title', f'Quiz: {lesson.title}')
        quiz.description = request.POST.get('description', '')
        quiz.passing_score = request.POST.get('passing_score', 70)
        quiz.save()

        messages.success(request, 'Quiz created! Now add questions.')
        return redirect('add_quiz_question', quiz_id=quiz.id)

    return render(request, 'instructor/add_quiz.html', {'lesson': lesson})


@login_required
@user_passes_test(is_instructor)
def add_quiz_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.lesson.course.instructor != request.user:
        messages.error(request, 'You cannot add questions to this quiz.')
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        QuizQuestion.objects.create(
            quiz=quiz,
            question_text=request.POST.get('question_text'),
            question_type=request.POST.get('question_type'),
            points=request.POST.get('points', 10),
            order=quiz.questions.count() + 1,
            option_a=request.POST.get('option_a', ''),
            option_b=request.POST.get('option_b', ''),
            option_c=request.POST.get('option_c', ''),
            option_d=request.POST.get('option_d', ''),
            correct_answer=request.POST.get('correct_answer')
        )
        messages.success(request, 'Question added!')
        return redirect('add_quiz_question', quiz_id=quiz.id)

    return render(request, 'instructor/add_quiz_question.html', {'quiz': quiz})


@login_required
@user_passes_test(is_instructor)
def add_assignment(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date = request.POST.get('due_date')
        total_points = request.POST.get('total_points', 100)

        if title and due_date:
            Assignment.objects.create(
                course=course, title=title, description=description,
                due_date=due_date, total_points=total_points
            )
            messages.success(request, f'Assignment "{title}" created successfully!')
            return redirect('manage_course', course_id=course.id)
        else:
            messages.error(request, 'Assignment title and due date are required.')

    return render(request, 'instructor/add_assignment.html', {'course': course})


@login_required
@user_passes_test(is_instructor)
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if assignment.course.instructor != request.user:
        messages.error(request, 'You cannot view submissions for this assignment.')
        return redirect('instructor_dashboard')

    submissions = assignment.submissions.all().order_by('-submitted_at')

    return render(request, 'instructor/view_submissions.html', {
        'assignment': assignment, 'submissions': submissions
    })


@login_required
@user_passes_test(is_instructor)
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)

    if submission.assignment.course.instructor != request.user:
        messages.error(request, 'You cannot grade this submission.')
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback', '')

        try:
            grade = int(grade)
            max_points = submission.assignment.total_points
            if grade < 0 or grade > max_points:
                messages.error(request, f'Grade must be between 0 and {max_points}')
            else:
                submission.grade = grade
                submission.feedback = feedback
                submission.save()

                try:
                    send_mail(
                        f'Assignment Graded: {submission.assignment.title}',
                        f'Hello {submission.student.username},\n\nYour assignment "{submission.assignment.title}" has been graded.\n\nGrade: {grade}/{max_points}\n\nFeedback: {feedback}\n\nLogin to view details.\n\nRegards,\nFunda Malitinne LMS',
                        'noreply@fundamalitinne.com', [submission.student.email], fail_silently=True
                    )
                except Exception as exc:
                    logger.warning("Failed to send grade notification: %s", exc)

                messages.success(request, 'Grade submitted! Student notified.')
                return redirect('view_submissions', assignment_id=submission.assignment.id)
        except ValueError:
            messages.error(request, 'Please enter a valid number for grade')

    return render(request, 'grade_submission.html', {'submission': submission})


# ==================== BULK UPLOAD ====================

@login_required
def api_users(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'GET':
        users = User.objects.all().values('id', 'username', 'email', 'role', 'is_approved', 'first_name', 'last_name')
        return JsonResponse(list(users), safe=False)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            User.objects.filter(id=data.get('id')).delete()
            return JsonResponse({'success': True})
        except Exception as exc:
            logger.warning("Failed to delete user via API: %s", exc)
            return JsonResponse({'error': 'Failed to delete'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def api_bulk_upload(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'POST' and request.FILES.get('csv'):
        try:
            csv_file = request.FILES['csv']
            decoded = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))

            created = 0
            errors = []

            for row in reader:
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                password = row.get('password', 'Student@123')

                if username and email:
                    user, created_flag = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'first_name': row.get('first_name', ''),
                            'last_name': row.get('last_name', ''),
                            'role': 'student',
                            'is_approved': True
                        }
                    )
                    if created_flag:
                        user.set_password(password)
                        user.save()
                        created += 1
                    else:
                        errors.append(f'{username} already exists')
                else:
                    errors.append('Missing username or email')

            return JsonResponse({'success': True, 'created': created, 'errors': errors[:5]})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'No CSV file provided'}, status=400)


@login_required
@user_passes_test(is_instructor)
def bulk_upload_page(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'bulk_upload.html', {'courses': courses})


@login_required
@user_passes_test(is_instructor)
def bulk_upload_process(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        csv_file = request.FILES.get('csv_file')
        send_welcome = request.POST.get('send_welcome') == 'on'
        auto_enroll = request.POST.get('auto_enroll') == 'on'

        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('bulk_upload_page')

        try:
            data = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(data))
            added = 0
            errors = []

            for row in reader:
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                password = row.get('password', 'Mal@@@123')

                if not username or not email:
                    errors.append('Missing username or email')
                    continue

                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': row.get('first_name', ''),
                        'last_name': row.get('last_name', ''),
                        'role': 'student',
                        'is_approved': True
                    }
                )

                if created:
                    user.set_password(password)
                    user.save()
                    added += 1

                    if send_welcome:
                        try:
                            send_mail(
                                'Welcome to Funda Malitinne LMS',
                                f'Hello {username},\n\nYour account has been created.\n\nUsername: {username}\nPassword: {password}\n\nLogin here: /login/\n\nRegards,\nFunda Malitinne Team',
                                'noreply@fundamalitinne.com', [email], fail_silently=True
                            )
                        except Exception as exc:
                            logger.warning("Failed to send learner welcome email: %s", exc)
                else:
                    if user.role != 'student':
                        user.role = 'student'
                        user.save()

                if auto_enroll and course_id:
                    try:
                        course = Course.objects.get(id=course_id, instructor=request.user)
                        if user not in course.students.all():
                            course.students.add(user)
                            Progress.objects.get_or_create(student=user, course=course)
                    except Course.DoesNotExist:
                        pass

            messages.success(request, f'Successfully added {added} new students!')
            if errors:
                messages.warning(request, f'Errors: {", ".join(errors[:3])}')
            return redirect('instructor_dashboard')
        except Exception as e:
            messages.error(request, f'Error processing CSV: {e!s}')
            return redirect('bulk_upload_page')

    return redirect('bulk_upload_page')


@login_required
@user_passes_test(is_instructor)
def bulk_upload_students(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('manage_course', course_id=course.id)

        data = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(data))
        added = 0
        errors = []

        for row in reader:
            username = row.get('username')
            email = row.get('email')
            password = row.get('password', 'Password123!')

            if username and email:
                user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'role': 'student'})
                if created:
                    user.set_password(password)
                    user.save()
                    course.students.add(user)
                    Progress.objects.get_or_create(student=user, course=course)
                    added += 1
                else:
                    if user not in course.students.all():
                        course.students.add(user)
                        Progress.objects.get_or_create(student=user, course=course)
                        added += 1
                    else:
                        errors.append(f'{username} already enrolled')

        messages.success(request, f'Added {added} students to the course!')
        if errors:
            messages.warning(request, f'Errors: {", ".join(errors[:5])}')
        return redirect('manage_course', course_id=course.id)

    return render(request, 'instructor/bulk_upload.html', {'course': course})


# ==================== ADMIN VIEWS ====================

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('company_home')

    section = request.GET.get('section', 'dashboard')
    all_users = User.objects.all().order_by('-date_joined')
    students = all_users.filter(role='student')
    instructors = all_users.filter(role='instructor')
    courses = Course.objects.all().order_by('-created_at')
    submissions = Submission.objects.all()

    return render(request, 'custom_admin/dashboard.html', {
        'section': section,
        'total_courses': courses.count(),
        'total_students': students.count(),
        'total_instructors': instructors.count(),
        'total_submissions': submissions.count(),
        'total_lessons': Lesson.objects.count(),
        'total_assignments': Assignment.objects.count(),
        'recent_courses': courses[:10],
        'recent_users': all_users[:10],
        'all_users': all_users,
        'students': students,
        'instructors': instructors,
        'courses': courses,
    })


@login_required
def delete_course(request, course_id):
    if request.user.role != 'admin':
        return redirect('company_home')
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, 'Course deleted successfully.')
    return redirect('admin_dashboard')


@login_required
def delete_user(request, user_id):
    if request.user.role != 'admin':
        return redirect('company_home')
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('admin_dashboard')


# ==================== NOTIFICATIONS ====================

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})


@login_required
def get_notifications(request):
    notifications = request.user.notifications.filter(is_read=False)[:10]
    data = [{'id': n.id, 'title': n.title, 'message': n.message, 'link': n.link} for n in notifications]
    return JsonResponse({'notifications': data, 'count': len(data)})


# ==================== ANNOUNCEMENTS ====================

@login_required
def course_announcements(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role == 'student' and request.user not in course.students.all():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('student_dashboard')

    if request.user.role == 'instructor' and course.instructor != request.user:
        messages.error(request, 'You do not own this course.')
        return redirect('instructor_dashboard')

    announcements = course.announcements.all().order_by('-is_pinned', '-created_at')

    if request.method == 'POST' and request.user.role == 'instructor':
        title = request.POST.get('title')
        content = request.POST.get('content')
        is_pinned = request.POST.get('is_pinned') == 'on'

        if title and content:
            Announcement.objects.create(course=course, title=title, content=content, author=request.user, is_pinned=is_pinned)
            messages.success(request, 'Announcement posted successfully!')
        else:
            messages.error(request, 'Title and content are required.')

        return redirect('course_announcements', course_id=course.id)

    return render(request, 'announcements.html', {'course': course, 'announcements': announcements})


@login_required
def toggle_announcement_pin(request, announcement_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    announcement = get_object_or_404(Announcement, id=announcement_id)

    if request.user.role != 'instructor' or announcement.course.instructor != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    announcement.is_pinned = not announcement.is_pinned
    announcement.save()
    return JsonResponse({'success': True, 'is_pinned': announcement.is_pinned})


@login_required
def delete_announcement(request, announcement_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    announcement = get_object_or_404(Announcement, id=announcement_id)

    if request.user.role != 'instructor' or announcement.course.instructor != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    announcement.delete()
    return JsonResponse({'success': True})


# ==================== FORUM ====================

@login_required
def lesson_discussions(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.user.is_authenticated:
        if request.user.role == 'student' and request.user not in lesson.course.students.all():
            messages.error(request, 'You are not enrolled in this course.')
            return redirect('course_detail', course_id=lesson.course.id)

    if request.method == 'POST' and 'create_discussion' in request.POST:
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if not title or not content:
            messages.error(request, 'Title and content are required.')
        else:
            topic = ForumTopic.objects.create(lesson=lesson, author=request.user, title=title, content=content)
            messages.success(request, 'Discussion posted successfully.')
            return redirect('discussion_detail', topic_id=topic.id)

    topics = ForumTopic.objects.filter(lesson=lesson).order_by('-is_pinned', '-created_at')
    return render(request, 'discussion/lesson_discussions.html', {'lesson': lesson, 'discussions': topics, 'topics': topics})


@login_required
def discussion_detail(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    lesson = topic.lesson

    if request.user.role == 'student':
        if request.user not in lesson.course.students.all():
            messages.warning(request, 'You need to be enrolled in this course to view discussions.')
            return redirect('course_detail', course_id=lesson.course.id)
    elif request.user.role == 'instructor':
        if lesson.course.instructor != request.user and request.user.role != 'admin':
            messages.error(request, 'You do not have permission to view this discussion.')
            return redirect('instructor_dashboard')

    topic.views_count += 1
    topic.save(update_fields=['views_count'])
    posts = topic.posts.filter(parent=None).prefetch_related('posts__author').order_by('created_at')

    if request.method == 'POST' and 'add_reply' in request.POST:
        if topic.is_closed:
            messages.error(request, 'This discussion is closed.')
            return redirect('discussion_detail', topic_id=topic.id)

        content = request.POST.get('content')
        parent_id = request.POST.get('parent_reply_id')

        if content:
            parent = None
            if parent_id:
                parent = get_object_or_404(ForumPost, id=parent_id)

            ForumPost.objects.create(topic=topic, author=request.user, content=content, parent=parent)
            messages.success(request, 'Your reply has been posted.')
        else:
            messages.error(request, 'Please enter some content for your reply.')

        return redirect('discussion_detail', topic_id=topic.id)

    if request.method == 'POST' and 'delete_reply' in request.POST:
        if request.user.role == 'instructor' and lesson.course.instructor == request.user:
            reply_id = request.POST.get('reply_id')
            try:
                ForumPost.objects.get(id=reply_id).delete()
                messages.success(request, 'Reply deleted successfully.')
            except ForumPost.DoesNotExist:
                messages.error(request, 'Reply not found.')
        else:
            messages.error(request, 'You do not have permission to delete this reply.')

        return redirect('discussion_detail', topic_id=topic.id)

    reply_list = []
    for post in posts:
        reply_list.append({
            'id': post.id,
            'author': post.author,
            'content': post.content,
            'created_at': post.created_at,
            'likes_count': post.likes_count,
            'nested_replies_list': post.posts.all().order_by('created_at'),
            'can_delete': request.user.role == 'instructor' and lesson.course.instructor == request.user
        })

    return render(request, 'discussion/discussion_detail.html', {
        'discussion': topic,
        'lesson': lesson,
        'replies': reply_list,
        'posts': reply_list,
        'can_delete_discussion': request.user.role == 'instructor' and lesson.course.instructor == request.user
    })


@login_required
def toggle_discussion_pin(request, discussion_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        topic = get_object_or_404(ForumTopic, id=discussion_id)

        if request.user.role != 'instructor' or topic.lesson.course.instructor != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        topic.is_pinned = not topic.is_pinned
        topic.save()
        return JsonResponse({'success': True, 'is_pinned': topic.is_pinned})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def toggle_discussion_lock(request, discussion_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        topic = get_object_or_404(ForumTopic, id=discussion_id)

        if request.user.role != 'instructor' or topic.lesson.course.instructor != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        topic.is_closed = not topic.is_closed
        topic.save()
        return JsonResponse({'success': True, 'is_locked': topic.is_closed, 'is_closed': topic.is_closed})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_discussion(request, discussion_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        topic = get_object_or_404(ForumTopic, id=discussion_id)
        lesson = topic.lesson

        if request.user.role != 'instructor' or lesson.course.instructor != request.user:
            return JsonResponse({'error': 'You do not have permission to delete this discussion'}, status=403)

        topic.posts.all().delete()
        topic.delete()
        return JsonResponse({'success': True, 'message': 'Discussion deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==================== ROSTER & ATTENDANCE ====================

@login_required
def course_roster(request, course_id):
    """Class list with progress. Staff only — learners may not see each other's
    personal information (POPIA)."""
    course = get_object_or_404(Course, id=course_id)

    if request.user.role == 'student':
        messages.error(request, 'The class roster is only available to facilitators.')
        return redirect('course_detail', course_id=course.id)

    if request.user.role == 'instructor' and course.instructor_id != request.user.id:
        messages.error(request, 'You do not own this course.')
        return redirect('instructor_dashboard')

    total_lessons = course.lessons.count()
    students_qs = course.students.order_by('first_name', 'last_name', 'username')

    completed_map = dict(
        Progress.objects.filter(course=course).annotate(done=Count('completed_lessons')).values_list('student_id', 'done')
    )
    att_rows = Attendance.objects.filter(course=course).values('student_id').annotate(
        total=Count('id'), present=Count('id', filter=Q(status='present')))
    attendance_map = {r['student_id']: (r['present'], r['total']) for r in att_rows}
    grade_map = dict(
        Submission.objects.filter(assignment__course=course, grade__isnull=False)
        .values('student_id').annotate(avg=Avg('grade')).values_list('student_id', 'avg')
    )
    last_seen = dict(students_qs.values_list('id', 'last_login'))

    students = []
    for student in students_qs:
        done = completed_map.get(student.id, 0)
        progress = int(done * 100 / total_lessons) if total_lessons else 0
        present, total = attendance_map.get(student.id, (0, 0))
        attendance = int(present * 100 / total) if total else None
        avg = grade_map.get(student.id)
        status = 'completed' if progress == 100 else 'on_track' if progress >= 50 else 'at_risk' if progress < 20 else 'in_progress'
        students.append({
            'student': student,
            'progress': progress,
            'lessons_done': done,
            'attendance': attendance,
            'grade': round(avg) if avg is not None else None,
            'status': status,
            'last_login': last_seen.get(student.id),
        })

    query = (request.GET.get('q') or '').strip().lower()
    if query:
        students = [s for s in students if query in (s['student'].get_full_name() + ' ' + s['student'].username + ' ' + s['student'].email).lower()]

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="roster-{course.id}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Username', 'Email', 'Lessons completed', 'Progress %', 'Attendance %', 'Average grade %', 'Last login'])
        for row in students:
            st = row['student']
            writer.writerow([st.get_full_name(), st.username, st.email, row['lessons_done'], row['progress'],
                             '' if row['attendance'] is None else row['attendance'], '' if row['grade'] is None else row['grade'],
                             row['last_login'].strftime('%Y-%m-%d %H:%M') if row['last_login'] else ''])
        AuditLog.objects.create(user=request.user, action='export', resource_type='course_roster', resource_id=course.id,
                                ip_address=get_client_ip(request))
        return response

    summary = {
        'count': len(students),
        'completed': sum(1 for s in students if s['status'] == 'completed'),
        'at_risk': sum(1 for s in students if s['status'] == 'at_risk'),
        'avg_progress': int(sum(s['progress'] for s in students) / len(students)) if students else 0,
    }
    pending_requests = course.enrollment_requests.filter(status='pending').select_related('student')

    return render(request, 'course_roster.html', {
        'course': course, 'students': students, 'summary': summary, 'total_lessons': total_lessons,
        'query': request.GET.get('q', ''), 'pending_requests': pending_requests,
    })


@login_required
def course_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user.role != 'instructor' or course.instructor != request.user:
        messages.error(request, 'Only instructors can view attendance.')
        return redirect('instructor_dashboard')

    attendances = Attendance.objects.filter(course=course).order_by('-date')
    return render(request, 'attendance.html', {'course': course, 'attendances': attendances})


@login_required
def mark_attendance(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    course = get_object_or_404(Course, id=request.POST.get('course_id'))

    if request.user.role != 'instructor' or course.instructor != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    student = get_object_or_404(User, id=request.POST.get('student_id'))

    attendance, created = Attendance.objects.get_or_create(
        student=student,
        course=course,
        date=request.POST.get('date'),
        defaults={'status': request.POST.get('status'), 'marked_by': request.user}
    )

    if not created:
        attendance.status = request.POST.get('status')
        attendance.marked_by = request.user
        attendance.save()

    return JsonResponse({'success': True})


# ==================== LESSON MODULE API ====================

@login_required
def api_module_content(request, module_id):
    try:
        module = LessonModule.objects.get(id=module_id)
    except LessonModule.DoesNotExist:
        return JsonResponse({'error': 'Module not found'}, status=404)

    if request.user.role == 'student' and request.user not in module.lesson.course.students.all():
        return JsonResponse({'error': 'You are not enrolled in this course'}, status=403)

    for prev_module in module.lesson.modules.filter(order__lt=module.order):
        if not UserModuleProgress.objects.filter(student=request.user, module=prev_module, completed=True).exists():
            return JsonResponse({'error': 'Complete previous modules first'}, status=403)

    return JsonResponse({
        'id': module.id,
        'title': module.title,
        'content': module.content,
        'content_type': module.content_type,
        'video_url': module.lesson.video_url if module.content_type == 'video' else None,
        'points': module.points,
        'time_estimate': module.time_estimate,
        'order': module.order,
        'total_modules': module.lesson.modules.count()
    })


@login_required
def api_module_quiz(request, module_id):
    try:
        module = LessonModule.objects.get(id=module_id)
    except LessonModule.DoesNotExist:
        return JsonResponse({'error': 'Module not found'}, status=404)

    if module.content_type != 'quiz':
        return JsonResponse({'error': 'This module does not have a quiz'}, status=400)

    if request.user.role == 'student' and request.user not in module.lesson.course.students.all():
        return JsonResponse({'error': 'You are not enrolled in this course'}, status=403)

    for prev_module in module.lesson.modules.filter(order__lt=module.order):
        if not UserModuleProgress.objects.filter(student=request.user, module=prev_module, completed=True).exists():
            return JsonResponse({'error': 'Complete previous modules first'}, status=403)

    questions = []
    if hasattr(module.lesson, 'quiz'):
        quiz = module.lesson.quiz
        for q in quiz.questions.all():
            questions.append({
                'id': q.id,
                'text': q.question_text,
                'options': [q.option_a, q.option_b, q.option_c, q.option_d] if q.question_type == 'multiple_choice' else ['True', 'False'],
                'type': q.question_type,
                'points': q.points
            })

    return JsonResponse({
        'id': module.id,
        'title': f"Quiz: {module.title}",
        'questions': questions,
        'points': module.points,
        'passing_score': 70,
        'time_limit': module.time_estimate
    })


@login_required
def api_module_complete(request, module_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        module = LessonModule.objects.get(id=module_id)
    except LessonModule.DoesNotExist:
        return JsonResponse({'error': 'Module not found'}, status=404)

    if request.user.role == 'student' and request.user not in module.lesson.course.students.all():
        return JsonResponse({'error': 'You are not enrolled in this course'}, status=403)

    for prev_module in module.lesson.modules.filter(order__lt=module.order):
        if not UserModuleProgress.objects.filter(student=request.user, module=prev_module, completed=True).exists():
            return JsonResponse({'error': f'Complete "{prev_module.title}" first', 'required_module': prev_module.title}, status=403)

    progress, _created = UserModuleProgress.objects.get_or_create(student=request.user, module=module)

    if progress.completed:
        return JsonResponse({'success': False, 'message': 'Module already completed'})

    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()

    interaction, _ = LessonInteraction.objects.get_or_create(student=request.user, lesson=module.lesson)
    completed_count = UserModuleProgress.objects.filter(student=request.user, module__lesson=module.lesson, completed=True).count()
    interaction.modules_completed = completed_count
    interaction.total_time_spent = getattr(interaction, 'total_time_spent', 0) + module.time_estimate * 60
    interaction.last_module_viewed = module.order
    interaction.save()

    streak, _ = DailyStreak.objects.get_or_create(user=request.user)
    streak.total_xp += module.points
    streak.save()

    total_modules = module.lesson.modules.count()
    lesson_completed = False
    lesson_completion_bonus = 0

    if completed_count == total_modules and not interaction.completed:
        interaction.completed = True
        interaction.completed_at = timezone.now()
        interaction.save()
        lesson_completed = True
        lesson_completion_bonus = 50
        streak.total_xp += lesson_completion_bonus
        streak.save()

        course_progress, _ = Progress.objects.get_or_create(student=request.user, course=module.lesson.course)
        if module.lesson not in course_progress.completed_lessons.all():
            course_progress.completed_lessons.add(module.lesson)

    check_for_badges(request.user)

    return JsonResponse({
        'success': True,
        'xp_earned': module.points,
        'bonus_xp': lesson_completion_bonus,
        'total_xp': module.points + lesson_completion_bonus,
        'modules_completed': completed_count,
        'total_modules': total_modules,
        'lesson_completed': lesson_completed,
        'progress_percentage': int((completed_count / total_modules) * 100) if total_modules > 0 else 0,
        'message': f'Completed "{module.title}"! +{module.points} XP' + (f' +{lesson_completion_bonus} bonus XP!' if lesson_completed else '')
    })


@login_required
def api_lesson_progress(request, lesson_id):
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return JsonResponse({'error': 'Lesson not found'}, status=404)

    if request.user.role == 'student' and request.user not in lesson.course.students.all():
        return JsonResponse({'error': 'You are not enrolled in this course'}, status=403)

    interaction, _ = LessonInteraction.objects.get_or_create(student=request.user, lesson=lesson)
    total_modules = lesson.modules.count()
    modules_completed = UserModuleProgress.objects.filter(student=request.user, module__lesson=lesson, completed=True).count()
    progress_percentage = int((modules_completed / total_modules) * 100) if total_modules > 0 else 0
    streak, _ = DailyStreak.objects.get_or_create(user=request.user)

    return JsonResponse({
        'lesson_id': lesson.id,
        'lesson_title': lesson.title,
        'modules_completed': modules_completed,
        'total_modules': total_modules,
        'progress_percentage': progress_percentage,
        'xp_earned': streak.total_xp,
        'time_spent': interaction.total_time_spent // 60,
        'completed': interaction.completed,
        'last_module_viewed': interaction.last_module_viewed
    })


@login_required
def api_lesson_complete(request, lesson_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return JsonResponse({'error': 'Lesson not found'}, status=404)

    if request.user.role == 'student' and request.user not in lesson.course.students.all():
        return JsonResponse({'error': 'You are not enrolled in this course'}, status=403)

    total_modules = lesson.modules.count()
    modules_completed = UserModuleProgress.objects.filter(student=request.user, module__lesson=lesson, completed=True).count()

    if total_modules > 0 and modules_completed < total_modules:
        return JsonResponse({'error': f'Complete all {total_modules} modules first', 'modules_remaining': total_modules - modules_completed}, status=400)

    interaction, _ = LessonInteraction.objects.get_or_create(student=request.user, lesson=lesson)

    if interaction.completed:
        return JsonResponse({'success': False, 'message': 'Lesson already completed'})

    interaction.completed = True
    interaction.completed_at = timezone.now()
    interaction.save()

    progress, _ = Progress.objects.get_or_create(student=request.user, course=lesson.course)
    if lesson not in progress.completed_lessons.all():
        progress.completed_lessons.add(lesson)

    streak, _ = DailyStreak.objects.get_or_create(user=request.user)
    streak.total_xp += 50
    streak.save()

    return JsonResponse({
        'success': True,
        'xp_earned': 50,
        'lesson_completed': True,
        'course_progress': progress.progress_percentage,
        'message': f'Congratulations! You completed "{lesson.title}"! +50 XP'
    })


@login_required
def api_check_module_status(request, lesson_id):
    try:
        lesson = Lesson.objects.get(id=lesson_id)
    except Lesson.DoesNotExist:
        return JsonResponse({'error': 'Lesson not found'}, status=404)

    modules = lesson.modules.all()
    completed_module_ids = []

    for module in modules:
        if UserModuleProgress.objects.filter(student=request.user, module=module, completed=True).exists():
            completed_module_ids.append(module.id)

    return JsonResponse({
        'lesson_id': lesson.id,
        'total_modules': modules.count(),
        'completed_modules': completed_module_ids,
        'all_completed': len(completed_module_ids) == modules.count() if modules.exists() else True
    })


# ==================== AI ASSISTANT ====================

@login_required
def ai_assistant_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    if request.user.role != 'admin':
        return JsonResponse({'error': 'Admin access required'}, status=403)

    try:
        data = json.loads(request.body)
        user_input = data.get('message', '')

        if not user_input:
            return JsonResponse({'error': 'No message provided'}, status=400)

        assistant = AIAdminAssistant()
        response = assistant.process(user_input)

        if response['action'] == 'list_courses':
            courses = Course.objects.all()
            response['data']['courses_count'] = courses.count()
            response['data']['courses'] = [{'id': c.id, 'title': c.title, 'level': c.level} for c in courses[:5]]

        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def ai_recommendations(request):
    if request.user.role != 'student':
        return redirect('instructor_dashboard')

    enrolled_courses = request.user.enrolled_courses.all()
    completed_count = in_progress_count = not_started_count = 0

    for course in enrolled_courses:
        progress, _ = Progress.objects.get_or_create(student=request.user, course=course)
        if progress.progress_percentage == 100:
            completed_count += 1
        elif progress.progress_percentage > 0:
            in_progress_count += 1
        else:
            not_started_count += 1

    total = completed_count + in_progress_count + not_started_count
    if total > 0:
        completed_percentage = int((completed_count / total) * 100)
        in_progress_percentage = int((in_progress_count / total) * 100)
        not_started_percentage = int((not_started_count / total) * 100)
        overall_progress = int((completed_count / total) * 100)
    else:
        completed_percentage = in_progress_percentage = not_started_percentage = overall_progress = 0

    recommendations = get_course_recommendations(request.user)

    return render(request, 'ai_dashboard.html', {
        'recommendations': recommendations,
        'completed_percentage': completed_percentage,
        'in_progress_percentage': in_progress_percentage,
        'not_started_percentage': not_started_percentage,
        'progress_percentage': overall_progress
    })


# ==================== INSTRUCTOR STUDENT VIEW ====================

@login_required
@user_passes_test(is_instructor)
def instructor_student_view(request, user_id):
    student = get_object_or_404(User, id=user_id, role='student')

    instructor_courses = Course.objects.filter(instructor=request.user)
    is_enrolled = student.enrolled_courses.filter(id__in=instructor_courses).exists()

    if not is_enrolled and request.user.role != 'admin':
        messages.error(request, 'You can only view students enrolled in your courses.')
        return redirect('instructor_dashboard')

    profile, _created = LearnerProfile.objects.get_or_create(user=student)
    documents = student.documents.all()
    logbooks = student.logbook_entries.all().order_by('-entry_date')[:10]

    course_progress = []
    for course in student.enrolled_courses.all():
        progress, _ = Progress.objects.get_or_create(student=student, course=course)
        course_progress.append({
            'course': course,
            'progress': progress.progress_percentage,
            'completed_lessons': progress.completed_lessons.count(),
            'total_lessons': course.lessons.count()
        })

    certificates = Certificate.objects.filter(student=student)

    return render(request, 'instructor/student_profile_view.html', {
        'student': student,
        'profile': profile,
        'documents': documents,
        'logbooks': logbooks,
        'course_progress': course_progress,
        'certificates': certificates,
        'can_edit': False,
        'is_instructor': True,
    })


# ==================== LEARNER PROFILE MANAGEMENT ====================

@login_required
@user_passes_test(is_admin)
def learner_profile_view(request, user_id):
    learner = get_object_or_404(User, id=user_id)
    profile, _created = LearnerProfile.objects.get_or_create(user=learner)

    AuditLog.objects.create(user=request.user, action='view', resource_type='LearnerProfile', resource_id=user_id, ip_address=get_client_ip(request))

    return render(request, 'admin/learner_profile.html', {
        'learner': learner,
        'profile': profile,
        'courses': Course.objects.filter(status='published'),
        'documents': learner.documents.all(),
        'logbooks': learner.logbook_entries.all()
    })


@login_required
@user_passes_test(is_admin)
def save_learner_profile(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    learner = get_object_or_404(User, id=user_id)
    profile, _created = LearnerProfile.objects.get_or_create(user=learner)

    try:
        data = json.loads(request.body)

        if 'full_name' in data:
            name_parts = data['full_name'].split(' ', 1)
            learner.first_name = name_parts[0]
            learner.last_name = name_parts[1] if len(name_parts) > 1 else ''

        learner.email = data.get('email', learner.email)
        learner.contact_number = data.get('phone_number', learner.contact_number)
        learner.id_number = data.get('id_number', learner.id_number)

        if data.get('date_of_birth'):
            learner.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()

        learner.gender = data.get('gender', learner.gender)
        learner.nationality = data.get('nationality', learner.nationality)
        learner.disability = data.get('disability', learner.disability)
        learner.preferred_language = data.get('preferred_language', learner.preferred_language)
        learner.save()

        profile.physical_address = data.get('physical_address', profile.physical_address)
        profile.emergency_contact_name = data.get('emergency_contact_name', profile.emergency_contact_name)
        profile.emergency_contact_phone = data.get('emergency_contact_phone', profile.emergency_contact_phone)
        profile.host_company_name = data.get('host_company', profile.host_company_name)

        if data.get('mou_start_date'):
            profile.mou_start_date = datetime.strptime(data['mou_start_date'], '%Y-%m-%d').date()
        if data.get('mou_end_date'):
            profile.mou_end_date = datetime.strptime(data['mou_end_date'], '%Y-%m-%d').date()

        profile.supervisor_name = data.get('supervisor_name', profile.supervisor_name)
        profile.supervisor_phone = data.get('supervisor_phone', profile.supervisor_phone)
        profile.supervisor_email = data.get('supervisor_email', profile.supervisor_email)

        if data.get('course_id'):
            profile.current_course_id = int(data['course_id'])
        if data.get('enrollment_date'):
            profile.enrollment_date = datetime.strptime(data['enrollment_date'], '%Y-%m-%d').date()

        profile.assessment_notes = data.get('assessment_notes', profile.assessment_notes)
        profile.certificate_issued = data.get('certificate_issued', False)
        if data.get('certificate_issued_date'):
            profile.certificate_issued_date = datetime.strptime(data['certificate_issued_date'], '%Y-%m-%d').date()

        profile.popia_consent = data.get('popia_consent', profile.popia_consent)
        if profile.popia_consent and not profile.popia_consent_date:
            profile.popia_consent_date = timezone.now()

        profile.save()

        AuditLog.objects.create(user=request.user, action='edit', resource_type='LearnerProfile', resource_id=user_id, ip_address=get_client_ip(request))
        return JsonResponse({'success': True, 'message': 'Profile saved successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@user_passes_test(is_admin)
def upload_learner_document(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    learner = get_object_or_404(User, id=user_id)

    if 'document' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    file = request.FILES['document']
    doc_type = request.POST.get('document_type', 'other')

    allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if file.content_type not in allowed_types:
        return JsonResponse({'error': 'Invalid file type'}, status=400)

    filename = get_valid_filename(file.name)

    doc = LearnerDocument(
        user=learner, document_type=doc_type, title=request.POST.get('title', filename),
        file=file, file_name=filename, file_size=file.size,
        description=request.POST.get('description', ''), uploaded_by=request.user
    )
    doc.save()

    AuditLog.objects.create(user=request.user, action='create', resource_type='LearnerDocument', resource_id=doc.id, ip_address=get_client_ip(request))

    return JsonResponse({'success': True, 'document': {
        'id': doc.id, 'type': doc.get_document_type_display(), 'name': doc.file_name,
        'date': doc.upload_date.strftime('%Y-%m-%d'),
        'size': f"{doc.file_size // 1024} KB" if doc.file_size < 1048576 else f"{doc.file_size // 1048576} MB"
    }})


@login_required
@user_passes_test(is_admin)
def delete_learner_document(request, doc_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    doc = get_object_or_404(LearnerDocument, id=doc_id)

    if doc.file and os.path.isfile(doc.file.path):
        os.remove(doc.file.path)

    doc.delete()
    return JsonResponse({'success': True})


@login_required
@user_passes_test(is_admin)
def download_learner_document(request, doc_id):
    doc = get_object_or_404(LearnerDocument, id=doc_id)

    AuditLog.objects.create(user=request.user, action='download', resource_type='LearnerDocument', resource_id=doc_id, ip_address=get_client_ip(request))

    if doc.file and os.path.isfile(doc.file.path):
        return FileResponse(open(doc.file.path, 'rb'), as_attachment=True, filename=doc.file_name)

    return JsonResponse({'error': 'File not found'}, status=404)


@login_required
@user_passes_test(is_admin)
def add_logbook_entry(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    learner = get_object_or_404(User, id=user_id)
    data = json.loads(request.body)

    entry = LogbookEntry.objects.create(
        user=learner,
        entry_date=datetime.strptime(data.get('entry_date'), '%Y-%m-%d').date(),
        hours_spent=data.get('hours_spent', 0),
        description=data.get('description', ''),
        skills_learned=data.get('skills_learned', '')
    )

    return JsonResponse({'success': True, 'entry': {
        'id': entry.id,
        'date': entry.entry_date.strftime('%Y-%m-%d'),
        'hours': str(entry.hours_spent),
        'description': entry.description,
        'skills': entry.skills_learned
    }})


@login_required
@user_passes_test(is_admin)
def export_learner_report(request, user_id):
    learner = get_object_or_404(User, id=user_id)
    LearnerProfile.objects.get_or_create(user=learner)
    documents = learner.documents.all()
    logbooks = learner.logbook_entries.all().order_by('-entry_date')

    course_progress = []
    for course in learner.enrolled_courses.all():
        progress, _ = Progress.objects.get_or_create(student=learner, course=course)
        course_progress.append({
            'course': course,
            'progress': progress.progress_percentage,
            'completed_lessons': progress.completed_lessons.count(),
            'total_lessons': course.lessons.count()
        })

    doc_rows = ""
    for doc in documents:
        doc_rows += f'<tr><td>{doc.get_document_type_display()}</td><td>{doc.file_name}</td><td>{doc.upload_date.strftime("%Y-%m-%d")}</td><td>{doc.file_size // 1024} KB</td></tr>'

    if not documents:
        doc_rows = '<tr><td colspan="4" style="text-align: center;">No documents uploaded</td></tr>'

    logbook_rows = ""
    for entry in logbooks:
        logbook_rows += f'<tr><td>{entry.entry_date.strftime("%Y-%m-%d")}</td><td>{entry.hours_spent}</td><td>{entry.description[:100]}</td><td>{entry.skills_learned[:100] if entry.skills_learned else "N/A"}</td><td><span style="color: {"green" if entry.supervisor_approved else "orange"};">{"Approved" if entry.supervisor_approved else "Pending"}</span></td></tr>'

    if not logbooks:
        logbook_rows = '<tr><td colspan="5" style="text-align: center;">No logbook entries</td></tr>'

    progress_rows = ""
    for cp in course_progress:
        status = "Completed" if cp['progress'] == 100 else "In Progress" if cp['progress'] > 0 else "Not Started"
        color = "green" if cp['progress'] == 100 else "orange" if cp['progress'] > 0 else "gray"
        progress_rows += f'''
        <tr>
            <td>{cp['course'].title}</td>
            <td><div class="progress-bar"><div class="progress-fill" style="width: {cp['progress']}%">{cp['progress']}%</div></div></td>
            <td>{cp['completed_lessons']} / {cp['total_lessons']}</td>
            <td><span style="color: {color};">{status}</span></td>
        </tr>
        '''

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>QCTO Learner Report - {learner.get_full_name() or learner.username}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; line-height: 1.6; color: #333; }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 3px solid #9f7734; padding-bottom: 20px; }}
        .header h1 {{ color: #9f7734; margin: 0; font-size: 28px; }}
        .section {{ margin-bottom: 25px; page-break-inside: avoid; }}
        .section-title {{ background: #9f7734; color: white; padding: 10px 15px; margin: 20px 0 10px 0; font-size: 18px; font-weight: bold; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        td, th {{ padding: 10px; border: 1px solid #ddd; }}
        th {{ background: #f5f5f5; text-align: left; font-weight: 600; }}
        .info-table td:first-child {{ background: #f9f9f9; font-weight: bold; width: 30%; }}
        .progress-bar {{ background: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden; }}
        .progress-fill {{ background: linear-gradient(90deg, #9f7734, #7a5828); height: 100%; border-radius: 10px; text-align: center; color: white; font-size: 11px; line-height: 20px; }}
        .footer {{ margin-top: 50px; font-size: 10px; text-align: center; border-top: 1px solid #ccc; padding-top: 20px; }}
        .popia-notice {{ background: #f0f9ff; padding: 15px; margin-top: 20px; font-size: 10px; border-left: 4px solid #9f7734; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>QCTO Learner Profile Report</h1>
        <p>Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Generated by: {request.user.get_full_name() or request.user.username}</p>
    </div>
    
    <div class="section">
        <div class="section-title">Section A: Personal Information</div>
        <table class="info-table">
            <tr><td>Full Name:</td><td>{learner.get_full_name() or learner.username}</td></tr>
            <tr><td>ID Number:</td><td>{learner.id_number or 'Not provided'}</td></tr>
            <tr><td>Date of Birth:</td><td>{learner.date_of_birth.strftime('%Y-%m-%d') if learner.date_of_birth else 'Not provided'}</td></tr>
            <tr><td>Email:</td><td>{learner.email}</td></tr>
            <tr><td>Phone:</td><td>{learner.contact_number or 'Not provided'}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">Section B: Course Progress</div>
        <table><thead><tr><th>Course</th><th>Progress</th><th>Lessons</th><th>Status</th></tr></thead><tbody>{progress_rows}</tbody></table>
    </div>
    
    <div class="section">
        <div class="section-title">Section C: Documents</div>
        <table><thead><tr><th>Type</th><th>File Name</th><th>Date</th><th>Size</th></tr></thead><tbody>{doc_rows}</tbody></table>
    </div>
    
    <div class="section">
        <div class="section-title">Section D: Logbook Entries</div>
        <table><thead><tr><th>Date</th><th>Hours</th><th>Description</th><th>Skills</th><th>Status</th></tr></thead><tbody>{logbook_rows}</tbody></table>
    </div>
    
    <div class="footer">
        <div class="popia-notice">
            <strong>POPIA Notice:</strong> This document contains personal information protected under POPIA. Unauthorized disclosure is prohibited.
        </div>
    </div>
</body>
</html>
"""

    AuditLog.objects.create(user=request.user, action='export', resource_type='LearnerProfile', resource_id=user_id, ip_address=get_client_ip(request), details={'format': 'HTML'})

    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="learner_report_{learner.username}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.html"'
    return response


@login_required
@user_passes_test(is_admin)
def get_backup_log_api(request):
    backups = BackupLog.objects.all()[:10]
    return JsonResponse({'backups': [{'timestamp': b.backup_timestamp.isoformat(), 'type': b.backup_type, 'size': b.backup_size, 'status': b.status} for b in backups]})


# ==================== CONTACT FORM / ENQUIRIES ====================

def _enquiry_rate_limited(request):
    key = f"enquiry:{get_client_ip(request)}"
    count = cache.get(key, 0)
    if count >= 5:
        return True
    cache.set(key, count + 1, 3600)
    return False


def contact_form_submit(request):
    """Handles the contact form AND programme 'enquire / join / partner' forms.
    Saves the enquiry, emails it to settings.CONTACT_EMAIL (hello@malitinne.co.za)
    and sends the visitor an acknowledgement."""
    if request.method != 'POST':
        return redirect('contact')

    back = request.POST.get('return_to') or ''
    if not url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}):
        back = reverse('contact')

    # Honeypot: real people never fill in this hidden field
    if request.POST.get('website'):
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect(back)

    first_name = (request.POST.get('first_name') or '').strip()
    last_name = (request.POST.get('last_name') or '').strip()
    name = (request.POST.get('name') or f"{first_name} {last_name}").strip()
    email = (request.POST.get('email') or '').strip()
    message = (request.POST.get('message') or '').strip()

    try:
        validate_email(email)
        email_ok = True
    except ValidationError:
        email_ok = False

    if not name or not email_ok or not message:
        messages.error(request, 'Please fill in your name, a valid email address and your message.')
        return redirect(back)
    if not request.POST.get('popia_consent'):
        messages.error(request, 'Please tick the box to allow us to use your details to respond to you (POPIA).')
        return redirect(back)
    if _enquiry_rate_limited(request):
        messages.error(request, 'You have sent several messages already. Please wait a while or call us on 073 931 7923.')
        return redirect(back)

    programme = None
    if request.POST.get('programme'):
        programme = Programme.objects.filter(pk=request.POST.get('programme'), is_published=True).first()
    enquiry_type = request.POST.get('enquiry_type') or ('programme' if programme else 'general')
    if enquiry_type not in dict(Enquiry.TYPE_CHOICES):
        enquiry_type = 'general'

    enquiry = Enquiry.objects.create(
        enquiry_type=enquiry_type, programme=programme, name=name[:150], email=email,
        phone=(request.POST.get('phone') or '').strip()[:30],
        organisation=(request.POST.get('organisation') or '').strip()[:200],
        client_type=(request.POST.get('client_type') or '').strip()[:60],
        message=message[:5000], popia_consent=True, ip_address=get_client_ip(request),
    )
    enquiry.email_sent = send_enquiry_notification(enquiry)
    enquiry.save(update_fields=['email_sent'])
    send_enquiry_acknowledgement(enquiry)

    messages.success(request, 'Thank you! Your message has been sent to our team. We will respond within two working days.')
    return redirect(back)


# ==================== APPROVALS (ADMIN) ====================

def _safe_next(request, fallback):
    nxt = request.POST.get('next') or ''
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return nxt
    return fallback

def _is_admin_user(user):
    return user.is_authenticated and (user.is_superuser or getattr(user, 'role', '') == 'admin')


@login_required
@user_passes_test(_is_admin_user)
def pending_approvals(request):
    pending_users = User.objects.filter(role='student', is_approved=False, is_active=True).order_by('date_joined')
    pending_enrolments = EnrollmentRequest.objects.filter(status='pending').select_related('student', 'course')
    recently_approved = User.objects.filter(role='student', is_approved=True, approved_at__isnull=False).order_by('-approved_at')[:10]
    return render(request, 'approvals.html', {
        'pending_users': pending_users, 'pending_enrolments': pending_enrolments, 'recently_approved': recently_approved,
        'courses': Course.objects.filter(status='published').order_by('title'),
    })


@login_required
@user_passes_test(_is_admin_user)
def approve_user(request, user_id):
    if request.method != 'POST':
        return redirect('pending_approvals')
    learner = get_object_or_404(User, id=user_id, role='student')
    learner.is_approved = True
    learner.is_active = True
    learner.approved_by = request.user
    learner.save()  # save() sends the "you're approved — log in here" email
    course_id = request.POST.get('course')
    if course_id:
        course = Course.objects.filter(id=course_id).first()
        if course:
            req, _ = EnrollmentRequest.objects.get_or_create(student=learner, course=course)
            req.approve(by=request.user)
    AuditLog.objects.create(user=request.user, action='edit', resource_type='user_approval', resource_id=learner.id,
                            ip_address=get_client_ip(request), details={'approved': True})
    messages.success(request, f'{learner.get_full_name() or learner.username} approved. A login link was emailed to {learner.email}.')
    return redirect(_safe_next(request, 'pending_approvals'))


@login_required
@user_passes_test(_is_admin_user)
def decline_user(request, user_id):
    if request.method != 'POST':
        return redirect('pending_approvals')
    learner = get_object_or_404(User, id=user_id, role='student', is_approved=False)
    reason = (request.POST.get('reason') or '').strip()[:500]
    learner.is_active = False
    learner.save(update_fields=['is_active'])
    send_account_declined_email(learner, reason)
    AuditLog.objects.create(user=request.user, action='edit', resource_type='user_approval', resource_id=learner.id,
                            ip_address=get_client_ip(request), details={'approved': False, 'reason': reason})
    messages.info(request, f'Registration for {learner.username} was declined and the learner was notified.')
    return redirect('pending_approvals')


@login_required
@user_passes_test(_is_admin_user)
def decide_enrollment(request, request_id):
    if request.method != 'POST':
        return redirect('pending_approvals')
    req = get_object_or_404(EnrollmentRequest, id=request_id)
    if request.POST.get('decision') == 'approve':
        req.approve(by=request.user)
        messages.success(request, f'{req.student.username} now has access to {req.course.title}.')
    else:
        req.decline(by=request.user)
        messages.info(request, f'Enrolment request from {req.student.username} declined.')
    send_enrollment_decision(req)
    return redirect(_safe_next(request, 'pending_approvals'))


# ==================== OPPORTUNITIES ====================

def opportunities_list(request):
    today = timezone.now().date()

    opportunities = Opportunity.objects.filter(
        status='published',
        opening_date__lte=today,
        closing_date__gte=today
    ).exclude(positions_filled__gte=F('available_positions'))

    opportunity_type = request.GET.get('type')
    if opportunity_type:
        opportunities = opportunities.filter(opportunity_type=opportunity_type)

    search_query = request.GET.get('search')
    if search_query:
        opportunities = opportunities.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    return render(request, 'malitinne/opportunities_list.html', {
        'opportunities': opportunities,
        'opportunity_types': Opportunity.OPPORTUNITY_TYPES,
        'today': today,
    })


def apply_for_opportunity(request, opportunity_id):
    opportunity = get_object_or_404(Opportunity, id=opportunity_id)

    if not opportunity.is_open:
        messages.error(request, 'This opportunity is no longer accepting applications. It has expired or been filled.')
        return redirect('opportunities')

    if request.method == 'POST':
        try:
            if not opportunity.is_open:
                messages.error(request, 'This opportunity closed while you were applying. Please check other opportunities.')
                return redirect('opportunities')

            application = Application.objects.create(
                opportunity=opportunity,
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                phone_number=request.POST.get('phone_number'),
                alternative_phone=request.POST.get('alternative_phone', ''),
                id_number=request.POST.get('id_number'),
                date_of_birth=request.POST.get('date_of_birth'),
                gender=request.POST.get('gender', ''),
                race=request.POST.get('race', ''),
                disability=request.POST.get('disability', ''),
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                province=request.POST.get('province'),
                postal_code=request.POST.get('postal_code', ''),
                highest_qualification=request.POST.get('highest_qualification'),
                institution=request.POST.get('institution'),
                year_completed=request.POST.get('year_completed'),
                field_of_study=request.POST.get('field_of_study', ''),
                work_experience=request.POST.get('work_experience', ''),
                skills=request.POST.get('skills'),
                hear_about_us=request.POST.get('hear_about_us', ''),
                additional_info=request.POST.get('additional_info', ''),
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )

            if request.FILES.get('cv'):
                application.cv = request.FILES['cv']
            if request.FILES.get('cover_letter'):
                application.cover_letter = request.FILES['cover_letter']
            if request.FILES.get('id_document'):
                application.id_document = request.FILES['id_document']
            if request.FILES.get('qualifications'):
                application.qualifications = request.FILES['qualifications']

            application.save()

            try:
                send_mail(
                    subject=f'Application Received - {opportunity.title}',
                    message=f'Dear {application.first_name},\n\nThank you for applying for {opportunity.title}.\n\nYour application number is: {application.application_number}\n\nWe will contact you regarding the status of your application.\n\nRegards,\nMalitinne Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[application.email],
                    fail_silently=True
                )
            except Exception as exc:
                logger.warning("Failed to send application confirmation email: %s", exc)

            admin_emails = User.objects.filter(role='admin', is_active=True).values_list('email', flat=True)
            for email in admin_emails:
                try:
                    send_mail(
                        subject=f'New Application: {opportunity.title}',
                        message=f'A new application has been submitted for {opportunity.title} by {application.full_name}.\n\nApplication Number: {application.application_number}\n\nLogin to admin panel to review.',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=True
                    )
                except Exception as exc:
                    logger.warning("Failed to send admin application notification: %s", exc)

            request.session['submitted_application'] = application.application_number
            messages.success(request, f'Application submitted successfully! Your reference number is {application.application_number}')
            return redirect('application_success', application_number=application.application_number)
        except Exception:
            logger.exception("Application submission failed")
            messages.error(request, 'Sorry, we could not submit your application. Please check your details and try again.')

    return render(request, 'malitinne/apply_dynamic.html', {'opportunity': opportunity})


def application_success(request, application_number):
    # POPIA: only the person who just submitted (same browser session) or staff may view it
    allowed = request.session.get('submitted_application') == application_number or (
        request.user.is_authenticated and (request.user.is_staff or request.user.role == 'admin'))
    if not allowed:
        raise Http404("Application not found")
    application = get_object_or_404(Application, application_number=application_number)
    return render(request, 'malitinne/application_success.html', {'application': application})


# ==================== LEARNER MANAGEMENT HUB ====================

@staff_member_required
def learner_management_hub(request):
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    project_filter = request.GET.get('project', '')
    department_filter = request.GET.get('department', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    sort_by = request.GET.get('sort', '-date_joined')
    page = request.GET.get('page', 1)

    learners = User.objects.filter(Q(role='student') | Q(role='learner')).select_related('learner_profile').prefetch_related('enrolled_courses', 'progress', 'certificates')

    if search_query:
        learners = learners.filter(
            Q(username__icontains=search_query) | Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) | Q(email__icontains=search_query) |
            Q(id_number__icontains=search_query) | Q(phone__icontains=search_query)
        )

    if status_filter:
        if status_filter == 'active':
            learners = learners.filter(is_active=True, is_approved=True)
        elif status_filter == 'inactive':
            learners = learners.filter(is_active=False)
        elif status_filter == 'pending':
            learners = learners.filter(is_approved=False, is_active=True)
        elif status_filter == 'blocked':
            learners = learners.filter(is_active=False, is_approved=True)

    if project_filter:
        learners = learners.filter(enrolled_courses__id=project_filter)
    if department_filter:
        learners = learners.filter(department=department_filter)
    if date_from:
        learners = learners.filter(date_joined__gte=date_from)
    if date_to:
        learners = learners.filter(date_joined__lte=date_to)

    learners = learners.annotate(
        course_count=Count('enrolled_courses', distinct=True),
        certificate_count=Count('certificates', distinct=True)
    ).order_by(sort_by)

    paginator = Paginator(learners, 50)
    page_obj = paginator.get_page(page)

    stats = {
        'total_learners': User.objects.filter(role__in=['student', 'learner']).count(),
        'active_learners': User.objects.filter(role__in=['student', 'learner'], is_active=True, is_approved=True).count(),
        'pending_approval': User.objects.filter(role__in=['student', 'learner'], is_approved=False).count(),
        'inactive_learners': User.objects.filter(role__in=['student', 'learner'], is_active=False).count(),
        'total_projects': Course.objects.filter(status='published').count(),
    }

    return render(request, 'learner_management_hub.html', {
        'learners': page_obj,
        'stats': stats,
        'projects': Course.objects.filter(status='published').values_list('id', 'title'),
        'departments': User.DEPARTMENT_CHOICES,
        'search_query': search_query,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'department_filter': department_filter,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'total_learners_count': learners.count(),
        'notification_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    })


@staff_member_required
def learner_detail_view(request, user_id):
    learner = get_object_or_404(User.objects.filter(role__in=['student', 'learner']), id=user_id)

    progress_data = Progress.objects.filter(student=learner).select_related('course')
    enrollments = learner.enrolled_courses.all()
    certificates = Certificate.objects.filter(student=learner).select_related('course')

    assessments = []
    if hasattr(learner, 'sign_offs'):
        assessments = learner.sign_offs.all().select_related('module', 'assessor')

    logbook_entries = []
    if hasattr(learner, 'logbook_entries'):
        logbook_entries = learner.logbook_entries.all().order_by('-entry_date')[:20]

    overall_progress = 0
    if progress_data.exists():
        total_courses = progress_data.count()
        completed_courses = progress_data.filter(completed_at__isnull=False).count()
        overall_progress = int((completed_courses / total_courses) * 100) if total_courses > 0 else 0

    profile_completion = 0
    if hasattr(learner, 'learner_profile'):
        profile_completion = learner.learner_profile.get_completion_percentage()

    return render(request, 'learner_detail.html', {
        'learner': learner,
        'progress_data': progress_data,
        'enrollments': enrollments,
        'certificates': certificates,
        'assessments': assessments,
        'logbook_entries': logbook_entries,
        'overall_progress': overall_progress,
        'profile_completion': profile_completion,
        'notification_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    })


@login_required
def ai_query_count_api(request):
    count = 0
    return JsonResponse({'count': count})


@login_required
def discussions_list(request):
    from core.models import ForumTopic
    topics = ForumTopic.objects.all().order_by('-created_at')
    return render(request, 'discussions_list.html', {
        'topics': topics,
        'notification_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    })


@staff_member_required
def bulk_upload_learners(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            file = request.FILES['file']

            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            required_columns = ['username', 'email', 'first_name', 'last_name']
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                return JsonResponse({'success': False, 'error': f'Missing columns: {", ".join(missing_cols)}'}, status=400)

            results = {'success': 0, 'failed': 0, 'errors': [], 'created': [], 'updated': []}

            for index, row in df.iterrows():
                try:
                    username = str(row.get('username', '')).strip()
                    email = str(row.get('email', '')).strip()

                    if not username or not email:
                        results['failed'] += 1
                        results['errors'].append(f'Row {index+2}: Missing username or email')
                        continue

                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'first_name': str(row.get('first_name', '')).strip()[:150],
                            'last_name': str(row.get('last_name', '')).strip()[:150],
                            'role': 'student',
                            'is_active': True,
                            'is_approved': True,
                        }
                    )

                    if not created:
                        user.email = email
                        user.first_name = str(row.get('first_name', '')).strip()[:150]
                        user.last_name = str(row.get('last_name', '')).strip()[:150]
                        user.save()
                        results['updated'].append(username)
                    else:
                        results['created'].append(username)

                    if 'phone' in df.columns:
                        user.phone = str(row.get('phone', '')).strip()[:20]

                    if 'id_number' in df.columns:
                        user.id_number = str(row.get('id_number', '')).strip()[:20]

                    if 'department' in df.columns and row.get('department'):
                        dept = str(row.get('department', '')).strip()
                        dept_choices = dict(User.DEPARTMENT_CHOICES)
                        if dept in dept_choices:
                            user.department = dept

                    if 'date_of_birth' in df.columns and pd.notna(row.get('date_of_birth')):
                        try:
                            user.date_of_birth = pd.to_datetime(row['date_of_birth']).date()
                        except (ValueError, TypeError):
                            pass

                    user.save()

                    if not hasattr(user, 'learner_profile'):
                        LearnerProfile.objects.create(user=user)

                    results['success'] += 1

                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f'Row {index+2}: {e!s}')

            return JsonResponse({'success': True, 'results': results})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)


@staff_member_required
def export_learners(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    learners = User.objects.filter(role__in=['student', 'learner'])

    if search_query:
        learners = learners.filter(
            Q(username__icontains=search_query) | Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) | Q(email__icontains=search_query)
        )

    if status_filter:
        if status_filter == 'active':
            learners = learners.filter(is_active=True, is_approved=True)
        elif status_filter == 'inactive':
            learners = learners.filter(is_active=False)
        elif status_filter == 'pending':
            learners = learners.filter(is_approved=False)

    wb = Workbook()
    ws = wb.active
    ws.title = "Learners"

    ws.append(['Username', 'Email', 'First Name', 'Last Name', 'Phone', 'ID Number', 'Department', 'Status', 'Approved', 'Date Joined', 'Last Login', 'Courses Enrolled', 'Certificates'])

    for learner in learners:
        ws.append([
            learner.username, learner.email, learner.first_name, learner.last_name,
            learner.phone or '', learner.id_number or '', learner.get_department_display() or '',
            'Active' if learner.is_active else 'Inactive',
            'Yes' if learner.is_approved else 'No',
            learner.date_joined.strftime('%Y-%m-%d') if learner.date_joined else '',
            learner.last_login.strftime('%Y-%m-%d %H:%M') if learner.last_login else '',
            learner.enrolled_courses.count(), learner.certificates.count(),
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=learners_export.xlsx'
    wb.save(response)
    return response


# ==================== OBSERVATION CHECKLIST ====================

@login_required
def get_observation_checklist(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.user.role == 'student' and request.user not in lesson.course.students.all():
        return JsonResponse({'error': 'Not enrolled'}, status=403)

    practical_modules = lesson.course.learning_modules.filter(module_type='practical')
    if not practical_modules.exists():
        return JsonResponse({'checklist': [], 'message': 'No practical checklist available'})

    module = practical_modules.first()
    checklist_items = module.checklist_items.all()

    results = {}
    if request.user.role == 'student':
        for result in StudentChecklistResult.objects.filter(student=request.user, item__in=checklist_items):
            results[result.item.id] = result.is_competent

    return JsonResponse({
        'module_id': module.id,
        'module_title': module.title,
        'checklist': [{'id': item.id, 'description': item.description, 'order': item.order, 'is_competent': results.get(item.id, False)} for item in checklist_items]
    })


@login_required
@user_passes_test(is_instructor)
def assess_checklist_item(request, item_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    item = get_object_or_404(ObservationChecklistItem, id=item_id)
    student_id = request.POST.get('student_id')
    is_competent = request.POST.get('is_competent') == 'true'
    comments = request.POST.get('comments', '')

    student = get_object_or_404(User, id=student_id, role='student')

    if student not in item.module.course.students.all():
        return JsonResponse({'error': 'Student not in this course'}, status=403)

    StudentChecklistResult.objects.update_or_create(
        student=student, item=item,
        defaults={'is_competent': is_competent, 'assessed_by': request.user, 'assessed_at': timezone.now(), 'comments': comments}
    )

    all_items = item.module.checklist_items.all()
    all_competent = all(
        StudentChecklistResult.objects.filter(student=student, item=i, is_competent=True).exists()
        for i in all_items
    )

    if all_competent:
        AssessorSignOff.objects.update_or_create(
            student=student, module=item.module,
            defaults={'assessor': request.user, 'outcome': 'competent', 'comments': f'Auto-signed off. {comments}', 'signed_at': timezone.now()}
        )
        return JsonResponse({'success': True, 'is_competent': is_competent, 'module_completed': True, 'message': f'Module {item.module.title} is now COMPETENT!'})

    return JsonResponse({'success': True, 'is_competent': is_competent, 'module_completed': False, 'message': f'Checklist item marked as {"competent" if is_competent else "not yet competent"}'})


@login_required
def get_module_competency_status(request, module_id):
    module = get_object_or_404(LearningModule, id=module_id)
    student_id = request.GET.get('student_id')

    if request.user.role == 'instructor' and student_id:
        student = get_object_or_404(User, id=student_id, role='student')
    elif request.user.role == 'student':
        student = request.user
    else:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    signoff = AssessorSignOff.objects.filter(student=student, module=module).first()
    checklist_items = module.checklist_items.all()
    completed_items = StudentChecklistResult.objects.filter(student=student, item__in=checklist_items, is_competent=True).count()
    evidence = ModuleEvidence.objects.filter(student=student, module=module)

    return JsonResponse({
        'module_id': module.id,
        'module_title': module.title,
        'module_type': module.module_type,
        'signoff_status': signoff.outcome if signoff else 'not_assessed',
        'checklist_total': checklist_items.count(),
        'checklist_completed': completed_items,
        'evidence_count': evidence.count(),
        'evidence_items': [{'id': e.id, 'title': e.title, 'verified': e.is_verified} for e in evidence],
        'is_competent': signoff and signoff.outcome == 'competent'
    })


# ==================== MODULE EVIDENCE ====================

@login_required
def upload_module_evidence(request, module_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    module = get_object_or_404(LearningModule, id=module_id)

    if request.user.role == 'student' and request.user not in module.course.students.all():
        return JsonResponse({'error': 'Not enrolled in this course'}, status=403)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    file = request.FILES['file']
    title = request.POST.get('title', file.name)
    description = request.POST.get('description', '')

    student = request.user if request.user.role == 'student' else None
    student_id = request.POST.get('student_id')
    if request.user.role == 'instructor':
        if not student_id:
            return JsonResponse({'error': 'Student is required'}, status=400)
        student = get_object_or_404(User, id=student_id, role='student')
        if module.course.instructor != request.user:
            return JsonResponse({'error': 'You do not own this course'}, status=403)
        if student not in module.course.students.all():
            return JsonResponse({'error': 'Student not in this course'}, status=403)

    allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if file.content_type not in allowed_types:
        return JsonResponse({'error': 'Invalid file type. PDF, DOC, or images only.'}, status=400)

    evidence = ModuleEvidence.objects.create(
        student=student, module=module, title=title, file=file,
        description=description, uploaded_at=timezone.now()
    )

    return JsonResponse({'success': True, 'evidence': {
        'id': evidence.id, 'title': evidence.title,
        'file_url': evidence.file.url if evidence.file else None,
        'uploaded_at': evidence.uploaded_at.strftime('%Y-%m-%d %H:%M'),
        'is_verified': evidence.is_verified
    }})


@login_required
def delete_module_evidence(request, evidence_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    evidence = get_object_or_404(ModuleEvidence, id=evidence_id)

    if request.user.role == 'student' and evidence.student != request.user:
        return JsonResponse({'error': 'Cannot delete other student\'s evidence'}, status=403)

    if request.user.role == 'instructor' and evidence.module.course.instructor != request.user:
        return JsonResponse({'error': 'You do not own this course'}, status=403)

    if evidence.file and os.path.isfile(evidence.file.path):
        os.remove(evidence.file.path)

    evidence.delete()
    return JsonResponse({'success': True})


@login_required
@user_passes_test(is_instructor)
def verify_module_evidence(request, evidence_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    evidence = get_object_or_404(ModuleEvidence, id=evidence_id)
    is_verified = request.POST.get('is_verified') == 'true'

    evidence.is_verified = is_verified
    evidence.verified_by = request.user
    evidence.verified_at = timezone.now() if is_verified else None
    evidence.save()

    return JsonResponse({'success': True, 'is_verified': evidence.is_verified, 'verified_by': request.user.username, 'verified_at': evidence.verified_at.strftime('%Y-%m-%d %H:%M') if evidence.verified_at else None})


# ==================== PORTFOLIO ====================

@login_required
def get_portfolio_status(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student_id = request.GET.get('student_id')

    if request.user.role == 'instructor' and student_id:
        student = get_object_or_404(User, id=student_id, role='student')
    elif request.user.role == 'student':
        student = request.user
    else:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    portfolio, _created = PortfolioOfEvidence.objects.get_or_create(student=student, course=course)
    modules = course.learning_modules.filter(module_type__in=['practical', 'work_experience'])

    evidence_counts = {module.id: ModuleEvidence.objects.filter(student=student, module=module).count() for module in modules}
    signoffs = {signoff.module_id: signoff.outcome for signoff in AssessorSignOff.objects.filter(student=student, module__in=modules)}

    return JsonResponse({
        'portfolio_id': portfolio.id,
        'status': portfolio.status,
        'submitted_at': portfolio.submitted_at.strftime('%Y-%m-%d %H:%M') if portfolio.submitted_at else None,
        'reviewed_at': portfolio.reviewed_at.strftime('%Y-%m-%d %H:%M') if portfolio.reviewed_at else None,
        'notes': portfolio.notes,
        'modules': [{'id': m.id, 'title': m.title, 'module_type': m.module_type, 'evidence_count': evidence_counts.get(m.id, 0), 'signoff_status': signoffs.get(m.id, 'not_assessed')} for m in modules]
    })


@login_required
def submit_portfolio(request, course_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if request.user.role != 'student':
        return JsonResponse({'error': 'Only students can submit portfolios'}, status=403)

    course = get_object_or_404(Course, id=course_id)
    portfolio, _created = PortfolioOfEvidence.objects.get_or_create(student=request.user, course=course)

    missing_signoffs = []
    for module in course.learning_modules.filter(module_type='practical'):
        if not AssessorSignOff.objects.filter(student=request.user, module=module, outcome='competent').exists():
            missing_signoffs.append(f"Practical: {module.title}")

    for module in course.learning_modules.filter(module_type='work_experience'):
        if not AssessorSignOff.objects.filter(student=request.user, module=module, outcome='competent').exists():
            missing_signoffs.append(f"Work Experience: {module.title}")

    if missing_signoffs:
        return JsonResponse({'success': False, 'error': 'Cannot submit portfolio until all modules are signed off as competent', 'missing_signoffs': missing_signoffs}, status=400)

    portfolio.status = 'submitted'
    portfolio.submitted_at = timezone.now()
    portfolio.save()

    for instructor in User.objects.filter(role__in=['instructor', 'admin']):
        send_notification(instructor, f'Portfolio Submitted - {course.title}', f'{request.user.get_full_name()} has submitted their portfolio for review', f'/admin/learner/{request.user.id}/')

    return JsonResponse({'success': True, 'message': 'Portfolio submitted for assessment', 'submitted_at': portfolio.submitted_at.strftime('%Y-%m-%d %H:%M')})


# ==================== IISA ====================

@login_required
def get_iisa_assessments(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assessments = course.summative_assessments.all()
    results = {}

    if request.user.role == 'student':
        for assessment in assessments:
            submission = SummativeAssessmentSubmission.objects.filter(assessment=assessment, student=request.user).first()
            if submission:
                results[assessment.id] = {'submitted': True, 'result': submission.result, 'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M'), 'feedback': submission.feedback}
            else:
                results[assessment.id] = {'submitted': False}

    return JsonResponse({'assessments': [{'id': a.id, 'title': a.title, 'instructions': a.instructions, 'due_date': a.due_date.strftime('%Y-%m-%d %H:%M'), 'status': results.get(a.id, {'submitted': False})} for a in assessments]})


@login_required
def submit_iisa(request, assessment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if request.user.role != 'student':
        return JsonResponse({'error': 'Only students can submit assessments'}, status=403)

    assessment = get_object_or_404(SummativeAssessment, id=assessment_id)

    existing = SummativeAssessmentSubmission.objects.filter(assessment=assessment, student=request.user).first()
    if existing:
        return JsonResponse({'error': 'You have already submitted this assessment'}, status=400)

    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    submission = SummativeAssessmentSubmission.objects.create(
        assessment=assessment, student=request.user, file_upload=request.FILES['file'],
        submitted_at=timezone.now(), result='pending'
    )

    return JsonResponse({'success': True, 'message': 'IISA assessment submitted successfully', 'submission_id': submission.id, 'submitted_at': submission.submitted_at.strftime('%Y-%m-%d %H:%M')})


@login_required
@user_passes_test(is_instructor)
def grade_iisa(request, assessment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    assessment = get_object_or_404(SummativeAssessment, id=assessment_id)
    student = get_object_or_404(User, id=request.POST.get('student_id'), role='student')
    result = request.POST.get('result')
    feedback = request.POST.get('feedback', '')

    submission = get_object_or_404(SummativeAssessmentSubmission, assessment=assessment, student=student)

    submission.result = result
    submission.assessed_by = request.user
    submission.assessed_at = timezone.now()
    submission.feedback = feedback
    submission.save()

    if result == 'competent':
        all_assessments = assessment.course.summative_assessments.all()
        all_passed = all(SummativeAssessmentSubmission.objects.filter(assessment=a, student=student, result='competent').exists() for a in all_assessments)

        if all_passed:
            progress = Progress.objects.get(student=student, course=assessment.course)
            if progress.progress_percentage == 100:
                _certificate, created = Certificate.objects.get_or_create(student=student, course=assessment.course)
                if created:
                    send_notification(student, f'Qualification Complete! - {assessment.course.title}', 'Congratulations! You have successfully completed all requirements including the IISA.', '/certificates/')

    return JsonResponse({'success': True, 'result': result, 'assessed_by': request.user.username, 'assessed_at': submission.assessed_at.strftime('%Y-%m-%d %H:%M')})


# ==================== ASSESSOR SIGN-OFF ====================

@login_required
@user_passes_test(is_instructor)
def assessor_signoff(request, module_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    module = get_object_or_404(LearningModule, id=module_id)
    student = get_object_or_404(User, id=request.POST.get('student_id'), role='student')
    outcome = request.POST.get('outcome')
    comments = request.POST.get('comments', '')

    if module.module_type == 'practical':
        checklist_items = module.checklist_items.all()
        if checklist_items.exists():
            completed = StudentChecklistResult.objects.filter(student=student, item__in=checklist_items, is_competent=True).count()
            if outcome == 'competent' and completed < checklist_items.count():
                return JsonResponse({'error': f'Cannot sign off as competent. Only {completed}/{checklist_items.count()} checklist items completed.'}, status=400)

    signoff, _created = AssessorSignOff.objects.update_or_create(
        student=student, module=module,
        defaults={'assessor': request.user, 'outcome': outcome, 'comments': comments, 'signed_at': timezone.now()}
    )

    _progress, _ = Progress.objects.get_or_create(student=student, course=module.course)

    return JsonResponse({'success': True, 'outcome': outcome, 'signed_at': signoff.signed_at.strftime('%Y-%m-%d %H:%M'), 'message': f'Module signed off as {outcome.replace("_", " ").upper()}'})


# ==================== ERROR HANDLERS ====================

def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)
