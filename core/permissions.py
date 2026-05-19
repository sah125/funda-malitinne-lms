from rest_framework import permissions

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
