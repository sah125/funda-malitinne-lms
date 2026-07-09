# create_basic_emergency_first_aid_course.py
"""
Django script to create the Basic Emergency First Aid Responder Skills Programme
Based on QCTO Curriculum Code: 900232-000-00-00
NQF Level: 2 | Credits: 2
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from core.models import (
    Course, Lesson, LearningModule, LessonModule, 
    Quiz, QuizQuestion, Assignment, User
)

User = get_user_model()

# ============================================================
# COURSE DETAILS
# ============================================================

COURSE_DATA = {
    'title': 'Basic Emergency First Aid Responder',
    'slug': 'basic-emergency-first-aid-responder',
    'description': '''
The Basic Emergency First Aid Responder skills programme equips learners with the 
foundational knowledge and practical skills to respond effectively to emergency 
situations. This programme covers fundamental first aid principles, scene safety, 
patient assessment, CPR, bleeding control, and management of common injuries 
and medical emergencies.

**QCTO Curriculum Code:** 900232-000-00-00
**NQF Level:** 2
**Credits:** 2

**Skills Programme ID:** SP-230801

**Entry Requirements:** Open Access

**Learning Outcomes:**
- Apply fundamental principles of basic emergency first aid
- Assess and manage emergency scenes safely
- Perform primary and secondary patient assessments
- Provide CPR and manage breathing difficulties
- Control bleeding and manage wounds
- Recognize and manage common medical emergencies
- Communicate effectively with emergency services
- Complete post-incident procedures
    ''',
    'level': 'beginner',
    'status': 'published',
    'price': 0.00,
}

# ============================================================
# KNOWLEDGE MODULE DATA
# ============================================================

KNOWLEDGE_MODULE = {
    'code': '900232-000-00-KM-01',
    'title': 'Fundamental Concepts and Principles of Basic Emergency First Aid',
    'description': '''
This knowledge module equips learners with a general understanding of the key 
concepts and principles that underpin the tasks performed by a basic emergency 
first aider.

**Module Code:** 900232-000-00-KM-01
**NQF Level:** 2
**Credits:** 1
**Notional Hours:** 10

**Topics Covered:**
1. Fundamental Principles and Objectives of Basic Emergency First Aid (10%)
2. Applied Basic Emergency First Aid (20%)
3. Basic Fundamentals of Human Anatomy and Physiology (30%)
4. Principles of Recognising Injuries and Illnesses (40%)
    ''',
    'module_type': 'knowledge',
    'order': 1,
    'is_visible': True,
}

KNOWLEDGE_TOPICS = [
    {
        'topic_code': 'KM-01-KT01',
        'title': 'Fundamental Principles and Objectives of Basic Emergency First Aid',
        'percentage': 10,
        'elements': [
            {'code': 'KT0101', 'title': 'The purpose of basic emergency first aid', 'percentage': 10},
            {'code': 'KT0102', 'title': 'The ABCs of emergency first aid - Airway, Breathing, and Circulation', 'percentage': 20},
            {'code': 'KT0103', 'title': 'The role of a basic First Aid Provider and the scope of practice', 'percentage': 30},
            {'code': 'KT0104', 'title': 'Fundamental legal and ethical principles in first aid', 'percentage': 30},
            {'code': 'KT0105', 'title': 'Maintaining personal health and safety as a First Aider', 'percentage': 10},
        ]
    },
    {
        'topic_code': 'KM-01-KT02',
        'title': 'Applied Basic Emergency First Aid',
        'percentage': 20,
        'elements': [
            {'code': 'KT0201', 'title': 'Scene safety and incident management', 'percentage': 20},
            {'code': 'KT0202', 'title': 'Principles of patient assessment', 'percentage': 20},
            {'code': 'KT0203', 'title': 'Communication in first aid situations', 'percentage': 10},
            {'code': 'KT0204', 'title': 'Appropriate action within scope of practice', 'percentage': 20},
            {'code': 'KT0205', 'title': 'Reassessment and monitoring of patient condition', 'percentage': 10},
            {'code': 'KT0206', 'title': 'Handover to emergency services', 'percentage': 10},
            {'code': 'KT0207', 'title': 'Record keeping and incident reporting', 'percentage': 5},
            {'code': 'KT0208', 'title': 'Post scene cleanup', 'percentage': 5},
        ]
    },
    {
        'topic_code': 'KM-01-KT03',
        'title': 'Human Anatomy and Physiology',
        'percentage': 30,
        'elements': [
            {'code': 'KT0301', 'title': 'Respiratory system and CPR', 'percentage': 30},
            {'code': 'KT0302', 'title': 'Cardiovascular system', 'percentage': 30},
            {'code': 'KT0303', 'title': 'Nervous system and head/spinal injuries', 'percentage': 20},
            {'code': 'KT0304', 'title': 'Musculoskeletal system', 'percentage': 15},
            {'code': 'KT0305', 'title': 'Integumentary system (skin, hair, nails)', 'percentage': 5},
        ]
    },
    {
        'topic_code': 'KM-01-KT04',
        'title': 'Recognise and Treat Emergencies, Injuries, and Illnesses',
        'percentage': 40,
        'elements': [
            {'code': 'KT0401', 'title': 'Primary assessment and life-saving treatments', 'percentage': 15},
            {'code': 'KT0402', 'title': 'Secondary assessment and vital signs', 'percentage': 10},
            {'code': 'KT0403', 'title': 'Controlling bleeding', 'percentage': 10},
            {'code': 'KT0404', 'title': 'Managing breathing difficulties and CPR', 'percentage': 15},
            {'code': 'KT0405', 'title': 'Managing unconscious patients', 'percentage': 10},
            {'code': 'KT0406', 'title': 'Identifying and treating shock', 'percentage': 10},
            {'code': 'KT0407', 'title': 'Sprains, strains, fractures, dislocations', 'percentage': 8},
            {'code': 'KT0408', 'title': 'Managing burns', 'percentage': 8},
            {'code': 'KT0409', 'title': 'Heart attack and stroke', 'percentage': 7},
            {'code': 'KT0410', 'title': 'Environmental emergencies (hypo/hyperthermia)', 'percentage': 7},
            {'code': 'KT0411', 'title': 'Poisoning, venomous bites, and stings', 'percentage': 10},
        ]
    }
]

# ============================================================
# PRACTICAL MODULE DATA
# ============================================================

PRACTICAL_MODULE = {
    'code': '900232-000-00-PM-01',
    'title': 'Provide Basic Emergency First Aid',
    'description': '''
This practical module provides learners with hands-on skills coaching in 
assessing and managing basic medical, trauma, and environmental emergencies.

**Module Code:** 900232-000-00-PM-01
**NQF Level:** 2
**Credits:** 1
**Notional Hours:** 10

**Practical Skills:**
1. Assess and manage an emergency scene
2. Manage breathing difficulties and perform CPR
3. Control bleeding and manage wounds
4. Manage unconsciousness and recovery position
5. Manage traumatic injuries
6. Communicate with patients and stakeholders
7. Handover to emergency services
8. Post-incident cleanup
    ''',
    'module_type': 'practical',
    'order': 2,
    'is_visible': True,
}

PRACTICAL_SKILLS = [
    {
        'code': 'PM-01-PS01',
        'title': 'Assess and manage an emergency',
        'elements': [
            {'code': 'PA0101', 'title': 'Assess emergency scene and make safe for entry'},
            {'code': 'PA0102', 'title': 'Assess and manage patients with breathing difficulties (CPR, AED, choking)'},
            {'code': 'PA0103', 'title': 'Assess and manage bleeding, wounds, and burns'},
            {'code': 'PA0104', 'title': 'Assess and manage unconsciousness and recovery position'},
            {'code': 'PA0105', 'title': 'Assess and manage traumatic injuries (fractures, shock)'},
            {'code': 'PA0106', 'title': 'Communicate with patient and stakeholders'},
            {'code': 'PA0107', 'title': 'Handover to emergency medical services'},
            {'code': 'PA0108', 'title': 'Perform post-incident cleanup'},
        ]
    }
]

# ============================================================
# QUIZ QUESTIONS
# ============================================================

QUIZ_QUESTIONS = [
    # KT0101 - Purpose of First Aid
    {
        'question': 'What is the PRIMARY purpose of basic emergency first aid?',
        'question_type': 'multiple_choice',
        'options': ['A. To provide a full medical diagnosis', 'B. To preserve life, prevent worsening, and promote recovery', 'C. To replace professional medical care', 'D. To provide long-term treatment'],
        'correct_answer': 'B',
        'points': 1,
        'order': 1,
        'explanation': 'The three main purposes of first aid are: Preserve Life, Prevent Worsening, and Promote Recovery.',
        'topic': 'KM-01-KT01'
    },
    # KT0102 - ABCs
    {
        'question': 'What do the ABCs of emergency first aid stand for?',
        'question_type': 'multiple_choice',
        'options': ['A. Airway, Breathing, Circulation', 'B. Airway, Blood, Consciousness', 'C. Assessment, Breathing, Care', 'D. Airway, Breathing, Chest compressions'],
        'correct_answer': 'A',
        'points': 1,
        'order': 2,
        'explanation': 'ABC stands for Airway, Breathing, Circulation - the priority order for assessment.',
        'topic': 'KM-01-KT01'
    },
    # KT0103 - Role of First Aider
    {
        'question': 'Which of the following is within the scope of practice for a basic first aid provider?',
        'question_type': 'multiple_choice',
        'options': ['A. Performing surgery', 'B. Administering prescription medications', 'C. Providing CPR and controlling bleeding', 'D. Diagnosing medical conditions'],
        'correct_answer': 'C',
        'points': 1,
        'order': 3,
        'explanation': 'Basic first aid includes CPR, bleeding control, wound care, and immobilization.',
        'topic': 'KM-01-KT01'
    },
    # KT0104 - Legal and Ethical
    {
        'question': 'What is the principle of "informed consent" in first aid?',
        'question_type': 'multiple_choice',
        'options': ['A. You should always treat without asking', 'B. You must explain treatment and get permission from a conscious patient', 'C. Consent is never needed in emergencies', 'D. Only doctors need consent'],
        'correct_answer': 'B',
        'points': 1,
        'order': 4,
        'explanation': 'Informed consent requires explaining what you will do and getting permission.',
        'topic': 'KM-01-KT01'
    },
    # KT0201 - Scene Safety
    {
        'question': 'What is the primary reason for ensuring scene safety?',
        'question_type': 'multiple_choice',
        'options': ['A. To look professional', 'B. To protect yourself and the patient from further harm', 'C. To have time to think', 'D. To wait for help to arrive'],
        'correct_answer': 'B',
        'points': 1,
        'order': 5,
        'explanation': 'Scene safety prevents additional injuries to responders, victims, and bystanders.',
        'topic': 'KM-01-KT02'
    },
    # KT0202 - Patient Assessment
    {
        'question': 'What is the correct order of a primary assessment?',
        'question_type': 'multiple_choice',
        'options': ['A. Circulation, Airway, Breathing', 'B. Breathing, Circulation, Airway', 'C. Airway, Breathing, Circulation', 'D. Airway, Circulation, Breathing'],
        'correct_answer': 'C',
        'points': 1,
        'order': 6,
        'explanation': 'The correct order is Airway, Breathing, Circulation (ABC).',
        'topic': 'KM-01-KT02'
    },
    # KT0301 - Respiratory System
    {
        'question': 'What is the function of the alveoli in the lungs?',
        'question_type': 'multiple_choice',
        'options': ['A. To filter air', 'B. To warm incoming air', 'C. To exchange oxygen and carbon dioxide', 'D. To produce mucus'],
        'correct_answer': 'C',
        'points': 1,
        'order': 7,
        'explanation': 'Alveoli are tiny air sacs where gas exchange occurs.',
        'topic': 'KM-01-KT03'
    },
    # KT0302 - Cardiovascular System
    {
        'question': 'What is the main function of the cardiovascular system?',
        'question_type': 'multiple_choice',
        'options': ['A. To digest food', 'B. To circulate blood and deliver oxygen to tissues', 'C. To filter waste from the body', 'D. To control movement'],
        'correct_answer': 'B',
        'points': 1,
        'order': 8,
        'explanation': 'The cardiovascular system circulates blood, delivering oxygen and nutrients.',
        'topic': 'KM-01-KT03'
    },
    # KT0401 - Primary Assessment
    {
        'question': 'What is the FIRST step in the primary assessment of an unconscious patient?',
        'question_type': 'multiple_choice',
        'options': ['A. Check for breathing', 'B. Check responsiveness', 'C. Open the airway', 'D. Check for bleeding'],
        'correct_answer': 'B',
        'points': 1,
        'order': 9,
        'explanation': 'The first step is checking for responsiveness.',
        'topic': 'KM-01-KT04'
    },
    # KT0404 - CPR
    {
        'question': 'What is the compression-to-breath ratio for adult CPR?',
        'question_type': 'multiple_choice',
        'options': ['A. 15:2', 'B. 30:2', 'C. 30:1', 'D. 15:1'],
        'correct_answer': 'B',
        'points': 1,
        'order': 10,
        'explanation': 'The ratio for adult CPR is 30 chest compressions to 2 rescue breaths.',
        'topic': 'KM-01-KT04'
    },
]

# ============================================================
# MAIN EXECUTION SCRIPT
# ============================================================

def create_course():
    """Create the complete Basic Emergency First Aid Responder course"""
    
    print("=" * 70)
    print("🏥 CREATING BASIC EMERGENCY FIRST AID RESPONDER SKILLS PROGRAMME")
    print("=" * 70)
    print()
    
    # Get or create instructor
    instructor = User.objects.filter(role='instructor').first()
    if not instructor:
        instructor = User.objects.filter(is_superuser=True).first()
    
    if not instructor:
        print("❌ No instructor found. Please create an instructor user first.")
        return
    
    print(f"📋 Instructor: {instructor.username} ({instructor.email})")
    print()
    
    # ============================================================
    # 1. CREATE THE COURSE
    # ============================================================
    
    print("📚 Creating Course...")
    course, created = Course.objects.get_or_create(
        title=COURSE_DATA['title'],
        defaults={
            'slug': COURSE_DATA['slug'],
            'description': COURSE_DATA['description'],
            'instructor': instructor,
            'level': COURSE_DATA['level'],
            'status': COURSE_DATA['status'],
            'price': COURSE_DATA['price'],
        }
    )
    
    if created:
        print(f"   ✅ Created: {course.title}")
    else:
        print(f"   ⏭️ Already exists: {course.title}")
    
    print()
    
    # ============================================================
    # 2. CREATE KNOWLEDGE MODULE
    # ============================================================
    
    print("📖 Creating Knowledge Module...")
    
    km, created = LearningModule.objects.get_or_create(
        course=course,
        title=KNOWLEDGE_MODULE['title'],
        defaults={
            'description': KNOWLEDGE_MODULE['description'],
            'module_type': KNOWLEDGE_MODULE['module_type'],
            'order': KNOWLEDGE_MODULE['order'],
            'is_visible': KNOWLEDGE_MODULE['is_visible'],
        }
    )
    
    if created:
        print(f"   ✅ Created Knowledge Module: {km.title}")
    else:
        print(f"   ⏭️ Knowledge Module already exists: {km.title}")
    
    km_lesson, created = Lesson.objects.get_or_create(
        course=course,
        title=f"Knowledge: {KNOWLEDGE_MODULE['title'][:50]}...",
        defaults={
            'content': KNOWLEDGE_MODULE['description'],
            'order': 1,
            'duration': 10,
        }
    )
    print(f"   ✅ Knowledge Lesson created: {km_lesson.title}")
    
    print()
    
    # ============================================================
    # 3. CREATE KNOWLEDGE TOPICS AS LESSONS
    # ============================================================
    
    print("📝 Creating Knowledge Topics...")
    
    topic_order = 2
    for topic in KNOWLEDGE_TOPICS:
        topic_title = f"{topic['topic_code']}: {topic['title']}"
        
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            title=topic_title[:200],
            defaults={
                'content': f"""
{topic['title']}

