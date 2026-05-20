
"""
Django management command to load the complete QCTO Office Administrator (SAQA ID 102161)
curriculum into the Funda Malitinne LMS.

Run with: python manage.py load_office_admin_course
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import (
    Course, LearningModule, Lesson, Quiz, QuizQuestion, Assignment, User
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Load QCTO Office Administrator (SAQA ID 102161) full curriculum into the LMS'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("Starting QCTO Office Administrator course creation...")
        self.stdout.write("=" * 60)

        # ------------------------------
        # 1. Create or get instructor
        # ------------------------------
        instructor, created = User.objects.get_or_create(
            username='admin',  # or use an existing admin/instructor
            defaults={
                'email': 'admin@malitinne.co.za',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'is_approved': True,
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            instructor.set_password('Admin@123')
            instructor.save()
            self.stdout.write(self.style.SUCCESS(f"Created instructor/admin: {instructor.username}"))

        # ------------------------------
        # 2. Create the main qualification course
        # ------------------------------
        course, created = Course.objects.get_or_create(
            title='Occupational Certificate: Office Administrator (SAQA ID 102161)',
            defaults={
                'description': """
This qualification is designed for learners seeking to become competent Office Administrators.
It covers all aspects of office administration, communication, protocol, computing, social media,
project management, resource management, tendering, document management, staffing, skills development,
public relations, and work-readiness.

**Qualification details:**
- SAQA ID: 102161
- NQF Level: 05
- Total credits: 445
- Knowledge modules: 15 (132 credits)
- Practical modules: 11 (155 credits)
- Workplace modules: 10 (158 credits)

