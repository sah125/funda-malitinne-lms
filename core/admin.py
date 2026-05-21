from django.contrib import admin
from .models import (
    User, Course, Lesson, Quiz, QuizQuestion, QuizAttempt, Assignment, 
    Submission, Progress, Certificate, Notification, Announcement, 
    CourseGroup, Attendance, LearningModule, LessonModule, UserModuleProgress,
    LessonInteraction, Badge, UserBadge, DailyStreak, LearnerProfile,
    LearnerDocument, LogbookEntry, BackupLog, AuditLog, ForumTopic, ForumPost
)

# ==================== USER ADMIN ====================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'date_joined')
    list_filter = ('role', 'is_approved', 'gender')
    search_fields = ('username', 'email', 'id_number')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        ('Account Information', {
            'fields': ('username', 'email', 'password', 'role', 'is_approved', 'is_active')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'id_number', 'date_of_birth', 'gender', 'nationality')
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'preferred_language', 'disability')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

# ==================== COURSE & LESSON ====================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'level', 'status', 'price', 'created_at')
    list_filter = ('level', 'status', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at',)  # Remove 'updated_at' from here
    
    fieldsets = (
        ('Course Information', {
            'fields': ('title', 'slug', 'description', 'instructor', 'level', 'status')
        }),
        ('Pricing & Media', {
            'fields': ('price', 'thumbnail', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('created_at',),  # Only include fields that exist
            'classes': ('collapse',)
        }),
    )
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'content')
    list_editable = ('order', 'duration')
    
    fieldsets = (
        ('Lesson Information', {
            'fields': ('course', 'title', 'content', 'order', 'duration')
        }),
        ('Media', {
            'fields': ('video_url', 'video_file', 'document', 'attachment')
        }),
        # Remove the Metadata fieldset if created_at and updated_at don't exist
    )
# ==================== QUIZ SYSTEM ====================
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'title', 'passing_score', 'time_limit')
    list_filter = ('lesson__course',)
    search_fields = ('title', 'description')
    # Remove filter_horizontal if it's not a many-to-many field
    
    fieldsets = (
        ('Quiz Information', {
            'fields': ('lesson', 'title', 'description')
        }),
        ('Settings', {
            'fields': ('passing_score', 'time_limit', 'is_active')
        }),
    )

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'question_type', 'points', 'order')
    list_filter = ('quiz', 'question_type')
    search_fields = ('question_text',)
    list_editable = ('points', 'order')
    
    fieldsets = (
        ('Question', {
            'fields': ('quiz', 'question_text', 'question_type', 'points', 'order')
        }),
        ('Options (for multiple choice)', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d'),
            'classes': ('collapse',)
        }),
        ('Answer', {
            'fields': ('correct_answer', 'explanation')
        }),
    )

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'score', 'percentage', 'passed', 'completed_at')
    list_filter = ('passed', 'completed_at', 'quiz')
    search_fields = ('student__username', 'quiz__title')
    readonly_fields = ('started_at', 'completed_at', 'answers')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# ==================== ASSIGNMENTS ====================
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'total_points', 'created_at')
    list_filter = ('course', 'due_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('course', 'title', 'description')
        }),
        ('Grading', {
            'fields': ('total_points', 'due_date')
        }),
    )

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade', 'is_late')
    list_filter = ('assignment', 'submitted_at', 'grade')
    search_fields = ('student__username', 'assignment__title')
    readonly_fields = ('submitted_at',)
    list_editable = ('grade',)
    
    def is_late(self, obj):
        return obj.is_late
    is_late.boolean = True
    is_late.short_description = 'Late Submission'
    
    fieldsets = (
        ('Submission Information', {
            'fields': ('assignment', 'student', 'file_upload', 'submitted_at')
        }),
        ('Grading', {
            'fields': ('grade', 'feedback')
        }),
    )

