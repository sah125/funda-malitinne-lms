from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Course, Lesson, Assignment, Submission, Notification,
    Progress, Certificate, Quiz, QuizQuestion, QuizAttempt,
    Announcement, CourseGroup, Attendance, LearningModule
)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_approved', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'is_approved')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'id_number')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_picture')}),
        ('Registration Details', {'fields': ('id_number', 'date_of_birth', 'gender', 'nationality', 'contact_number', 'disability', 'preferred_language')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Approval', {'fields': ('is_approved', 'approved_at')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Role', {'fields': ('role',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_approved'),
        }),
    )
    
    actions = ['approve_users']
    
    def approve_users(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_approved=True, approved_at=timezone.now())
        self.message_user(request, f'{updated} users were successfully approved.')
    approve_users.short_description = "Approve selected users"

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'level', 'status', 'price', 'created_at')
    list_filter = ('level', 'status', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')
    filter_horizontal = ('students',)

class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'duration')
    list_filter = ('course',)
    search_fields = ('title', 'content')

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'total_points')
    list_filter = ('course', 'due_date')
    search_fields = ('title', 'description')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade')
    list_filter = ('assignment__course',)
    search_fields = ('student__username', 'assignment__title')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'title')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'passing_score')
    list_filter = ('lesson__course',)
    search_fields = ('title',)

class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'question_type', 'points')
    list_filter = ('quiz__lesson__course', 'question_type')
    search_fields = ('question_text',)

class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'certificate_number', 'issued_at')
    list_filter = ('course',)
    search_fields = ('student__username', 'certificate_number')

class ProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress_percentage', 'completed_at')
    list_filter = ('course',)
    search_fields = ('student__username', 'course__title')

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'author', 'is_pinned', 'created_at')
    list_filter = ('course', 'is_pinned')
    search_fields = ('title', 'content')

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'status')
    list_filter = ('course', 'status', 'date')
    search_fields = ('student__username',)

class LearningModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_visible')
    list_filter = ('course', 'is_visible')
    search_fields = ('title',)

class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'member_count', 'created_at')
    list_filter = ('course',)
    search_fields = ('name',)

# Register all models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Certificate, CertificateAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizQuestion, QuizQuestionAdmin)
admin.site.register(QuizAttempt)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(CourseGroup, CourseGroupAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(LearningModule, LearningModuleAdmin)