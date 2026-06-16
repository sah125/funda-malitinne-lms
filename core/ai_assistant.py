# core/ai_assistant.py
import re
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import User, TenderOpportunity, Attendance, PortfolioOfEvidence, ForumTopic, AuditLog
from .portal_helpers import calculate_project_health, get_urgent_actions, get_overall_stats

class AIAdminAssistant:
    def __init__(self):
        self.user_input = ""
    
    def process(self, user_input):
        self.user_input = user_input.lower().strip()
        
        # Detect commands
        if re.search(r'(show|list|view).*course', self.user_input):
            return self._list_courses()
        
        elif re.search(r'(find|search|get).*student', self.user_input):
            return self._find_student()
        
        elif re.search(r'(update|change|set).*mark|grade', self.user_input):
            return self._update_marks()
        
        elif re.search(r'(enrolled|taking|registered).*course', self.user_input):
            return self._check_enrollment()
        
        elif re.search(r'(stat|dashboard|overview|how many)', self.user_input):
            return self._get_stats()
        
        elif re.search(r'help', self.user_input):
            return self._help()
        
        else:
            return self._unknown()
    
    def _list_courses(self):
        return {
            "action": "list_courses",
            "entity": "course",
            "filters": {},
            "data": {"message": "Fetching all courses..."},
            "confidence": 0.95
        }
    
    def _find_student(self):
        name_match = re.search(r'student\s+([A-Za-z]+)', self.user_input)
        name = name_match.group(1) if name_match else None
        
        return {
            "action": "get_student_info",
            "entity": "student",
            "filters": {"name": name} if name else {},
            "data": {"message": f"Searching for student {name}..." if name else "Which student would you like to find?"},
            "confidence": 0.90
        }
    
    def _update_marks(self):
        name_match = re.search(r'(?:of|for|to)\s+([A-Za-z]+)', self.user_input)
        marks_match = re.search(r'(\d+(?:\.\d+)?)', self.user_input)
        
        name = name_match.group(1) if name_match else None
        marks = float(marks_match.group(1)) if marks_match else None
        
        return {
            "action": "update_marks",
            "entity": "student",
            "filters": {"name": name} if name else {},
            "data": {
                "marks": marks,
                "message": f"Ready to update {name}'s marks to {marks}%" if name and marks else "Please specify student name and marks."
            },
            "confidence": 0.85
        }
    
    def _check_enrollment(self):
        return {
            "action": "check_enrollment",
            "entity": "student",
            "filters": {},
            "data": {"message": "Checking enrollment status..."},
            "confidence": 0.80
        }
    
    def _get_stats(self):
        return {
            "action": "get_stats",
            "entity": "system",
            "filters": {},
            "data": {"message": "Fetching system statistics..."},
            "confidence": 0.98
        }
    
    def _help(self):
        return {
            "action": "help",
            "entity": "system",
            "filters": {},
            "data": {
                "message": """I can help you with:
• "Show me all courses"
• "Find student Tamarah"
• "Update John's marks to 85%"
• "Is Tamarah enrolled?"
• "Show system statistics"
• "Help" for this menu"""
            },
            "confidence": 0.99
        }
    
    def _unknown(self):
        return {
            "action": "unknown",
            "entity": "",
            "filters": {},
            "data": {"message": "I didn't understand. Try 'Help' to see what I can do."},
            "confidence": 0.30
        }


def process_operation_query(query, user):
    """
    Process operational queries from staff
    """
    query_lower = query.lower()
    
    # Check for attendance queries
    if 'attendance' in query_lower and ('below' in query_lower or 'under' in query_lower):
        threshold = extract_threshold(query)
        return get_projects_below_attendance(threshold)
    
    # Check for inactive learners
    if 'inactive' in query_lower or 'not active' in query_lower:
        days = extract_days(query)
        return get_inactive_learners(days)
    
    # Check for POE queries
    if 'poe' in query_lower and ('missing' in query_lower or 'outstanding' in query_lower):
        return get_missing_poe_learners()
    
    # Check for risk queries
    if 'risk' in query_lower or 'high risk' in query_lower:
        return get_high_risk_projects()
    
    # Check for ticket queries
    if 'ticket' in query_lower or 'issue' in query_lower:
        return get_open_tickets()
    
    # Check for compliance queries
    if 'compliance' in query_lower or 'qcto' in query_lower:
        return get_compliance_status()
    
    # General summary
    if 'summary' in query_lower or 'overview' in query_lower:
        return get_system_summary()
    
    # Default: Return help
    return {
        'type': 'help',
        'message': 'I can help with:\n- Attendance reports\n- Inactive learners\n- POE status\n- Risk analysis\n- Ticket overview\n- Compliance status',
        'suggestions': [
            'Show projects with low attendance',
            'List inactive learners',
            'Show missing POEs',
            'What are the high risk projects?',
            'Show open tickets',
            'Give me a system summary'
        ]
    }