This topic covers {topic['percentage']}% of the Knowledge Module content.

Topics covered:
{chr(10).join([f"  • {elem['code']}: {elem['title']} ({elem['percentage']}%)" for elem in topic['elements']])}

Learning Objectives:
After completing this topic, you will be able to:
{chr(10).join([f"  • Explain {elem['title'].lower()}" for elem in topic['elements']])}
                """,
                'order': topic_order,
                'duration': max(2, int(10 * topic['percentage'] / 100)),
            }
        )
        print(f"   ✅ Topic: {topic['topic_code']} - {topic['title'][:40]}...")
        topic_order += 1
    
    print()
    
    # ============================================================
    # 4. CREATE PRACTICAL MODULE
    # ============================================================
    
    print("🩹 Creating Practical Module...")
    
    pm, created = LearningModule.objects.get_or_create(
        course=course,
        title=PRACTICAL_MODULE['title'],
        defaults={
            'description': PRACTICAL_MODULE['description'],
            'module_type': PRACTICAL_MODULE['module_type'],
            'order': PRACTICAL_MODULE['order'],
            'is_visible': PRACTICAL_MODULE['is_visible'],
        }
    )
    
    if created:
        print(f"   ✅ Created Practical Module: {pm.title}")
    else:
        print(f"   ⏭️ Practical Module already exists: {pm.title}")
    
    pm_lesson, created = Lesson.objects.get_or_create(
        course=course,
        title=f"Practical: {PRACTICAL_MODULE['title'][:50]}...",
        defaults={
            'content': PRACTICAL_MODULE['description'],
            'order': topic_order,
            'duration': 10,
        }
    )
    print(f"   ✅ Practical Lesson created: {pm_lesson.title}")
    topic_order += 1
    
    print()
    
    # ============================================================
    # 5. CREATE PRACTICAL SKILLS
    # ============================================================
    
    print("🔧 Creating Practical Skills...")
    
    for skill in PRACTICAL_SKILLS:
        for element in skill['elements']:
            skill_title = f"{element['code']}: {element['title']}"
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                title=skill_title[:200],
                defaults={
                    'content': f"""
{element['title']}

