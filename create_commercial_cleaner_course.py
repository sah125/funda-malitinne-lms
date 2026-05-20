#!/usr/bin/env python3
import os
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Course, Lesson, Quiz, QuizQuestion, Assignment

User = get_user_model()

def create_commercial_cleaner_course():
    print("Starting QCTO Commercial Cleaner course creation...")

    # Get or create instructor
    instructor, created = User.objects.get_or_create(
        username='cleaner_instructor',
        defaults={
            'email': 'instructor@serviceseta.org.za',
            'first_name': 'Nozipho',
            'last_name': 'Zondo',
            'role': 'instructor',
            'is_approved': True
        }
    )
    if created:
        instructor.set_password('Cleaner@123')
        instructor.save()
        print(f"✓ Created instructor: {instructor.username}")
    else:
        print(f"✓ Found instructor: {instructor.username}")

    # Create main qualification course
    course, created = Course.objects.get_or_create(
        title='Occupational Certificate: Commercial Cleaner (SAQA ID 118709)',
        defaults={
            'description': """This qualification is for learners pursuing a career as a Commercial Cleaner.
It covers the knowledge, practical skills, and workplace experience required to clean commercial premises including offices, retail complexes, warehouses, and ablution facilities.

Total credits: 120 (Knowledge: 39, Practical: 35, Workplace: 46)
NQF Level: 1
Curriculum Code: 811201000-00-00

The curriculum is structured into three components:
- Knowledge Modules (8 modules)
- Practical Skill Modules (7 modules)
- Workplace Experience Modules (7 modules)

Upon completion, learners can work in commercial cleaning, specialising in areas like kitchenette cleaning, ablution cleaning, floor cleaning, or above-surface cleaning.""",
            'instructor': instructor,
            'level': 'beginner',
            'price': 0,
            'status': 'published'
        }
    )
    if created:
        print(f"✓ Created course: {course.title}")
    else:
        print(f"⚠ Course already exists: {course.title}")

    # ========================
    # 1. KNOWLEDGE MODULES (KM-01 to KM-08)
    # ========================
    km_modules = [
        {'order': 1, 'code': 'KM-01', 'title': 'Introduction to the world of work', 'credits': 6, 'nqf': 1,
         'purpose': 'Build understanding of employment contracts, relationships, work ethics, performance, and basic communication at work.'},
        {'order': 2, 'code': 'KM-02', 'title': 'Basics of health, safety and the environment', 'credits': 5, 'nqf': 2,
         'purpose': 'Understand basic principles of health, safety, and the environment including PPE, hazard identification, and emergency procedures.'},
        {'order': 3, 'code': 'KM-03', 'title': 'Introduction to Commercial Cleaning', 'credits': 5, 'nqf': 1,
         'purpose': 'Understand commercial cleaning services, principles of cleaning, attributes of a cleaner, customer care, and lost property handling.'},
        {'order': 4, 'code': 'KM-04', 'title': 'Commercial cleaning equipment, chemicals and consumables', 'credits': 5, 'nqf': 1,
         'purpose': 'Learn types and functions of cleaning equipment, handling, storage, chemical categories, and PPE.'},
        {'order': 5, 'code': 'KM-05', 'title': 'Basics of Cleaning Commercial Kitchenette', 'credits': 5, 'nqf': 1,
         'purpose': 'Understand kitchenette components, equipment, cutlery, crockery, and their cleaning procedures.'},
        {'order': 6, 'code': 'KM-06', 'title': 'Cleaning Ablution Facilities', 'credits': 5, 'nqf': 1,
         'purpose': 'Understand components of ablution facilities (urinals, basins, dispensers) and cleaning procedures.'},
        {'order': 7, 'code': 'KM-07', 'title': 'Basics of Cleaning Commercial floor surface', 'credits': 4, 'nqf': 1,
         'purpose': 'Understand floor types (hard, textile, resilient) and cleaning methodologies for each.'},
        {'order': 8, 'code': 'KM-08', 'title': 'Introduction to above the floor surface', 'credits': 4, 'nqf': 1,
         'purpose': 'Learn to clean above-floor surfaces: furniture, partitions, fittings, and quality checking.'}
    ]

    for km in km_modules:
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            title=f"{km['code']}: {km['title']} (NQF{km['nqf']}, Cr{km['credits']})",
            defaults={
                'content': f"""**Module Purpose:** {km['purpose']}

**Learning Hours:** {km['credits'] * 10} notional hours (1 credit = 10 hours)

This knowledge module covers all topics required by the QCTO curriculum. 
Refer to the official learner guide and curriculum document for detailed content.

**Key Topics:** (as per curriculum specification)
- Topic elements and internal assessment criteria
- Formative assessments available in the quiz section

**Assessment:** Complete the quiz below to test your understanding.""",
                'duration': km['credits'] * 10,  # notional hours converted to minutes? Keep as hours? Use hours.
                'order': km['order']
            }
        )
        # override duration to be in minutes? LMS likely expects minutes. Use credits*10*60? Actually typical LMS uses minutes, but we'll set as hours for clarity. Adjust: use minutes = credits*10*60? Let's use minutes = credits*60 (1 credit=1 hour? Many LMS use minutes. For simplicity, use credits*60 minutes.
        if created:
            lesson.duration = km['credits'] * 60  # minutes
            lesson.save()
        print(f"  {'Created' if created else 'Already exists'}: {lesson.title}")

    # ========================
    # 2. PRACTICAL SKILL MODULES (PM-01 to PM-07)
    # ========================
    pm_modules = [
        {'order': 9, 'code': 'PM-01', 'title': 'Complete before shift duties', 'credits': 3,
         'practical_skills': 'Don PPE, check tools/equipment functionality, collect consumables and chemicals.'},
        {'order': 10, 'code': 'PM-02', 'title': 'Clean above floor surfaces', 'credits': 6,
         'practical_skills': 'Confirm surface/soilage, use cleaning methods (dusting, wiping, spot removal), clean upholstery.'},
        {'order': 11, 'code': 'PM-03', 'title': 'Clean the commercial kitchenette', 'credits': 6,
         'practical_skills': 'Clean floors, cupboards, appliances (fridge, microwave, stove), kitchenware, refill dispensers.'},
        {'order': 12, 'code': 'PM-04', 'title': 'Clean ablution facilities', 'credits': 5,
         'practical_skills': 'Clean surfaces (walls, floors, skirting), toilets/urinals, basins/baths/showers, replenish dispensers.'},
        {'order': 13, 'code': 'PM-05', 'title': 'Clean and maintain storeroom', 'credits': 4,
         'practical_skills': 'Store chemicals safely, clean storeroom, pack equipment and tools, maintain inventory.'},
        {'order': 14, 'code': 'PM-06', 'title': 'Clean floor surfaces', 'credits': 6,
         'practical_skills': 'Complete cleaning on all floor types (sweep, mop, vacuum, scrub), periodic cleaning (strip, seal, buff).'},
        {'order': 15, 'code': 'PM-07', 'title': 'Check and confirm completed tasks', 'credits': 5,
         'practical_skills': 'Clean/care for equipment, replenish consumables, remove PPE, report defects and maintenance.'}
    ]

    for pm in pm_modules:
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            title=f"{pm['code']}: {pm['title']} (Practical, Cr{pm['credits']})",
            defaults={
                'content': f"""**Practical Skill Module:** {pm['title']}

**Credits:** {pm['credits']} (notional hours: {pm['credits']*10})

**Practical Skills Covered:**
{pm['practical_skills']}

**Learning Environment:** Simulated or real workplace (commercial cleaning environment)

**Assessment:** Demonstration of skills via practical observation checklist (see workplace logbook).

**Related workplace module:** WM-{pm['code'][-2:]} – Procedures for {pm['title'].lower()}
""",
                'duration': pm['credits'] * 60,  # minutes
                'order': pm['order']
            }
        )
        print(f"  {'Created' if created else 'Already exists'}: {lesson.title}")

    # ========================
    # 3. WORKPLACE EXPERIENCE MODULES (WM-01 to WM-07)
    # ========================
    wm_modules = [
        {'order': 16, 'code': 'WM-01', 'title': 'Procedures for completing before shift duties', 'credits': 4,
         'work_activities': 'Don PPE, check tools/equipment, collect consumables/chemicals under supervision and independently (5 times).'},
        {'order': 17, 'code': 'WM-02', 'title': 'Procedures for cleaning above the floor surfaces', 'credits': 7,
         'work_activities': 'Confirm surface/soilage, apply cleaning methods, clean upholstery (3 times independently).'},
        {'order': 18, 'code': 'WM-03', 'title': 'Procedures for cleaning the commercial kitchenette', 'credits': 7,
         'work_activities': 'Clean floors, cupboards, appliances, kitchenware, refill dispensers (5 times).'},
        {'order': 19, 'code': 'WM-04', 'title': 'Procedures for cleaning ablution facilities', 'credits': 7,
         'work_activities': 'Clean surfaces, toilets/urinals, basins/baths/showers, replenish dispensers (5 times).'},
        {'order': 20, 'code': 'WM-05', 'title': 'Procedures for cleaning and maintaining storeroom', 'credits': 5,
         'work_activities': 'Store chemicals safely, clean storeroom, pack equipment and tools (5 times).'},
        {'order': 21, 'code': 'WM-06', 'title': 'Procedures for cleaning floor surfaces', 'credits': 10,
         'work_activities': 'Complete cleaning on all floor surfaces, floor buffing (5 times).'},
        {'order': 22, 'code': 'WM-07', 'title': 'Procedures for checking and confirming completed tasks', 'credits': 6,
         'work_activities': 'Clean/care for equipment, replenish consumables, remove PPE, report defects (5 times).'}
    ]

    for wm in wm_modules:
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            title=f"{wm['code']}: {wm['title']} (Workplace, Cr{wm['credits']})",
            defaults={
                'content': f"""**Workplace Experience Module:** {wm['title']}

**Credits:** {wm['credits']}

**Work Activities:**
{wm['work_activities']}

**Evidence:** Attendance register and work task observation checklist signed by supervisor.

**Contextualised Workplace Knowledge Required:**
- Company policies (health & safety, quality assurance, hand washing, PPE, cleaning procedures)
- Equipment maintenance and reporting procedures

**Duration:** Minimum {wm['credits']*10} notional hours spread over up to 5 weeks.

**Logbook:** Complete the Statement of Work Experience (Section 4 of curriculum) with supervisor signatures.
""",
                'duration': wm['credits'] * 60,
                'order': wm['order']
            }
        )
        print(f"  {'Created' if created else 'Already exists'}: {lesson.title}")

    # ========================
    # 4. QUIZZES for each Knowledge Module (formative assessment)
    # ========================
    # Sample quiz questions based on Internal Assessment Criteria from curriculum
    quiz_data = {
        'KM-01': [
            {'text': 'Which of the following is a legal right of an employee?', 'options': ['Working unlimited hours without rest', 'A safe working environment', 'No leave entitlement', 'Employer cannot terminate employment'], 'correct': 'B'},
            {'text': 'What is the purpose of a job card?', 'options': ['To record employee attendance', 'To outline the tasks, resources, and standards for a job', 'To apply for leave', 'To evaluate employee performance yearly'], 'correct': 'B'},
            {'text': 'Which of the following is an example of unethical behaviour at work?', 'options': ['Reporting a safety hazard', 'Using company time for personal tasks', 'Helping a colleague', 'Wearing correct PPE'], 'correct': 'B'},
        ],
        'KM-02': [
            {'text': 'What does PPE stand for?', 'options': ['Personal Protection Equipment', 'Personal Protective Equipment', 'Public Protective Equipment', 'Personnel Protective Equipment'], 'correct': 'B'},
            {'text': 'When should you consult a Material Safety Data Sheet (MSDS)?', 'options': ['Only when a chemical spills', 'Before using any chemical', 'After finishing work', 'Never'], 'correct': 'B'},
            {'text': 'Which of the following is a principle of good ergonomics?', 'options': ['Lifting with your back', 'Adjusting workstations to fit the worker', 'Standing in one place for hours', 'Ignoring discomfort'], 'correct': 'B'},
        ],
        'KM-03': [
            {'text': 'What does the cleaning principle "clean from top to bottom" mean?', 'options': ['Start with floors, end with ceilings', 'Start with high surfaces, then lower surfaces', 'Clean only the middle areas', 'Clean in any order'], 'correct': 'B'},
            {'text': 'Why is colour coding used in commercial cleaning?', 'options': ['Decoration', 'To prevent cross-contamination (e.g., kitchen vs. toilets)', 'To make cloths expensive', 'For marketing'], 'correct': 'B'},
            {'text': 'How should lost property be handled?', 'options': ['Keep it for yourself', 'Throw it away', 'Store following company procedures and report', 'Leave it on the floor'], 'correct': 'C'},
        ],
        'KM-04': [
            {'text': 'Which chemical category is used for removing grease and oil?', 'options': ['Acid', 'Alkaline', 'Neutral', 'Solvent'], 'correct': 'B'},
            {'text': 'How should cleaning equipment be stored after use?', 'options': ['Wet and dirty', 'Cleaned, dried, and stored according to procedures', 'Left in the work area', 'Stacked randomly'], 'correct': 'B'},
            {'text': 'What does the pH scale measure?', 'options': ['Temperature', 'Acidity or alkalinity', 'Volume', 'Pressure'], 'correct': 'B'},
        ],
        'KM-05': [
            {'text': 'What is the correct procedure for cleaning kitchenware?', 'options': ['Wash, then dry, then pack away', 'Dry, then wash, then pack', 'Pack first, then wash', 'Only rinse'], 'correct': 'A'},
            {'text': 'Which kitchenette component requires damp wiping and disinfection of touch points?', 'options': ['Fridge handle only', 'All surfaces including cupboards and appliance exteriors', 'Only the floor', 'Only the bin'], 'correct': 'B'},
        ],
        'KM-06': [
            {'text': 'Why should caution signs be placed when cleaning ablution facilities?', 'options': ['To decorate', 'To warn others of wet floors and hazards', 'To advertise', 'To mark territory'], 'correct': 'B'},
            {'text': 'What is the correct colour coding for cleaning toilet areas?', 'options': ['Red (often for high-risk areas like toilets)', 'Blue', 'Green', 'Yellow'], 'correct': 'A'},
        ],
        'KM-07': [
            {'text': 'Which type of floor surface requires vacuuming instead of sweeping?', 'options': ['Hard floor (tile)', 'Textile floor (carpet)', 'Resilient floor (vinyl)', 'Concrete'], 'correct': 'B'},
            {'text': 'What is the purpose of floor sealing?', 'options': ['To make the floor slippery', 'To protect the floor from damage and stains', 'To remove dirt', 'To increase dust'], 'correct': 'B'},
        ],
        'KM-08': [
            {'text': 'When cleaning above-floor surfaces, what order should you follow?', 'options': ['Furniture first, then partitions', 'Top to bottom, dusting high surfaces before lower ones', 'Windows first, then desks', 'Any order'], 'correct': 'B'},
            {'text': 'Why is it important to inspect surfaces after cleaning?', 'options': ['To waste time', 'To ensure quality and remove missed spots', 'To report to the manager only', 'It is optional'], 'correct': 'B'},
        ],
    }

    for km_code, questions in quiz_data.items():
        # Find the lesson for this KM
        km_lesson = Lesson.objects.filter(course=course, title__startswith=f"{km_code}:").first()
        if km_lesson:
            quiz, created = Quiz.objects.get_or_create(
                lesson=km_lesson,
                defaults={
                    'title': f'{km_code} Formative Assessment',
                    'description': f'Test your understanding of {km_lesson.title}. Answer the following questions based on the knowledge module.',
                    'passing_score': 70,
                }
            )
            if created:
                print(f"✓ Created quiz for {km_code}")
                # Add questions
                for idx, q in enumerate(questions, 1):
                    QuizQuestion.objects.get_or_create(
                        quiz=quiz,
                        order=idx,
                        defaults={
                            'question_text': q['text'],
                            'question_type': 'multiple_choice',
                            'points': 10,
                            'option_a': q['options'][0] if len(q['options']) > 0 else '',
                            'option_b': q['options'][1] if len(q['options']) > 1 else '',
                            'option_c': q['options'][2] if len(q['options']) > 2 else '',
                            'option_d': q['options'][3] if len(q['options']) > 3 else '',
                            'correct_answer': q['correct']
                        }
                    )
            else:
                print(f"⚠ Quiz already exists for {km_code}")

    # ========================
    # 5. PRACTICAL ASSIGNMENTS (summative assessment)
    # ========================
    assignments = [
        {
            'title': 'Practical Assignment: Simulated before-shift duties',
            'description': """In a simulated or real workplace setting, perform the following tasks under supervision:
1. Don the correct PPE for a cleaning assignment (e.g., gloves, apron, safety shoes, mask if required).
2. Inspect and test cleaning equipment (mop, bucket, vacuum, trolley) for functionality and safety.
3. Collect correct consumables (colour-coded cloths, mop heads) and chemicals (diluted according to MSDS) for a given area (e.g., office floor).
4. Complete an inspection checklist and report any damaged equipment.
Submit the completed checklist and a short video/photo evidence.""",
            'due_days': 14,
            'total_points': 100
        },
        {
            'title': 'Practical Assignment: Clean a commercial kitchenette',
            'description': """Clean a commercial kitchenette following the five-step process:
- Clean kitchen floors (damp mop)
- Clean cupboards and surfaces (damp wipe, touch point disinfection)
- Clean appliances (microwave, fridge exterior, kettle, stove top)
- Clean kitchenware (wash, dry, pack away)
- Refill soap and paper towel dispensers
Submit a cleaning log with before/after photos and a supervisor observation checklist.""",
            'due_days': 21,
            'total_points': 100
        },
        {
            'title': 'Practical Assignment: Clean ablution facilities',
            'description': """Clean a toilet/bathroom facility following proper procedures:
- Place caution sign
- Clean surfaces (walls, skirting, pipes, floor)
- Clean toilet and urinal (apply chemical, scrub, flush, wipe)
- Clean basins (scrub, rinse, wipe)
- Replenish dispensers (soap, toilet paper, hand towels)
- Record usage of chemicals and consumables
Submit evidence via supervisor-signed observation checklist and photographs of key steps.""",
            'due_days': 21,
            'total_points': 100
        },
        {
            'title': 'Workplace Logbook: Floor cleaning and buffing',
            'description': """Over a period of 5 weeks, complete at least 5 floor cleaning tasks (different surfaces: hard, carpet, resilient) that include:
- Sweeping, mopping, or vacuuming
- Spot removal
- Application of floor finish (where applicable)
- One floor buffing or burnishing task
Maintain a logbook with dates, signatures of supervisor, and notes on challenges. Submit a summary report and the signed logbook pages (scanned).""",
            'due_days': 35,
            'total_points': 100
        },
        {
            'title': 'End-of-task duties assignment',
            'description': """After completing any cleaning task, demonstrate end-of-task duties:
- Clean and store all equipment (mops, buckets, vacuum) correctly
- Wipe down chemical containers and store safely
- Remove and dispose/store PPE appropriately (doffing)
- Complete a defect report if any equipment is damaged
- Submit a completed "end of task" checklist and a brief reflection on why these steps are important for safety and compliance.""",
            'due_days': 14,
            'total_points': 50
        }
    ]

    for assign in assignments:
        Assignment.objects.get_or_create(
            course=course,
            title=assign['title'],
            defaults={
                'description': assign['description'],
                'due_date': datetime.now() + timedelta(days=assign['due_days']),
                'total_points': assign['total_points']
            }
        )
    print(f"✓ Added {len(assignments)} practical assignments")

    # ========================
    # 6. Summary
    # ========================
    print("\n" + "="*60)
    print("✅ QCTO Commercial Cleaner course structure loaded successfully!")
    print(f"📚 Course: {course.title}")
    print(f"🔗 Course URL: /course/{course.id}/")
    print(f"📊 Total lessons created: {Lesson.objects.filter(course=course).count()}")
    print(f"📝 Quizzes created: {Quiz.objects.filter(lesson__course=course).count()}")
    print(f"✍️ Assignments created: {Assignment.objects.filter(course=course).count()}")
    print("="*60)
    print("\nNote: This is a foundational structure. Instructors should enrich lessons with detailed content,")
    print("videos, downloadable resources (MSDS, checklists), and link to the official curriculum document.")
    print("Workplace modules require physical worksite approval and supervisor sign-off as per curriculum Section 4.")


if __name__ == '__main__':
    create_commercial_cleaner_course()