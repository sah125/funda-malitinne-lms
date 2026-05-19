from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from core.models import Course, User, Lesson, Quiz, Assignment
from .serializers import CourseSerializer, CourseDetailSerializer, UserSerializer, LessonSerializer
from .permissions import IsInstructor, IsAdmin, IsEnrolledInCourse

class HealthCheckView:
    """Health check endpoint for monitoring"""
    @staticmethod
    @require_http_methods(["GET"])
    def health_check(request):
        """Simple health check endpoint"""
        try:
            # Check database
            User.objects.count()
            return JsonResponse({
                'status': 'healthy',
                'service': 'funda_malitinne_lms',
                'message': 'Application is running'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course operations"""
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter courses based on user role"""
        user = self.request.user
        
        if user.role == 'admin':
            return Course.objects.all()
        elif user.role == 'instructor':
            return Course.objects.filter(instructor=user)
        else:  # student
            return Course.objects.filter(students=user) | Course.objects.filter(status='published')
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseSerializer
    
    def perform_create(self, serializer):
        """Set instructor to current user"""
        if self.request.user.role in ['instructor', 'admin']:
            serializer.save(instructor=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        """Enroll user in course"""
        course = self.get_object()
        course.students.add(request.user)
        return Response({'status': 'enrolled'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unenroll(self, request, pk=None):
        """Unenroll user from course"""
        course = self.get_object()
        course.students.remove(request.user)
        return Response({'status': 'unenrolled'})
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def is_enrolled(self, request, pk=None):
        """Check if user is enrolled"""
        course = self.get_object()
        is_enrolled = course.students.filter(id=request.user.id).exists()
        return Response({'enrolled': is_enrolled})


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User operations"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only current user for students, all users for admins"""
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdmin])
    def approve_users(self, request):
        """Approve pending users"""
        user_ids = request.data.get('user_ids', [])
        updated = User.objects.filter(id__in=user_ids).update(is_approved=True)
        return Response({'approved': updated})