This is a practical skill that requires hands-on demonstration.

Skills to Practice:
- Demonstrate {element['title'].lower()}
- Follow correct procedures and safety protocols
- Apply theory knowledge in practical scenarios

Assessment Criteria:
- Correct technique and procedure
- Safety awareness
- Effective communication
- Completion within time limits

Simulation Guidelines:
- Use appropriate equipment and manikins
- Practice in realistic scenarios
- Receive feedback and improve
                    """,
                    'order': topic_order,
                    'duration': 2,
                }
            )
            print(f"   ✅ Practical Skill: {element['code']} - {element['title'][:40]}...")
            topic_order += 1
    
    print()
    
    # ============================================================
    # 6. CREATE QUIZZES FOR KNOWLEDGE TOPICS (FIXED)
    # ============================================================
    
    print("📝 Creating Quizzes...")
    
    for topic in KNOWLEDGE_TOPICS:
        topic_code = topic['topic_code']
        topic_title = topic['title']
        
        # Find the lesson for this topic
        lesson = Lesson.objects.filter(
            course=course,
            title__icontains=topic_code
        ).first()
        
        if lesson:
            # Check if quiz already exists
            existing_quiz = Quiz.objects.filter(lesson=lesson).first()
            
            if existing_quiz:
                print(f"   ⏭️ Quiz already exists: {topic_title[:40]}...")
                quiz = existing_quiz
            else:
                # Create quiz
                quiz = Quiz.objects.create(
                    lesson=lesson,
                    title=f"Quiz: {topic_title[:40]}...",
                    description=f"Knowledge check for {topic_title}",
                    passing_score=70,
                    time_limit=10,
                )
                print(f"   ✅ Created Quiz: {topic_title[:40]}...")
            
            # Add questions for this topic (only if quiz was newly created)
            if not existing_quiz:
                topic_questions = [q for q in QUIZ_QUESTIONS if q.get('topic') == topic_code]
                for q_data in topic_questions[:5]:
                    QuizQuestion.objects.create(
                        quiz=quiz,
                        question_text=q_data['question'],
                        question_type=q_data['question_type'],
                        points=q_data['points'],
                        order=q_data['order'],
                        option_a=q_data['options'][0] if len(q_data['options']) > 0 else '',
                        option_b=q_data['options'][1] if len(q_data['options']) > 1 else '',
                        option_c=q_data['options'][2] if len(q_data['options']) > 2 else '',
                        option_d=q_data['options'][3] if len(q_data['options']) > 3 else '',
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data.get('explanation', ''),
                    )
                print(f"      ✅ Added {len(topic_questions[:5])} questions")
    
    print()
    
    # ============================================================
    # 7. CREATE ASSIGNMENTS
    # ============================================================
    
    print("📋 Creating Assignments...")
    
    assignments = [
        {
            'title': 'Module 1: Knowledge Assessment - First Aid Principles',
            'description': """