**Exit Level Outcomes:**
1. Manage resources according to good governance policies and procedures.
2. Manage, coordinate and assist in administrative and clerical support using computerised systems.
3. Assist in selection, induction, employee wellness and skills development.
4. Process data to complete a Workplace Skills Plan.
5. Assist in marketing, public relations and advocacy administration.
6. Communicate effectively to maintain effective customer relationships.
7. Plan, administer and provide support services to special projects.
                """,
                'instructor': instructor,
                'level': 'intermediate',
                'price': 0,
                'status': 'published'
            }
        )
        self.stdout.write(self.style.SUCCESS(f"\n✅ Course created/updated: {course.title}"))
        self.stdout.write(f"   Course ID: {course.id} | URL: /course/{course.id}/")

        # ------------------------------
        # 3. Define Knowledge Modules (KM-01 to KM-15)
        # ------------------------------
        knowledge_modules_data = [
            {
                'code': 'KM-01',
                'title': 'Effective office administration and management',
                'credits': 10,
                'order': 1,
                'description': 'Basic organisation and administrative concepts (30%), office design trends (30%), working with internal staff (40%).',
                'kts': [
                    {'code': 'KT0101', 'title': 'Administration concepts', 'order': 1,
                     'content': 'Office administration is a set of day-to-day activities related to financial planning, record keeping, billing, personnel, physical distribution and logistics. Key roles: Receptionist (handles mail, meetings, public inquiries) and Personal Assistant (supports manager with data, travel, documents).',
                     'quiz_questions': [
                         {'text': 'What are some responsibilities that a receptionist is entrusted with?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['Allocate mail', 'Organise meetings', 'Communicate with public', 'All of the Above'],
                          'correct': 'D'},
                         {'text': 'Personal Assistants are commonly associated with an office manager that help maintain efficiency through providing...',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['Manager', 'CFO', 'Personal Assistants', 'CEO'], 'correct': 'C'},
                     ]},
                    {'code': 'KT0102', 'title': 'Elements of an organizational structure', 'order': 2,
                     'content': 'Organizational structure elements: Hierarchy, Control, Policies, Work Coordination, Communication, Work Specialization, Division of Department, Chain of Command (Authority, Responsibility, Unified Command), Span of Control.',
                     'quiz_questions': []},
                    {'code': 'KT0103', 'title': 'Roles and responsibilities in administration', 'order': 3,
                     'content': 'Administrator roles: Directing Processes, Staff Development, Liaising between Management and Staff. Responsibilities: Coordinate office activities, supervise staff, manage agendas, handle correspondence, support budgeting, maintain records, track supplies, prepare reports.',
                     'quiz_questions': []},
                    {'code': 'KT0104', 'title': 'Roles of a manager', 'order': 4,
                     'content': 'Manager responsibilities: Plan, Organize and Implement, Direct, Monitor, Evaluate. Managers lead departments or functional areas.',
                     'quiz_questions': []},
                    {'code': 'KT0105', 'title': 'Support structures within an organization', 'order': 5,
                     'content': 'Types of organizational structures: Pre-bureaucratic (centralized, small), Bureaucratic (hierarchy, rules, merit), Post-bureaucratic (consensus, network), Functional (by speciality), Divisional (by product/region), Matrix (both function and product).',
                     'quiz_questions': []},
                    {'code': 'KT0106', 'title': 'The growing organization, size and complexity', 'order': 6,
                     'content': 'Factors affecting structure: Size (larger -> more formal), Life Cycle (startup to mature), Strategy (growth vs stability), Business Environment (dynamic vs stable).',
                     'quiz_questions': []},
                    {'code': 'KT0107', 'title': 'Monitoring and compliance in administration cycle', 'order': 7,
                     'content': 'Two types of monitoring: Compliance monitoring (adhering to laws/standards) and Performance monitoring (efficiency and effectiveness). Methods include self-assessment tools, audits, benchmarking, and internal reviews.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-02',
                'title': 'Business communication and customer services',
                'credits': 8,
                'order': 2,
                'description': 'Concise business communication media (13%), organisational communication (13%), multi-cultural communication (13%), oral communication and listening skills (13%), conflict and stress (13%), problem solving and decision making (13%), business letters (13%), report writing (9%).',
                'kts': [
                    {'code': 'KT0201', 'title': 'Telephone message', 'order': 1,
                     'content': 'Telephone etiquette: Answer professionally, provide company name, take accurate messages with caller name, number, and message. Always represent the company positively.',
                     'quiz_questions': [
                         {'text': 'What is the most important rule when answering the phone at work?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['Speak quickly', 'Use a script', 'Act as representative of the company', 'Transfer all calls'],
                          'correct': 'C'},
                     ]},
                    {'code': 'KT0202', 'title': 'Fax message', 'order': 2,
                     'content': 'Fax (facsimile) is telephonic transmission of scanned printed material. Modern methods include fax machines, PC software, and online fax services.',
                     'quiz_questions': []},
                    {'code': 'KT0203', 'title': 'Memo', 'order': 3,
                     'content': 'A memo is a short, to-the-point communication. Basic reasons: to persuade action, issue a directive, or provide a report. Format: TO, FROM, DATE, SUBJECT.',
                     'quiz_questions': [
                         {'text': 'What are the basic reasons to write a memo?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['To persuade action', 'To issue a directive', 'To provide a report', 'All of the Above'],
                          'correct': 'D'},
                     ]},
                    {'code': 'KT0204', 'title': 'Forms and questionnaires', 'order': 4,
                     'content': 'Questionnaires are research instruments consisting of series of questions. Types: dichotomous, nominal-polytomous, ordinal-polytomous, continuous.',
                     'quiz_questions': [
                         {'text': 'What is a questionnaire?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['A type of memo', 'A research instrument consisting of questions', 'A meeting agenda', 'A financial report'],
                          'correct': 'B'},
                     ]},
                    {'code': 'KT0205', 'title': 'Email', 'order': 5,
                     'content': 'Electronic mail operates across computer networks. Types: web-based email (Gmail), POP3, IMAP, MAPI. Email provides written record, reduces cost, increases speed.',
                     'quiz_questions': [
                         {'text': 'Which protocol provides features to manage a mailbox from multiple devices?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['MAPI', 'Microsoft Exchange Server', 'IMAP email servers', 'None of the Above'],
                          'correct': 'C'},
                     ]},
                    {'code': 'KT0206', 'title': 'Notices', 'order': 6,
                     'content': 'Notice is the legal concept describing awareness of legal process affecting rights, obligations or duties. Types: public notice, actual notice, constructive notice, implied notice.',
                     'quiz_questions': []},
                    {'code': 'KT0207', 'title': 'Scanning', 'order': 7,
                     'content': 'A document scanner optically scans images, printed text or handwriting and converts it into a digital image.',
                     'quiz_questions': []},
                    {'code': 'KT0208', 'title': 'Organisational communication', 'order': 8,
                     'content': 'Internal communication is key to success. Vertical communication (up/down hierarchy) and horizontal (same level). Formal channels follow authority lines; informal channels (grapevine) are unofficial.',
                     'quiz_questions': [
                         {'text': 'External business communication is any information the company distributes to the public.',
                          'type': 'true_false', 'points': 2, 'options': [], 'correct': 'True'},
                         {'text': 'Horizontal communication is communication either up or down the formal hierarchy.',
                          'type': 'true_false', 'points': 2, 'options': [], 'correct': 'False'},
                     ]},
                ]
            },
            {
                'code': 'KM-03',
                'title': 'Office protocol, deportment and etiquette',
                'credits': 8,
                'order': 3,
                'description': 'International protocol (25%), cultural diversity (25%), multi-cultural communication (25%), grooming and deportment (25%).',
                'kts': [
                    {'code': 'KT0301', 'title': 'International protocol', 'order': 1,
                     'content': 'Protocol is the etiquette of diplomacy and affairs of state. It includes forms of address, introductions, and official order of precedence.',
                     'quiz_questions': [
                         {'text': 'What is the etiquette of diplomacy and affairs of state?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['Legislature', 'Protocol', 'Constitution', 'Law by Government'], 'correct': 'B'},
                     ]},
                    {'code': 'KT0302', 'title': 'Cultural diversity', 'order': 2,
                     'content': 'Cultural diversity brings together diverse cultures and ethnic backgrounds. Benefits: encourages creativity, builds respect, improves customer service, enhances work environment.',
                     'quiz_questions': [
                         {'text': 'What are benefits to having diversity in the workplace?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['Better understand demographics', 'Align culture with demographic make-up', 'Increased customer satisfaction', 'All of the Above'],
                          'correct': 'D'},
                         {'text': 'Multiculturalism brings together a diverse set of cultures and ethnic backgrounds in the work environment.',
                          'type': 'true_false', 'points': 2, 'options': [], 'correct': 'True'},
                     ]},
                    {'code': 'KT0303', 'title': 'Multi-cultural communication', 'order': 3,
                     'content': 'Use SOFTEN approach: Smile, Open gestures, Forward lean, Touch, Eye contact, Nod. Non-verbal communication varies across cultures (eye contact, personal space, gestures).',
                     'quiz_questions': []},
                    {'code': 'KT0304', 'title': 'Grooming and deportment', 'order': 4,
                     'content': 'First impressions are critical. Dress professionally, maintain good hygiene, firm handshake, confident posture, active listening.',
                     'quiz_questions': [
                         {'text': 'What are areas of communication that you may want to practice?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['Non-verbal communication', 'Conversation skills', 'Assertiveness', 'All of the Above'],
                          'correct': 'D'},
                     ]},
                ]
            },
            {
                'code': 'KM-04',
                'title': 'Apply End User Computing',
                'credits': 6,
                'order': 4,
                'description': 'Understand Keyboard functions (5%), create/edit/format word documents (20%), understand and use presentation software (20%), understand and apply GUI based spreadsheet (20%), create/send/receive email (20%), use World Wide Web (10%), ICT safety and security (5%).',
                'kts': [
                    {'code': 'KT0401', 'title': 'Keyboard functions', 'order': 1,
                     'content': 'Keyboard sections: QWERTY keys, function keys (F1-F12), numeric keypad, cursor control keys, special keys (Enter, Backspace, Tab, Shift, Caps Lock, Ctrl, Alt).',
                     'quiz_questions': [
                         {'text': 'The long bar across the bottom of the keyboard is the...',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['Tab key', 'Space bar', 'Shift key', 'Enter key'], 'correct': 'B'},
                         {'text': 'What does GIGO stand for?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['Garbage In, Garbage Out', 'Get In, Get Out', 'Google Input, Google Output', 'General Input/General Output'],
                          'correct': 'A'},
                     ]},
                    {'code': 'KT0402', 'title': 'Word processing', 'order': 2,
                     'content': 'Microsoft Word is a word-processing application. Key features: creating, editing, formatting documents, importing data, document management.',
                     'quiz_questions': [
                         {'text': 'What is the purpose of a word processor?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['To process words', 'To process documents', 'To process emails', 'To process files'],
                          'correct': 'A'},
                     ]},
                    {'code': 'KT0403', 'title': 'Presentation software', 'order': 3,
                     'content': 'PowerPoint allows creation of slides with text, images, clip art. Use design templates or blank presentations. Add slides, format text, insert media.',
                     'quiz_questions': []},
                    {'code': 'KT0404', 'title': 'Spreadsheet applications', 'order': 4,
                     'content': 'Excel uses rows (1-65536) and columns (A-Z...). Cells identified by column+row (e.g., A1). Formulas start with = (e.g., =B2+B3+B4).',
                     'quiz_questions': []},
                    {'code': 'KT0405', 'title': 'Email management', 'order': 5,
                     'content': 'Email etiquette: specific subject line, professional tone, avoid ALL CAPS, proofread, include signature, use folders, move messages, manage contacts.',
                     'quiz_questions': []},
                    {'code': 'KT0406', 'title': 'Internet basics', 'order': 6,
                     'content': 'The Internet is a worldwide network of networks. World Wide Web uses browsers (Chrome, Firefox). URLs, domain names (e.g., .com, .edu, .gov).',
                     'quiz_questions': [
                         {'text': 'What is the Internet?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['A single computer', 'A worldwide telecommunications system', 'A type of software', 'A web browser'],
                          'correct': 'B'},
                     ]},
                    {'code': 'KT0407', 'title': 'ICT safety and security', 'order': 7,
                     'content': 'Protect against viruses, spam, malware. Use antivirus software, firewalls, strong passwords, regular backups, and be cautious with email attachments.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-05',
                'title': 'Social media and digital literacy',
                'credits': 5,
                'order': 5,
                'description': 'Introduction to social media (50%), social media as a communication tool (50%).',
                'kts': [
                    {'code': 'KT0501', 'title': 'Introduction to social media', 'order': 1,
                     'content': 'Social media is the collective of online communication channels dedicated to community-based input, interaction, content-sharing and collaboration. Examples: Facebook, Twitter, LinkedIn, YouTube, Instagram, Pinterest.',
                     'quiz_questions': [
                         {'text': 'What is social media?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['A type of newspaper', 'Collective of online communications channels for community-based interaction', 'A television network', 'A government agency'],
                          'correct': 'B'},
                     ]},
                    {'code': 'KT0502', 'title': 'Social media as a communication tool', 'order': 2,
                     'content': 'Social media has shifted communication from one-way to two-way. Brands can engage directly with customers. Benefits: increased exposure, traffic, leads, marketplace insight.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-06',
                'title': 'Introductory project management',
                'credits': 2,
                'order': 6,
                'description': 'Project management and operating environment (10%), project life cycle (10%), management structures (10%), planning (10%), scope management (10%), scheduling and resource management (10%), risk and issue management (10%), quality management (10%), communication (10%), leadership and teamwork (10%).',
                'kts': [
                    {'code': 'KT0601', 'title': 'Project management fundamentals', 'order': 1,
                     'content': 'A project is a temporary endeavour to create a unique product or service. Project management is the application of knowledge, skills, tools, and techniques to project activities.',
                     'quiz_questions': [
                         {'text': 'What is a project?',
                          'type': 'multiple_choice', 'points': 2,
                          'options': ['Ongoing operations', 'A temporary endeavour to create a unique product or service', 'A department', 'A meeting'],
                          'correct': 'B'},
                     ]},
                    {'code': 'KT0602', 'title': 'Project life cycle', 'order': 2,
                     'content': 'Project life cycle phases: Initiation, Planning, Execution, Monitoring & Control, Closure.',
                     'quiz_questions': []},
                    {'code': 'KT0603', 'title': 'Project management planning', 'order': 3,
                     'content': 'Project management plan includes scope, schedule, cost, quality, resource, communication, risk, procurement, and stakeholder management.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-07',
                'title': 'Computerised Project Management',
                'credits': 15,
                'order': 7,
                'description': 'Use of project management software (e.g., MS Project, Jira, Trello) to plan, schedule, track, and report on projects.',
                'kts': [
                    {'code': 'KT0701', 'title': 'Introduction to project management software', 'order': 1,
                     'content': 'Project management software helps plan, schedule, allocate resources, track progress, and manage budgets. Examples: Microsoft Project, Trello, Asana, Jira.',
                     'quiz_questions': []},
                    {'code': 'KT0702', 'title': 'Creating and scheduling tasks', 'order': 2,
                     'content': 'Tasks are broken down into work packages. Use Gantt charts to visualise schedule, dependencies, critical path. Set milestones and deadlines.',
                     'quiz_questions': []},
                    {'code': 'KT0703', 'title': 'Resource management', 'order': 3,
                     'content': 'Resources include people, equipment, materials, and budget. Assign resources to tasks, level overallocation, track actual vs planned usage.',
                     'quiz_questions': []},
                ]
            },
            # KM-08 to KM-15 (placeholders with basic structure)
            {
                'code': 'KM-08',
                'title': 'Basic business calculations',
                'credits': 5,
                'order': 8,
                'description': 'Perform financial calculations, select appropriate methods, check calculations, prepare banking and petty cash documents, process invoices.',
                'kts': [
                    {'code': 'KT0801', 'title': 'Financial calculations', 'order': 1,
                     'content': 'Perform calculations involving percentages, markups, discounts, VAT, simple interest, and currency conversions.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-09',
                'title': 'Resource and procurement management',
                'credits': 15,
                'order': 9,
                'description': 'Principles of financial and supply chain management, budgeting, procurement, asset management, stocktaking, disposal management.',
                'kts': [
                    {'code': 'KT0901', 'title': 'Procurement principles', 'order': 1,
                     'content': 'Procurement is the process of obtaining goods and services. Includes requisition, sourcing, purchase order, receipt, payment.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-10',
                'title': 'Tender and procurement processes',
                'credits': 5,
                'order': 10,
                'description': 'Tendering procedures, bid documentation, evaluation criteria, contract award.',
                'kts': [
                    {'code': 'KT1001', 'title': 'Tendering process', 'order': 1,
                     'content': 'Tender is a formal offer to supply goods or services at a stated price. Process includes advertising, bid submission, evaluation, award.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-11',
                'title': 'Document management and record keeping',
                'credits': 15,
                'order': 11,
                'description': 'Document origination, filing systems, distribution, storage, archiving, disposal.',
                'kts': [
                    {'code': 'KT1101', 'title': 'Document management systems', 'order': 1,
                     'content': 'Document management includes capture, storage, retrieval, sharing, and disposal. Electronic document management systems (EDMS) improve efficiency.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-12',
                'title': 'Staffing and people support',
                'credits': 15,
                'order': 12,
                'description': 'Recruitment, selection, induction, employee wellness, skills development.',
                'kts': [
                    {'code': 'KT1201', 'title': 'Recruitment and selection', 'order': 1,
                     'content': 'Recruitment process: job analysis, advertising, shortlisting, interviewing, reference checks, offer.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-13',
                'title': 'Principles of NQF in relation to Skills development and WSP administration',
                'credits': 12,
                'order': 13,
                'description': 'NQF structure, SAQA, QCTO, SETAs, Workplace Skills Plan (WSP) development, training needs analysis.',
                'kts': [
                    {'code': 'KT1301', 'title': 'Workplace Skills Plan (WSP)', 'order': 1,
                     'content': 'WSP is a plan that identifies training needs within an organisation and allocates resources to address them.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-14',
                'title': 'Public relations, marketing and advocacy',
                'credits': 6,
                'order': 14,
                'description': 'PR principles, marketing communication, advocacy campaigns, media relations.',
                'kts': [
                    {'code': 'KT1401', 'title': 'Public relations basics', 'order': 1,
                     'content': 'PR manages the spread of information between an organisation and the public. Includes press releases, media relations, crisis communication.',
                     'quiz_questions': []},
                ]
            },
            {
                'code': 'KM-15',
                'title': 'Ready for work standards',
                'credits': 5,
                'order': 15,
                'description': 'Professional conduct, ethics, interpersonal management, office orientation, dress code, employment legislation.',
                'kts': [
                    {'code': 'KT1501', 'title': 'Work-readiness', 'order': 1,
                     'content': 'Work-readiness includes punctuality, professional appearance, communication skills, teamwork, problem-solving, and ethical behaviour.',
                     'quiz_questions': []},
                ]
            },
        ]

        # ------------------------------
        # 4. Create LearningModules and Lessons (KTs)
        # ------------------------------
        for km_data in knowledge_modules_data:
            # Create LearningModule (grouping for KTs)
            learning_module, created = LearningModule.objects.get_or_create(
                course=course,
                title=km_data['title'],
                defaults={
                    'description': km_data['description'],
                    'order': km_data['order'],
                    'is_visible': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"\n📘 Created LearningModule: {km_data['code']} - {km_data['title']}"))
            else:
                self.stdout.write(f"\n   LearningModule exists: {km_data['title']}")

            # Create Lessons (KTs) within this LearningModule
            for kt in km_data['kts']:
                lesson, created = Lesson.objects.get_or_create(
                    course=course,
                    title=kt['title'],
                    defaults={
                        'content': kt['content'],
                        'duration': 30,  # minutes, adjust as needed
                        'order': kt['order'],
                        'module': learning_module
                    }
                )
                if created:
                    self.stdout.write(f"   ✅ Created lesson: {kt['code']} - {kt['title']}")
                else:
                    self.stdout.write(f"   ⚠️ Lesson already exists: {kt['title']}")

                # Create quiz for lesson if questions exist
                if kt.get('quiz_questions'):
                    quiz, quiz_created = Quiz.objects.get_or_create(
                        lesson=lesson,
                        defaults={
                            'title': f'Formative Assessment: {kt["title"]}',
                            'description': f'Test your knowledge of {kt["title"]}.',
                            'passing_score': 70,
                        }
                    )
                    if quiz_created:
                        self.stdout.write(f"      📝 Created quiz for {kt['title']}")

                        # Add quiz questions
                        for idx, q in enumerate(kt['quiz_questions'], start=1):
                            # Map correct answer to option letter
                            correct_option = q['correct'].upper()
                            # Build options list
                            if q['type'] == 'multiple_choice':
                                options = q.get('options', [])
                                if len(options) >= 4:
                                    opt_a = options[0] if len(options) > 0 else ''
                                    opt_b = options[1] if len(options) > 1 else ''
                                    opt_c = options[2] if len(options) > 2 else ''
                                    opt_d = options[3] if len(options) > 3 else ''
                                else:
                                    opt_a = opt_b = opt_c = opt_d = ''
                            else:  # true_false
                                opt_a = 'True'
                                opt_b = 'False'
                                opt_c = ''
                                opt_d = ''
                                if correct_option == 'TRUE':
                                    correct_option = 'A'
                                else:
                                    correct_option = 'B'

                            QuizQuestion.objects.get_or_create(
                                quiz=quiz,
                                order=idx,
                                defaults={
                                    'question_text': q['text'],
                                    'question_type': q['type'],
                                    'points': q.get('points', 10),
                                    'option_a': opt_a,
                                    'option_b': opt_b,
                                    'option_c': opt_c,
                                    'option_d': opt_d,
                                    'correct_answer': correct_option
                                }
                            )
                            self.stdout.write(f"         Added question {idx}: {q['text'][:50]}...")

        # ------------------------------
        # 5. Add Practical Assignments (example from curriculum)
        # ------------------------------
        assignments_data = [
            {
                'title': 'Practical Assignment: Create a trip itinerary',
                'description': """Prepare a detailed travel itinerary for a business trip. Include:
- Destination(s), dates, travel times
- Accommodation details
- Meeting schedule
- Transportation arrangements
- Budget summary
Submit a professional document following organisational standards.""",
                'due_days': 30,
                'points': 100,
            },
            {
                'title': 'Practical Assignment: Organise a meeting',
                'description': """Plan and document a formal meeting. Provide:
- Notice of meeting (agenda)
- Venue booking and catering plan
- Meeting pack (reports, presentations)
- Draft minutes template
- Action log
Submit all documents as a single portfolio.""",
                'due_days': 45,
                'points': 100,
            },
            {
                'title': 'Practical Assignment: Develop a Workplace Skills Plan (WSP)',
                'description': """Using provided training data, complete a WSP template including:
- Training needs analysis
- Priority skills areas
- Budget allocation
- Implementation timeline
- Reporting metrics""",
                'due_days': 60,
                'points': 100,
            },
            {
                'title': 'Summative Portfolio of Evidence (POE)',
                'description': """Compile all formative assessments, workplace logbooks, and practical assignments into a single PDF portfolio.
Include signed declarations, supervisor reports, and evidence of competence against all exit level outcomes.
Submit via LMS for final assessment.""",
                'due_days': 120,
                'points': 200,
            }
        ]

        for assign in assignments_data:
            assign_obj, created = Assignment.objects.get_or_create(
                course=course,
                title=assign['title'],
                defaults={
                    'description': assign['description'],
                    'due_date': timezone.now() + timezone.timedelta(days=assign['due_days']),
                    'total_points': assign['points']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created assignment: {assign['title']}"))
            else:
                self.stdout.write(f"   Assignment exists: {assign['title']}")

        # ------------------------------
        # 6. Final output
        # ------------------------------
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ QCTO Office Administrator course structure loaded successfully!"))
        self.stdout.write(f"🔗 Course URL: /course/{course.id}/")
        self.stdout.write(f"📚 Total LearningModules: {LearningModule.objects.filter(course=course).count()}")
        self.stdout.write(f"📖 Total Lessons: {Lesson.objects.filter(course=course).count()}")
        self.stdout.write(f"📝 Total Quizzes: {Quiz.objects.filter(lesson__course=course).count()}")
        self.stdout.write(f"📄 Total Assignments: {Assignment.objects.filter(course=course).count()}")
        self.stdout.write("=" * 60)