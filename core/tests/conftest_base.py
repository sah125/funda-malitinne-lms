from django.contrib.auth import get_user_model

from core.models import Course, Lesson, Progress

User = get_user_model()


def make_student(username="student1", password="TestPass123!"):
    return User.objects.create_user(
        username=username,
        password=password,
        role="student",
        is_active=True,
        is_approved=True,
        email=f"{username}@test.local",
    )


def make_instructor(username="instructor1", password="TestPass123!"):
    return User.objects.create_user(
        username=username,
        password=password,
        role="instructor",
        is_active=True,
        is_approved=True,
        email=f"{username}@test.local",
    )


def make_admin(username="admin1", password="TestPass123!"):
    return User.objects.create_user(
        username=username,
        password=password,
        role="admin",
        is_active=True,
        is_approved=True,
        email=f"{username}@test.local",
    )


def make_course(instructor, title="Test Course"):
    return Course.objects.create(
        title=title,
        instructor=instructor,
        status="published",
    )


def make_enrollment(student, course):
    course.students.add(student)
    return Progress.objects.get_or_create(student=student, course=course)[0]