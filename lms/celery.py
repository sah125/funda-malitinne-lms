"""
Celery tasks for Funda Malitinne LMS
"""
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.models import User, Course, Progress, Notification

@shared_task
def send_registration_email(user_id):
    """Send registration confirmation email"""
    try:
        user = User.objects.get(id=user_id)
        context = {
            'user': user,
            'verification_link': f'/verify-email/{user.verification_token}/'
        }
        html_message = render_to_string('email/registration_approved.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            'Welcome to Funda Malitinne LMS',
            plain_message,
            'noreply@fundamalitinne.com',
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending registration email: {e}")


@shared_task
def send_course_enrollment_email(user_id, course_id):
    """Send course enrollment confirmation email"""
    try:
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)
        
        context = {
            'user': user,
            'course': course,
            'course_link': f'/course/{course.id}/'
        }
        html_message = render_to_string('email/course_enrollment.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            f'Welcome to {course.title}',
            plain_message,
            'noreply@fundamalitinne.com',
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending enrollment email: {e}")


@shared_task
def send_submission_grade_email(submission_id):
    """Send grade notification email to student"""
    try:
        from core.models import Submission
        submission = Submission.objects.get(id=submission_id)
        
        context = {
            'student': submission.student,
            'assignment': submission.assignment,
            'score': submission.score,
            'feedback': submission.feedback,
        }
        html_message = render_to_string('email/submission_graded.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            f'Your assignment has been graded: {submission.assignment.title}',
            plain_message,
            'noreply@fundamalitinne.com',
            [submission.student.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending grade email: {e}")


@shared_task
def send_announcement_notification(announcement_id):
    """Send announcement to all course enrollees"""
    try:
        from core.models import Announcement
        announcement = Announcement.objects.get(id=announcement_id)
        
        # Get all students enrolled in the course
        students = announcement.course.students.all()
        
        for student in students:
            context = {
                'student': student,
                'course': announcement.course,
                'announcement': announcement,
            }
            html_message = render_to_string('email/announcement.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                f'New announcement in {announcement.course.title}',
                plain_message,
                'noreply@fundamalitinne.com',
                [student.email],
                html_message=html_message,
                fail_silently=False,
            )
    except Exception as e:
        print(f"Error sending announcements: {e}")


@shared_task
def update_daily_streak():
    """Update daily streaks for all active users"""
    try:
        from core.models import DailyStreak
        from django.utils import timezone
        from datetime import timedelta
        
        yesterday = timezone.now().date() - timedelta(days=1)
        
        for streak in DailyStreak.objects.all():
            # Check if user logged in yesterday
            last_access = streak.user.last_login.date() if streak.user.last_login else None
            
            if last_access == yesterday:
                streak.current_streak += 1
            elif last_access != timezone.now().date():
                streak.current_streak = 0
            
            streak.save()
    except Exception as e:
        print(f"Error updating streaks: {e}")


@shared_task
def send_deadline_reminder():
    """Send assignment deadline reminders"""
    try:
        from core.models import Assignment
        from django.utils import timezone
        from datetime import timedelta
        
        tomorrow = timezone.now() + timedelta(days=1)
        
        assignments = Assignment.objects.filter(
            due_date__date=tomorrow.date(),
            due_date__gte=timezone.now()
        )
        
        for assignment in assignments:
            students = assignment.course.students.all()
            
            for student in students:
                context = {
                    'student': student,
                    'assignment': assignment,
                    'course': assignment.course,
                }
                html_message = render_to_string('email/assignment_reminder.html', context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    f'Assignment due tomorrow: {assignment.title}',
                    plain_message,
                    'noreply@fundamalitinne.com',
                    [student.email],
                    html_message=html_message,
                    fail_silently=False,
                )
    except Exception as e:
        print(f"Error sending reminders: {e}")
