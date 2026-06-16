from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import (
    User, Course, TenderOpportunity, Attendance, Progress, 
    PortfolioOfEvidence, Submission, ForumTopic, Notification,
    AuditLog, LearnerProfile
)


def calculate_project_health(project):
    """
    Calculate health metrics for a project (tender opportunity)
    Returns dict with all metrics
    """
    # Get learners enrolled in this project
    learners = User.objects.filter(
        role='student',
        is_approved=True,
        enrolled_courses__tender_opportunity=project
    ).distinct()
    
    total_learners = learners.count()
    
    if total_learners == 0:
        return {
            'id': project.id,
            'name': project.title,
            'learners': 0,
            'attendance': 0,
            'poe_completion': 0,
            'avg_progress': 0,
            'risk': 'low',
            'open_tickets': 0,
            'status': project.status
        }
    
    # Calculate Attendance (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    attendance_records = Attendance.objects.filter(
        student__in=learners,
        date__gte=thirty_days_ago
    )
    total_attendance = attendance_records.count()
    present_attendance = attendance_records.filter(status='present').count()
    attendance_pct = round((present_attendance / total_attendance * 100) if total_attendance > 0 else 0, 1)
    
    # Calculate POE Completion
    poe_submitted = PortfolioOfEvidence.objects.filter(
        student__in=learners,
        status='submitted'
    ).count()
    poe_pct = round((poe_submitted / total_learners * 100), 1)
    
    # Calculate Course Progress
    progress_records = Progress.objects.filter(
        student__in=learners,
        course__tender_opportunity=project
    )
    avg_progress = progress_records.aggregate(
        avg=Avg('progress_percentage')
    )['avg'] or 0
    
    # Count open tickets (forum topics marked as tickets)
    open_tickets = ForumTopic.objects.filter(
        project=project,
        is_ticket=True,
        is_resolved=False
    ).count()
    
    # Determine risk level
    risk = 'low'
    if attendance_pct < 70 or poe_pct < 60 or avg_progress < 50:
        risk = 'high'
    elif attendance_pct < 85 or poe_pct < 80 or avg_progress < 70:
        risk = 'medium'
    
    return {
        'id': project.id,
        'name': project.title,
        'learners': total_learners,
        'attendance': attendance_pct,
        'poe_completion': poe_pct,
        'avg_progress': round(avg_progress, 1),
        'risk': risk,
        'open_tickets': open_tickets,
        'status': project.status
    }


def get_urgent_actions():
    """
    Get list of urgent actions that need attention
    Returns list of action dicts
    """
    actions = []
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # 1. Learners without POE
    learners_without_poe = User.objects.filter(
        role='student',
        is_approved=True
    ).exclude(portfolios__isnull=False
              ).count()
    
    if learners_without_poe > 0:
        actions.append({
            'priority': 'critical',
            'icon': '📄',
            'description': f'Learners missing Portfolio of Evidence',
            'count': learners_without_poe,
            'action_url': '/admin/learners/missing-poe/'
        })
    
    # 2. Projects with low attendance
    projects = TenderOpportunity.objects.filter(status__in=['new', 'viewed', 'active'])
    low_attendance_projects = []
    for project in projects:
        health = calculate_project_health(project)
        if health['attendance'] < 70 and health['learners'] > 0:
            low_attendance_projects.append(project.title)
    
    if low_attendance_projects:
        actions.append({
            'priority': 'high',
            'icon': '📊',
            'description': f'Projects below 70% attendance: {", ".join(low_attendance_projects[:3])}',
            'count': len(low_attendance_projects),
            'action_url': '/staff-portal/?tab=attendance'
        })
    
    # 3. Inactive learners (not logged in for 7+ days)
    inactive_threshold = now - timedelta(days=7)
    inactive_learners = User.objects.filter(
        role='student',
        is_approved=True,
        last_login__lt=inactive_threshold
    ).count()
    
    if inactive_learners > 0:
        actions.append({
            'priority': 'medium',
            'icon': '👤',
            'description': f'Inactive learners (7+ days)',
            'count': inactive_learners,
            'action_url': '/admin/learners/inactive/'
        })
    
    # 4. Overdue assessments
    overdue_submissions = Submission.objects.filter(
        submitted_at__lt=now - timedelta(days=7),
        grade__isnull=True
    ).count()
    
    if overdue_submissions > 0:
        actions.append({
            'priority': 'high',
            'icon': '📝',
            'description': f'Overdue assessments waiting for grading',
            'count': overdue_submissions,
            'action_url': '/instructor/pending-gradings/'
        })
    
    # 5. POPIA consent missing
    missing_consent = LearnerProfile.objects.filter(
        popia_consent=False
    ).count()
    
    if missing_consent > 0:
        actions.append({
            'priority': 'medium',
            'icon': '🔒',
            'description': f'Learners missing POPIA consent',
            'count': missing_consent,
            'action_url': '/admin/learners/popia-consent/'
        })
    
    return actions[:5]  # Return top 5 urgent actions


def get_overall_stats():
    """
    Get overall system stats
    """
    now = timezone.now()
    
    total_projects = TenderOpportunity.objects.filter(
        status__in=['new', 'viewed', 'active']
    ).count()
    
    total_learners = User.objects.filter(
        role='student',
        is_approved=True
    ).count()
    
    # Overall attendance (last 30 days)
    thirty_days_ago = now - timedelta(days=30)
    attendance_total = Attendance.objects.filter(
        date__gte=thirty_days_ago
    ).count()
    attendance_present = Attendance.objects.filter(
        date__gte=thirty_days_ago,
        status='present'
    ).count()
    overall_attendance = round(
        (attendance_present / attendance_total * 100) if attendance_total > 0 else 0,
        1
    )
    
    # Open tickets
    open_tickets = ForumTopic.objects.filter(
        is_ticket=True,
        is_resolved=False
    ).count()
    
    # AI queries today
    ai_queries_today = AuditLog.objects.filter(
        action='ai_query',
        timestamp__date=now.date()
    ).count()
    
    return {
        'total_projects': total_projects,
        'total_learners': total_learners,
        'overall_attendance': overall_attendance,
        'open_tickets': open_tickets,
        'ai_queries_today': ai_queries_today
    }
