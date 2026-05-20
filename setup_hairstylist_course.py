# core/management/commands/load_qcto_course.py
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import Course, Lesson, Quiz, QuizQuestion, Assignment

User = get_user_model()

class Command(BaseCommand):
    help = 'Load QCTO Management Assistant course structure into the LMS'

    def handle(self, *args, **options):
        self.stdout.write("Starting QCTO course creation...")

        # Create or get instructor (assume 'phumlani' exists, or create one)
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
            self.stdout.write(self.style.SUCCESS(f"Created instructor {instructor.username}"))

        # Create main qualification course
        course, created = Course.objects.get_or_create(
            title='Occupational Certificate: Management Assistant (SAQA ID 101876)',
            defaults={
                'description': """This qualification is designed for learners pursuing a career as a Management Assistant. 
It covers document management, computerised information processing, resource and procurement management, 
social media and digital literacy, office protocol, business communication, work-readiness, 
basic business calculations, introductory project management, and meeting administration.

The qualification consists of 12 knowledge modules, 8 practical modules, and 8 workplace modules.
Total credits: 316, NQF Level 5.""",
                'instructor': instructor,
                'level': 'intermediate',
                'price': 0,
                'status': 'published'
            }
        )
        self.stdout.write(self.style.SUCCESS(f"Course created/updated: {course.title}"))

        # Define knowledge modules (KM)
        # Each KM is a lesson, but we can also group them into sections.
        # Here we create a lesson for each knowledge module.
        knowledge_modules = [
            {
                'order': 1,
                'code': 'KM-01',
                'title': 'Document management and record-keeping',
                'content': """This module covers:
- Origination of documents (10%)
- Creation of a filing system (15%)
- Distribution of documents (15%)
- Filing categories (15%)
- Storage of documentation (15%)
- Archiving of documents (15%)
- Disposal of outdated documentation (15%)

Key learning outcomes:
- Understand types of document origination
- Create and maintain filing systems
- Distribute documents correctly
- Categorise and store documents properly
- Archive and dispose of records according to legislation""",
                'duration': 45,  # placeholder
            },
            {
                'order': 2,
                'code': 'KM-02',
                'title': 'Computerised Information Processing',
                'content': """This module covers:
- Concise communication documents (10%)
- Meeting documents (10%)
- Display documents (10%)
- Function documents (10%)
- Presentation documents (10%)
- Marketing documentation (10%)
- Report documents (10%)
- Financial documents (10%)
- Research document (10%)
- Formatting large documents (10%)

Learners will be able to create, design and produce organisational documents using complex technical features.""",
                'duration': 45,
            },
            {
                'order': 3,
                'code': 'KM-03',
                'title': 'Resource and procurement management',
                'content': """This module covers:
- Principles of financial and supply chain management (20%)
- Budgeting and expenditure (20%)
- Procurement (20%)
- Asset management and stocktaking (20%)
- Disposal management (20%)

Focus on obtaining goods and services efficiently and allocating resources.""",
                'duration': 45,
            },
            {
                'order': 4,
                'code': 'KM-04',
                'title': 'Social media and digital literacy',
                'content': """This module covers:
- Introduction to different social media platforms (50%)
- Social media as a communication tool (50%)

Learners will understand how to access, scan and evaluate online environments and use digital technology for networking and communication.""",
                'duration': 45,
            },
            {
                'order': 5,
                'code': 'KM-05',
                'title': 'Office protocol, deportment and etiquette',
                'content': """This module covers:
- International protocol (25%)
- Cultural diversity (25%)
- Multi-cultural communication (25%)
- Grooming and deportment (25%)

Develop professional image, etiquette, and cross-cultural communication skills.""",
                'duration': 45,
            },
            {
                'order': 6,
                'code': 'KM-06',
                'title': 'Business communication and customer services',
                'content': """This module covers:
- Concise business communication media (13%)
- Organisational communication (13%)
- Multi-cultural communication (13%)
- Oral communication and listening skills (13%)
- Conflict and stress (13%)
- Problem solving and decision making (13%)
- Business letters (13%)
- Report writing (9%)

Build effective communication and customer service skills.""",
                'duration': 45,
            },
            {
                'order': 7,
                'code': 'KM-07',
                'title': 'Ready for work standards',
                'content': """This module covers:
- Rules of professional conduct and ethics (20%)
- Interpersonal management (20%)
- Work-readiness (office orientation, etiquette, dress code) (40%)
- Legislation governing employment (20%)

Prepare learners for professional workplace standards and legal compliance.""",
                'duration': 45,
            },
            {
                'order': 8,
                'code': 'KM-08',
                'title': 'Basic business calculations',
                'content': """This module covers:
- Perform financial calculations (20%)
- Select appropriate methods and carry out financial calculations (20%)
- Check calculations and record outcomes (20%)
- Prepare and process banking and petty cash documents (20%)
- Prepare and process invoices for payment to creditors and for debtors (20%)

Develop numeracy skills for routine financial transactions.""",
                'duration': 45,
            },
            {
                'order': 9,
                'code': 'KM-09',
                'title': 'Apply End User Computing',
                'content': """This module covers:
- Understand keyboard functions (5%)
- Create, edit and format word documents (20%)
- Understand and use presentation software (20%)
- Understand and apply GUI based spreadsheet (20%)
- Create, send and receive e-mail messages (20%)
- Demonstrate ability to use the World Wide Web (10%)
- Safety and security of ICT (5%)

Essential computer literacy for office administration.""",
                'duration': 45,
            },
            {
                'order': 10,
                'code': 'KM-10',
                'title': 'Business documentation and design',
                'content': """This module covers:
- Establishing documentation standards (20%)
- Managing template design and development (20%)
- Developing standardised text for documents (20%)
- Developing and implementing strategies to ensure the use of standard documentation (20%)
- Develop and implement strategies for maintenance and continuous improvement of standard documentation (20%)

Learn to create, manage and improve organisational documentation.""",
                'duration': 45,
            },
            {
                'order': 11,
                'code': 'KM-11',
                'title': 'Meeting Administration',
                'content': """This module covers:
- Overview of meetings (20%)
- Pre-meeting logistics and procurement (20%)
- During meeting procedures (20%)
- How to write the minutes (20%)
- Post meeting activities (20%)

Master the complete cycle of meeting preparation, execution, and follow-up.""",
                'duration': 45,
            },
            {
                'order': 12,
                'code': 'KM-12',
                'title': 'Introductory project management',
                'content': """This module covers:
- Project management and the operating environment (10%)
- Project Life cycle (10%)
- Management structures (10%)
- Project management planning (10%)
- Scope management (10%)
- Scheduling and resource management (10%)
- Risk management and issue management (10%)
- Project quality management (10%)
- Communication (10%)
- Leadership and teamwork (10%)

Introduction to the key elements of the project management life-cycle.""",
                'duration': 45,
            },
        ]

        # Create lessons for each KM
        for km in knowledge_modules:
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                title=km['title'],
                defaults={
                    'content': km['content'],
                    'duration': km['duration'],
                    'order': km['order']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created lesson: {lesson.title}"))
            else:
                self.stdout.write(f"  Lesson already exists: {lesson.title}")

        # Optional: Add quizzes (formative assessments) for each KM
        # Example: Quiz for KM-01 (Document management)
        km01_lesson = Lesson.objects.filter(course=course, title='Document management and record-keeping').first()
        if km01_lesson:
            quiz, created = Quiz.objects.get_or_create(
                lesson=km01_lesson,
                defaults={
                    'title': 'Formative Assessment - Document Management',
                    'description': 'Test your understanding of document origination, filing, storage, archiving and disposal.',
                    'passing_score': 70,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created quiz for {km01_lesson.title}"))
                # Add sample questions from the formative assessment workbook
                # Example questions (you can expand with full set)
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
                # Add more questions as needed...

        # Create assignments for practical modules (example)
        # Practical Module 1: Create a trip itinerary
        Assignment.objects.get_or_create(
            course=course,
            title='Practical Assignment: Create a trip itinerary',
            defaults={
                'description': """Prepare a detailed travel itinerary for a business trip. Include:
- Destination(s), dates, travel times
- Accommodation details
- Meeting schedule
- Transportation arrangements
- Budget summary
Submit a professional document following organisational standards.""",
                'due_date': timezone.now() + timezone.timedelta(days=30),
                'total_points': 100
            }
        )
        self.stdout.write(self.style.SUCCESS("Added assignment: Create a trip itinerary"))

        self.stdout.write(self.style.SUCCESS("\n✅ QCTO course structure loaded successfully!"))
        self.stdout.write(f"🔗 Course URL: /course/{course.id}/")