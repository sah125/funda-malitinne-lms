from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
import hashlib
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password_expires = models.DateTimeField(blank=True, null=True)
    
    # New fields for registration
    id_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    disability = models.TextField(blank=True, null=True, help_text="Please specify any disability or leave blank if none")
    preferred_language = models.CharField(max_length=50, default='English')
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(blank=True, null=True)
    DEPARTMENT_CHOICES = (
        ('skills_development', 'Skills Development'),
        ('finance', 'Finance'),
        ('hr', 'Human Resources'),
        ('operations', 'Operations'),
        ('project_management', 'Project Management'),
        ('management', 'Management'),
    )
    department = models.CharField(max_length=30, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def send_reset_email(self):
        self.reset_password_token = get_random_string(64)
        self.reset_password_expires = timezone.now() + timezone.timedelta(hours=24)
        self.save()
        
        try:
            html_message = render_to_string('email/reset_password.html', {
                'user': self,
                'reset_link': f'/reset-password/{self.reset_password_token}/'
            })
            send_mail(
                'Password Reset - Funda Malitinne LMS',
                f'Click here to reset your password: /reset-password/{self.reset_password_token}/',
                'noreply@fundamalitinne.com',
                [self.email],
                html_message=html_message,
                fail_silently=True
            )
        except:
            pass

class Course(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    created_at = models.DateTimeField(auto_now_add=True)
    featured_image = models.ImageField(upload_to='courses/', blank=True, null=True)
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_rating = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(20)
        super().save(*args, **kwargs)
    
    @property
    def total_students(self):
        return self.students.count()
    
    @property
    def total_lessons(self):
        return self.lessons.count()
    
    @property
    def total_quizzes(self):
        return Quiz.objects.filter(lesson__course=self).count()

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    document = models.FileField(
        upload_to='lesson_documents/',
        blank=True,
        null=True,
        help_text="PDF or DOC file - students can view but not download"
    )
    duration = models.IntegerField(default=0, help_text="Duration in minutes")
    order = models.IntegerField(default=0)
    # Module relationship (add this field)
    module = models.ForeignKey('LearningModule', on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons')
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    passing_score = models.IntegerField(default=70)
    time_limit = models.IntegerField(default=0, help_text="Time limit in minutes (0 = no limit)")
    
    def __str__(self):
        return f"Quiz: {self.lesson.title}"
    
    @property
    def total_points(self):
        return sum(q.points for q in self.questions.all())

class QuizQuestion(models.Model):
    QUESTION_TYPES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    points = models.IntegerField(default=10)
    order = models.IntegerField(default=0)
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_answer = models.CharField(max_length=255)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quiz.lesson.title} - Q{self.order}"

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.IntegerField(null=True, blank=True)
    percentage = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    answers = models.JSONField(default=dict)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['quiz', 'student']
    
    def __str__(self):
        return f"{self.quiz.lesson.title} - {self.student.username}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    total_points = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_past_due(self):
        return timezone.now() > self.due_date

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file_upload = models.FileField(
        upload_to='submissions/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'zip'])]
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
    
    def __str__(self):
        return f"{self.assignment.title} - {self.student.username}"

class Progress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress')
    completed_lessons = models.ManyToManyField(Lesson, blank=True)
    completed_quizzes = models.ManyToManyField(Quiz, blank=True)
    completed_assignments = models.ManyToManyField(Assignment, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    @property
    def progress_percentage(self):
        total = self.course.lessons.count()
        if total == 0:
            return 0
        completed = self.completed_lessons.count()
        return int((completed / total) * 100)
    
    def check_completion(self):
        if self.progress_percentage == 100 and not self.certificate_issued:
            self.completed_at = timezone.now()
            self.certificate_issued = True
            self.save()
            return True
        return False
    
    @property
    def practical_progress_percentage(self):
        modules = self.course.learning_modules.filter(module_type='practical')
        total = modules.count()
        if total == 0:
            return 0
        done = AssessorSignOff.objects.filter(student=self.student, module__in=modules, outcome='competent').count()
        return int((done / total) * 100)
    
    @property
    def work_experience_progress_percentage(self):
        modules = self.course.learning_modules.filter(module_type='work_experience')
        total = modules.count()
        if total == 0:
            return 0
        done = AssessorSignOff.objects.filter(student=self.student, module__in=modules, outcome='competent').count()
        return int((done / total) * 100)
    
    @property
    def overall_qualification_percentage(self):
        parts = [self.progress_percentage]
        if self.course.learning_modules.filter(module_type='practical').exists():
            parts.append(self.practical_progress_percentage)
        if self.course.learning_modules.filter(module_type='work_experience').exists():
            parts.append(self.work_experience_progress_percentage)
        return int(sum(parts) / len(parts)) if parts else 0

class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    certificate_number = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"Certificate - {self.course.title} - {self.student.username}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            import time
            unique_string = f"{self.course.id}{self.student.id}{time.time()}"
            self.certificate_number = hashlib.md5(unique_string.encode()).hexdigest()[:16].upper()
        super().save(*args, **kwargs)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    



class LessonModule(models.Model):
    """Module within a lesson for step-by-step learning"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    content = models.TextField()
    content_type = models.CharField(max_length=20, choices=[
        ('text', 'Text Content'),
        ('video', 'Video Content'),
        ('interactive', 'Interactive Element'),
        ('quiz', 'Quick Quiz'),
        ('coding', 'Coding Exercise'),
        ('scenario', 'Scenario Based'),
    ], default='text')
    order = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    time_estimate = models.IntegerField(help_text="Time in minutes", default=5)
    points = models.IntegerField(default=10)
    
    class Meta:
        ordering = ['order']

class UserModuleProgress(models.Model):
    """Track progress through individual modules"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(LessonModule, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(default=0)  # seconds
    score = models.IntegerField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['student', 'module']

class LessonInteraction(models.Model):
    """Track student interaction with lessons (prevents auto-complete)"""
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    last_activity = models.DateTimeField(auto_now=True)
    total_time_spent = models.IntegerField(default=0)  # seconds
    modules_completed = models.IntegerField(default=0)
    last_module_viewed = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'lesson']

class Badge(models.Model):
    """Gamification badges"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    points_required = models.IntegerField(default=0)
    lessons_completed = models.IntegerField(default=0)
    courses_completed = models.IntegerField(default=0)
    
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

class DailyStreak(models.Model):
    """Track daily login streaks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streaks')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_active = models.DateField(auto_now=True)
    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)


# ==================== NEW MODELS (BLACKBOARD-STYLE) ====================

class Announcement(models.Model):
    """Course announcements like Blackboard"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']


class CourseGroup(models.Model):
    """Study groups within a course like Blackboard"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='course_groups', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.title} - {self.name}"
    
    @property
    def member_count(self):
        return self.members.count()


class Attendance(models.Model):
    """Attendance tracking like Blackboard"""
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    
    class Meta:
        unique_together = ['student', 'course', 'date']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.date}"


class LearningModule(models.Model):
    """Group lessons into modules like Blackboard"""
    MODULE_TYPE_CHOICES = (
        ('knowledge', 'Knowledge Module'),
        ('practical', 'Practical Skill Module'),
        ('work_experience', 'Work Experience Module'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='learning_modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    module_type = models.CharField(max_length=20, choices=MODULE_TYPE_CHOICES, default='knowledge')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def lesson_count(self):
        return self.lessons.count()
    
    @property
    def total_duration(self):
        return sum(l.duration for l in self.lessons.all())
    

# ==================== LEARNER PROFILE SYSTEM (QCTO COMPLIANT) ====================

class LearnerProfile(models.Model):
    """Extended learner profile for QCTO compliance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')
    
    # Section A: Personal & Contact (additional fields beyond User model)
    physical_address = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Section C: Internship / Workplace Experience
    host_company_name = models.CharField(max_length=255, blank=True, null=True)
    mou_file = models.FileField(upload_to='mou_documents/', blank=True, null=True)
    mou_start_date = models.DateField(blank=True, null=True)
    mou_end_date = models.DateField(blank=True, null=True)
    supervisor_name = models.CharField(max_length=200, blank=True, null=True)
    supervisor_phone = models.CharField(max_length=20, blank=True, null=True)
    supervisor_email = models.EmailField(blank=True, null=True)
    
    # Section D: Academic Tracking
    current_course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrolled_learners')
    enrollment_date = models.DateField(blank=True, null=True)
    expected_completion_date = models.DateField(blank=True, null=True)
    assessment_notes = models.TextField(blank=True, null=True)
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_date = models.DateField(blank=True, null=True)
    
    # POPIA Compliance
    popia_consent = models.BooleanField(default=False)
    popia_consent_date = models.DateTimeField(blank=True, null=True)
    data_processing_consent = models.BooleanField(default=False)
    
    # Timestamps
    profile_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Learner Profile"
        verbose_name_plural = "Learner Profiles"
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name() or self.user.username}"
    
    def get_completion_percentage(self):
        """Calculate profile completion percentage for QCTO reporting"""
        fields = [self.physical_address, self.emergency_contact_name, self.id_number,
                  self.host_company_name, self.supervisor_name]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100) if fields else 0


class LearnerDocument(models.Model):
    """Documents uploaded for learners (ID, qualifications, CV, agreements)"""
    DOCUMENT_TYPES = (
        ('id_copy', 'Certified ID Copy'),
        ('qualification', 'Highest Qualification'),
        ('cv', 'Curriculum Vitae'),
        ('learner_agreement', 'Signed Learner Agreement'),
        ('proof_of_residence', 'Proof of Residence'),
        ('medical_certificate', 'Medical Certificate'),
        ('other', 'Other Document'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(upload_to='learner_documents/%Y/%m/%d/')
    file_name = models.CharField(max_length=500)
    file_size = models.IntegerField(help_text="File size in bytes", default=0)
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    upload_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_documents')
    verified_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_document_type_display()}"


class LogbookEntry(models.Model):
    """Workplace experience logbook entries"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logbook_entries')
    module = models.ForeignKey(LearningModule, on_delete=models.SET_NULL, null=True, blank=True, related_name='logbook_entries')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='logbook_entries')
    entry_date = models.DateField()
    hours_spent = models.DecimalField(max_digits=5, decimal_places=1, default=0, help_text="Hours spent on this activity")
    description = models.TextField()
    skills_learned = models.TextField(blank=True, null=True)
    supervisor_comments = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='logbook_attachments/%Y/%m/', blank=True, null=True)
    supervisor_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approved_logbooks')
    approved_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-entry_date']
        verbose_name_plural = "Logbook entries"
    
    def __str__(self):
        return f"{self.user.username} - {self.entry_date}"


class BackupLog(models.Model):
    """Track system backups for QCTO 5.5 compliance"""
    backup_timestamp = models.DateTimeField(auto_now_add=True)
    backup_type = models.CharField(max_length=50, choices=[('full', 'Full Backup'), ('incremental', 'Incremental')])
    backup_size = models.BigIntegerField(help_text="Size in bytes", default=0)
    status = models.CharField(max_length=20, choices=[('success', 'Success'), ('failed', 'Failed'), ('in_progress', 'In Progress')])
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-backup_timestamp']
    
    def __str__(self):
        return f"Backup on {self.backup_timestamp.strftime('%Y-%m-%d %H:%M')}"


class AuditLog(models.Model):
    """Track all data access for POPIA compliance"""
    ACTION_CHOICES = (
        ('view', 'View'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('download', 'Download'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=100)
    resource_id = models.IntegerField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.resource_type} - {self.timestamp}"


# ==================== FORUM SYSTEM ====================

class ForumTopic(models.Model):
    """Main forum topic/discussion post for a lesson"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='forum_topics')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics')
    title = models.CharField(max_length=300)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # NEW FIELDS FOR TICKETING
    is_ticket = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_tickets'
    )
    project = models.ForeignKey(
        'TenderOpportunity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical')
        ],
        default='medium'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Forum Topic'
        verbose_name_plural = 'Forum Topics'
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class ForumPost(models.Model):
    """Forum post/reply to a topic"""
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='posts'
    )
    likes_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Forum Post'
        verbose_name_plural = 'Forum Posts'
    
    def __str__(self):
        return f"Post by {self.author.username} on {self.topic.title}"


#------------------------------- oportunity ------------------------------#
class Opportunity(models.Model):
    OPPORTUNITY_TYPES = (
        ('learnership', 'Learnership'),
        ('internship', 'Internship'),
        ('apprenticeship', 'Apprenticeship'),
        ('job', 'Job Vacancy'),
        ('funding', 'Funding Opportunity'),
        ('bursary', 'Bursary'),
        ('training', 'Training Programme'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Basic Information
    title = models.CharField(max_length=200)
    opportunity_type = models.CharField(max_length=50, choices=OPPORTUNITY_TYPES)
    reference_number = models.CharField(max_length=50, unique=True, blank=True)
    description = models.TextField()
    requirements = models.TextField(help_text="List requirements, one per line or use bullet points")
    responsibilities = models.TextField(blank=True, help_text="Key responsibilities for the role")
    
    # Location & Logistics
    location = models.CharField(max_length=200)
    remote_options = models.BooleanField(default=False)
    stipend_amount = models.CharField(max_length=100, blank=True, help_text="e.g., R3500 per month")
    funding_amount = models.CharField(max_length=100, blank=True, help_text="e.g., Up to R100,000")
    
    # Dates
    opening_date = models.DateField()
    closing_date = models.DateField()
    expected_start_date = models.DateField(null=True, blank=True)
    
    # Capacity
    available_positions = models.IntegerField(default=1)
    positions_filled = models.IntegerField(default=0)
    
    # Status & Visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    priority = models.IntegerField(default=0, help_text="Higher number = higher priority in listings")
    
    # Additional Info
    contact_email = models.EmailField(default='careers@malitinne.co.za')
    contact_person = models.CharField(max_length=100, blank=True)
    application_instructions = models.TextField(blank=True, help_text="Special instructions for applying")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_opportunities')
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name_plural = "Opportunities"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            import uuid
            self.reference_number = f"MAL-{self.opportunity_type[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def is_open(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'published' and self.opening_date <= today <= self.closing_date and self.positions_filled < self.available_positions
    
    @property
    def remaining_positions(self):
        return self.available_positions - self.positions_filled
    
    def __str__(self):
        return f"{self.title} ({self.get_opportunity_type_display()})"


class Application(models.Model):
    APPLICATION_STATUS = (
        ('pending', 'Pending Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Stage'),
        ('assessment', 'Assessment Stage'),
        ('offered', 'Offer Extended'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    
    # Application Information
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    application_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    alternative_phone = models.CharField(max_length=20, blank=True)
    
    # Demographics
    id_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=(
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('prefer_not', 'Prefer not to say')
    ), blank=True)
    race = models.CharField(max_length=50, choices=(
        ('african', 'African'), ('coloured', 'Coloured'), ('indian', 'Indian'), ('white', 'White'), ('other', 'Other')
    ), blank=True, help_text="For BBBEE/Employment Equity purposes")
    disability = models.CharField(max_length=100, blank=True, help_text="Specify disability if applicable")
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=50, choices=(
        ('EC', 'Eastern Cape'), ('FS', 'Free State'), ('GP', 'Gauteng'), 
        ('KZN', 'KwaZulu-Natal'), ('LP', 'Limpopo'), ('MP', 'Mpumalanga'), 
        ('NC', 'Northern Cape'), ('NW', 'North West'), ('WC', 'Western Cape')
    ))
    postal_code = models.CharField(max_length=10)
    
    # Education & Experience
    highest_qualification = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year_completed = models.IntegerField()
    field_of_study = models.CharField(max_length=200, blank=True)
    
    work_experience = models.TextField(blank=True, help_text="Previous work experience")
    skills = models.TextField(help_text="Relevant skills, separated by commas")
    
    # Documents
    cv = models.FileField(upload_to='applications/cvs/%Y/%m/', null=True, blank=True)
    cover_letter = models.FileField(upload_to='applications/cover_letters/%Y/%m/', null=True, blank=True)
    id_document = models.FileField(upload_to='applications/ids/%Y/%m/', null=True, blank=True)
    qualifications = models.FileField(upload_to='applications/qualifications/%Y/%m/', null=True, blank=True)
    
    # Additional Information
    hear_about_us = models.CharField(max_length=200, blank=True, help_text="How did you hear about this opportunity?")
    additional_info = models.TextField(blank=True, help_text="Any additional information you'd like to share")
    
    # Status & Tracking
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='pending')
    status_notes = models.TextField(blank=True, help_text="Internal notes about application status")
    
    # Review Information
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True, help_text="Application score out of 100")
    
    # Submission
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            import uuid
            self.application_number = f"APP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.full_name} - {self.opportunity.title}"


class ObservationChecklistItem(models.Model):
    """A single competency an assessor checks off during a practical demonstration"""
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='checklist_items')
    description = models.CharField(max_length=500)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.description[:50]}"


class StudentChecklistResult(models.Model):
    """Whether a student demonstrated a specific competency"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checklist_results')
    item = models.ForeignKey(ObservationChecklistItem, on_delete=models.CASCADE, related_name='results')
    is_competent = models.BooleanField(default=False)
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='checklist_assessments')
    assessed_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['student', 'item']

    def __str__(self):
        return f"{self.student.username} - {self.item.description[:30]} - {'Competent' if self.is_competent else 'Not yet'}"


class ModuleEvidence(models.Model):
    """Evidence uploaded by a student for a practical or work-experience module"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_evidence')
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='evidence_items')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='module_evidence/%Y/%m/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_evidence')
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.student.username} - {self.module.title} - {self.title}"


class AssessorSignOff(models.Model):
    """Assessor's final sign-off on a student's competence for a module"""
    OUTCOME_CHOICES = (
        ('competent', 'Competent'),
        ('not_yet_competent', 'Not Yet Competent'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sign_offs')
    module = models.ForeignKey(LearningModule, on_delete=models.CASCADE, related_name='sign_offs')
    assessor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assessments_given')
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default='not_yet_competent')
    comments = models.TextField(blank=True, null=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'module']

    def __str__(self):
        return f"{self.student.username} - {self.module.title} - {self.get_outcome_display()}"


class PortfolioOfEvidence(models.Model):
    """Aggregated portfolio of evidence for a qualification, submitted for assessment"""
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('returned', 'Returned for Revision'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='portfolios')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_portfolios')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.get_status_display()}"


class SummativeAssessment(models.Model):
    """Internal Integrated Summative Assessment (IISA) for a qualification"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='summative_assessments')
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class SummativeAssessmentSubmission(models.Model):
    RESULT_CHOICES = (
        ('pending', 'Pending Assessment'),
        ('competent', 'Competent'),
        ('not_yet_competent', 'Not Yet Competent'),
    )
    assessment = models.ForeignKey(SummativeAssessment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='summative_submissions')
    file_upload = models.FileField(upload_to='summative_submissions/%Y/%m/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='summative_assessments_given')
    assessed_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['assessment', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.assessment.title} - {self.get_result_display()}"


class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date', '-priority']

    def __str__(self):
        return f"{self.title} ({self.assigned_to.username})"


class Meeting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings')
    attendees = models.ManyToManyField(User, related_name='meetings', blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, help_text="Room name or video call link")

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class StaffAnnouncement(models.Model):
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('hr', 'HR'),
        ('policy', 'Policy Update'),
        ('event', 'Event'),
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='staff_announcements')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


# ==================== TENDER & OPPORTUNITY TRACKING (PHASE 2) ====================

class TenderSource(models.Model):
    """Sources to crawl for opportunities (eTenders, SETA portals, etc.)"""
    SOURCE_TYPES = (
        ('etenders', 'National eTenders Portal'),
        ('seta', 'SETA Portal'),
        ('municipality', 'Municipality Website'),
        ('other', 'Other Source'),
    )
    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    base_url = models.URLField()
    search_keywords = models.TextField(help_text="Comma-separated keywords to filter")
    is_active = models.BooleanField(default=True)
    last_crawled = models.DateTimeField(null=True, blank=True)
    crawl_frequency_hours = models.IntegerField(default=24)
    
    def __str__(self):
        return self.name


class TenderOpportunity(models.Model):
    """Crawled tender/opportunity from various sources"""
    STATUS_CHOICES = (
        ('new', 'New'),
        ('viewed', 'Viewed'),
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('expired', 'Expired'),
    )
    
    CATEGORY_CHOICES = (
        ('training', 'Training & Skills Development'),
        ('consulting', 'Consulting Services'),
        ('supplies', 'Supplies & Equipment'),
        ('construction', 'Construction'),
        ('other', 'Other'),
    )
    
    source = models.ForeignKey(TenderSource, on_delete=models.SET_NULL, null=True, related_name='opportunities')
    tender_id = models.CharField(max_length=100, help_text="Original tender ID from source")
    title = models.CharField(max_length=500)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='training')
    
    published_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField()
    opening_date = models.DateField(null=True, blank=True)
    
    estimated_value = models.CharField(max_length=200, blank=True, help_text="Estimated value range")
    bidder_deposit = models.CharField(max_length=200, blank=True)
    
    location = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=300, blank=True, help_text="Issuing department/agency")
    
    document_url = models.URLField(blank=True, help_text="Link to original tender document")
    local_document = models.FileField(upload_to='tenders/%Y/%m/', blank=True, null=True)
    
    ai_relevance_score = models.FloatField(default=0, help_text="0-100 score based on business fit")
    ai_confidence = models.FloatField(default=0, help_text="Confidence in scoring")
    ai_match_reasons = models.TextField(blank=True, help_text="Why this tender is relevant")
    
    internal_notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tenders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tenders')
    
    class Meta:
        unique_together = ['source', 'tender_id']
        ordering = ['closing_date', '-ai_relevance_score']
    
    def __str__(self):
        return f"{self.title} (Closes: {self.closing_date})"
    
    @property
    def days_until_close(self):
        from django.utils import timezone
        delta = self.closing_date - timezone.now().date()
        return delta.days
    
    @property
    def is_urgent(self):
        return self.days_until_close <= 7 and self.status == 'new'
    
    @property
    def is_open(self):
        from django.utils import timezone
        return self.closing_date >= timezone.now().date() and self.status not in ['expired', 'lost']


