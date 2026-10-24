"""Staff portal (/staff-portal/...): dashboard, tenders & grants, calendar, report,
shared drive and discussions. Staff = users with role admin or instructor."""
import calendar as pycalendar
import csv
import logging
import os
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
from functools import wraps

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import get_valid_filename
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from . import tender_intel
from .models import (
    BidProfile,
    DocumentCategory,
    DocumentDownloadLog,
    ForumTopic,
    Meeting,
    Notification,
    SharedDocument,
    StaffAnnouncement,
    Task,
    TenderOpportunity,
    TenderSource,
    User,
)

logger = logging.getLogger(__name__)

ALLOWED_UPLOAD_EXT = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'webp', 'txt', 'zip'}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
INLINE_TYPES = {'pdf': 'application/pdf', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                'webp': 'image/webp', 'gif': 'image/gif', 'txt': 'text/plain; charset=utf-8'}
ICS_SALT = 'staff-portal-calendar'


# =========================================================================== access
def staff_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if getattr(request.user, 'role', None) not in ('admin', 'instructor'):
            messages.error(request, 'The staff portal is for Malitinne staff only.')
            return redirect('student_dashboard')
        return view(request, *args, **kwargs)
    return wrapper


def admin_only(view):
    @wraps(view)
    @staff_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'admin':
            return HttpResponseForbidden('Only administrators can do this.')
        return view(request, *args, **kwargs)
    return wrapper


def _visible_documents(user):
    """POPIA: management/sensitive files are for admins only; private files for their owner."""
    qs = SharedDocument.objects.select_related('category', 'uploaded_by')
    if user.role == 'admin':
        return qs.filter(Q(visibility__in=['all_staff', 'management', 'department']) | Q(uploaded_by=user))
    return qs.filter(
        (Q(visibility='all_staff') & Q(is_sensitive=False))
        | Q(visibility='department', allowed_departments=user)
        | Q(uploaded_by=user)
    ).distinct()


def _can_see(user, doc):
    return _visible_documents(user).filter(pk=doc.pk).exists()


def _shell(request, active, **ctx):
    """Context shared by every staff page (sidebar badges, user menu)."""
    today = timezone.localdate()
    open_qs = TenderOpportunity.objects.filter(status__in=TenderOpportunity.ACTIVE_STATUSES)
    ctx.update({
        'active_nav': active,
        'today': today,
        'nav_urgent_tenders': open_qs.filter(closing_date__gte=today, closing_date__lte=today + timedelta(days=7))
                                     .exclude(fit_verdict='low').count(),
        'nav_expiring_docs': SharedDocument.objects.filter(is_current=True, expiry_date__lte=today + timedelta(days=30))
                                                   .exclude(doc_type='other').count(),
        'nav_pending_approvals': (User.objects.filter(role='student', is_approved=False, is_active=True).count()
                                  if request.user.role == 'admin' else 0),
        'notification_count': Notification.objects.filter(user=request.user, is_read=False).count(),
    })
    return ctx


