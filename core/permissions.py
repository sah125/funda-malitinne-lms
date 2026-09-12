from functools import wraps

from django.core.exceptions import PermissionDenied
from rest_framework import permissions


def is_instructor(user):
    return user.is_authenticated and user.role == 'instructor'


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


def is_staff_role(user):
    return user.is_authenticated and user.role in ('admin', 'instructor')


def can_manage_course(user, course):
    return user.role == 'admin' or course.instructor_id == user.id


def can_view_course(user, course):
    if user.role == 'admin':
        return True
    if user.role == 'instructor':
        return course.instructor_id == user.id
    return course.students.filter(id=user.id).exists()


def instructor_owns_course(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .models import Course

        course_id = kwargs.get('course_id')
        if course_id:
            course = Course.objects.filter(id=course_id).first()
            if not course or not can_manage_course(request.user, course):
                raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper

class IsInstructor(permissions.BasePermission):
    """Permission to check if user is an instructor"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'instructor'


class IsAdmin(permissions.BasePermission):
    """Permission to check if user is an admin"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsStudent(permissions.BasePermission):
    """Permission to check if user is a student"""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'student'


class IsInstructorOrAdmin(permissions.BasePermission):
    """Permission to check if user is an instructor or admin"""

    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and
                request.user.role in ['instructor', 'admin'])


class IsEnrolledInCourse(permissions.BasePermission):
    """Permission to check if user is enrolled in a course"""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'instructor':
            return obj.instructor == request.user
        if request.user.role == 'student':
            return obj.students.filter(id=request.user.id).exists()
        return False


class IsOwnProfile(permissions.BasePermission):
    """Permission to check if user is accessing their own profile"""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj == request.user


class IsSubmissionOwner(permissions.BasePermission):
    """Permission to check if user is the submission owner or instructor"""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if request.user.role == 'instructor':
            return obj.assignment.course.instructor == request.user
        if request.user.role == 'student':
            return obj.student == request.user
        return False
