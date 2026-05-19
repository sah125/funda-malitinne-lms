"""
Create initial admin user and demo data
Usage: python manage.py create_demo_data
"""
from django.core.management.base import BaseCommand
from core.models import User, Course, Lesson
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial admin user and demo data'

    def handle(self, *args, **options):
        # Create superuser if doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@fundamalitinne.com',
                password='admin123456',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('✓ Admin user created (admin/admin123456)'))
        else:
            self.stdout.write(self.style.WARNING('• Admin user already exists'))

        # Create test instructor
        if not User.objects.filter(username='instructor').exists():
            instructor = User.objects.create_user(
                username='instructor',
                email='instructor@fundamalitinne.com',
                password='instructor123456',
                role='instructor',
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS('✓ Instructor user created'))
        else:
            self.stdout.write(self.style.WARNING('• Instructor user already exists'))

        # Create test student
        if not User.objects.filter(username='student').exists():
            student = User.objects.create_user(
                username='student',
                email='student@fundamalitinne.com',
                password='student123456',
                role='student'
            )
            self.stdout.write(self.style.SUCCESS('✓ Student user created'))
        else:
            self.stdout.write(self.style.WARNING('• Student user already exists'))

        self.stdout.write(self.style.SUCCESS('✓ Demo data setup complete!'))
