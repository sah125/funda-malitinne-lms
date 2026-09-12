from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from core.models import Lesson, Quiz, QuizAttempt

from .conftest_base import (
    make_course,
    make_enrollment,
    make_instructor,
    make_student,
)


class CourseIsolationPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.instructor_a = make_instructor("instructor_a")
        self.instructor_b = make_instructor("instructor_b")
        self.course_x = make_course(self.instructor_a, "Course X")
        self.course_y = make_course(self.instructor_b, "Course Y")
        self.lesson_x = Lesson.objects.create(
            course=self.course_x,
            title="Lesson X",
            content="Lesson content",
        )

    def test_instructor_b_cannot_manage_course_a(self):
        self.client.force_login(self.instructor_b)
        response = self.client.get(reverse("manage_course", args=[self.course_x.id]))
        self.assertNotEqual(response.status_code, 200)

    def test_instructor_a_can_manage_own_course(self):
        self.client.force_login(self.instructor_a)
        response = self.client.get(reverse("manage_course", args=[self.course_x.id]))
        self.assertEqual(response.status_code, 200)

    def test_instructor_b_cannot_add_lesson_to_course_a(self):
        self.client.force_login(self.instructor_b)
        response = self.client.get(reverse("add_lesson", args=[self.course_x.id]))
        self.assertNotEqual(response.status_code, 200)

    def test_instructor_b_cannot_edit_lesson_in_course_a(self):
        self.client.force_login(self.instructor_b)
        response = self.client.get(reverse("edit_lesson", args=[self.lesson_x.id]))
        self.assertNotEqual(response.status_code, 200)

    def test_instructor_b_cannot_post_new_lesson_to_course_a(self):
        self.client.force_login(self.instructor_b)
        initial_count = Lesson.objects.filter(course=self.course_x).count()
        response = self.client.post(
            reverse("add_lesson", args=[self.course_x.id]),
            {"title": "Unauthorized lesson", "content": "Should not be created"},
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(Lesson.objects.filter(course=self.course_x).count(), initial_count)


class StudentInstructorToolPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = make_student("student_tools")
        self.instructor = make_instructor("instructor_tools")
        self.course = make_course(self.instructor, "Instructor Tools Course")

    def test_student_cannot_view_instructor_dashboard(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("instructor_dashboard"))
        self.assertNotEqual(response.status_code, 200)

    def test_student_cannot_view_create_course(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("create_course"))
        self.assertNotEqual(response.status_code, 200)

    def test_student_cannot_manage_course(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("manage_course", args=[self.course.id]))
        self.assertNotEqual(response.status_code, 200)

    def test_student_cannot_post_lesson(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("add_lesson", args=[self.course.id]),
            {"title": "Unauthorized lesson", "content": "Should not be created"},
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Lesson.objects.filter(course=self.course).exists())


class StudentCourseDataPermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_a = make_student("student_a")
        self.student_b = make_student("student_b")
        self.instructor = make_instructor("instructor_course_data")
        self.course = make_course(self.instructor, "Protected Course")
        make_enrollment(self.student_a, self.course)
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Protected Lesson",
            content="Protected content",
            document=SimpleUploadedFile("protected.txt", b"protected document"),
        )
        self.quiz = Quiz.objects.create(lesson=self.lesson, title="Protected Quiz")

    def test_unenrolled_student_cannot_view_course(self):
        self.client.force_login(self.student_b)
        response = self.client.get(reverse("course_detail", args=[self.course.id]))
        self.assertNotEqual(response.status_code, 200)

    def test_unenrolled_student_cannot_view_lesson(self):
        self.client.force_login(self.student_b)
        response = self.client.get(reverse("lesson_detail", args=[self.lesson.id]))
        self.assertNotEqual(response.status_code, 200)

    def test_unenrolled_student_cannot_submit_quiz(self):
        self.client.force_login(self.student_b)
        response = self.client.post(reverse("take_quiz", args=[self.quiz.id]), {})
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(QuizAttempt.objects.filter(quiz=self.quiz, student=self.student_b).exists())

    def test_unenrolled_student_cannot_view_document(self):
        self.client.force_login(self.student_b)
        response = self.client.get(reverse("view_document", args=[self.lesson.id]))
        self.assertNotEqual(response.status_code, 200)


class AdminRoutePermissionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = make_student("student_admin_routes")
        self.other_student = make_student("other_student")
        self.instructor = make_instructor("instructor_admin_routes")

    def test_student_cannot_view_admin_dashboard(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertNotEqual(response.status_code, 200)

    def test_instructor_cannot_view_admin_dashboard(self):
        self.client.force_login(self.instructor)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertNotEqual(response.status_code, 200)

    def test_student_cannot_view_learner_hub(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("learner_hub"))
        self.assertNotEqual(response.status_code, 200)

    def test_student_cannot_view_other_learner_detail(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("learner_detail", args=[self.other_student.id]))
        self.assertNotEqual(response.status_code, 200)

    def test_student_cannot_call_users_api(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("api_users"))
        self.assertEqual(response.status_code, 403)

    def test_instructor_cannot_call_users_api(self):
        self.client.force_login(self.instructor)
        response = self.client.get(reverse("api_users"))
        self.assertEqual(response.status_code, 403)


class AnonymousRoutePermissionTests(TestCase):
    def test_anonymous_student_dashboard_redirects(self):
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_anonymous_instructor_dashboard_redirects(self):
        response = self.client.get(reverse("instructor_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_admin_dashboard_redirects(self):
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_learner_hub_redirects(self):
        response = self.client.get(reverse("learner_hub"))
        self.assertEqual(response.status_code, 302)

    def test_anonymous_home_loads(self):
        response = self.client.get(reverse("company_home"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_programmes_loads(self):
        response = self.client.get(reverse("programmes"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_opportunities_loads(self):
        response = self.client.get(reverse("opportunities"))
        self.assertEqual(response.status_code, 200)