from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .conftest_base import make_admin, make_instructor, make_student

User = get_user_model()


class RegistrationTests(TestCase):
    def registration_data(self, **overrides):
        data = {
            "username": "newstudent",
            "email": "newstudent@test.local",
            "password": "TestPass123!",
            "password2": "TestPass123!",
            "full_name": "New Student",
            "id_number": "9001010000000",
            "date_of_birth": "1990-01-01",
            "gender": "female",
            "nationality": "South African",
            "contact_number": "0712345678",
            "disability": "None",
            "preferred_language": "English",
        }
        data.update(overrides)
        return data

    def test_registration_creates_unapproved_student_with_custom_fields(self):
        response = self.client.post(reverse("register"), self.registration_data())

        self.assertRedirects(response, reverse("login"))
        user = User.objects.get(username="newstudent")
        self.assertEqual(user.role, "student")
        self.assertFalse(user.is_approved)
        self.assertEqual(user.id_number, "9001010000000")
        self.assertEqual(user.date_of_birth.isoformat(), "1990-01-01")
        self.assertEqual(user.gender, "female")
        self.assertEqual(user.nationality, "South African")
        self.assertEqual(user.contact_number, "0712345678")
        self.assertEqual(user.preferred_language, "English")

    def test_duplicate_username_does_not_create_second_user(self):
        User.objects.create_user(
            username="newstudent",
            email="first@test.local",
            password="TestPass123!",
        )

        response = self.client.post(reverse("register"), self.registration_data())

        self.assertEqual(User.objects.filter(username="newstudent").count(), 1)
        self.assertContains(response, "Username already exists.")

    def test_duplicate_email_does_not_create_second_user(self):
        User.objects.create_user(
            username="existing",
            email="newstudent@test.local",
            password="TestPass123!",
        )

        response = self.client.post(reverse("register"), self.registration_data(username="other"))

        self.assertEqual(User.objects.filter(email="newstudent@test.local").count(), 1)
        self.assertContains(response, "Email already exists.")

    def test_password_mismatch_does_not_create_user(self):
        response = self.client.post(
            reverse("register"),
            self.registration_data(password2="DifferentPass123!"),
        )

        self.assertFalse(User.objects.filter(username="newstudent").exists())
        self.assertContains(response, "Passwords do not match.")


class LoginTests(TestCase):
    def test_student_login_redirects_to_student_dashboard(self):
        make_student(username="student-login")

        response = self.client.post(
            reverse("login"),
            {"username": "student-login", "password": "TestPass123!"},
        )

        self.assertRedirects(response, reverse("student_dashboard"))

    def test_instructor_login_redirects_to_instructor_dashboard(self):
        make_instructor(username="instructor-login")

        response = self.client.post(
            reverse("login"),
            {"username": "instructor-login", "password": "TestPass123!"},
        )

        self.assertRedirects(response, reverse("instructor_dashboard"))

    def test_admin_login_redirects_to_admin_dashboard(self):
        make_admin(username="admin-login")

        response = self.client.post(
            reverse("login"),
            {"username": "admin-login", "password": "TestPass123!"},
        )

        self.assertRedirects(response, reverse("admin_dashboard"))

    def test_invalid_credentials_render_error_without_redirect(self):
        response = self.client.post(
            reverse("login"),
            {"username": "missing", "password": "wrong"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_unapproved_student_currently_logs_in(self):
        user = User.objects.create_user(
            username="pending-login",
            email="pending-login@test.local",
            password="TestPass123!",
            role="student",
            is_active=True,
            is_approved=False,
        )

        response = self.client.post(
            reverse("login"),
            {"username": user.username, "password": "TestPass123!"},
        )

        self.assertRedirects(response, reverse("student_dashboard"))

    def test_logout_clears_session_and_redirects_to_login(self):
        user = make_student(username="logout-user")
        self.client.force_login(user)

        response = self.client.get(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class PasswordResetTests(TestCase):
    def test_forgot_password_populates_reset_token(self):
        user = make_student(username="reset-user")

        response = self.client.post(reverse("forgot_password"), {"email": user.email})

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.reset_password_token)
        self.assertContains(response, "Password reset link sent to your email.")

    def test_valid_reset_token_renders_reset_form(self):
        user = make_student(username="valid-reset")
        user.reset_password_token = "valid-token"
        user.reset_password_expires = timezone.now() + timedelta(hours=1)
        user.save(update_fields=["reset_password_token", "reset_password_expires"])

        response = self.client.get(reverse("reset_password", args=["valid-token"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'name="password2"')
        self.assertContains(response, 'method="POST"')

    def test_unknown_or_expired_reset_token_renders_invalid_state(self):
        response = self.client.get(reverse("reset_password", args=["unknown-token"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Link Expired")
        self.assertContains(response, "invalid or has expired")

        user = make_student(username="expired-reset")
        user.reset_password_token = "expired-token"
        user.reset_password_expires = timezone.now() - timedelta(minutes=1)
        user.save(update_fields=["reset_password_token", "reset_password_expires"])

        response = self.client.get(reverse("reset_password", args=["expired-token"]))

        self.assertContains(response, "Link Expired")