# =========================================================================== calendar events
def _events(user, start, end):
    """Everything with a date between start and end (inclusive), as plain dicts."""
    events = []
    tenders = TenderOpportunity.objects.exclude(status__in=['lost', 'declined', 'expired'])
    for t in tenders.filter(closing_date__range=(start, end)):
        events.append({'date': t.closing_date, 'time': t.closing_time, 'kind': 'closing',
                       'title': f'Closes: {t.title}', 'url': t.get_absolute_url(), 'tone': t.fit_verdict, 'obj': t})
    for t in tenders.filter(status__in=TenderOpportunity.ACTIVE_STATUSES, closing_date__range=(start, end + timedelta(days=6))):
        d = t.internal_deadline
        if d and start <= d <= end and t.fit_verdict != 'low':
            events.append({'date': d, 'time': None, 'kind': 'deadline', 'title': f'Bid ready: {t.title}',
                           'url': t.get_absolute_url(), 'tone': t.fit_verdict, 'obj': t})
    for t in tenders.filter(briefing_at__date__range=(start, end)):
        local = timezone.localtime(t.briefing_at)
        events.append({'date': local.date(), 'time': local.time(), 'kind': 'briefing',
                       'title': ('Compulsory briefing: ' if t.briefing_compulsory else 'Briefing: ') + t.title,
                       'url': t.get_absolute_url(), 'tone': 'briefing', 'obj': t})
    for t in tenders.filter(follow_up_date__range=(start, end)):
        events.append({'date': t.follow_up_date, 'time': None, 'kind': 'follow_up', 'title': f'Follow up: {t.title}',
                       'url': t.get_absolute_url(), 'tone': 'follow_up', 'obj': t})
    for doc in _visible_documents(user).filter(is_current=True, expiry_date__range=(start, end)):
        events.append({'date': doc.expiry_date, 'time': None, 'kind': 'expiry', 'title': f'Expires: {doc.title}',
                       'url': reverse('shared_drive') + f'?type={doc.doc_type}', 'tone': 'expiry', 'obj': doc})
    meetings = Meeting.objects.filter(Q(organizer=user) | Q(attendees=user), start_time__date__range=(start, end)).distinct()
    for m in meetings:
        local = timezone.localtime(m.start_time)
        events.append({'date': local.date(), 'time': local.time(), 'kind': 'meeting', 'title': m.title,
                       'url': '', 'tone': 'meeting', 'obj': m})
    for task in Task.objects.filter(assigned_to=user, due_date__range=(start, end)).exclude(status='done'):
        events.append({'date': task.due_date, 'time': None, 'kind': 'task', 'title': f'Task: {task.title}',
                       'url': '', 'tone': 'task', 'obj': task})
    for e in events:  # calendar cells are narrow: the coloured dot already says what kind of date it is
        e['short'] = e['title'].split(': ', 1)[-1] if e['kind'] != 'meeting' else e['title']
    order = {'briefing': 0, 'meeting': 1, 'closing': 2, 'deadline': 3, 'expiry': 4, 'follow_up': 5, 'task': 6}
    events.sort(key=lambda e: (e['date'], e['time'] or datetime.min.time(), order.get(e['kind'], 9)))
    return events


# =========================================================================== dashboard
@staff_required
def staff_portal(request):
    from .portal_helpers import calculate_project_health, delivery_projects, get_overall_stats, get_urgent_actions
    today = timezone.localdate()
    open_qs = TenderOpportunity.objects.filter(status__in=TenderOpportunity.ACTIVE_STATUSES).exclude(closing_date__lt=today)
    vault = tender_intel.document_vault()
    vault_rows = _vault_rows(vault)
    projects_health = [h for h in (calculate_project_health(p) for p in delivery_projects()[:12]) if h['learners']]
    projects_health.sort(key=lambda h: {'high': 0, 'medium': 1, 'low': 2}.get(h['risk'], 3))
    ctx = _shell(request, 'dashboard',
        best_matches=open_qs.exclude(fit_verdict='low').order_by('-ai_relevance_score', 'closing_date')[:6],
        kpi_strong=open_qs.filter(fit_verdict='strong').count(),
        kpi_closing=open_qs.filter(closing_date__lte=today + timedelta(days=7)).exclude(fit_verdict='low').count(),
        kpi_in_progress=TenderOpportunity.objects.filter(status__in=['preparing', 'applied', 'shortlisted']).count(),
        kpi_vault_ready=sum(1 for r in vault_rows if r['state'] in ('valid', 'none')),
        kpi_vault_total=len(vault_rows),
        vault_attention=[r for r in vault_rows if r['state'] in ('missing', 'expired', 'expiring')][:6],
        agenda=_events(request.user, today, today + timedelta(days=14))[:12],
        my_tasks=Task.objects.filter(assigned_to=request.user).exclude(status='done').order_by('due_date')[:6],
        announcements=StaffAnnouncement.objects.all()[:4],
        projects_health=projects_health,
        urgent_actions=get_urgent_actions(),
        stats=get_overall_stats(),
        active_learners=User.objects.filter(role='student', is_approved=True).count(),
        recent_docs=_visible_documents(request.user).filter(is_current=True)[:5],
    )
    return render(request, 'staff/dashboard.html', ctx)