Complete the following knowledge assessment:

1. Explain the ABCs of emergency first aid and why they are fundamental.

2. Describe the role of a basic First Aid Provider and the scope of practice.

3. Identify and discuss three legal and ethical principles that must be adhered to when providing first aid.

4. Explain the importance of personal health and safety as a First Aider.

5. Describe the process for assessing an emergency incident scene.

Reference: KM-01-KT01, KM-01-KT02
""",
            'total_points': 100,
            'due_date': '2026-08-15',
            'order': 1,
        },
        {
            'title': 'Module 2: Human Anatomy and Physiology Assignment',
            'description': """
Complete the following anatomy and physiology assignment:

1. Explain how the respiratory system works and how injuries to this system can threaten life.

2. Describe the structure and function of the cardiovascular system.

3. Explain the importance of the nervous system in head and spinal cord injuries.

4. Describe the musculoskeletal system and common injuries.

5. Explain the integumentary system and its role in wound care.

Reference: KM-01-KT03
""",
            'total_points': 100,
            'due_date': '2026-08-22',
            'order': 2,
        },
        {
            'title': 'Module 3: Emergency Management Assignment',
            'description': """
Complete the following emergency management assignment:

1. Describe the principles and processes of primary assessment.

2. Explain the concepts of secondary assessment and treating as per findings.