# ==================== PROGRESS & CERTIFICATES ====================
@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress_percentage', 'certificate_issued')
    list_filter = ('course', 'certificate_issued')
    search_fields = ('student__username', 'course__title')
    readonly_fields = ('progress_percentage',)
    
    fieldsets = (
        ('Progress', {
            'fields': ('student', 'course', 'completed_lessons')
        }),
        ('Certificate', {
            'fields': ('certificate_issued', 'certificate_issued_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'certificate_number', 'issued_at')
    list_filter = ('course', 'issued_at')
    search_fields = ('student__username', 'certificate_number')
    readonly_fields = ('certificate_number', 'issued_at')
    
    fieldsets = (
        ('Certificate Information', {
            'fields': ('student', 'course', 'certificate_number')
        }),
        ('Issuance', {
            'fields': ('issued_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False

# ==================== NOTIFICATIONS ====================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Notification', {
            'fields': ('user', 'title', 'message', 'link')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )

# ==================== ANNOUNCEMENTS ====================
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'author', 'is_pinned', 'created_at')
    list_filter = ('course', 'is_pinned', 'created_at')
    search_fields = ('title', 'content')
    list_editable = ('is_pinned',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Announcement', {
            'fields': ('course', 'title', 'content', 'author')
        }),
        ('Options', {
            'fields': ('is_pinned',)
        }),
    )

# ==================== COURSE GROUPS ====================
@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'created_by', 'member_count', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'
    
    fieldsets = (
        ('Group Information', {
            'fields': ('course', 'name', 'description', 'created_by')
        }),
        ('Members', {
            'fields': ('members',)
        }),
    )

# ==================== ATTENDANCE ====================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'status', 'marked_by')
    list_filter = ('course', 'status', 'date')
    search_fields = ('student__username', 'course__title')
    date_hierarchy = 'date'
    list_editable = ('status',)
    
    fieldsets = (
        ('Attendance Record', {
            'fields': ('student', 'course', 'date', 'status', 'marked_by')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

# ==================== LEARNING MODULES ====================
@admin.register(LearningModule)
class LearningModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_visible', 'lesson_count')
    list_filter = ('course', 'is_visible')
    search_fields = ('title',)
    list_editable = ('order', 'is_visible')
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Lessons'
    
    fieldsets = (
        ('Module Information', {
            'fields': ('course', 'title', 'description', 'order', 'is_visible')
        }),
    )

@admin.register(LessonModule)
class LessonModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'content_type', 'order', 'points', 'time_estimate')
    list_filter = ('lesson', 'content_type')
    search_fields = ('title',)
    list_editable = ('order', 'points', 'time_estimate')
    
    fieldsets = (
        ('Module Information', {
            'fields': ('lesson', 'title', 'content', 'content_type', 'order')
        }),
        ('Gamification', {
            'fields': ('points', 'time_estimate')
        }),
    )

@admin.register(UserModuleProgress)
class UserModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'module', 'completed', 'completed_at')
    list_filter = ('completed', 'module__lesson')
    search_fields = ('student__username', 'module__title')
    readonly_fields = ('completed_at',)
    
    def has_add_permission(self, request):
        return False

@admin.register(LessonInteraction)
class LessonInteractionAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'modules_completed', 'completed')
    list_filter = ('completed', 'lesson__course')
    search_fields = ('student__username', 'lesson__title')
    
    def has_add_permission(self, request):
        return False

# ==================== LEARNER PROFILE ====================
@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'host_company_name', 'current_course', 'certificate_issued', 'popia_consent')
    list_filter = ('certificate_issued', 'popia_consent')
    search_fields = ('user__username', 'user__email', 'host_company_name')
    # Remove filter_horizontal if assigned_modules doesn't exist
    
    fieldsets = (
        ('Learner Information', {
            'fields': ('user', 'current_course', 'enrollment_date', 'expected_completion_date')
        }),
        ('Internship/Workplace', {
            'fields': ('host_company_name', 'mou_start_date', 'mou_end_date')
        }),
        ('Supervisor Details', {
            'fields': ('supervisor_name', 'supervisor_phone', 'supervisor_email')
        }),
        ('Assessment', {
            'fields': ('assessment_notes', 'certificate_issued', 'certificate_issued_date')
        }),
        ('POPIA Compliance', {
            'fields': ('popia_consent', 'popia_consent_date')
        }),
        ('Additional Information', {
            'fields': ('physical_address',),
            'classes': ('collapse',)
        }),
    )

@admin.register(LearnerDocument)
class LearnerDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'upload_date', 'file_size_kb', 'is_verified', 'verified_by')
    list_filter = ('document_type', 'is_verified', 'upload_date')
    search_fields = ('user__username', 'title', 'file_name')
    list_editable = ('is_verified',)
    
    def file_size_kb(self, obj):
        return f"{obj.file_size // 1024} KB" if obj.file_size else "0 KB"
    file_size_kb.short_description = 'Size'
    
    fieldsets = (
        ('Document Information', {
            'fields': ('user', 'document_type', 'title', 'description')
        }),
        ('File Details', {
            'fields': ('file', 'file_name', 'file_size')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verified_at')
        }),
    )

@admin.register(LogbookEntry)
class LogbookEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'entry_date', 'hours_spent', 'supervisor_approved', 'approved_by')
    list_filter = ('supervisor_approved', 'entry_date')
    search_fields = ('user__username', 'description', 'skills_learned')
    date_hierarchy = 'entry_date'
    list_editable = ('supervisor_approved',)
    
    fieldsets = (
        ('Log Entry', {
            'fields': ('user', 'entry_date', 'hours_spent', 'description', 'skills_learned')
        }),
        ('Supervisor Approval', {
            'fields': ('supervisor_approved', 'approved_by', 'approved_at', 'supervisor_notes')
        }),
    )

# ==================== COMPLIANCE & AUDIT ====================
@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    list_display = ('backup_timestamp', 'backup_type', 'backup_size_mb', 'status')
    list_filter = ('status', 'backup_type', 'backup_timestamp')
    search_fields = ('performed_by__username',)
    readonly_fields = ('backup_timestamp',)
    
    def backup_size_mb(self, obj):
        return f"{obj.backup_size / (1024*1024):.2f} MB" if obj.backup_size else "0 MB"
    backup_size_mb.short_description = 'Size'
    
    fieldsets = (
        ('Backup Information', {
            'fields': ('backup_type', 'backup_timestamp', 'backup_size', 'status')
        }),
        ('Metadata', {
            'fields': ('performed_by', 'error_message')
        }),
    )
    
    def has_add_permission(self, request):
        return False

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource_type', 'resource_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'resource_type', 'timestamp')
    search_fields = ('user__username', 'resource_type', 'resource_id')
    readonly_fields = ('timestamp', 'ip_address')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Audit Information', {
            'fields': ('user', 'action', 'resource_type', 'resource_id', 'ip_address')
        }),
        ('Details', {
            'fields': ('details', 'timestamp')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# ==================== GAMIFICATION ====================
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_required', 'lessons_completed', 'courses_completed')
    search_fields = ('name', 'description')
    
    fieldsets = (
        ('Badge Information', {
            'fields': ('name', 'description', 'icon')
        }),
        ('Requirements', {
            'fields': ('points_required', 'lessons_completed', 'courses_completed')
        }),
    )

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('badge', 'earned_at')
    search_fields = ('user__username', 'badge__name')
    readonly_fields = ('earned_at',)
    
    def has_add_permission(self, request):
        return False

@admin.register(DailyStreak)
class DailyStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'longest_streak', 'total_xp', 'level')
    search_fields = ('user__username',)
    
    fieldsets = (
        ('Streak Information', {
            'fields': ('user', 'current_streak', 'longest_streak')
        }),
        ('Experience', {
            'fields': ('total_xp', 'level')
        }),
    )
    
    def has_add_permission(self, request):
        return False

# ==================== FORUM SYSTEM ====================
@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'author', 'posts_count', 'created_at')
    list_filter = ('lesson', 'created_at')
    search_fields = ('title', 'content')
    
    def posts_count(self, obj):
        return obj.posts.count()
    posts_count.short_description = 'Posts'
    
    fieldsets = (
        ('Topic Information', {
            'fields': ('lesson', 'title', 'content', 'author')
        }),
        ('Settings', {
            'fields': ('is_pinned', 'is_locked')
        }),
    )

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'short_content', 'created_at', 'likes_count')
    list_filter = ('topic', 'created_at')
    search_fields = ('content', 'author__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'
    
    fieldsets = (
        ('Post Information', {
            'fields': ('topic', 'author', 'content')
        }),
        ('Parent Reply', {
            'fields': ('parent',)
        }),
        ('Engagement', {
            'fields': ('likes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )