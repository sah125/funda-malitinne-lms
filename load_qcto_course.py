#!/usr/bin/env python3
import os
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Course, Lesson, Quiz, QuizQuestion, Assignment

User = get_user_model()

def create_qcto_course():
    print("Starting QCTO Management Assistant course creation...")

    # Get or create instructor
    instructor, created = User.objects.get_or_create(
        username='phumlani',
        defaults={
            'email': 'phumlani@malitinne.co.za',
            'first_name': 'Phumlani',
            'last_name': 'Phakathi',
            'role': 'instructor',
            'is_approved': True
        }
    )
    if created:
        instructor.set_password('Phumlani@123')
        instructor.save()
        print(f"✓ Created instructor: {instructor.username}")
    else:
        print(f"✓ Found instructor: {instructor.username}")

    # Create main qualification course
    course, created = Course.objects.get_or_create(
        title='Occupational Certificate: Management Assistant (SAQA ID 101876)',
        defaults={
            'description': """This qualification is designed for learners pursuing a career as a Management Assistant. 
It covers document management, computerised information processing, resource and procurement management, 
social media and digital literacy, office protocol, business communication, work-readiness, 
basic business calculations, introductory project management, and meeting administration.

Total credits: 316, NQF Level 5.""",
            'instructor': instructor,
            'level': 'intermediate',
            'price': 0,
            'status': 'published'
        }
    )
    if created:
        print(f"✓ Created course: {course.title}")
    else:
        print(f"⚠ Course already exists: {course.title}")

    # Knowledge modules (12)
    km_list = [
        {'order': 1, 'title': 'Document management and record-keeping', 'code': 'KM-01'},
        {'order': 2, 'title': 'Computerised Information Processing', 'code': 'KM-02'},
        {'order': 3, 'title': 'Resource and procurement management', 'code': 'KM-03'},
        {'order': 4, 'title': 'Social media and digital literacy', 'code': 'KM-04'},
        {'order': 5, 'title': 'Office protocol, deportment and etiquette', 'code': 'KM-05'},
        {'order': 6, 'title': 'Business communication and customer services', 'code': 'KM-06'},
        {'order': 7, 'title': 'Ready for work standards', 'code': 'KM-07'},
        {'order': 8, 'title': 'Basic business calculations', 'code': 'KM-08'},
        {'order': 9, 'title': 'Apply End User Computing', 'code': 'KM-09'},
        {'order': 10, 'title': 'Business documentation and design', 'code': 'KM-10'},
        {'order': 11, 'title': 'Meeting Administration', 'code': 'KM-11'},
        {'order': 12, 'title': 'Introductory project management', 'code': 'KM-12'},
    ]

    for km in km_list:
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            title=f"{km['code']}: {km['title']}",
            defaults={
                'content': f"This module covers the QCTO knowledge module {km['code']}. Refer to the official learning material for detailed content.",
                'duration': 45,
                'order': km['order']
            }
        )
        print(f"  {'Created' if created else 'Already exists'}: {lesson.title}")

    # Add a sample quiz for KM-01
    km01_lesson = Lesson.objects.filter(course=course, title__contains='KM-01').first()
    if km01_lesson:
        quiz, created = Quiz.objects.get_or_create(
            lesson=km01_lesson,
            defaults={
                'title': 'KM-01 Formative Assessment',
                'description': 'Test your understanding of document management and record-keeping.',
                'passing_score': 70,
            }
        )
        if created:
            print(f"✓ Created quiz for KM-01")
            QuizQuestion.objects.get_or_create(
                quiz=quiz,
                order=1,
                defaults={
                    'question_text': 'Define the term **document origination** in the context of document management and record-keeping.',
                    'question_type': 'multiple_choice',
                    'points': 10,
                    'option_a': 'The process of destroying old documents',
                    'option_b': 'The creation or generation of documents, whether by verbal, written or electronic instruction',
                    'option_c': 'Filing documents alphabetically',
                    'option_d': 'Storing documents offsite',
                    'correct_answer': 'B'
                }
            )
            QuizQuestion.objects.get_or_create(
                quiz=quiz,
                order=2,
                defaults={
                    'question_text': 'List three types of document origination.',
                    'question_type': 'multiple_choice',
                    'points': 10,
                    'option_a': 'Verbal, written, electronic instruction',
                    'option_b': 'Fax, email, memo',
                    'option_c': 'Circulars, letters, reports',
                    'option_d': 'Archiving, filing, disposal',
                    'correct_answer': 'A'
                }
            )
        else:
            print(f"⚠ Quiz already exists for KM-01")

    # Create a sample assignment
    Assignment.objects.get_or_create(
        course=course,
        title='Practical Assignment: Create a meeting agenda and minutes',
        defaults={
            'description': 'Prepare a meeting agenda and draft minutes for a simulated management meeting. Include action items, decisions, and follow-up tasks.',
            'due_date': datetime.now() + timedelta(days=30),
            'total_points': 100
        }
    )
    print("✓ Added assignment: Create a meeting agenda and minutes")

    print("\n✅ QCTO course structure loaded successfully!")
    print(f"🔗 Course URL: /course/{course.id}/")

if __name__ == '__main__':
    create_qcto_course()