3. Describe the methods for controlling bleeding.

4. Explain the principles for managing a patient who is not breathing.

5. Describe the concepts for managing an unconscious patient.

6. Explain the methods for identifying and treating shock.

Reference: KM-01-KT04
""",
            'total_points': 100,
            'due_date': '2026-08-29',
            'order': 3,
        },
        {
            'title': 'Module 4: Practical Skills Assignment',
            'description': """
Complete the following practical skills assignment:

1. Demonstrate scene assessment and safety procedures.

2. Demonstrate CPR for adult, child, and infant.

3. Demonstrate bleeding control and wound management.

4. Demonstrate management of unconsciousness and recovery position.

5. Demonstrate management of fractures and shock.

6. Demonstrate effective handover to emergency services.

Reference: PM-01-PS01
""",
            'total_points': 100,
            'due_date': '2026-09-05',
            'order': 4,
        },
    ]
    
    for assignment_data in assignments:
        assignment, created = Assignment.objects.get_or_create(
            course=course,
            title=assignment_data['title'],
            defaults={
                'description': assignment_data['description'],
                'total_points': assignment_data['total_points'],
                'due_date': assignment_data['due_date'],
                'order': assignment_data['order'],
            }
        )
        
        if created:
            print(f"   ✅ Created Assignment: {assignment_data['title'][:40]}...")
        else:
            print(f"   ⏭️ Assignment already exists: {assignment_data['title'][:40]}...")
    
    print()
    
    # ============================================================
    # 8. SUMMARY
    # ============================================================
    
    print("=" * 70)
    print("✅ SKILLS PROGRAMME CREATION COMPLETE!")
    print("=" * 70)
    print()
    print(f"📚 COURSE: {course.title}")
    print(f"   • ID: {course.id}")
    print(f"   • Instructor: {course.instructor.username}")
    print(f"   • Level: {course.level}")
    print(f"   • Status: {course.status}")
    print()
    print(f"📖 MODULES:")
    print(f"   • Knowledge Module: 1")
    print(f"   • Practical Module: 1")
    print()
    print(f"📝 LESSONS: {Lesson.objects.filter(course=course).count()}")
    print(f"   • Knowledge Topics: {len(KNOWLEDGE_TOPICS)}")
    print(f"   • Practical Skills: {len(PRACTICAL_SKILLS[0]['elements'])}")
    print()
    print(f"📋 QUIZZES: {Quiz.objects.filter(lesson__course=course).count()}")
    print(f"📋 ASSIGNMENTS: {Assignment.objects.filter(course=course).count()}")
    print()
    print("=" * 70)
    print("🎯 QCTO COMPLIANCE:")
    print(f"   • Curriculum Code: 900232-000-00-00")
    print(f"   • Skills Programme ID: SP-230801")
    print(f"   • NQF Level: 2")
    print(f"   • Credits: 2")
    print("=" * 70)


# ============================================================
# RUN THE SCRIPT
# ============================================================

if __name__ == '__main__':
    create_course()