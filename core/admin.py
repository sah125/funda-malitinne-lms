from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from .models import User, Course, Lesson, Assignment, Submission, Progress, Quiz, QuizQuestion, QuizAttempt, Certificate, Notification

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_approved', 'is_staff')
    search_fields = ('username', 'email', 'id_number')
    list_editable = ('is_approved',)
    actions = ['approve_users', 'send_approval_emails']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Information', {'fields': ('id_number', 'date_of_birth', 'gender', 'nationality', 'contact_number', 'disability', 'preferred_language')}),
        ('Approval Status', {'fields': ('is_approved', 'approved_at')}),
        ('Role', {'fields': ('role',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Personal Information', {'fields': ('id_number', 'date_of_birth', 'gender', 'nationality', 'contact_number')}),
        ('Role', {'fields': ('role',)}),
    )
    
    def approve_users(self, request, queryset):
        for user in queryset:
            user.is_approved = True
            user.approved_at = timezone.now()
            user.save()
            
            try:
                html_message = render_to_string('email/registration_approved.html', {'user': user})
                send_mail(
                    'Registration Approved - Funda Malitinne LMS',
                    f'Dear {user.username},\n\nYour registration has been approved! You can now log in.\n\nUsername: {user.username}\n\nLogin here: http://127.0.0.1:8000/login/',
                    'noreply@fundamalitinne.com',
                    [user.email],
                    html_message=html_message,
                    fail_silently=True
                )
            except:
                pass
        self.message_user(request, f'{queryset.count()} users approved.')
    approve_users.short_description = "Approve selected users"
    
    def send_approval_emails(self, request, queryset):
        count = 0
        for user in queryset.filter(is_approved=True):
            try:
                html_message = render_to_string('email/registration_approved.html', {'user': user})
                send_mail(
                    'Registration Approved - Funda Malitinne LMS',
                    'Your account has been approved!',
                    'noreply@fundamalitinne.com',
                    [user.email],
                    html_message=html_message,
                    fail_silently=True
                )
                count += 1
            except:
                pass
        self.message_user(request, f'Approval emails sent to {count} users.')
    send_approval_emails.short_description = "Send approval emails to selected approved users"

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'level', 'total_students', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('title',)
    filter_horizontal = ('students',)

class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration')
    list_filter = ('course',)

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'total_points')
    list_filter = ('course',)

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade')
    list_filter = ('assignment__course',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Progress)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(QuizAttempt)
admin.site.register(Certificate)
admin.site.register(Notification)