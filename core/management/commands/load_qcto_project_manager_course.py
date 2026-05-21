# core/management/commands/load_qcto_project_manager_course.py
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import (
    Course, Lesson, Quiz, QuizQuestion, Assignment, 
    LearningModule, LessonModule, User, Progress
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Load complete QCTO Occupational Certificate: Project Manager (SAQA ID 101869)'

    def handle(self, *args, **options):
        self.stdout.write("=" * 80)
        self.stdout.write("QCTO OCCUPATIONAL CERTIFICATE: PROJECT MANAGER")
        self.stdout.write("SAQA ID: 101869 | NQF Level 05 | Credits: 240")
        self.stdout.write("=" * 80)
        self.stdout.write("")

        # ============================================================
        # CREATE OR GET INSTRUCTOR
        # ============================================================
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
            self.stdout.write(self.style.SUCCESS(f"✓ Created instructor: {instructor.username}"))
        else:
            self.stdout.write(f"✓ Using existing instructor: {instructor.username}")

        # ============================================================
        # CREATE MAIN QUALIFICATION COURSE
        # ============================================================
        course, created = Course.objects.get_or_create(
            title='Occupational Certificate: Project Manager (SAQA ID 101869)',
            defaults={
                'description': """This qualification is designed for learners pursuing a career as a Project Manager. 
A Project Manager applies knowledge of project management to achieve project objectives in a specific field of application.

QUALIFICATION OVERVIEW:
• NQF Level: 05
• Total Credits: 240
• Registration: 2018-07-01 to 2025-12-30
• Last Enrolment: 2026-12-30
• Last Achievement: 2029-12-30

QUALIFICATION STRUCTURE:
• Knowledge Modules: 11 modules (80 credits)
• Practical Skill Modules: 13 modules (100 credits)
• Work Experience Modules: 4 modules (60 credits)

EXIT LEVEL OUTCOMES:
1. Initiate a project to address specific project objectives.
2. Plan and prepare the delivery of a project.
3. Execute and control the delivery of a project management plan.
4. Manage the project close out process.

This qualification replaces: 
• National Certificate: Generic Project Management (Level 4, 146 credits)
• FET Certificate: Project Management (Level 4, 136 credits)
• National Certificate: Project Management (Level 5, 120 credits)
• National Diploma: Project Management (Level 5, 247 credits)""",
                'instructor': instructor,
                'level': 'intermediate',
                'price': 0,
                'status': 'published'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Course created: {course.title}"))
        else:
            self.stdout.write(f"✓ Course already exists: {course.title}")

        # ============================================================
        # KNOWLEDGE MODULES (KM) - 11 modules, 80 credits
        # ============================================================
        self.stdout.write("")
        self.stdout.write("-" * 60)
        self.stdout.write("KNOWLEDGE MODULES (80 Credits)")
        self.stdout.write("-" * 60)

        knowledge_modules_data = [
            {
                'code': 'KM-01',
                'title': 'Introductory Studies for Project Managers',
                'credits': 4,
                'order': 1,
                'description': """This foundational module explores project management as a career, the skills development landscape for project managers, the structure and focus of the qualification, learning delivery methods, and final assessment and certification processes. Topics include KT0101 Career opportunities, KT0102 Skills development landscape, KT0103 Structure and focus of this qualification, KT0104 Structured learning and delivery, KT0105 Final assessment and certification."""
            },
            {
                'code': 'KM-02',
                'title': 'Project Integration Management',
                'credits': 4,
                'order': 2,
                'description': """This module covers the processes and activities needed to identify, define, combine, unify, and coordinate the various processes and project management activities. Topics include: KT01 Project charters, KT02 Project management plan, KT03 Direct and manage project work, KT04 Monitor and control project work, KT05 Integrated change control, KT06 Project close out."""
            },
            {
                'code': 'KM-03',
                'title': 'Project Scope Management',
                'credits': 8,
                'order': 3,
                'description': """This module ensures that the project includes all the work required, and only the work required, to complete the project successfully. Topics include: KT01 Scope management planning, KT02 Requirements and needs, KT03 Define scope, KT04 Work breakdown structures, KT05 Validate scope, KT06 Control scope."""
            },
            {
                'code': 'KM-04',
                'title': 'Project Time Management',
                'credits': 8,
                'order': 4,
                'description': """This module covers the processes required to manage the timely completion of the project. Topics include: KT01 Plan schedule management, KT02 Define schedule activities, KT03 Sequence activities, KT04 Estimate activity resources, KT05 Estimate activity duration, KT06 Develop schedule, KT07 Control schedule."""
            },
            {
                'code': 'KM-05',
                'title': 'Project Cost Management',
                'credits': 8,
                'order': 5,
                'description': """This module covers the processes involved in planning, estimating, budgeting, financing, funding, managing, and controlling costs so that the project can be completed within the approved budget. Topics include: KT01 Plan cost management, KT02 Estimate costs, KT03 Project budgeting concepts, KT04 Control costs."""
            },
            {
                'code': 'KM-06',
                'title': 'Project Quality Management',
                'credits': 8,
                'order': 6,
                'description': """This module covers the processes and activities of the performing organization that determine quality policies, objectives, and responsibilities so that the project will satisfy the needs for which it was undertaken. Topics include: KT01 Plan quality management, KT02 Perform quality assurance, KT03 Control quality."""
            },
            {
                'code': 'KM-07',
                'title': 'Project Human Resource Management',
                'credits': 8,
                'order': 7,
                'description': """This module covers the processes that organize, manage, and lead the project team. Topics include: KT01 Plan HR management, KT02 Acquire a project team, KT03 Develop a project team, KT04 Manage a project team. Additional topics: Team employment concepts, Team selection and interviewing, Employment law, Skills gap analysis, Training needs evaluation."""
            },
            {
                'code': 'KM-08',
                'title': 'Project Communications Management',
                'credits': 8,
                'order': 8,
                'description': """This module covers the processes required to ensure timely and appropriate planning, collection, creation, distribution, storage, retrieval, management, control, monitoring, and ultimate disposition of project information. Topics include: KT01 Plan communications management, KT02 Manage communications, KT03 Control communications."""
            },
            {
                'code': 'KM-09',
                'title': 'Project Risk Management',
                'credits': 8,
                'order': 9,
                'description': """This module covers the processes of conducting risk management planning, identification, analysis, response planning, and controlling risk on a project. Topics include: KT01 Plan risk management, KT02 Identify risks, KT03 Qualitative risk analysis, KT04 Quantitative risk analysis, KT05 Plan risk response, KT06 Control risks."""
            },
            {
                'code': 'KM-10',
                'title': 'Project Procurement Management',
                'credits': 8,
                'order': 10,
                'description': """This module covers the processes necessary to purchase or acquire products, services, or results needed from outside the project team. Topics include: KT01 Plan procurement management, KT02 Conduct procurement, KT03 Control procurement."""
            },
            {
                'code': 'KM-11',
                'title': 'Project Stakeholder Management',
                'credits': 8,
                'order': 11,
                'description': """This module covers the processes required to identify the people, groups, or organizations that could impact or be impacted by the project, to analyze stakeholder expectations and their impact on the project, and to develop appropriate management strategies for effectively engaging stakeholders. Topics include: KT01 Stakeholder identification, KT02 Plan stakeholder management, KT03 Manage stakeholder engagements, KT04 Control stakeholder engagements."""
            }
        ]

        for km_data in knowledge_modules_data:
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                title=f"{km_data['code']}: {km_data['title']}",
                defaults={
                    'content': km_data['description'],
                    'duration': km_data['credits'] * 10,
                    'order': km_data['order']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created KM: {km_data['code']} - {km_data['title']} ({km_data['credits']} credits)"))
            else:
                self.stdout.write(f"  ○ KM already exists: {km_data['code']} - {km_data['title']}")

        # ============================================================
        # PRACTICAL SKILL MODULES (PM) - 13 modules, 100 credits
        # ============================================================
        self.stdout.write("")
        self.stdout.write("-" * 60)
        self.stdout.write("PRACTICAL SKILL MODULES (100 Credits)")
        self.stdout.write("-" * 60)

        practical_modules_data = [
            {
                'code': 'PM-01',
                'title': 'Initiate a project',
                'credits': 4,
                'order': 12,
                'description': """This practical module focuses on project initiation activities including:
• Developing project charters
• Identifying stakeholders
• Conducting feasibility studies
• Creating business cases
• Establishing project governance structures
• Defining high-level scope and objectives
• Securing project authorization and funding"""
            },
            {
                'code': 'PM-02',
                'title': 'Plan and develop a project management approach and scope statement',
                'credits': 8,
                'order': 13,
                'description': """This module covers detailed project planning including:
• Developing comprehensive scope statements
• Creating work breakdown structures (WBS)
• Establishing acceptance criteria
• Defining deliverables and milestones
• Documenting assumptions and constraints
• Creating project management plans"""
            },
            {
                'code': 'PM-03',
                'title': 'Plan and develop a project timeline and schedule',
                'credits': 8,
                'order': 14,
                'description': """This module focuses on schedule development:
• Creating activity lists and attributes
• Developing network diagrams
• Applying critical path method (CPM)
• Using scheduling software (MS Project, Primavera)
• Resource leveling and optimization
• Creating Gantt charts and milestone schedules"""
            },
            {
                'code': 'PM-04',
                'title': 'Plan for and project the cost of a project',
                'credits': 8,
                'order': 15,
                'description': """This module covers cost estimation and budgeting:
• Applying cost estimation techniques (analogous, parametric, bottom-up)
• Developing cost baselines
• Creating contingency reserves
• Cost aggregation and funding limit reconciliation
• Life-cycle costing and value engineering"""
            },
            {
                'code': 'PM-05',
                'title': 'Plan project management systems',
                'credits': 8,
                'order': 16,
                'description': """This module covers project management systems development:
• Quality management systems
• Communication management systems
• Risk management frameworks
• Procurement management systems
• Human resource management systems
• Document management and version control"""
            },
            {
                'code': 'PM-06',
                'title': 'Monitor and control the scope of a project',
                'credits': 8,
                'order': 17,
                'description': """This module focuses on scope control:
• Scope verification and validation
• Preventing scope creep
• Managing change requests
• Updating scope baseline
• Requirements traceability
• Configuration management"""
            },
            {
                'code': 'PM-07',
                'title': 'Control the project delivery schedules and costs',
                'credits': 8,
                'order': 18,
                'description': """This module covers schedule and cost control:
• Earned Value Management (EVM)
• Schedule variance and cost variance analysis
• Performance measurement baselines
• Forecasting and trend analysis
• Schedule compression techniques
• Cost control and budget tracking"""
            },
            {
                'code': 'PM-08',
                'title': 'Control the project quality',
                'credits': 8,
                'order': 19,
                'description': """This module covers quality management:
• Quality control techniques (control charts, Pareto analysis)
• Quality audits and inspections
• Statistical sampling and testing
• Corrective and preventive actions
• Continuous improvement (PDCA cycle)
• Cost of quality (COQ) analysis"""
            },
            {
                'code': 'PM-09',
                'title': 'Manage and control the human resources of a project',
                'credits': 8,
                'order': 20,
                'description': """This module covers HR management:
• Team acquisition and onboarding
• Performance management and appraisals
• Training and development
• Conflict resolution and negotiation
• Motivation and team building
• Resource calendars and allocation"""
            },
            {
                'code': 'PM-10',
                'title': 'Conduct and control project communication and stakeholder interaction',
                'credits': 8,
                'order': 21,
                'description': """This module covers communication management:
• Communication planning and execution
• Stakeholder engagement strategies
• Meeting facilitation and management
• Status reporting and dashboards
• Information distribution systems
• Feedback collection and analysis"""
            },
            {
                'code': 'PM-11',
                'title': 'Manage and control project risks',
                'credits': 8,
                'order': 22,
                'description': """This module covers risk management:
• Risk identification and documentation
• Qualitative and quantitative risk analysis
• Risk response planning (avoid, mitigate, transfer, accept)
• Risk monitoring and control
• Contingency and reserve analysis
• Monte Carlo simulation and decision trees"""
            },
            {
                'code': 'PM-12',
                'title': 'Manage and control project procurement activities',
                'credits': 8,
                'order': 23,
                'description': """This module covers procurement management:
• Make-or-buy analysis
• RFQ/RFP development and management
• Bidder conferences and proposal evaluation
• Contract negotiation and administration
• Supplier performance management
• Claims administration and dispute resolution"""
            },
            {
                'code': 'PM-13',
                'title': 'Manage and control project close-out activities',
                'credits': 8,
                'order': 24,
                'description': """This module covers project closure:
• Final deliverable acceptance and sign-off
• Lessons learned documentation
• Project archives and knowledge transfer
• Resource demobilization
• Contract closure and financial reconciliation
• Post-project reviews and benefits realization"""
            }
        ]

        for pm_data in practical_modules_data:
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                title=f"{pm_data['code']}: {pm_data['title']}",
                defaults={
                    'content': pm_data['description'],
                    'duration': pm_data['credits'] * 10,
                    'order': pm_data['order']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created PM: {pm_data['code']} - {pm_data['title']} ({pm_data['credits']} credits)"))
            else:
                self.stdout.write(f"  ○ PM already exists: {pm_data['code']} - {pm_data['title']}")

        # ============================================================
        # WORK EXPERIENCE MODULES (WM) - 4 modules, 60 credits
        # ============================================================
        self.stdout.write("")
        self.stdout.write("-" * 60)
        self.stdout.write("WORK EXPERIENCE MODULES (60 Credits)")
        self.stdout.write("-" * 60)

        work_modules_data = [
            {
                'code': 'WM-01',
                'title': 'Attend to project initiation management processes',
                'credits': 10,
                'order': 25,
                'description': """Workplace experience in project initiation:

EXPERIENCE REQUIREMENTS:
• Participate in project charter development
• Assist in stakeholder identification and analysis
• Contribute to business case development
• Support feasibility studies
• Help establish project governance

EVIDENCE TO COLLECT:
• Project charter drafts and final versions
• Stakeholder registers
• Business case documents
• Meeting minutes from initiation meetings
• Supervisor sign-offs on completed tasks

MINIMUM DURATION: 100 hours of workplace exposure"""
            },
            {
                'code': 'WM-02',
                'title': 'Attend to project planning processes',
                'credits': 20,
                'order': 26,
                'description': """Workplace experience in project planning:

EXPERIENCE REQUIREMENTS:
• Develop work breakdown structures (WBS)
• Create project schedules using planning software
• Assist in cost estimation and budgeting
• Contribute to risk identification and analysis
• Help develop quality management plans
• Participate in communication planning

EVIDENCE TO COLLECT:
• WBS documentation
• Project schedule files (MS Project, etc.)
• Cost estimates and budget spreadsheets
• Risk registers
• Quality management plans
• Communication management plans

MINIMUM DURATION: 200 hours of workplace exposure"""
            },
            {
                'code': 'WM-03',
                'title': 'Attend to project execution and control processes',
                'credits': 20,
                'order': 27,
                'description': """Workplace experience in project execution and control:

EXPERIENCE REQUIREMENTS:
• Monitor project progress against baselines
• Track and report on schedule and cost performance
• Participate in risk monitoring and response
• Assist in quality control activities
• Support stakeholder communication
• Manage change requests and issue logs
• Contribute to procurement administration

EVIDENCE TO COLLECT:
• Status reports and dashboards
• Performance measurement data (EVM)
• Risk monitoring logs
• Quality control checklists and test results
• Communication records and meeting minutes
• Change request logs
• Procurement documentation

MINIMUM DURATION: 200 hours of workplace exposure"""
            },
            {
                'code': 'WM-04',
                'title': 'Attend to project close out processes',
                'credits': 10,
                'order': 28,
                'description': """Workplace experience in project close-out:

EXPERIENCE REQUIREMENTS:
• Assist in final deliverable acceptance
• Participate in lessons learned sessions
• Help archive project documentation
• Support resource demobilization
• Contribute to contract closure
• Assist in post-project reviews

EVIDENCE TO COLLECT:
• Project closure reports
• Lessons learned documentation
• Archived project files
• Supervisor sign-offs
• Client acceptance certificates
• Post-project review reports

MINIMUM DURATION: 100 hours of workplace exposure"""
            }
        ]

        for wm_data in work_modules_data:
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                title=f"{wm_data['code']}: {wm_data['title']}",
                defaults={
                    'content': wm_data['description'],
                    'duration': wm_data['credits'] * 10,
                    'order': wm_data['order']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created WM: {wm_data['code']} - {wm_data['title']} ({wm_data['credits']} credits)"))
            else:
                self.stdout.write(f"  ○ WM already exists: {wm_data['code']} - {wm_data['title']}")

        # ============================================================
        # CREATE FORMATIVE ASSESSMENTS (QUIZZES FOR KEY MODULES)
        # ============================================================
        self.stdout.write("")
        self.stdout.write("-" * 60)
        self.stdout.write("FORMATIVE ASSESSMENTS (Quizzes)")
        self.stdout.write("-" * 60)

        # Quiz for KM-01 (Introductory Studies) - using __contains to match
        km01_lesson = Lesson.objects.filter(course=course, title__icontains='KM-01').first()
        if km01_lesson:
            quiz, created = Quiz.objects.get_or_create(
                lesson=km01_lesson,
                defaults={
                    'title': 'Formative Assessment: Introduction to Project Management',
                    'description': 'Test your understanding of project management careers, qualifications, and the project management framework.',
                    'passing_score': 70,
                    'time_limit': 45,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created quiz for KM-01"))
                
                quiz_questions = [
                    {
                        'order': 1,
                        'text': 'What is a project according to the PMBOK definition?',
                        'type': 'multiple_choice',
                        'points': 10,
                        'options': {
                            'A': 'Ongoing operations of an organization',
                            'B': 'A temporary endeavor undertaken to create a unique product, service, or result',
                            'C': 'A permanent functional activity',
                            'D': 'A routine business process'
                        },
                        'correct': 'B'
                    },
                    {
                        'order': 2,
                        'text': 'Which of the following is NOT a characteristic of a project?',
                        'type': 'multiple_choice',
                        'points': 10,
                        'options': {
                            'A': 'Temporary nature',
                            'B': 'Unique deliverables',
                            'C': 'Ongoing and repetitive',
                            'D': 'Defined start and end'
                        },
                        'correct': 'C'
                    },
                    {
                        'order': 3,
                        'text': 'What is the difference between project management and operations management?',
                        'type': 'multiple_choice',
                        'points': 10,
                        'options': {
                            'A': 'Project management is for temporary work, operations for ongoing work',
                            'B': 'There is no difference',
                            'C': 'Operations management is only for manufacturing',
                            'D': 'Project management is easier than operations'
                        },
                        'correct': 'A'
                    },
                    {
                        'order': 4,
                        'text': 'What does the acronym SMART stand for in project objectives?',
                        'type': 'multiple_choice',
                        'points': 10,
                        'options': {
                            'A': 'Simple, Measurable, Achievable, Relevant, Timely',
                            'B': 'Specific, Measurable, Achievable, Relevant, Time-bound',
                            'C': 'Specific, Meaningful, Accountable, Reliable, Tested',
                            'D': 'Simple, Manageable, Actionable, Responsible, Trackable'
                        },
                        'correct': 'B'
                    },
                    {
                        'order': 5,
                        'text': 'True or False: A project manager is responsible for balancing scope, time, cost, and quality constraints.',
                        'type': 'true_false',
                        'points': 10,
                        'options': {
                            'A': 'True',
                            'B': 'False'
                        },
                        'correct': 'A'
                    },
                    {
                        'order': 6,
                        'text': 'What are the five process groups in project management?',
                        'type': 'multiple_choice',
                        'points': 10,
                        'options': {
                            'A': 'Plan, Do, Check, Act, Close',
                            'B': 'Initiate, Plan, Execute, Monitor & Control, Close',
                            'C': 'Start, Organize, Execute, Review, Finish',
                            'D': 'Define, Design, Develop, Deploy, Close'
                        },
                        'correct': 'B'
                    },
                    {
                        'order': 7,
                        'text': 'Which of the following is a key benefit of stakeholder management?',
                        'type': 'multiple_choice',
                        'points': 10,
                        'options': {
                            'A': 'Increased project costs',
                            'B': 'Better risk identification and management',
                            'C': 'Longer project duration',
                            'D': 'Reduced communication'
                        },
                        'correct': 'B'
                    },
                    {
                        'order': 8,
                        'text': 'What is the triple constraint in project management?',
                        'type': 'multiple_choice',
                        'points': 10,
                        'options': {
                            'A': 'Quality, Risk, Communication',
                            'B': 'Scope, Time, Cost',
                            'C': 'People, Process, Technology',
                            'D': 'Plan, Execute, Close'
                        },
                        'correct': 'B'
                    }
                ]
                
                for q_data in quiz_questions:
                    QuizQuestion.objects.get_or_create(
                        quiz=quiz,
                        order=q_data['order'],
                        defaults={
                            'question_text': q_data['text'],
                            'question_type': q_data['type'],
                            'points': q_data['points'],
                            'option_a': q_data['options'].get('A', ''),
                            'option_b': q_data['options'].get('B', ''),
                            'option_c': q_data['options'].get('C', ''),
                            'option_d': q_data['options'].get('D', ''),
                            'correct_answer': q_data['correct']
                        }
                    )
                self.stdout.write(f"    Added {len(quiz_questions)} questions to KM-01 quiz")
            else:
                self.stdout.write(f"  ○ Quiz already exists for KM-01")
        else:
            self.stdout.write(self.style.WARNING("  ⚠ KM-01 lesson not found for quiz creation"))

        # ============================================================
        # CREATE PRACTICAL ASSIGNMENTS
        # ============================================================
        self.stdout.write("")
        self.stdout.write("-" * 60)
        self.stdout.write("PRACTICAL ASSIGNMENTS")
        self.stdout.write("-" * 60)

        assignments_data = [
            {
                'title': 'Assignment 1: Project Charter Development',
                'description': """Develop a comprehensive project charter for a real or simulated project of your choice. Include:

1. Project title and description
2. Business case and justification
3. High-level scope and objectives (SMART criteria)
4. Key stakeholders and their roles
5. High-level risks and assumptions
6. Preliminary budget and timeline
7. Success criteria and acceptance criteria
8. Project manager authority and sponsor approval

Submit a professional document (5-10 pages) following organizational standards.""",
                'due_days': 21,
                'points': 100
            },
            {
                'title': 'Assignment 2: Work Breakdown Structure (WBS) Creation',
                'description': """Create a detailed Work Breakdown Structure for a project of your choice. Requirements:

1. Decompose the project into at least 3 levels
2. Include a WBS dictionary with descriptions for each work package
3. Show the WBS in both chart and outline format
4. Identify control accounts and work packages
5. Demonstrate proper WBS numbering system
6. Include at least 20 work packages

Submit your WBS as both a diagram and a structured document.""",
                'due_days': 21,
                'points': 100
            },
            {
                'title': 'Assignment 3: Project Schedule Development',
                'description': """Using project management software (MS Project, Primavera, or similar), create a complete project schedule:

Requirements:
1. Activity list with minimum 30 activities
2. Activity sequencing with logical dependencies (FS, SS, FF, SF)
3. Duration estimates for each activity
4. Resource assignments and leveling
5. Critical path identification
6. Gantt chart with milestones
7. Schedule baseline

Export and submit your schedule file along with a PDF report.""",
                'due_days': 28,
                'points': 150
            },
            {
                'title': 'Assignment 4: Risk Management Plan',
                'description': """Develop a comprehensive Risk Management Plan for a project:

Requirements:
1. Risk management methodology
2. Risk identification using multiple techniques (brainstorming, checklists, SWOT)
3. Qualitative risk analysis (probability-impact matrix)
4. Quantitative risk analysis where appropriate
5. Risk response strategies for top 10 risks
6. Risk register with minimum 20 risks
7. Contingency and reserve analysis
8. Risk monitoring and control procedures

Submit a complete risk management plan (10-15 pages).""",
                'due_days': 28,
                'points': 150
            },
            {
                'title': 'Assignment 5: Earned Value Management (EVM) Analysis',
                'description': """Given a project scenario, perform an Earned Value Management analysis:

Tasks:
1. Calculate PV, EV, AC for each reporting period
2. Compute CV, SV, CPI, SPI
3. Perform EAC, ETC, and VAC calculations
4. Analyze performance trends
5. Provide forecast and recommendations
6. Create EVM graphs and S-curves
7. Write a performance report (5-10 pages)

Submit calculations, graphs, and written analysis.""",
                'due_days': 21,
                'points': 100
            },
            {
                'title': 'Assignment 6: Project Closure Report and Lessons Learned',
                'description': """Develop a comprehensive project closure report for a completed project:

Requirements:
1. Final project performance summary (scope, time, cost, quality)
2. Deliverable acceptance documentation
3. Lessons learned register (minimum 15 entries)
4. Recommendations for future projects
5. Knowledge transfer plan
6. Resource release documentation
7. Post-project review plan

Submit complete closure documentation (10-15 pages).""",
                'due_days': 21,
                'points': 100
            }
        ]

        for assign_data in assignments_data:
            assignment, created = Assignment.objects.get_or_create(
                course=course,
                title=assign_data['title'],
                defaults={
                    'description': assign_data['description'],
                    'due_date': timezone.now() + timezone.timedelta(days=assign_data['due_days']),
                    'total_points': assign_data['points']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Created assignment: {assign_data['title']}"))

        # ============================================================
        # FINAL SUMMARY
        # ============================================================
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("✓ QCTO OCCUPATIONAL CERTIFICATE: PROJECT MANAGER LOADED SUCCESSFULLY!"))
        self.stdout.write("=" * 80)
        self.stdout.write("")
        self.stdout.write("QUALIFICATION STATISTICS:")
        self.stdout.write(f"  • Course: {course.title}")
        self.stdout.write(f"  • SAQA ID: 101869")
        self.stdout.write(f"  • NQF Level: 05")
        self.stdout.write(f"  • Total Credits: 240")
        self.stdout.write("")
        self.stdout.write("MODULE BREAKDOWN:")
        self.stdout.write(f"  • Knowledge Modules (KM): 11 modules (80 credits)")
        self.stdout.write(f"  • Practical Skill Modules (PM): 13 modules (100 credits)")
        self.stdout.write(f"  • Work Experience Modules (WM): 4 modules (60 credits)")
        self.stdout.write(f"  • Total Lessons: {Lesson.objects.filter(course=course).count()}")
        self.stdout.write(f"  • Formative Quizzes: {Quiz.objects.filter(lesson__course=course).count()}")
        self.stdout.write(f"  • Practical Assignments: {Assignment.objects.filter(course=course).count()}")
        self.stdout.write("")
        self.stdout.write("EXIT LEVEL OUTCOMES:")
        self.stdout.write("  1. Initiate a project to address specific project objectives")
        self.stdout.write("  2. Plan and prepare the delivery of a project")
        self.stdout.write("  3. Execute and control the delivery of a project management plan")
        self.stdout.write("  4. Manage the project close out process")
        self.stdout.write("")
        self.stdout.write(f"🔗 Course URL: /course/{course.id}/")
        self.stdout.write(f"👨‍🏫 Instructor: {instructor.username}")
        self.stdout.write("")
        self.stdout.write("ASSESSMENT INFORMATION:")
        self.stdout.write("  • Internal Formative Assessment: Quizzes and assignments throughout")
        self.stdout.write("  • Work Experience Portfolio: Evidence from workplace modules")
        self.stdout.write("  • External Integrated Summative Assessment (EISA): Conducted by Services SETA")
        self.stdout.write("")
        self.stdout.write("REGISTRATION DATES:")
        self.stdout.write("  • Registration Start: 2018-07-01")
        self.stdout.write("  • Registration End: 2025-12-30")
        self.stdout.write("  • Last Enrolment: 2026-12-30")
        self.stdout.write("  • Last Achievement: 2029-12-30")
        self.stdout.write("")
        self.stdout.write("=" * 80)