# =========================================================================== tenders
class OpportunityForm(forms.ModelForm):
    class Meta:
        model = TenderOpportunity
        fields = ['kind', 'title', 'reference', 'department', 'province', 'closing_date', 'closing_time',
                  'briefing_at', 'briefing_venue', 'briefing_compulsory', 'value_amount', 'source_url',
                  'document_url', 'description']
        labels = {'department': 'Issued by (department / municipality / SETA)', 'reference': 'Bid / reference number',
                  'briefing_at': 'Briefing session (date & time)', 'source_url': 'Where we found it (link)',
                  'document_url': 'Tender document (link)', 'value_amount': 'Estimated value (R)',
                  'description': 'Scope / description'}
        widgets = {
            'closing_date': forms.DateInput(attrs={'type': 'date'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
            'briefing_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'rows': 6}),
            'province': forms.Select(choices=[('', 'Not stated')] + [(p, p) for p in tender_intel.PROVINCES]),
        }


class TrackingForm(forms.ModelForm):
    class Meta:
        model = TenderOpportunity
        fields = ['status', 'assigned_to', 'follow_up_date', 'follow_up_notes', 'internal_notes', 'local_document']
        labels = {'assigned_to': 'Bid owner', 'internal_notes': 'Internal notes', 'local_document': 'Attach our bid / tender pack'}
        widgets = {'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
                   'follow_up_notes': forms.TextInput(),
                   'internal_notes': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(role__in=['admin', 'instructor'], is_active=True)
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].empty_label = 'Unassigned'


class BidProfileForm(forms.ModelForm):
    class Meta:
        model = BidProfile
        exclude = ['updated_at']
        widgets = {k: forms.Textarea(attrs={'rows': 8}) for k in
                   ['core_keywords', 'related_keywords', 'exclude_keywords', 'target_provinces', 'accreditations']}
        widgets['home_province'] = forms.Select(choices=[(p, p) for p in tender_intel.PROVINCES])


def _rescore(opp):
    tender_intel.apply_assessment(opp, tender_intel.assess(opp, BidProfile.load()))


@staff_required
def tender_dashboard(request):
    today = timezone.localdate()
    qs = TenderOpportunity.objects.select_related('source', 'assigned_to')
    view = request.GET.get('view', 'open')
    if view == 'open':
        qs = qs.filter(status__in=TenderOpportunity.ACTIVE_STATUSES).exclude(closing_date__lt=today)
    elif view == 'mine':
        qs = qs.filter(assigned_to=request.user)
    elif view == 'closed':
        qs = qs.filter(Q(status__in=['won', 'lost', 'declined', 'expired']) | Q(closing_date__lt=today))
    filters = {k: request.GET.get(k, '') for k in ('q', 'kind', 'verdict', 'eligibility', 'province', 'status')}
    if filters['q']:
        q = filters['q']
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(department__icontains=q) | Q(reference__icontains=q))
    for key, field_name in (('kind', 'kind'), ('verdict', 'fit_verdict'), ('eligibility', 'eligibility_status'),
                            ('province', 'province'), ('status', 'status')):
        if filters[key]:
            qs = qs.filter(**{field_name: filters[key]})
    sort = request.GET.get('sort', 'score')
    order = {'score': ['-ai_relevance_score', 'closing_date'], 'closing': ['closing_date', '-ai_relevance_score'],
             'newest': ['-created_at']}.get(sort, ['-ai_relevance_score'])
    if sort == 'closing':
        from django.db.models import F
        qs = qs.order_by(F('closing_date').asc(nulls_last=True), '-ai_relevance_score')
    else:
        qs = qs.order_by(*order)
    page = Paginator(qs, 25).get_page(request.GET.get('page'))

    open_qs = TenderOpportunity.objects.filter(status__in=TenderOpportunity.ACTIVE_STATUSES).exclude(closing_date__lt=today)
    params = request.GET.copy()
    params.pop('page', None)
    ctx = _shell(request, 'tenders',
        page=page, filters=filters, view=view, sort=sort, querystring=params.urlencode(),
        stat_strong=open_qs.filter(fit_verdict='strong').count(),
        stat_closing=open_qs.filter(closing_date__lte=today + timedelta(days=7)).exclude(fit_verdict='low').count(),
        stat_grants=open_qs.filter(kind='grant').count(),
        stat_in_progress=TenderOpportunity.objects.filter(status__in=['preparing', 'applied', 'shortlisted']).count(),
        stat_won=TenderOpportunity.objects.filter(status='won', updated_at__year=today.year).count(),
        sources=TenderSource.objects.filter(source_type__in=['ocds', 'watch_page']).order_by('source_type', 'name'),
        scan_running=bool(cache.get('tender-scan-running')),
        kinds=TenderOpportunity.KIND_CHOICES, verdicts=TenderOpportunity.VERDICT_CHOICES,
        eligibilities=TenderOpportunity.ELIGIBILITY_CHOICES, statuses=TenderOpportunity.STATUS_CHOICES,
        provinces=tender_intel.PROVINCES,
    )
    return render(request, 'staff/tenders.html', ctx)


@staff_required
def tender_detail(request, tender_id):
    opp = get_object_or_404(TenderOpportunity.objects.select_related('source', 'assigned_to'), pk=tender_id)
    if opp.status == 'new':
        opp.status = 'viewed'
        opp.save(update_fields=['status', 'updated_at'])
    form = TrackingForm(instance=opp)
    if request.method == 'POST':
        action = request.POST.get('action', 'track')
        if action == 'rescore':
            _rescore(opp)
            opp.save()
            messages.success(request, 'Fit score and eligibility re-checked against today\'s documents.')
            return redirect(opp)
        form = TrackingForm(request.POST, request.FILES, instance=opp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Saved.')
            return redirect(opp)
    vault = tender_intel.document_vault()
    today = timezone.localdate()
    closing = (datetime.combine(opp.closing_date, opp.closing_time) if opp.closing_date and opp.closing_time
               else opp.closing_date)
    timeline = []
    for label, value in [('Published', opp.published_date),
                         ('Compulsory briefing' if opp.briefing_compulsory else 'Briefing session',
                          timezone.localtime(opp.briefing_at) if opp.briefing_at else None),
                         ('Our bid ready (internal)', opp.internal_deadline),
                         ('Closes', closing)]:
        if value:
            day = value.date() if isinstance(value, datetime) else value
            timeline.append({'label': label, 'when': value, 'has_time': isinstance(value, datetime), 'past': day < today})
    upcoming = [t for t in timeline if not t['past']]
    if upcoming:
        upcoming[0]['next'] = True
    return render(request, 'staff/tender_detail.html', _shell(request, 'tenders',
        opp=opp, form=form, timeline=timeline, vault=vault,
        ics_url=reverse('tender_ics', args=[opp.pk])))


@staff_required
def tender_edit(request, tender_id=None):
    opp = get_object_or_404(TenderOpportunity, pk=tender_id) if tender_id else None
    form = OpportunityForm(request.POST or None, instance=opp)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        if not obj.pk:
            obj.created_by = request.user
            obj.tender_id = f'manual-{timezone.now():%Y%m%d%H%M%S}-{request.user.pk}'
        _rescore(obj)
        obj.save()
        messages.success(request, f'Saved. Fit score {obj.fit_score} ({obj.get_fit_verdict_display().lower()}).')
        return redirect(obj)
    return render(request, 'staff/tender_form.html', _shell(request, 'tenders', form=form, opp=opp))


@require_POST
@admin_only
def run_tender_crawl(request):
    """Start a scan in the background (it can take a minute) and come straight back."""
    if not cache.add('tender-scan-running', 1, timeout=15 * 60):
        messages.info(request, 'A scan is already running. Refresh in a minute.')
        return redirect('tender_dashboard')
    try:
        subprocess.Popen(
            [sys.executable, str(settings.BASE_DIR / 'manage.py'), 'staff_daily', '--scan-only', '--release-lock'],
            cwd=str(settings.BASE_DIR), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True, env=os.environ.copy())
        messages.success(request, 'Scan started. New tenders and grants appear here within a minute or two.')
    except OSError as exc:
        cache.delete('tender-scan-running')
        messages.error(request, f'Could not start the scan: {exc}')
    return redirect('tender_dashboard')


@admin_only
def bid_profile(request):
    profile = BidProfile.load()
    form = BidProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        count = tender_intel.rescore_all()
        messages.success(request, f'Bid profile saved and {count} open opportunities re-scored.')
        return redirect('tender_dashboard')
    return render(request, 'staff/bid_profile.html', _shell(request, 'tenders', form=form))


@staff_required
def tender_calendar(request):
    today = timezone.localdate()
    try:
        first = datetime.strptime(request.GET.get('month', ''), '%Y-%m').date()
    except ValueError:
        first = today.replace(day=1)
    cal = pycalendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(first.year, first.month)
    events = _events(request.user, weeks[0][0], weeks[-1][-1])
    by_day = defaultdict(list)
    for e in events:
        by_day[e['date']].append(e)
    grid = [[{'date': d, 'in_month': d.month == first.month, 'is_today': d == today, 'events': by_day.get(d, [])}
             for d in week] for week in weeks]
    prev_month = (first - timedelta(days=1)).replace(day=1)
    next_month = (first + timedelta(days=32)).replace(day=1)
    token = signing.dumps(request.user.pk, salt=ICS_SALT)
    feed = request.build_absolute_uri(reverse('calendar_ics') + f'?token={token}')
    upcoming = [e for e in _events(request.user, today, today + timedelta(days=45))]
    return render(request, 'staff/calendar.html', _shell(request, 'calendar',
        grid=grid, month=first, prev_month=prev_month, next_month=next_month, upcoming=upcoming[:30],
        feed_url=feed, feed_webcal=feed.replace('https://', 'webcal://').replace('http://', 'webcal://')))


def _ics_escape(text):
    return str(text).replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def _ics(events, name):
    stamp = timezone.now().strftime('%Y%m%dT%H%M%SZ')
    host = settings.SITE_URL.split('//')[-1]
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Malitinne//Staff portal//EN', 'CALSCALE:GREGORIAN',
             f'X-WR-CALNAME:{_ics_escape(name)}', 'X-WR-TIMEZONE:Africa/Johannesburg']
    for i, e in enumerate(events):
        uid = f"{e['kind']}-{getattr(e['obj'], 'pk', i)}-{e['date']:%Y%m%d}@{host}"
        lines += ['BEGIN:VEVENT', f'UID:{uid}', f'DTSTAMP:{stamp}']
        if e['time']:
            start = timezone.make_aware(datetime.combine(e['date'], e['time'])).astimezone(dt_timezone.utc)
            end = start + timedelta(hours=1)
            lines += [f'DTSTART:{start:%Y%m%dT%H%M%SZ}', f'DTEND:{end:%Y%m%dT%H%M%SZ}']
        else:
            lines += [f"DTSTART;VALUE=DATE:{e['date']:%Y%m%d}", f"DTEND;VALUE=DATE:{e['date'] + timedelta(days=1):%Y%m%d}"]
        lines.append(f"SUMMARY:{_ics_escape(e['title'])}")
        if e['url']:
            lines.append(f"URL:{settings.SITE_URL}{e['url']}")
        if e['kind'] in ('closing', 'deadline', 'briefing', 'expiry'):
            lines += ['BEGIN:VALARM', 'ACTION:DISPLAY', f"DESCRIPTION:{_ics_escape(e['title'])}",
                      'TRIGGER:-P2D' if e['kind'] in ('closing', 'expiry') else 'TRIGGER:-PT2H', 'END:VALARM']
        lines.append('END:VEVENT')
    lines.append('END:VCALENDAR')
    folded = []
    for line in lines:  # RFC 5545: lines over 75 octets are folded
        while len(line.encode()) > 74:
            cut = 74
            while len(line[:cut].encode()) > 74:
                cut -= 1
            folded.append(line[:cut])
            line = ' ' + line[cut:]
        folded.append(line)
    return '\r\n'.join(folded) + '\r\n'


def calendar_ics(request):
    """Subscribable feed for Outlook / Google / phone calendars. Secured by a signed per-user token."""
    try:
        user_id = signing.loads(request.GET.get('token', ''), salt=ICS_SALT)
        user = User.objects.get(pk=user_id, is_active=True, role__in=['admin', 'instructor'])
    except (signing.BadSignature, User.DoesNotExist):
        raise Http404
    today = timezone.localdate()
    body = _ics(_events(user, today - timedelta(days=30), today + timedelta(days=270)), 'Malitinne tenders & deadlines')
    resp = HttpResponse(body, content_type='text/calendar; charset=utf-8')
    resp['Content-Disposition'] = 'inline; filename="malitinne-staff.ics"'
    resp['Cache-Control'] = 'private, max-age=900'
    return resp


@staff_required
def tender_ics(request, tender_id):
    opp = get_object_or_404(TenderOpportunity, pk=tender_id)
    start = min(d for d in [opp.closing_date, opp.internal_deadline, timezone.localdate()] if d)
    events = [e for e in _events(request.user, start - timedelta(days=60), (opp.closing_date or start) + timedelta(days=1))
              if getattr(e['obj'], 'pk', None) == opp.pk and isinstance(e['obj'], TenderOpportunity)]
    resp = HttpResponse(_ics(events, opp.title[:60]), content_type='text/calendar; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="tender-{opp.pk}.ics"'
    return resp


@staff_required
def tender_report(request):
    today = timezone.localdate()
    period = request.GET.get('period', 'quarter')
    if period == 'month':
        start = today.replace(day=1)
    elif period == 'year':
        start = today.replace(month=1, day=1)
    else:
        period = 'quarter'
        start = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
    found = TenderOpportunity.objects.filter(created_at__date__gte=start)
    decided = TenderOpportunity.objects.filter(updated_at__date__gte=start)
    submitted = decided.filter(status__in=['applied', 'shortlisted', 'won', 'lost'])
    won, lost = decided.filter(status='won'), decided.filter(status='lost')
    decisions = won.count() + lost.count()

    if request.GET.get('format') == 'csv':
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="malitinne-tenders-{start:%Y%m%d}-{today:%Y%m%d}.csv"'
        resp.write('\ufeff')  # Excel opens UTF-8 correctly
        w = csv.writer(resp)
        w.writerow(['Title', 'Type', 'Reference', 'Issued by', 'Province', 'Closing date', 'Fit score', 'Fit',
                    'Eligibility', 'Status', 'Bid owner', 'Value (R)', 'Found on', 'Link'])
        for t in (found | submitted).distinct().select_related('assigned_to').order_by('closing_date'):
            w.writerow([t.title, t.get_kind_display(), t.reference, t.department, t.province, t.closing_date or '',
                        t.fit_score, t.get_fit_verdict_display(), t.get_eligibility_status_display(), t.get_status_display(),
                        t.assigned_to.get_full_name() or t.assigned_to.username if t.assigned_to else '',
                        t.value_amount or '', f'{t.created_at:%Y-%m-%d}', t.source_url or t.document_url])
        return resp

    open_qs = TenderOpportunity.objects.filter(status__in=TenderOpportunity.ACTIVE_STATUSES).exclude(closing_date__lt=today)
    funnel = [
        ('Found', found.count()),
        ('Good fit', found.exclude(fit_verdict='low').count()),
        ('Bids submitted', submitted.count()),
        ('Shortlisted', decided.filter(status__in=['shortlisted', 'won']).count()),
        ('Won', won.count()),
    ]
    top = max(funnel[0][1], 1)
    vault_rows = _vault_rows(tender_intel.document_vault())
    return render(request, 'staff/report.html', _shell(request, 'report',
        period=period, start=start,
        funnel=[{'label': l, 'value': v, 'pct': round(100 * v / top)} for l, v in funnel],
        win_rate=round(100 * won.count() / decisions) if decisions else None,
        value_won=won.aggregate(v=Sum('value_amount'))['v'],
        by_kind=found.values('kind').annotate(n=Count('id')).order_by('-n'),
        by_province=found.exclude(province='').values('province').annotate(n=Count('id')).order_by('-n')[:9],
        top_buyers=found.exclude(fit_verdict='low').exclude(department='').values('department')
                        .annotate(n=Count('id')).order_by('-n')[:8],
        upcoming=open_qs.exclude(fit_verdict='low').filter(closing_date__lte=today + timedelta(days=30))
                        .order_by('closing_date')[:15],
        vault_rows=vault_rows,
        sources=TenderSource.objects.filter(source_type__in=['ocds', 'watch_page']).order_by('name'),
        kind_labels=dict(TenderOpportunity.KIND_CHOICES),
    ))


# =========================================================================== shared drive
def _vault_rows(vault, user=None):
    visible = set(_visible_documents(user).filter(pk__in=[d.pk for d in vault.values()]).values_list('pk', flat=True)) if user else None
    rows = []
    for key, label, icon, needs_expiry, hint in tender_intel.VAULT_TYPES:
        doc = vault.get(key)
        state = 'missing' if not doc else doc.expiry_state
        if doc and needs_expiry and not doc.expiry_date:
            state = 'no_date'
        rows.append({'key': key, 'label': label, 'icon': icon, 'hint': hint, 'doc': doc, 'state': state,
                     'needs_expiry': needs_expiry, 'can_open': bool(doc) and (visible is None or doc.pk in visible)})
    return rows


class UploadForm(forms.Form):
    file = forms.FileField()
    title = forms.CharField(max_length=255, required=False)
    doc_type = forms.ChoiceField(choices=SharedDocument.DOC_TYPE_CHOICES, initial='other')
    category = forms.ModelChoiceField(DocumentCategory.objects.all(), required=False, empty_label='No folder')
    reference_number = forms.CharField(max_length=120, required=False)
    issued_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    expiry_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    visibility = forms.ChoiceField(choices=[('all_staff', 'All staff'), ('management', 'Management only'),
                                            ('private', 'Only me')], initial='all_staff')
    tags = forms.CharField(max_length=500, required=False)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
    replaces = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def clean_file(self):
        f = self.cleaned_data['file']
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        if ext not in ALLOWED_UPLOAD_EXT:
            raise forms.ValidationError('This file type is not allowed. Use PDF, Word, Excel, PowerPoint, images, text or ZIP.')
        if f.size > MAX_UPLOAD_BYTES:
            raise forms.ValidationError('Files must be 25 MB or smaller.')
        return f


SENSITIVE_TYPES = {'director_id'}


@staff_required
def shared_drive(request):
    docs = _visible_documents(request.user)
    filters = {k: request.GET.get(k, '') for k in ('q', 'folder', 'type', 'state')}
    show_old = request.GET.get('versions') == 'all'
    if not show_old:
        docs = docs.filter(is_current=True)
    if filters['q']:
        q = filters['q']
        docs = docs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(tags__icontains=q)
                           | Q(file_name__icontains=q) | Q(reference_number__icontains=q))
    if filters['folder']:
        docs = docs.filter(category__slug=filters['folder'])
    if filters['type']:
        docs = docs.filter(doc_type=filters['type'])
    today = timezone.localdate()
    if filters['state'] == 'expiring':
        docs = docs.filter(expiry_date__gte=today, expiry_date__lte=today + timedelta(days=30))
    elif filters['state'] == 'expired':
        docs = docs.filter(expiry_date__lt=today)
    sort = request.GET.get('sort', 'recent')
    docs = docs.order_by({'recent': '-uploaded_at', 'name': 'title', 'popular': '-download_count',
                          'expiry': 'expiry_date'}.get(sort, '-uploaded_at'))
    page = Paginator(docs, 30).get_page(request.GET.get('page'))
    visible_current = _visible_documents(request.user).filter(is_current=True)
    folder_counts = dict(visible_current.values_list('category__slug').annotate(n=Count('id')))
    folders = [{'obj': c, 'count': folder_counts.get(c.slug, 0)} for c in DocumentCategory.objects.filter(parent=None)]
    params = request.GET.copy()
    params.pop('page', None)
    initial_type = request.GET.get('upload', '')
    form = UploadForm(initial={'doc_type': initial_type or 'other'})
    return render(request, 'staff/drive.html', _shell(request, 'drive',
        page=page, filters=filters, sort=sort, show_old=show_old, querystring=params.urlencode(),
        folders=folders, vault_rows=_vault_rows(tender_intel.document_vault(), request.user),
        doc_types=SharedDocument.DOC_TYPE_CHOICES, form=form, open_upload=bool(initial_type),
        total_docs=visible_current.count(),
        can_manage=request.user.role == 'admin'))


@staff_required
def upload_document(request):
    if request.method != 'POST':
        return redirect('shared_drive')
    wants_json = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    form = UploadForm(request.POST, request.FILES)
    if not form.is_valid():
        errors = '; '.join(f"{', '.join(v)}" for v in form.errors.values())
        if wants_json:
            return JsonResponse({'error': errors}, status=400)
        messages.error(request, f'Upload failed: {errors}')
        return redirect('shared_drive')
    data = form.cleaned_data
    f = data['file']
    previous = None
    if data.get('replaces'):
        previous = _visible_documents(request.user).filter(pk=data['replaces'], is_current=True).first()
    if previous is None and data['doc_type'] in tender_intel.VAULT_TYPE_KEYS:
        previous = SharedDocument.objects.filter(doc_type=data['doc_type'], is_current=True).order_by('-uploaded_at').first()
    version = '1.0'
    if previous:
        try:
            version = f'{int(float(previous.version)) + 1}.0'
        except ValueError:
            version = '2.0'
    sensitive = data['doc_type'] in SENSITIVE_TYPES or (data.get('category') and data['category'].slug == 'learner-admin')
    doc = SharedDocument.objects.create(
        title=data['title'] or (previous.title if previous else os.path.splitext(f.name)[0].replace('_', ' ')),
        description=data['description'], category=data['category'] or (previous.category if previous else None),
        file=f, file_name=get_valid_filename(f.name), file_size=f.size, mime_type=f.content_type or '',
        version=version, previous_version=previous, doc_type=data['doc_type'],
        reference_number=data['reference_number'], issued_date=data['issued_date'], expiry_date=data['expiry_date'],
        visibility='management' if sensitive and data['visibility'] == 'all_staff' else data['visibility'],
        is_sensitive=bool(sensitive), tags=data['tags'], uploaded_by=request.user,
    )
    if previous:
        SharedDocument.objects.filter(pk=previous.pk).update(is_current=False)
    if doc.doc_type in tender_intel.VAULT_TYPE_KEYS:
        tender_intel.rescore_all()
    if doc.visibility == 'all_staff':
        for staff in User.objects.filter(role__in=['instructor', 'admin'], is_active=True).exclude(pk=request.user.pk):
            Notification.objects.create(user=staff, title=f'New document: {doc.title}',
                                        message=f'{request.user.get_full_name() or request.user.username} added it to the Shared Drive.',
                                        link=reverse('shared_drive') + f'?q={doc.title[:40]}')
    if wants_json:
        return JsonResponse({'success': True, 'id': doc.pk, 'title': doc.title})
    messages.success(request, f'"{doc.title}" uploaded' + (f' as version {version}.' if previous else '.'))
    return redirect(request.POST.get('next') or 'shared_drive')


@xframe_options_sameorigin  # lets the drive show PDFs / images in its own preview window
@staff_required
def download_document(request, doc_id):
    doc = get_object_or_404(SharedDocument, pk=doc_id)
    if not _can_see(request.user, doc):
        return HttpResponseForbidden("You don't have permission to open this document.")
    if not doc.file or not doc.file.storage.exists(doc.file.name):
        raise Http404('File not found')
    inline = request.GET.get('inline') == '1' and doc.extension in INLINE_TYPES
    DocumentDownloadLog.objects.create(document=doc, user=request.user, ip_address=_client_ip(request))
    SharedDocument.objects.filter(pk=doc.pk).update(download_count=doc.download_count + 1)
    resp = FileResponse(doc.file.open('rb'), as_attachment=not inline, filename=doc.file_name,
                        content_type=INLINE_TYPES.get(doc.extension) if inline else None)
    resp['X-Content-Type-Options'] = 'nosniff'
    resp['Cache-Control'] = 'private, no-store'
    if inline and doc.extension == 'txt':
        resp['Content-Security-Policy'] = "default-src 'none'; sandbox"
    return resp


@staff_required
def delete_document(request, doc_id):
    if request.method not in ('POST', 'DELETE'):
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    doc = get_object_or_404(SharedDocument, pk=doc_id)
    if request.user.role != 'admin' and doc.uploaded_by_id != request.user.pk:
        return JsonResponse({'error': 'Only the uploader or an administrator can delete this document.'}, status=403)
    if doc.is_current and doc.previous_version_id:
        SharedDocument.objects.filter(pk=doc.previous_version_id).update(is_current=True)
    title, storage, name = doc.title, doc.file.storage, doc.file.name
    doc.delete()
    if name and storage.exists(name):
        storage.delete(name)
    if request.method == 'DELETE' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, f'Deleted "{title}".')
    return redirect(request.POST.get('next') or 'shared_drive')


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return (forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')) or None


# =========================================================================== discussions
@staff_required
def discussions_list(request):
    tab = request.GET.get('tab', 'all')
    q = request.GET.get('q', '')
    topics = ForumTopic.objects.select_related('author', 'lesson__course', 'project').annotate(replies=Count('posts'))
    if tab == 'tickets':
        topics = topics.filter(is_ticket=True, is_resolved=False)
    elif tab == 'unanswered':
        topics = topics.filter(replies=0, is_closed=False)
    elif tab == 'mine':
        topics = topics.filter(Q(author=request.user) | Q(lesson__course__instructor=request.user))
    if q:
        topics = topics.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(author__username__icontains=q))
    topics = topics.order_by('-is_pinned', '-updated_at')
    all_topics = ForumTopic.objects.all()
    return render(request, 'staff/discussions.html', _shell(request, 'discussions',
        page=Paginator(topics, 25).get_page(request.GET.get('page')), tab=tab, q=q,
        count_all=all_topics.count(),
        count_tickets=all_topics.filter(is_ticket=True, is_resolved=False).count(),
        count_unanswered=all_topics.annotate(n=Count('posts')).filter(n=0, is_closed=False).count()))


# =========================================================================== notifications
@staff_required
def notifications(request):
    qs = Notification.objects.filter(user=request.user)
    if request.method == 'POST':
        qs.filter(is_read=False).update(is_read=True)
        return redirect('notifications')
    return render(request, 'staff/notifications.html', _shell(request, 'notifications',
                  items=qs.order_by('-created_at')[:100]))
