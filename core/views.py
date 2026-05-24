from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse, FileResponse, Http404
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.db.models import Count, Q, Avg
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import get_valid_filename
import json
import csv
import io
import mimetypes
import os
import time
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings

from .ai_assistant import AIAdminAssistant
from .ai_recommendations import get_course_recommendations
from .models import (
    User, Course, Lesson, Assignment, Submission, Progress, 
    Quiz, QuizQuestion, QuizAttempt, Certificate, Notification,
    Announcement, CourseGroup, Attendance, LearningModule,
    LearnerProfile, LearnerDocument, LogbookEntry, BackupLog, AuditLog,
    LessonModule, UserModuleProgress, LessonInteraction, DailyStreak, Badge, UserBadge,
    ForumTopic, ForumPost
)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from io import BytesIO
from django.shortcuts import render, get_object_or_404
from .models import Lesson

def lesson_discussions(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    return render(request, 'lesson_discussions.html', {
        'lesson': lesson
    })

# ==================== HELPER FUNCTIONS ====================

def is_instructor(user):
    return user.is_authenticated and user.role == 'instructor'

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def send_notification(user, title, message, link=None):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link
    )

def get_client_ip(request):
    """Get client IP address for audit logging"""
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


def programmes_page(request):
    """Display skills programmes page"""
    return render(request, 'malitinne/programmes.html')

def clients_page(request):
    """Display clients and testimonials page"""
    return render(request, 'malitinne/clients.html')

# Add these functions to your views.py (near your other discussion views)

@login_required
def delete_reply(request, reply_id):
    """Delete a reply (instructor or admin only)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        reply = get_object_or_404(ForumPost, id=reply_id)
        topic = reply.topic
        lesson = topic.lesson
        
        # Check permissions - only instructor of the course or admin can delete
        if request.user.role == 'instructor':
            if lesson.course.instructor != request.user:
                return JsonResponse({'error': 'You do not have permission to delete this reply'}, status=403)
        elif request.user.role != 'admin':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Delete the reply
        reply.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Reply deleted successfully'
        })
        
    except ForumPost.DoesNotExist:
        return JsonResponse({'error': 'Reply not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def like_reply(request, reply_id):
    """Like or unlike a reply"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        reply = get_object_or_404(ForumPost, id=reply_id)
        
        # Toggle like
        if request.user in reply.likes.all():
            reply.likes.remove(request.user)
            liked = False
        else:
            reply.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': reply.likes.count()
        })
        
    except ForumPost.DoesNotExist:
        return JsonResponse({'error': 'Reply not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Also add toggle_discussion_close if you haven't already
@login_required
def toggle_discussion_close(request, discussion_id):
    """Toggle close/lock status of a discussion (instructor only)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        topic = get_object_or_404(ForumTopic, id=discussion_id)
        
        # Check if user has permission
        if request.user.role == 'instructor':
            if topic.lesson.course.instructor != request.user:
                return JsonResponse({'error': 'You do not own this course'}, status=403)
        elif request.user.role != 'admin':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        # Toggle the is_locked status (or is_closed if you prefer)
        # Make sure your ForumTopic model has an 'is_locked' field
        if hasattr(topic, 'is_locked'):
            topic.is_locked = not topic.is_locked
            topic.save()
            is_closed = topic.is_locked
        else:
            # If is_locked doesn't exist, you might need to add it to your model
            return JsonResponse({'error': 'Discussion locking not implemented'}, status=501)
        
        return JsonResponse({
            'success': True,
            'is_closed': is_closed,
            'message': f'Discussion {"closed" if is_closed else "reopened"} successfully'
        })
        
    except ForumTopic.DoesNotExist:
        return JsonResponse({'error': 'Discussion not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ==================== AUTHENTICATION VIEWS ====================

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            if user.role == 'student':
                return redirect('student_dashboard')
            elif user.role == 'instructor':
                return redirect('instructor_dashboard')
            else:
                return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        full_name = request.POST.get('full_name', '').split(' ', 1)
        first_name = full_name[0] if full_name else ''
        last_name = full_name[1] if len(full_name) > 1 else ''
        
        id_number = request.POST.get('id_number')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        nationality = request.POST.get('nationality')
        contact_number = request.POST.get('contact_number')
        disability = request.POST.get('disability')
        preferred_language = request.POST.get('preferred_language')
        
        if password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='student',
                is_active=True,
                is_approved=False
            )
            
            user.id_number = id_number
            if date_of_birth:
                user.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            user.gender = gender
            user.nationality = nationality
            user.contact_number = contact_number
            user.disability = disability
            user.preferred_language = preferred_language
            user.save()
            
            try:
                html_message = render_to_string('email/registration_pending.html', {
                    'user': user,
                    'full_name': f"{first_name} {last_name}"
                })
                send_mail(
                    'Registration Received - Funda Malitinne LMS',
                    f'Dear {first_name},\n\nYour registration has been received. You will receive an email once approved.\n\nRegards,\nFunda Malitinne Team',
                    'noreply@fundamalitinne.com',
                    [email],
                    html_message=html_message,
                    fail_silently=True
                )
            except:
                pass
            
            admins = User.objects.filter(role='admin', is_approved=True)
            for admin in admins:
                try:
                    html_message = render_to_string('email/admin_approval_needed.html', {'user': user, 'admin': admin})
                    send_mail(
                        f'New Student Registration - {username}',
                        f'A new student has registered. Please review and approve their account.\n\nUsername: {username}\nEmail: {email}',
                        'noreply@fundamalitinne.com',
                        [admin.email],
                        html_message=html_message,
                        fail_silently=True
                    )
                except:
                    pass
            
            messages.success(request, 'Registration submitted! Please wait for admin approval.')
            return redirect('login')
    
    return render(request, 'register.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            user.send_reset_email()
            messages.success(request, 'Password reset link sent to your email.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
    
    return render(request, 'forgot_password.html')

def reset_password(request, token):
    try:
        user = User.objects.get(reset_password_token=token, reset_password_expires__gt=timezone.now())
        valid = True
    except User.DoesNotExist:
        valid = False
        user = None
    
    if request.method == 'POST' and valid:
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password == password2:
            user.set_password(password)
            user.reset_password_token = None
            user.reset_password_expires = None
            user.save()
            messages.success(request, 'Password reset successful!')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    
    return render(request, 'reset_password.html', {'valid': valid, 'user': user})

# ==================== HOME VIEWS ====================

def home(request):
    courses = Course.objects.filter(status='published')[:6]
    return render(request, 'home.html', {'courses': courses})

def company_home(request):
    return render(request, 'malitinne/home.html')

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
    
    return render(request, 'student_dashboard.html', {
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
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all().order_by('order')
    assignments = course.assignments.all()
    quizzes = []
    
    progress = None
    if request.user.role == 'student':
        if request.user not in course.students.all():
            messages.warning(request, 'You need to enroll in this course first.')
            return redirect('student_dashboard')
        progress, created = Progress.objects.get_or_create(student=request.user, course=course)
    
    for lesson in lessons:
        if hasattr(lesson, 'quiz'):
            quiz = lesson.quiz
            quiz_attempt = None
            if request.user.is_authenticated:
                quiz_attempt = QuizAttempt.objects.filter(quiz=quiz, student=request.user).first()
            quizzes.append({'quiz': quiz, 'attempt': quiz_attempt, 'lesson': lesson})
    
    return render(request, 'course_detail.html', {
        'course': course,
        'lessons': lessons,
        'assignments': assignments,
        'quizzes': quizzes,
        'progress': progress
    })

@login_required
def enroll_course(request, course_id):
    if request.user.role != 'student':
        return JsonResponse({'error': 'Only students can enroll'}, status=403)
    
    course = get_object_or_404(Course, id=course_id)
    if request.user not in course.students.all():
        course.students.add(request.user)
        Progress.objects.get_or_create(student=request.user, course=course)
        send_notification(request.user, 'Course Enrolled', f'You have successfully enrolled in {course.title}', f'/course/{course.id}/')
        messages.success(request, f'Successfully enrolled in {course.title}!')
    else:
        messages.info(request, f'You are already enrolled in {course.title}')
    
    return redirect('student_dashboard')

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    if request.user.role != 'student':
        return redirect('instructor_dashboard')
    
    if request.user not in course.students.all():
        messages.warning(request, 'You need to enroll in this course first.')
        return redirect('course_detail', course_id=course.id)
    
    progress, created = Progress.objects.get_or_create(student=request.user, course=course)
    
    if request.method == 'POST' and 'complete' in request.POST:
        if lesson not in progress.completed_lessons.all():
            progress.completed_lessons.add(lesson)
            messages.success(request, f'✅ Lesson "{lesson.title}" marked as complete!')
            
            if progress.progress_percentage == 100:
                certificate, cert_created = Certificate.objects.get_or_create(student=request.user, course=course)
                if cert_created:
                    messages.success(request, '🎉 CONGRATULATIONS! You have completed the course! 🎉')
        else:
            messages.info(request, 'Lesson already completed')
        
        return redirect('course_detail', course_id=course.id)
    
    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'course': course,
        'progress': progress
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
        mime_type, encoding = mimetypes.guess_type(file_path)
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
        
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=request.user,
            score=score,
            percentage=percentage,
            passed=passed,
            answers=answers,
            completed_at=timezone.now()
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
    return render(request, 'take_quiz.html', {
        'quiz': quiz,
        'lesson': lesson,
        'questions': questions
    })

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
    
    return render(request, 'submit_assignment.html', {
        'assignment': assignment,
        'submission': existing
    })

@login_required
def certificates(request):
    if request.user.role != 'student':
        return redirect('instructor_dashboard')
    
    certificates = Certificate.objects.filter(student=request.user).select_related('course')
    return render(request, 'certificates.html', {'certificates': certificates})

@login_required
def debug_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    progress, created = Progress.objects.get_or_create(student=request.user, course=course)
    
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
    
    certificate, created = Certificate.objects.get_or_create(student=request.user, course=course)
    
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
    
    return render(request, 'instructor_dashboard.html', {
        'courses': courses,
        'total_courses': courses.count(),
        'total_students': total_students,
        'total_lessons': total_lessons,
        'pending_grading': pending_grading
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
                title=title,
                description=description,
                instructor=request.user,
                level=level,
                price=price,
                status='published'
            )
            messages.success(request, f'Course "{title}" created successfully!')
            return redirect('manage_course', course_id=course.id)
        else:
            messages.error(request, 'Course title is required')
    
    return render(request, 'instructor/create_course.html')

@login_required
@user_passes_test(is_instructor)
def manage_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lessons = course.lessons.all().order_by('order')
    assignments = course.assignments.all()
    students = course.students.all()
    
    return render(request, 'instructor/manage_course.html', {
        'course': course,
        'lessons': lessons,
        'assignments': assignments,
        'students': students
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
                course=course,
                title=title,
                content=content,
                video_url=video_url,
                duration=duration,
                order=order
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
        quiz, created = Quiz.objects.get_or_create(lesson=lesson)
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
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        points = request.POST.get('points', 10)
        correct_answer = request.POST.get('correct_answer')
        
        QuizQuestion.objects.create(
            quiz=quiz,
            question_text=question_text,
            question_type=question_type,
            points=points,
            order=quiz.questions.count() + 1,
            option_a=request.POST.get('option_a', ''),
            option_b=request.POST.get('option_b', ''),
            option_c=request.POST.get('option_c', ''),
            option_d=request.POST.get('option_d', ''),
            correct_answer=correct_answer
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
                course=course,
                title=title,
                description=description,
                due_date=due_date,
                total_points=total_points
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
        'assignment': assignment,
        'submissions': submissions
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
                        'noreply@fundamalitinne.com',
                        [submission.student.email],
                        fail_silently=True
                    )
                except:
                    pass
                
                messages.success(request, f'Grade submitted! Student notified.')
                return redirect('view_submissions', assignment_id=submission.assignment.id)
        except ValueError:
            messages.error(request, 'Please enter a valid number for grade')
    
    return render(request, 'grade_submission.html', {'submission': submission})

# ==================== BULK STUDENT UPLOAD ====================

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
            user_id = data.get('id')
            User.objects.filter(id=user_id).delete()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'error': 'Failed to delete'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_bulk_upload(request):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST' and request.FILES.get('csv'):
        try:
            csv_file = request.FILES['csv']
            decoded = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded)
            reader = csv.DictReader(io_string)
            
            created = 0
            errors = []
            
            for row in reader:
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                password = row.get('password', 'Student@123')
                first_name = row.get('first_name', '')
                last_name = row.get('last_name', '')
                
                if username and email:
                    user, created_flag = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
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
        
        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return redirect('bulk_upload_page')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('bulk_upload_page')
        
        try:
            data = csv_file.read().decode('utf-8')
            io_string = io.StringIO(data)
            reader = csv.DictReader(io_string)
            
            added = 0
            errors = []
            
            for row in reader:
                username = row.get('username', '').strip()
                email = row.get('email', '').strip()
                password = row.get('password', 'Mal@@@123')
                first_name = row.get('first_name', '')
                last_name = row.get('last_name', '')
                
                if not username or not email:
                    errors.append(f'Missing username or email')
                    continue
                
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
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
                                f'Hello {username},\n\nYour account has been created.\n\nUsername: {username}\nPassword: {password}\n\nLogin here: http://127.0.0.1:8000/login/\n\nRegards,\nFunda Malitinne Team',
                                'noreply@fundamalitinne.com',
                                [email],
                                fail_silently=True
                            )
                        except:
                            pass
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
            messages.error(request, f'Error processing CSV: {str(e)}')
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
        io_string = io.StringIO(data)
        reader = csv.DictReader(io_string)
        
        added = 0
        errors = []
        
        for row in reader:
            username = row.get('username')
            email = row.get('email')
            password = row.get('password', 'Password123!')
            
            if username and email:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'email': email, 'role': 'student'}
                )
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
    
    context = {
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
    }
    return render(request, 'custom_admin/dashboard.html', context)

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

# ==================== NOTIFICATION VIEWS ====================

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

# ==================== FORUM SYSTEM ====================

@login_required
def discussion_detail(request, topic_id):
    """View a single discussion topic and its replies"""
    topic = get_object_or_404(ForumTopic, id=topic_id)
    lesson = topic.lesson
    
    # Check permissions
    if request.user.role == 'student':
        if request.user not in lesson.course.students.all():
            messages.warning(request, 'You need to be enrolled in this course to view discussions.')
            return redirect('course_detail', course_id=lesson.course.id)
    elif request.user.role == 'instructor':
        if lesson.course.instructor != request.user and request.user.role != 'admin':
            messages.error(request, 'You do not have permission to view this discussion.')
            return redirect('instructor_dashboard')
    
    # Get all posts (replies) for this topic
    posts = topic.posts.filter(parent=None).order_by('created_at')
    
    # Handle new reply
    if request.method == 'POST' and 'add_reply' in request.POST:
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_reply_id')
        
        if content:
            parent = None
            if parent_id:
                parent = get_object_or_404(ForumPost, id=parent_id)
            
            ForumPost.objects.create(
                topic=topic,
                author=request.user,
                content=content,
                parent=parent
            )
            messages.success(request, 'Your reply has been posted.')
        else:
            messages.error(request, 'Please enter some content for your reply.')
        
        return redirect('discussion_detail', topic_id=topic.id)
    
    # Handle delete reply (instructor only)
    if request.method == 'POST' and 'delete_reply' in request.POST:
        if request.user.role == 'instructor' and lesson.course.instructor == request.user:
            reply_id = request.POST.get('reply_id')
            try:
                reply = ForumPost.objects.get(id=reply_id)
                reply.delete()
                messages.success(request, 'Reply deleted successfully.')
            except ForumPost.DoesNotExist:
                messages.error(request, 'Reply not found.')
        else:
            messages.error(request, 'You do not have permission to delete this reply.')
        
        return redirect('discussion_detail', topic_id=topic.id)
    
    # Prepare replies with nested structure
    reply_list = []
    for post in posts:
        reply_data = {
            'id': post.id,
            'author': post.author,
            'content': post.content,
            'created_at': post.created_at,
            'likes_count': post.likes.count(),
            'replies': post.replies.all().order_by('created_at'),
            'can_delete': request.user.role == 'instructor' and lesson.course.instructor == request.user
        }
        reply_list.append(reply_data)
    
    context = {
        'discussion': topic,
        'lesson': lesson,
        'posts': reply_list,
        'can_delete_discussion': request.user.role == 'instructor' and lesson.course.instructor == request.user
    }
    
    return render(request, 'discussion/discussion_detail.html', context)



@login_required
def toggle_discussion_pin(request, discussion_id):
    """Toggle pin status of a discussion (instructor only)"""
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
    """Toggle lock status of a discussion (instructor only)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        topic = get_object_or_404(ForumTopic, id=discussion_id)
        
        if request.user.role != 'instructor' or topic.lesson.course.instructor != request.user:
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        topic.is_locked = not topic.is_locked
        topic.save()
        
        return JsonResponse({'success': True, 'is_locked': topic.is_locked})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)






# Add this function near your other discussion-related views (around the lesson_discussions function)

@login_required
def delete_discussion(request, discussion_id):
    """Delete a discussion topic (instructor only)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        topic = get_object_or_404(ForumTopic, id=discussion_id)
        lesson = topic.lesson
        
        # Check if user is instructor of this course
        if request.user.role != 'instructor' or lesson.course.instructor != request.user:
            return JsonResponse({'error': 'You do not have permission to delete this discussion'}, status=403)
        
        # Delete all posts first (cascade should handle this, but to be safe)
        topic.posts.all().delete()
        topic.delete()
        
        return JsonResponse({'success': True, 'message': 'Discussion deleted successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ==================== COURSE ROSTER ====================

@login_required
def course_roster(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.role == 'student' and request.user not in course.students.all():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('student_dashboard')
    
    if request.user.role == 'instructor' and course.instructor != request.user:
        messages.error(request, 'You do not own this course.')
        return redirect('instructor_dashboard')
    
    students = []
    for student in course.students.all():
        progress, _ = Progress.objects.get_or_create(student=student, course=course)
        
        attendance_count = Attendance.objects.filter(student=student, course=course, status='present').count()
        total_attendance = Attendance.objects.filter(student=student, course=course).count()
        attendance_percent = int((attendance_count / total_attendance) * 100) if total_attendance > 0 else 0
        
        submissions = Submission.objects.filter(student=student, assignment__course=course, grade__isnull=False)
        avg_grade = submissions.aggregate(avg=Avg('grade'))['avg'] or 0
        
        students.append({
            'student': student,
            'progress': progress.progress_percentage,
            'attendance': attendance_percent,
            'grade': f"{avg_grade:.0f}%" if avg_grade > 0 else "N/A"
        })
    
    return render(request, 'course_roster.html', {'course': course, 'students': students})

# ==================== ATTENDANCE ====================

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
    
    course_id = request.POST.get('course_id')
    student_id = request.POST.get('student_id')
    status = request.POST.get('status')
    date = request.POST.get('date')
    
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.role != 'instructor' or course.instructor != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    student = get_object_or_404(User, id=student_id)
    
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        course=course,
        date=date,
        defaults={'status': status, 'marked_by': request.user}
    )
    
    if not created:
        attendance.status = status
        attendance.marked_by = request.user
        attendance.save()
    
    return JsonResponse({'success': True})

# ==================== MODERN LESSON API ENDPOINTS ====================

@login_required
def api_module_content(request, module_id):
    try:
        module = LessonModule.objects.get(id=module_id)
    except LessonModule.DoesNotExist:
        return JsonResponse({'error': 'Module not found'}, status=404)
    
    if request.user.role == 'student' and request.user not in module.lesson.course.students.all():
        return JsonResponse({'error': 'You are not enrolled in this course'}, status=403)
    
    previous_modules = module.lesson.modules.filter(order__lt=module.order)
    for prev_module in previous_modules:
        progress_exists = UserModuleProgress.objects.filter(student=request.user, module=prev_module, completed=True).exists()
        if not progress_exists:
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
    
    previous_modules = module.lesson.modules.filter(order__lt=module.order)
    for prev_module in previous_modules:
        progress_exists = UserModuleProgress.objects.filter(student=request.user, module=prev_module, completed=True).exists()
        if not progress_exists:
            return JsonResponse({'error': 'Complete previous modules first'}, status=403)
    
    questions = []
    if hasattr(module.lesson, 'quiz'):
        quiz = module.lesson.quiz
        quiz_questions = quiz.questions.all()
        
        for q in quiz_questions:
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
    
    previous_modules = module.lesson.modules.filter(order__lt=module.order)
    for prev_module in previous_modules:
        progress_exists = UserModuleProgress.objects.filter(student=request.user, module=prev_module, completed=True).exists()
        if not progress_exists:
            return JsonResponse({'error': f'Complete "{prev_module.title}" first', 'required_module': prev_module.title}, status=403)
    
    progress, created = UserModuleProgress.objects.get_or_create(student=request.user, module=module)
    
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
    bonus_xp = 50
    streak.total_xp += bonus_xp
    streak.save()
    
    return JsonResponse({
        'success': True,
        'xp_earned': bonus_xp,
        'lesson_completed': True,
        'course_progress': progress.progress_percentage,
        'message': f'Congratulations! You completed "{lesson.title}"! +{bonus_xp} XP'
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


# ==================== INSTRUCTOR STUDENT VIEW (READ ONLY) ====================

@login_required
@user_passes_test(is_instructor)
def instructor_student_view(request, user_id):
    """Instructor view of student profile - Read only"""
    student = get_object_or_404(User, id=user_id, role='student')
    
    # Check if this student is enrolled in any of the instructor's courses
    instructor_courses = Course.objects.filter(instructor=request.user)
    is_enrolled = student.enrolled_courses.filter(id__in=instructor_courses).exists()
    
    if not is_enrolled and request.user.role != 'admin':
        messages.error(request, 'You can only view students enrolled in your courses.')
        return redirect('instructor_dashboard')
    
    # Get student profile data
    profile, created = LearnerProfile.objects.get_or_create(user=student)
    documents = student.documents.all()
    logbooks = student.logbook_entries.all().order_by('-entry_date')[:10]
    
    # Get academic progress
    enrolled_courses = student.enrolled_courses.all()
    course_progress = []
    for course in enrolled_courses:
        progress, _ = Progress.objects.get_or_create(student=student, course=course)
        course_progress.append({
            'course': course,
            'progress': progress.progress_percentage,
            'completed_lessons': progress.completed_lessons.count(),
            'total_lessons': course.lessons.count()
        })
    
    # Get certificates
    certificates = Certificate.objects.filter(student=student)
    
    context = {
        'student': student,
        'profile': profile,
        'documents': documents,
        'logbooks': logbooks,
        'course_progress': course_progress,
        'certificates': certificates,
        'can_edit': False,  # Read-only mode
        'is_instructor': True,
    }
    return render(request, 'instructor/student_profile_view.html', context)

# ==================== LEARNER PROFILE MANAGEMENT (QCTO COMPLIANT) ====================

@login_required
@user_passes_test(is_admin)
def learner_profile_view(request, user_id):
    learner = get_object_or_404(User, id=user_id)
    profile, created = LearnerProfile.objects.get_or_create(user=learner)
    
    AuditLog.objects.create(user=request.user, action='view', resource_type='LearnerProfile', resource_id=user_id, ip_address=get_client_ip(request))
    
    courses = Course.objects.filter(status='published')
    documents = learner.documents.all()
    logbooks = learner.logbook_entries.all()
    
    return render(request, 'admin/learner_profile.html', {
        'learner': learner, 'profile': profile, 'courses': courses,
        'documents': documents, 'logbooks': logbooks
    })

@login_required
@user_passes_test(is_admin)
def save_learner_profile(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    learner = get_object_or_404(User, id=user_id)
    profile, created = LearnerProfile.objects.get_or_create(user=learner)
    
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
    timestamp = int(time.time())
    unique_filename = f"{user_id}_{doc_type}_{timestamp}_{filename}"
    
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
        user=learner, entry_date=datetime.strptime(data.get('entry_date'), '%Y-%m-%d').date(),
        hours_spent=data.get('hours_spent', 0), description=data.get('description', ''),
        skills_learned=data.get('skills_learned', '')
    )
    
    return JsonResponse({'success': True, 'entry': {
        'id': entry.id, 'date': entry.entry_date.strftime('%Y-%m-%d'),
        'hours': str(entry.hours_spent), 'description': entry.description, 'skills': entry.skills_learned
    }})

@login_required
@user_passes_test(is_admin)
def export_learner_report(request, user_id):
    """Export learner profile as HTML report (no external dependencies)"""
    learner = get_object_or_404(User, id=user_id)
    profile, created = LearnerProfile.objects.get_or_create(user=learner)
    documents = learner.documents.all()
    logbooks = learner.logbook_entries.all().order_by('-entry_date')
    
    # Get course progress
    course_progress = []
    for course in learner.enrolled_courses.all():
        progress, _ = Progress.objects.get_or_create(student=learner, course=course)
        course_progress.append({
            'course': course,
            'progress': progress.progress_percentage,
            'completed_lessons': progress.completed_lessons.count(),
            'total_lessons': course.lessons.count()
        })
    
    # Build document rows
    document_rows = ""
    for doc in documents:
        document_rows += f"""
        <tr>
            <td>{doc.get_document_type_display()}</td>
            <td>{doc.file_name}</td>
            <td>{doc.upload_date.strftime('%Y-%m-%d')}</td>
            <td>{doc.file_size // 1024} KB</td>
        </tr>
        """
    
    if not documents:
        document_rows = '<tr><td colspan="4" style="text-align: center;">No documents uploaded</td></tr>'
    
    # Build logbook rows
    logbook_rows = ""
    for entry in logbooks:
        logbook_rows += f"""
        <tr>
            <td>{entry.entry_date.strftime('%Y-%m-%d')}</td>
            <td>{entry.hours_spent}</td>
            <td>{entry.description[:100]}</td>
            <td>{entry.skills_learned[:100] if entry.skills_learned else 'N/A'}</td>
            <td><span style="color: {'green' if entry.supervisor_approved else 'orange'};">{'Approved' if entry.supervisor_approved else 'Pending'}</span></td>
        </tr>
        """
    
    if not logbooks:
        logbook_rows = '<tr><td colspan="5" style="text-align: center;">No logbook entries</td></tr>'
    
    # Build course progress rows
    progress_rows = ""
    for cp in course_progress:
        status = "Completed" if cp['progress'] == 100 else "In Progress" if cp['progress'] > 0 else "Not Started"
        color = "green" if cp['progress'] == 100 else "orange" if cp['progress'] > 0 else "gray"
        progress_rows += f"""
        <tr>
            <td>{cp['course'].title}</td>
            <td>
                <div style="background: #e0e0e0; border-radius: 10px; height: 20px; width: 100%; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #9f7734, #7a5828); width: {cp['progress']}%; height: 100%; border-radius: 10px; text-align: center; color: white; font-size: 11px; line-height: 20px;">
                        {cp['progress']}%
                    </div>
                </div>
            </td>
            <td>{cp['completed_lessons']} / {cp['total_lessons']}</td>
            <td><span style="color: {color};">{status}</span></td>
        </tr>
        """
    
    if not course_progress:
        progress_rows = '<tr><td colspan="4" style="text-align: center;">No courses enrolled</td></tr>'
    
    # Generate full HTML
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>QCTO Learner Report - {learner.get_full_name() or learner.username}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #9f7734;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #9f7734;
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            color: #666;
            margin: 5px 0;
        }}
        .section {{
            margin-bottom: 25px;
            page-break-inside: avoid;
        }}
        .section-title {{
            background: #9f7734;
            color: white;
            padding: 10px 15px;
            margin: 20px 0 10px 0;
            font-size: 18px;
            font-weight: bold;
            border-radius: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        td, th {{
            padding: 10px;
            border: 1px solid #ddd;
        }}
        th {{
            background: #f5f5f5;
            text-align: left;
            font-weight: 600;
        }}
        .info-table td:first-child {{
            background: #f9f9f9;
            font-weight: bold;
            width: 30%;
        }}
        .footer {{
            margin-top: 50px;
            font-size: 10px;
            text-align: center;
            border-top: 1px solid #ccc;
            padding-top: 20px;
        }}
        .popia-notice {{
            background: #f0f9ff;
            padding: 15px;
            margin-top: 20px;
            font-size: 10px;
            border-left: 4px solid #9f7734;
        }}
        .watermark {{
            text-align: center;
            font-size: 9px;
            color: #999;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📄 QCTO Learner Profile Report</h1>
        <p><strong>Generated on:</strong> {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Generated by:</strong> {request.user.get_full_name() or request.user.username}</p>
        <p><strong>Report ID:</strong> QCTO-{learner.id}-{timezone.now().strftime('%Y%m%d')}</p>
    </div>
    
    <div class="section">
        <div class="section-title">👤 Section A: Personal Information</div>
        <table class="info-table">
            <tr><td>Full Name:</td><td>{learner.get_full_name() or learner.username}</td></tr>
            <tr><td>ID Number:</td><td>{learner.id_number or 'Not provided'}</td></tr>
            <tr><td>Date of Birth:</td><td>{learner.date_of_birth.strftime('%Y-%m-%d') if learner.date_of_birth else 'Not provided'}</td></tr>
            <tr><td>Gender:</td><td>{learner.get_gender_display() or 'Not provided'}</td></tr>
            <tr><td>Nationality:</td><td>{learner.nationality or 'South African'}</td></tr>
            <tr><td>Email:</td><td>{learner.email}</td></tr>
            <tr><td>Phone Number:</td><td>{learner.contact_number or 'Not provided'}</td></tr>
            <tr><td>Physical Address:</td><td>{profile.physical_address or 'Not provided'}</td></tr>
            <tr><td>Preferred Language:</td><td>{learner.preferred_language or 'English'}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">🎓 Section B: Academic Information</div>
        <table class="info-table">
            <tr><td>Current Course:</td><td>{profile.current_course.title if profile.current_course else 'Not enrolled'}</td></tr>
            <tr><td>Enrollment Date:</td><td>{profile.enrollment_date.strftime('%Y-%m-%d') if profile.enrollment_date else 'Not set'}</td></tr>
            <tr><td>Expected Completion:</td><td>{profile.expected_completion_date.strftime('%Y-%m-%d') if profile.expected_completion_date else 'Not set'}</td></tr>
            <tr><td>Certificate Issued:</td><td>{'Yes' if profile.certificate_issued else 'No'}</td></tr>
            <tr><td>Certificate Date:</td><td>{profile.certificate_issued_date.strftime('%Y-%m-%d') if profile.certificate_issued_date else 'N/A'}</td></tr>
            <tr><td>POPIA Consent:</td><td>{'Yes' if profile.popia_consent else 'No'}</td></tr>
            <tr><td>Consent Date:</td><td>{profile.popia_consent_date.strftime('%Y-%m-%d') if profile.popia_consent_date else 'N/A'}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">📊 Section C: Course Progress</div>
        <table>
            <thead>
                <tr>
                    <th>Course Title</th>
                    <th>Progress</th>
                    <th>Lessons Completed</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {progress_rows}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">📄 Section D: Uploaded Documents</div>
        <table>
            <thead>
                <tr>
                    <th>Document Type</th>
                    <th>File Name</th>
                    <th>Upload Date</th>
                    <th>Size</th>
                </tr>
            </thead>
            <tbody>
                {document_rows}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">📘 Section E: Logbook / Workplace Experience</div>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Hours</th>
                    <th>Description</th>
                    <th>Skills Learned</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {logbook_rows}
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">🏢 Section F: Internship / Workplace Details</div>
        <table class="info-table">
            <tr><td>Host Company:</td><td>{profile.host_company_name or 'Not provided'}</td></tr>
            <tr><td>MoU Period:</td><td>{profile.mou_start_date.strftime('%Y-%m-%d') if profile.mou_start_date else 'N/A'} to {profile.mou_end_date.strftime('%Y-%m-%d') if profile.mou_end_date else 'N/A'}</td></tr>
            <tr><td>Supervisor Name:</td><td>{profile.supervisor_name or 'Not assigned'}</td></tr>
            <tr><td>Supervisor Contact:</td><td>{profile.supervisor_phone or 'N/A'} / {profile.supervisor_email or 'N/A'}</td></tr>
        </table>
    </div>
    
    <div class="footer">
        <div class="popia-notice">
            <strong>🔒 POPIA Notice (Protection of Personal Information Act No. 4 of 2013):</strong><br>
            This document contains personal information that is protected under POPIA. Unauthorized disclosure, distribution, or copying of this information is prohibited. 
            The information contained in this report is for official QCTO verification and training provider purposes only. 
            All personal information is processed in accordance with the POPIA regulations.
        </div>
        <div class="watermark">
            Funda Malitinne Learning Management System | QCTO Compliant Report | Version 1.0
        </div>
    </div>
</body>
</html>
"""
    
    # Log the export for audit trail
    AuditLog.objects.create(
        user=request.user,
        action='export',
        resource_type='LearnerProfile',
        resource_id=user_id,
        ip_address=get_client_ip(request),
        details={'format': 'HTML', 'report_type': 'QCTO_Learner_Report'}
    )
    
    # Return as HTML file (can be saved as HTML or printed to PDF by browser)
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="learner_report_{learner.username}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.html"'
    return response

@login_required
@user_passes_test(is_admin)
def get_backup_log_api(request):
    backups = BackupLog.objects.all()[:10]
    return JsonResponse({'backups': [{'timestamp': b.backup_timestamp.isoformat(), 'type': b.backup_type, 'size': b.backup_size, 'status': b.status} for b in backups]})



@login_required
def instructor_dashboard(request):
    if request.user.role != 'instructor':
        return redirect('student_dashboard')
    
    courses = Course.objects.filter(instructor=request.user)
    
    total_students = sum(course.students.count() for course in courses)
    total_lessons = sum(course.lessons.count() for course in courses)
    pending_grading = Submission.objects.filter(assignment__course__instructor=request.user, grade__isnull=True).count()
    
    # Get all students enrolled in instructor's courses (for the students table)
    all_students = []
    for course in courses:
        for student in course.students.all():
            progress, _ = Progress.objects.get_or_create(student=student, course=course)
            enrollment_date = student.date_joined.date() if student.date_joined else None
            
            # Check if student already added (avoid duplicates if in multiple courses)
            if not any(s['student'].id == student.id for s in all_students):
                all_students.append({
                    'student': student,
                    'course': course,
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
def contact_form_submit(request):
    """Handle contact form submissions"""
    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            organisation = request.POST.get('organisation', '')
            client_type = request.POST.get('client_type', '')
            message = request.POST.get('message', '')
            
            # Validate required fields
            if not first_name or not last_name or not email or not message:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('company_home')  # Remove the +#contact part
            
            # Prepare email content
            full_name = f"{first_name} {last_name}"
            
            subject = f"New Contact Form Submission from {full_name}"
            
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #9f7734;">New Contact Form Submission</h2>
                <p><strong>Name:</strong> {full_name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Organisation:</strong> {organisation or 'Not provided'}</p>
                <p><strong>I am a:</strong> {client_type or 'Not specified'}</p>
                <p><strong>Message:</strong></p>
                <p style="background: #f5f5f5; padding: 15px; border-left: 4px solid #9f7734;">{message.replace(chr(10), '<br>')}</p>
                <hr>
                <p style="font-size: 12px; color: #666;">Submitted from: Funda Malitinne Website Contact Form</p>
            </body>
            </html>
            """
            
            plain_message = f"""
            New Contact Form Submission
            
            Name: {full_name}
            Email: {email}
            Organisation: {organisation or 'Not provided'}
            I am a: {client_type or 'Not specified'}
            
            Message:
            {message}
            """
            
            # Send to your email address
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['sah.sakhile@gmail.com'],
                html_message=html_message,
                fail_silently=False
            )
            
            # Send auto-reply to the user
            auto_reply_html = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #9f7734;">Thank you for contacting Malitinne!</h2>
                <p>Dear {full_name},</p>
                <p>Thank you for reaching out to us. We have received your message and one of our representatives will get back to you within 24-48 business hours.</p>
                <p><strong>Your message summary:</strong></p>
                <p style="background: #f5f5f5; padding: 15px; border-left: 4px solid #9f7734;">{message[:200]}{'...' if len(message) > 200 else ''}</p>
                <p>In the meantime, you can:</p>
                <ul>
                    <li>Visit our <a href="https://www.malitinne.co.za/lms/">LMS Portal</a> to explore available courses</li>
                    <li>Call us directly at 073 931 7923</li>
                </ul>
                <p>Best regards,<br>
                <strong>Malitinne Team</strong></p>
                <hr>
                <p style="font-size: 10px; color: #666;">This is an automated response. Please do not reply to this email.</p>
            </body>
            </html>
            """
            
            send_mail(
                subject="Thank you for contacting Malitinne",
                message=f"Thank you for contacting us, {full_name}. We will get back to you soon.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=auto_reply_html,
                fail_silently=True
            )
            
            messages.success(request, 'Thank you! Your message has been sent. We will contact you soon.')
            
        except Exception as e:
            # Log the error for debugging
            print(f"Contact form error: {str(e)}")
            messages.error(request, 'An error occurred. Please try again or call us directly at 073 931 7923.')
        
        # Redirect with anchor to contact section
        response = redirect('company_home')
        response['Location'] += '#contact'
        return response
    
    return redirect('company_home')

@login_required
@user_passes_test(is_admin)
def export_learner_report(request, user_id):
    """Export learner profile as HTML report (no PDF dependencies)"""
    learner = get_object_or_404(User, id=user_id)
    profile = LearnerProfile.objects.get_or_create(user=learner)[0]
    documents = learner.documents.all()
    logbooks = learner.logbook_entries.all().order_by('-entry_date')
    
    # Get course progress
    course_progress = []
    for course in learner.enrolled_courses.all():
        progress, _ = Progress.objects.get_or_create(student=learner, course=course)
        course_progress.append({
            'course': course,
            'progress': progress.progress_percentage,
            'completed_lessons': progress.completed_lessons.count(),
            'total_lessons': course.lessons.count()
        })
    
    # Generate HTML report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>QCTO Learner Report - {learner.get_full_name()|default:learner.username}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #9f7734;
                padding-bottom: 20px;
            }}
            .header h1 {{
                color: #9f7734;
                margin: 0;
            }}
            .section {{
                margin-bottom: 25px;
                page-break-inside: avoid;
            }}
            .section-title {{
                background: #9f7734;
                color: white;
                padding: 10px;
                margin: 20px 0 10px 0;
                font-size: 16px;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }}
            td, th {{
                padding: 8px;
                border: 1px solid #ddd;
            }}
            th {{
                background: #f5f5f5;
                text-align: left;
            }}
            .footer {{
                margin-top: 50px;
                font-size: 10px;
                text-align: center;
                border-top: 1px solid #ccc;
                padding-top: 20px;
            }}
            .popia-notice {{
                background: #f0f9ff;
                padding: 15px;
                margin-top: 20px;
                font-size: 9px;
            }}
            .label {{
                font-weight: bold;
                width: 30%;
                background: #f9f9f9;
            }}
            .progress-bar {{
                background: #e0e0e0;
                border-radius: 10px;
                height: 20px;
                overflow: hidden;
            }}
            .progress-fill {{
                background: linear-gradient(90deg, #9f7734, #7a5828);
                height: 100%;
                border-radius: 10px;
                text-align: center;
                color: white;
                font-size: 11px;
                line-height: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>QCTO Learner Profile Report</h1>
            <p>Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Generated by: {request.user.get_full_name()|default:request.user.username}</p>
        </div>
        
        <div class="section">
            <div class="section-title">Section A: Personal Information</div>
            <table>
                <tr><td class="label">Full Name:</td><td>{learner.get_full_name()|default:learner.username}</td></tr>
                <tr><td class="label">ID Number:</td><td>{learner.id_number|default:"Not provided"}</td></tr>
                <tr><td class="label">Date of Birth:</td><td>{learner.date_of_birth.strftime('%Y-%m-%d') if learner.date_of_birth else "Not provided"}</td></tr>
                <tr><td class="label">Gender:</td><td>{learner.get_gender_display()|default:"Not provided"}</td></tr>
                <tr><td class="label">Nationality:</td><td>{learner.nationality|default:"South African"}</td></tr>
                <tr><td class="label">Email:</td><td>{learner.email}</td></tr>
                <tr><td class="label">Phone:</td><td>{learner.contact_number|default:"Not provided"}</td></tr>
                <tr><td class="label">Address:</td><td>{profile.physical_address|default:"Not provided"}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Section B: Academic Information</div>
            <table>
                <tr><td class="label">Current Course:</td><td>{profile.current_course.title if profile.current_course else "Not enrolled"}</td></tr>
                <tr><td class="label">Enrollment Date:</td><td>{profile.enrollment_date.strftime('%Y-%m-%d') if profile.enrollment_date else "Not set"}</td></tr>
                <tr><td class="label">Certificate Issued:</td><td>{"Yes" if profile.certificate_issued else "No"}</td></tr>
                <tr><td class="label">Certificate Date:</td><td>{profile.certificate_issued_date.strftime('%Y-%m-%d') if profile.certificate_issued_date else "N/A"}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Section C: Course Progress</div>
            <table>
                <thead><tr><th>Course</th><th>Progress</th><th>Lessons Completed</th><th>Status</th></tr></thead>
                <tbody>
                    {''.join([f'<tr><td>{cp["course"].title}</td><td><div class="progress-bar"><div class="progress-fill" style="width: {cp["progress"]}%">{cp["progress"]}%</div></div></td><td>{cp["completed_lessons"]}/{cp["total_lessons"]}</td><td>{"Completed" if cp["progress"] == 100 else "In Progress"}</td></tr>' for cp in course_progress])}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Section D: Documents Uploaded</div>
            <table>
                <thead><tr><th>Document Type</th><th>File Name</th><th>Upload Date</th></tr></thead>
                <tbody>
                    {''.join([f'<tr><td>{doc.get_document_type_display()}</td><td>{doc.file_name}</td><td>{doc.upload_date.strftime("%Y-%m-%d")}</td></tr>' for doc in documents])}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">Section E: Logbook Entries</div>
            <table>
                <thead><tr><th>Date</th><th>Hours</th><th>Description</th><th>Skills Learned</th></tr></thead>
                <tbody>
                    {''.join([f'<tr><td>{entry.entry_date.strftime("%Y-%m-%d")}</td><td>{entry.hours_spent}</td><td>{entry.description|truncatewords:20}</td><td>{entry.skills_learned|truncatewords:10}</td></tr>' for entry in logbooks])}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>This report is QCTO compliant and contains verified learner information.</p>
            <div class="popia-notice">
                <strong>POPIA Notice:</strong> This document contains personal information protected under the Protection of Personal Information Act (POPIA) No. 4 of 2013. 
                Unauthorized disclosure is prohibited. The information in this report is for official QCTO verification purposes only.
            </div>
        </div>
    </body>
    </html>
    """
    
    # Log the export
    AuditLog.objects.create(
        user=request.user,
        action='export',
        resource_type='LearnerProfile',
        resource_id=user_id,
        ip_address=get_client_ip(request),
        details={'format': 'HTML'}
    )
    
    # Return as HTML file (can be printed to PDF by user or saved as HTML)
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="learner_report_{learner.username}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.html"'
    return response