def extract_threshold(query):
    """Extract threshold from query (e.g., 'below 75%')"""
    import re
    matches = re.findall(r'below\s+(\d+)', query.lower())
    if matches:
        return int(matches[0])
    return 80  # Default


def extract_days(query):
    """Extract days from query"""
    import re
    matches = re.findall(r'(\d+)\s+days?', query.lower())
    if matches:
        return int(matches[0])
    return 7  # Default


def get_projects_below_attendance(threshold=80):
    """Find projects with attendance below threshold"""
    projects = TenderOpportunity.objects.filter(status__in=['new', 'viewed', 'active'])
    results = []
    
    for project in projects:
        health = calculate_project_health(project)
        if health['attendance'] < threshold and health['learners'] > 0:
            results.append({
                'name': project.title,
                'attendance': health['attendance'],
                'learners': health['learners'],
                'risk': health['risk']
            })
    
    return {
        'type': 'attendance_report',
        'threshold': threshold,
        'projects': results,
        'count': len(results),
        'message': f'Found {len(results)} projects with attendance below {threshold}%'
    }


def get_inactive_learners(days=7):
    """Get learners inactive for X days"""
    cutoff = timezone.now() - timedelta(days=days)
    learners = User.objects.filter(
        role='student',
        is_approved=True,
        last_login__lt=cutoff
    ).values('id', 'username', 'email', 'last_login')
    
    return {
        'type': 'inactive_learners',
        'days': days,
        'learners': list(learners)[:20],
        'count': learners.count(),
        'message': f'Found {learners.count()} learners inactive for {days}+ days'
    }


def get_missing_poe_learners():
    """Get learners without POE submission"""
    learners_with_poe = PortfolioOfEvidence.objects.values_list('student', flat=True).distinct()
    learners = User.objects.filter(
        role='student',
        is_approved=True
    ).exclude(
        id__in=learners_with_poe
    ).values('id', 'username', 'email', 'first_name', 'last_name')
    
    return {
        'type': 'missing_poe',
        'learners': list(learners)[:20],
        'count': learners.count(),
        'message': f'Found {learners.count()} learners without POE'
    }


def get_high_risk_projects():
    """Get projects marked as high risk"""
    projects = TenderOpportunity.objects.filter(status__in=['new', 'viewed', 'active'])
    results = []
    
    for project in projects:
        health = calculate_project_health(project)
        if health['risk'] == 'high' and health['learners'] > 0:
            results.append({
                'name': project.title,
                'attendance': health['attendance'],
                'poe': health['poe_completion'],
                'learners': health['learners'],
                'open_tickets': health['open_tickets']
            })
    
    return {
        'type': 'risk_report',
        'projects': results,
        'count': len(results),
        'message': f'Found {len(results)} high risk projects'
    }


def get_open_tickets():
    """Get open tickets"""
    tickets = ForumTopic.objects.filter(
        is_ticket=True,
        is_resolved=False
    ).select_related('project').values(
        'id', 'title', 'project__title', 'created_at', 'priority'
    )
    
    return {
        'type': 'tickets',
        'tickets': list(tickets)[:20],
        'count': tickets.count(),
        'message': f'Found {tickets.count()} open tickets'
    }


def get_compliance_status():
    """Get overall compliance status"""
    learners = User.objects.filter(role='student', is_approved=True)
    total_learners = learners.count()
    
    # POPIA consent
    from .models import LearnerProfile
    consented = LearnerProfile.objects.filter(popia_consent=True).count()
    
    # Attendance compliance (80%+)
    projects = TenderOpportunity.objects.filter(status__in=['new', 'viewed', 'active'])
    compliant_projects = 0
    for project in projects:
        health = calculate_project_health(project)
        if health['attendance'] >= 80:
            compliant_projects += 1
    
    # POE compliance
    poe_submitted = PortfolioOfEvidence.objects.filter(
        student__in=learners,
        status='submitted'
    ).count()
    
    return {
        'type': 'compliance',
        'total_learners': total_learners,
        'popia_consent': f"{round((consented/total_learners*100) if total_learners > 0 else 0, 1)}%",
        'attendance_compliance': f"{round((compliant_projects/projects.count()*100) if projects.count() > 0 else 0, 1)}%",
        'poe_compliance': f"{round((poe_submitted/total_learners*100) if total_learners > 0 else 0, 1)}%",
        'message': 'Compliance status generated'
    }


def get_system_summary():
    """Get overall system summary"""
    stats = get_overall_stats()
    urgent_actions = get_urgent_actions()
    
    return {
        'type': 'summary',
        'stats': stats,
        'urgent_actions': urgent_actions,
        'message': f"System Summary: {stats['total_projects']} projects, {stats['total_learners']} learners, {stats['open_tickets']} open tickets"
    }