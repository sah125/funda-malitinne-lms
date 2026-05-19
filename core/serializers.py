from rest_framework import serializers
from core.models import User, Course, Lesson, Quiz, QuizQuestion, Assignment, Submission, Progress, Certificate

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'profile_picture')
        read_only_fields = ('id',)


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for User model"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 
                 'profile_picture', 'date_of_birth', 'gender', 'is_approved', 'approved_at')
        read_only_fields = ('id', 'is_approved', 'approved_at')


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'description', 'content', 'video_url', 'order', 'created_at')
        read_only_fields = ('id', 'created_at')


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer for QuizQuestion model"""
    class Meta:
        model = QuizQuestion
        fields = ('id', 'question_text', 'question_type', 'points', 'order')
        read_only_fields = ('id',)


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for Quiz model"""
    questions = QuizQuestionSerializer(many=True, read_only=True, source='quizquestion_set')
    
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'passing_score', 'attempts_allowed', 'questions')
        read_only_fields = ('id',)


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model"""
    class Meta:
        model = Assignment
        fields = ('id', 'title', 'description', 'instructions', 'due_date', 'max_score', 'created_at')
        read_only_fields = ('id', 'created_at')


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model"""
    class Meta:
        model = Submission
        fields = ('id', 'student', 'assignment', 'submitted_at', 'submission_file', 'score', 'feedback')
        read_only_fields = ('id', 'submitted_at')


class ProgressSerializer(serializers.ModelSerializer):
    """Serializer for Progress model"""
    class Meta:
        model = Progress
        fields = ('id', 'student', 'course', 'completion_percentage', 'last_accessed', 'completed_at')
        read_only_fields = ('id',)


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    instructor = UserSerializer(read_only=True)
    lessons_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'short_description', 'instructor', 'level', 
                 'price', 'featured_image', 'status', 'created_at', 'lessons_count')
        read_only_fields = ('id', 'created_at')
    
    def get_lessons_count(self, obj):
        return obj.lesson_set.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Course model with lessons"""
    instructor = UserSerializer(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True, source='lesson_set')
    
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'short_description', 'instructor', 'level', 
                 'price', 'featured_image', 'status', 'created_at', 'lessons')
        read_only_fields = ('id', 'created_at')


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for Certificate model"""
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Certificate
        fields = ('id', 'student', 'course', 'issued_date', 'certificate_number')
        read_only_fields = ('id', 'issued_date', 'certificate_number')
