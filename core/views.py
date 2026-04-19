from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse, FileResponse, Http404
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.db.models import Count, Q
from .models import User, Course, Lesson, Assignment, Submission, Progress, Quiz, QuizQuestion, QuizAttempt, Certificate, Notification
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import json
import csv
import io
import mimetypes
import os

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
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        # Get personal details
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
        
        # Validation
        if password != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            # Create user with pending approval
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='student',  # Force student role only
                is_active=True,
                is_approved=False  # Needs admin approval
            )
            
            # Save additional fields
            user.id_number = id_number
            if date_of_birth:
                user.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            user.gender = gender
            user.nationality = nationality
            user.contact_number = contact_number
            user.disability = disability
            user.preferred_language = preferred_language
            user.save()
            
            # Send notification email to student
            try:
                html_message = render_to_string('email/registration_pending.html', {
                    'user': user,
                    'full_name': f"{first_name} {last_name}"
                })
                send_mail(
                    'Registration Received - Funda Malitinne LMS',
                    f'Dear {first_name},\n\nYour registration has been received. You will receive an email once your account is approved.\n\nRegards,\nFunda Malitinne Team',
                    'noreply@fundamalitinne.com',
                    [email],
                    html_message=html_message,
                    fail_silently=True
                )
            except:
                pass
            
            # Send notification to admins
            admins = User.objects.filter(role='admin', is_approved=True)
            for admin in admins:
                try:
                    html_message = render_to_string('email/admin_approval_needed.html', {
                        'user': user,
                        'admin': admin
                    })
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
            
            messages.success(request, 'Registration submitted successfully! Please wait for admin approval. You will receive an email once approved.')
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
            messages.success(request, 'Password reset successful! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
    
    return render(request, 'reset_password.html', {'valid': valid, 'user': user})

# ==================== HOME VIEW ====================

def home(request):
    courses = Course.objects.filter(status='published')[:6]
    return render(request, 'home.html', {'courses': courses})

# ==================== STUDENT VIEWS ====================

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('instructor_dashboard')
    
    enrolled_courses = request.user.enrolled_courses.all()
    available_courses = Course.objects.filter(status='published').exclude(id__in=enrolled_courses)
    
    # Calculate progress for each course
    for course in enrolled_courses:
        progress, _ = Progress.objects.get_or_create(student=request.user, course=course)
        course.progress_percent = progress.progress_percentage
        course.completed = progress.progress_percentage == 100
    
    # Get recent notifications
    notifications = request.user.notifications.filter(is_read=False)[:5]
    
    return render(request, 'student_dashboard.html', {
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses,
        'notifications': notifications,
        'notification_count': notifications.count()
    })

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    assignments = course.assignments.all()
    quizzes = []
    
    progress = None
    if request.user.role == 'student':
        progress, created = Progress.objects.get_or_create(student=request.user, course=course)
        # Check if user is enrolled
        if request.user not in course.students.all():
            messages.warning(request, 'You need to enroll in this course first.')
            return redirect('student_dashboard')
    
    # Get quizzes for each lesson
    for lesson in lessons:
        if hasattr(lesson, 'quiz'):
            quiz = lesson.quiz
            quiz_attempt = None
            if request.user.is_authenticated:
                quiz_attempt = QuizAttempt.objects.filter(quiz=quiz, student=request.user).first()
            quizzes.append({
                'quiz': quiz,
                'attempt': quiz_attempt,
                'lesson': lesson
            })
    
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
    
    # Check if student is enrolled
    if request.user not in course.students.all():
        messages.warning(request, 'You need to enroll in this course first.')
        return redirect('course_detail', course_id=course.id)
    
    # Get or create progress
    progress, created = Progress.objects.get_or_create(
        student=request.user,
        course=course
    )
    
    # Handle mark as complete
    if request.method == 'POST':
        if 'complete' in request.POST:
            if lesson not in progress.completed_lessons.all():
                progress.completed_lessons.add(lesson)
                messages.success(request, f'✅ Lesson "{lesson.title}" marked as complete!')
                
                # Check if course is now complete
                if progress.progress_percentage == 100:
                    # Generate certificate
                    certificate, cert_created = Certificate.objects.get_or_create(
                        student=request.user,
                        course=course
                    )
                    if cert_created:
                        messages.success(request, '🎉 CONGRATULATIONS! You have completed the course! 🎉')
                        messages.success(request, f'Your certificate number: {certificate.certificate_number}')
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
    
    # Check if user is enrolled (for students)
    if request.user.role == 'student':
        if request.user not in lesson.course.students.all():
            return HttpResponseForbidden("You are not enrolled in this course.")
    
    if not lesson.document:
        raise Http404("No document available for this lesson.")
    
    # Get the file path
    file_path = lesson.document.path
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise Http404("Document file not found.")
    
    # Read the file
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    # For PDF files - force display in browser
    if file_path.endswith('.pdf'):
        response = HttpResponse(file_data, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
    else:
        # For other files
        mime_type, encoding = mimetypes.guess_type(file_path)
        response = HttpResponse(file_data, content_type=mime_type or 'application/octet-stream')
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
    
    # Prevent caching issues
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    lesson = quiz.lesson
    course = lesson.course
    
    if request.user.role != 'student' or request.user not in course.students.all():
        messages.error(request, 'You need to be enrolled to take this quiz.')
        return redirect('course_detail', course_id=course.id)
    
    # Check if already attempted
    existing_attempt = QuizAttempt.objects.filter(quiz=quiz, student=request.user).first()
    if existing_attempt and existing_attempt.completed_at:
        messages.warning(request, 'You have already completed this quiz.')
        return redirect('course_detail', course_id=course.id)
    
    if request.method == 'POST':
        # Process quiz answers
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
        
        # Update progress
        progress, _ = Progress.objects.get_or_create(student=request.user, course=course)
        if lesson not in progress.completed_lessons.all():
            progress.completed_lessons.add(lesson)
        
        if passed:
            messages.success(request, f'Quiz completed! Score: {score}/{total_points} ({percentage:.0f}%) - PASSED!')
        else:
            messages.warning(request, f'Quiz completed! Score: {score}/{total_points} ({percentage:.0f}%) - Failed. Passing score is {quiz.passing_score}%')
        
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
        else:
            Submission.objects.create(
                assignment=assignment,
                student=request.user,
                file_upload=file
            )
        
        send_notification(assignment.course.instructor, 'New Submission', f'{request.user.username} submitted {assignment.title}', f'/instructor/grade/{existing.id if existing else "new"}/')
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
    
    # Check if user completed the course
    progress = get_object_or_404(Progress, student=request.user, course=course)
    
    if progress.progress_percentage < 100:
        messages.error(request, 'You must complete 100% of the course to get a certificate.')
        return redirect('course_detail', course_id=course.id)
    
    # Get or create certificate
    certificate, created = Certificate.objects.get_or_create(
        student=request.user,
        course=course
    )
    
    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Border
    p.setStrokeColorRGB(0.4, 0.2, 0.6)
    p.setLineWidth(5)
    p.rect(30, 30, width - 60, height - 60)
    
    # Title
    p.setFillColorRGB(0.4, 0.2, 0.6)
    p.setFont("Helvetica-Bold", 32)
    p.drawCentredString(width/2, height - 120, "CERTIFICATE OF COMPLETION")
    
    # Subtitle
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(width/2, height - 160, "This certificate is proudly presented to")
    
    # Name
    p.setFont("Helvetica-Bold", 28)
    p.setFillColorRGB(0.4, 0.2, 0.6)
    name = request.user.get_full_name() or request.user.username
    p.drawCentredString(width/2, height - 220, name.upper())
    
    # Description
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0, 0, 0)
    p.drawCentredString(width/2, height - 270, "For successfully completing the course")
    
    # Course name
    p.setFont("Helvetica-Bold", 18)
    p.setFillColorRGB(0.4, 0.2, 0.6)
    p.drawCentredString(width/2, height - 310, course.title)
    
    # Date
    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.drawCentredString(width/2, height - 380, f"Issued on: {certificate.issued_at.strftime('%B %d, %Y')}")
    p.drawCentredString(width/2, height - 400, f"Certificate Number: {certificate.certificate_number}")
    
    # Signature line
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
    
    total_students = sum(course.total_students for course in courses)
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
    lessons = course.lessons.all()
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
        return HttpResponseForbidden()
    
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
        return HttpResponseForbidden()
    
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
        return HttpResponseForbidden()
    
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
    
    return render(request, 'instructor/add_assignment.html', {'course': course})

@login_required
@user_passes_test(is_instructor)
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if assignment.course.instructor != request.user:
        return HttpResponseForbidden()
    
    submissions = assignment.submissions.all().order_by('-submitted_at')
    
    return render(request, 'instructor/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions
    })