# ==================== SHARED DOCUMENT DRIVE (PHASE 3) ====================

class DocumentCategory(models.Model):
    """Categories for organizing shared documents"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-folder')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Document categories"
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name


class SharedDocument(models.Model):
    """Document shared in the company drive"""
    VISIBILITY_CHOICES = (
        ('all_staff', 'All Staff'),
        ('management', 'Management Only'),
        ('department', 'Specific Department'),
        ('private', 'Private (Owner Only)'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, related_name='documents')
    
    file = models.FileField(upload_to='shared_drive/%Y/%m/')
    file_name = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0, help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True)
    
    version = models.CharField(max_length=20, default='1.0')
    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='later_versions')
    
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='all_staff')
    allowed_departments = models.ManyToManyField('User', limit_choices_to={'role__in': ['instructor', 'admin']}, blank=True, related_name='accessible_docs')
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents_shared')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    download_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name.split('/')[-1]
            if not self.file_size and hasattr(self.file, 'size'):
                self.file_size = self.file.size
        super().save(*args, **kwargs)


class DocumentDownloadLog(models.Model):
    """Track who downloaded which document"""
    document = models.ForeignKey(SharedDocument, on_delete=models.CASCADE, related_name='download_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_downloads')
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f"{self.user.username} downloaded {self.document.title}"


class CrawlLog(models.Model):
    """Log of automated crawl operations"""
    source = models.ForeignKey(TenderSource, on_delete=models.CASCADE, related_name='crawl_logs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    opportunities_found = models.IntegerField(default=0)
    opportunities_new = models.IntegerField(default=0)
    status = models.CharField(max_length=50, choices=[('success', 'Success'), ('failed', 'Failed'), ('in_progress', 'In Progress')])
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"Crawl {self.source.name} - {self.started_at}"