@login_required
@user_passes_test(is_instructor)
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback', '')
        
        submission.grade = int(grade)
        submission.feedback = feedback
        submission.save()
        
        # Send email notification to student
        try:
            send_mail(
                f'Assignment Graded: {submission.assignment.title}',
                f'Hello {submission.student.username},\n\nYour assignment "{submission.assignment.title}" has been graded.\n\nGrade: {grade}/{submission.assignment.total_points}\n\nFeedback: {feedback}\n\nLogin to view details.\n\nRegards,\nFunda Malitinne LMS',
                'noreply@fundamalitinne.com',
                [submission.student.email],
                fail_silently=True
            )
        except:
            pass
        
        messages.success(request, f'Grade submitted! Student notified.')
        return redirect('view_submissions', assignment_id=submission.assignment.id)
    
    return render(request, 'grade_submission.html', {'submission': submission})

# ==================== BULK STUDENT UPLOAD ====================

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
                    errors.append(f'Missing username or email for row: {row}')
                    continue
                
                # Check if user exists
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'role': 'student'
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
                    # Update role if needed
                    if user.role != 'student':
                        user.role = 'student'
                        user.save()
                
                # Enroll in course
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
                    defaults={
                        'email': email,
                        'role': 'student'
                    }
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
        return redirect('home')
    
    context = {
        'total_courses': Course.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_instructors': User.objects.filter(role='instructor').count(),
        'total_submissions': Submission.objects.count(),
        'recent_courses': Course.objects.order_by('-created_at')[:10],
        'recent_users': User.objects.order_by('-date_joined')[:10],
    }
    return render(request, 'custom_admin/dashboard.html', context)

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