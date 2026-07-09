#!/usr/bin/env python3
"""
Advanced Emergency First Aid Responder Course Creation Script
Course Code: SP-230803
Curriculum Code: 900234-000-00-00
NQF Level: 4
Credits: 6

Run with: python manage.py shell < create_advanced_first_aid.py
Or: python3 create_advanced_first_aid.py (if using django-extensions)
"""

import os
import sys
import django
from datetime import datetime, timedelta

from django.utils import timezone
from django.utils.text import slugify

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    print("Make sure you're in the correct directory with manage.py")
    sys.exit(1)

from django.contrib.auth import get_user_model
from core.models import Course, LearningModule, Lesson, Quiz, QuizQuestion, Assignment, User

User = get_user_model()

def create_advanced_course():
    """Create the Advanced Emergency First Aid Responder course"""
    
    print("\n" + "="*70)
    print("ADVANCED EMERGENCY FIRST AID RESPONDER COURSE CREATION")
    print("="*70)
    
    # ============================================================
    # 1. CREATE COURSE
    # ============================================================
    print("\n[1] Creating Course...")
    
    instructor, _ = User.objects.get_or_create(
        username='advanced_first_aid_instructor',
        defaults={
            'email': 'instructor@example.com',
            'role': 'instructor',
            'is_active': True,
        }
    )

    course_data = {
        'title': 'Advanced Emergency First Aid Responder',
        'slug': slugify('Advanced Emergency First Aid Responder'),
        'description': """
This skills programme equips learners to operate as the first critical link in the emergency care continuum.
It provides advanced knowledge of anatomy, physiology, and risk-based first aid to manage complex emergencies,
coordinate responses, and provide critical care until professional medical help arrives.
""",
        'instructor': instructor,
        'level': 'advanced',
        'status': 'published',
        'price': 0.00,
    }
    
    course, created = Course.objects.get_or_create(
        slug=course_data['slug'],
        defaults=course_data
    )
    
    if created:
        print(f"  ✅ Created Course: {course.title}")
    else:
        print(f"  ℹ️ Course already exists: {course.title}")
    
    # ============================================================
    # 2. KNOWLEDGE MODULE - KM-01
    # ============================================================
    print("\n[2] Creating Knowledge Module (KM-01)...")
    
    km_data = {
        'course': course,
        'title': 'Concepts and Principles of Advanced Emergency First Aid',
        'description': 'This module covers the comprehensive theoretical knowledge required for an advanced first aid responder.',
        'module_type': 'knowledge',
        'order': 1,
        'is_visible': True,
    }
    
    km, created = LearningModule.objects.get_or_create(
        course=course,
        title=km_data['title'],
        defaults=km_data
    )
    
    if created:
        print(f"  ✅ Created Knowledge Module: {km.title}")
    else:
        print(f"  ℹ️ Knowledge Module already exists.")
    
    # ============================================================
    # 3. KNOWLEDGE TOPICS (KT01 - KT04)
    # ============================================================
    print("\n[3] Creating Knowledge Topics...")
    
    knowledge_topics = {
        'KT01': {
            'title': 'Principles for Providing Risk Based First Aid',
            'order': 1,
            'elements': [
                'The role of the advanced emergency first aider within the chain of survival, emergency health care system, and interaction with other emergency response services',
                'Legal and ethical principles for provision of risk based advanced first aid (Duty of care, negligence, consent, recording, criminal and civil liability)',
                'Maintaining personal health and safety as advanced emergency first aider (PPE, universal precautions, mental preparedness)',
                'Basic awareness of mental health of the advanced emergency first aider and the patient (Support for stress and post-traumatic stress, burnout, compassion fatigue)',
                'Basic awareness and sensitivity of cultural and gender diversity with specific reference to the provisioning of advanced emergency first aid care'
            ]
        },
        'KT02': {
            'title': 'Effective Applied Advanced Emergency First Aid',
            'order': 2,
            'elements': [
                'Hazard and risk assessment concepts and principles within the contexts of providing advanced emergency first aid',
                'Concepts and principles of the assessment of affected persons on an incident scene (Incident investigation, causation models)',
                'Key principles and concepts of communication with bystanders, emergency services, and the patient during an incident',
                'Fundamental concepts and principles that underpin the actions required for providing advanced emergency first aid care (Assess, Plan, Implement, Evaluate)',
                'Importance and principles of ongoing re-assessment and monitoring of the affected person\'s conditions (Primary and Secondary surveys)',
                'Importance and key principles of the handover between advanced emergency first aiders and emergency medical services including transportation options',
                'Importance of effective record keeping and incident reporting and the potential impact of incorrect record keeping',
                'The principles and practices that underpin post scene cleanup and post exposure prophylaxis'
            ]
        },
        'KT03': {
            'title': 'Human Anatomy and Physiology for Advanced Emergency First Aid',
            'order': 3,
            'elements': [
                'Principles of anatomical position and relationship to providing advanced emergency first aid care',
                'Meaning and implication of directional terms (Anterior/Posterior, Superior/Inferior, Medial/Lateral, Proximal/Distal, Contralateral/Ipsilateral, Superficial/Deep)',
                'Familiarity with surface anatomy - identifying and palpating bony landmarks, superficial muscles, and surface features',
                'Location and boundaries of the anatomical body cavities (Cranial, Spinal, Thoracic, Abdominal, Pelvic)',
                'Structure and functions of the integumentary system (Skin, hair, nails, glands)',
                'Structure and functions of the musculoskeletal system (Bones, muscles, joints)',
                'Structure and functions of the nervous system (Brain, spinal cord, nerves)',
                'Structure and functions of the endocrine system (Hormone-producing glands)',
                'Structure and functions of the cardiovascular system (Heart, blood vessels, blood)',
                'Structure and functions of the lymphatic system (Lymph nodes, lymphatic vessels, lymph)',
                'Structure and functions of the immune system (Organs, cells, molecules involved in defense against pathogens)',
                'Structure and functions of the respiratory system (Lungs, airways, breathing)',
                'Structure and functions of the gastrointestinal system (Organs involved in digestion and absorption of food)',
                'Structure and functions of the renal system (Kidneys, ureters, bladder, urethra)',
                'Structure and functions of the reproductive system (Organs involved in reproduction)'
            ]
        },
        'KT04': {
            'title': 'Concepts and Principles of Providing Advanced Emergency Level First Aid',
            'order': 4,
            'elements': [
                'Concepts and principles of the primary assessment and treating as per findings (ABCDE approach: Airway, Breathing, Circulation, Disability, Exposure)',
                'Concepts and principles of the secondary assessment - patient history, head-to-toe examination, vital signs (pulse, breathing, LOC, skin condition, pupils, blood pressure, glucose)',
                'Concepts and principles of controlling bleeding - managing catastrophic bleeding, identifying wounds, applying appropriate treatment',
                'Concepts and principles of treating and managing breathing difficulties - choking, establishing/maintaining airway, oxygen and bag valve mask techniques',
                'Concepts and principles of managing a patient who is not breathing - CPR for adults, children, and infants, using an AED',
                'Concepts and principles of managing an unconscious patient - identifying the cause and providing appropriate treatment',
                'Concepts and principles of identifying and managing shock - failure to pump, fluid loss, blood vessel dilation',
                'Concepts and principles of managing head and spinal injuries - maintaining and protecting the patient from further injury',
                'Concepts and principles of managing chest injuries - sucking chest wounds and flail chest',
                'Concepts and principles of managing abdominal injuries - bowel evisceration',
                'Concepts and principles of managing pelvic injuries - splinting an unstable pelvis',
                'Concepts and principles of managing extremity trauma - treating and immobilizing fractures',
                'Concepts and principles of managing burns - thermal, chemical, radiation, and electrical burns',
                'Concepts and principles of responding to cardiac arrest or heart attack',
                'Concepts and principles of responding to stroke',
                'Concepts and principles of responding to anaphylaxis',
                'Concepts and principles of responding to diabetic emergencies',
                'Concepts and principles of responding to seizures',
                'Concepts and principles of responding to asthma attacks',
                'Concepts and principles of thermal stress - hyperthermia and hypothermia',
                'Concepts and principles of responding to water emergencies - drowning incidents',
                'Concepts and principles of different types of poisoning (inhaled, injected, ingested, absorbed)',
                'Concepts and principles of managing bites and stings - animals and insects',
                'Concepts and principles of limiting the risks when encountering a communicable disease',
                'Concepts and principles of attending to emergency childbirth'
            ]
        }
    }
    
    for topic_code, topic_data in knowledge_topics.items():
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            module=km,
            title=topic_data['title'],
            defaults={
                'order': topic_data['order'],
                'content': f"""
<h2>{topic_data['title']}</h2>
<p>This topic covers the essential knowledge required for advanced emergency first aid response.</p>
<h3>Key Elements:</h3>
<ul>
    {''.join([f'<li>{e}</li>' for e in topic_data['elements']])}
</ul>
""",
                'duration': 30,
            }
        )
        if created:
            print(f"  ✅ Created Knowledge Topic: {lesson.title}")
        else:
            print(f"  ℹ️ Knowledge Topic already exists: {lesson.title}")
    
    # ============================================================
    # 4. PRACTICAL MODULE - PM-01
    # ============================================================
    print("\n[4] Creating Practical Module (PM-01)...")
    
    pm_data = {
        'course': course,
        'title': 'Applying Advanced Emergency First Aid Techniques',
        'description': 'This module focuses on the practical application of advanced first aid techniques in simulated and real-world emergency scenarios.',
        'module_type': 'practical',
        'order': 2,
        'is_visible': True,
    }
    
    pm, created = LearningModule.objects.get_or_create(
        course=course,
        title=pm_data['title'],
        defaults=pm_data
    )
    
    if created:
        print(f"  ✅ Created Practical Module: {pm.title}")
    else:
        print(f"  ℹ️ Practical Module already exists.")
    
    # ============================================================
    # 5. PRACTICAL SKILLS
    # ============================================================
    print("\n[5] Creating Practical Skills...")
    
    practical_skills = [
        {
            'title': 'Scene Assessment and Management (Primary Survey)',
            'order': 1,
            'description': 'Conducting a thorough primary survey using the ABCDE approach. Ensuring scene safety, identifying hazards, activating emergency response, and initiating triage when necessary.',
            'elements': [
                'Perform a danger assessment and ensure scene safety',
                'Check for response using the AVPU scale',
                'Activate emergency response system',
                'Assess and manage Airway with C-spine precautions',
                'Assess and manage Breathing and ventilation',
                'Assess and manage Circulation with hemorrhage control',
                'Assess Disability using GCS and pupillary response',
                'Expose and examine the patient while maintaining environmental control'
            ]
        },
        {
            'title': 'Catastrophic Bleeding Control',
            'order': 2,
            'description': 'Application of tourniquets (C-A-T), wound packing with haemostatic agents, and pressure dressings for life-threatening hemorrhage control.',
            'elements': [
                'Identify life-threatening external bleeding',
                'Apply direct pressure to wounds',
                'Use of pressure dressings and bandages',
                'Application of tourniquets to extremities',
                'Wound packing for junctional and deep wounds',
                'Application of haemostatic agents',
                'Monitor for signs of shock and re-evaluate interventions'
            ]
        },
        {
            'title': 'Advanced Airway Management',
            'order': 3,
            'description': 'Use of airway adjuncts (oropharyngeal/nasopharyngeal airways), suction devices, and oxygen administration techniques.',
            'elements': [
                'Opening and maintaining the airway using head-tilt chin-lift and jaw thrust',
                'Insertion of oropharyngeal airway (OPA)',
                'Insertion of nasopharyngeal airway (NPA)',
                'Use of suction devices to clear airways',
                'Oxygen delivery systems and administration',
                'Bag-valve-mask (BVM) ventilation techniques',
                'Recognition of airway compromise and need for advanced interventions'
            ]
        },
        {
            'title': 'Adult, Child and Infant CPR and AED Use',
            'order': 4,
            'description': 'Performing high-quality CPR and using an Automated External Defibrillator (AED) effectively for all age groups, including team resuscitation.',
            'elements': [
                'Adult CPR (30:2 compressions to breaths)',
                'Child CPR (30:2 compressions to breaths)',
                'Infant CPR (30:2 compressions to breaths)',
                'High-quality chest compressions (rate, depth, recoil)',
                'Rescue breaths technique for all age groups',
                'AED operation and pad placement for adults and children',
                'Team resuscitation dynamics and role switching',
                'Post-resuscitation care'
            ]
        },
        {
            'title': 'Spinal Immobilisation and Patient Movement',
            'order': 5,
            'description': 'Applying manual in-line stabilisation and using equipment like head blocks, straps, spine boards, and scoop stretchers to immobilise patients with suspected spinal injuries.',
            'elements': [
                'Manual in-line spinal stabilisation',
                'Application of cervical collar',
                'Log roll technique for spinal precautions',
                'Use of spine board or scoop stretcher',
                'Application of head blocks and straps',
                'Proper patient transfer techniques',
                'One-man and two-man carries'
            ]
        },
        {
            'title': 'Secondary Survey and Advanced Vital Signs',
            'order': 6,
            'description': 'Conducting a systematic head-to-toe examination, including the use of vital sign equipment: blood pressure cuff, stethoscope, pulse oximeter, thermometer, and pupillary torch.',
            'elements': [
                'Obtain AMPLE history (Allergies, Medications, Past history, Last meal, Events)',
                'Head-to-toe physical examination',
                'Vital signs assessment: pulse, respiratory rate, blood pressure',
                'Pulse oximetry and oxygen saturation monitoring',
                'Temperature assessment',
                'Pupillary examination',
                'Blood glucose testing',
                'Skin assessment for colour, temperature, and moisture'
            ]
        },
        {
            'title': 'Managing Medical Emergencies',
            'order': 7,
            'description': 'Practical management of scenarios such as stroke, seizure, anaphylaxis (using auto-injectors), asthma (using spacers), and diabetic emergencies (blood glucose testing).',
            'elements': [
                'Stroke assessment and management (FAST)',
                'Seizure management and post-seizure care',
                'Anaphylaxis recognition and epinephrine auto-injector use',
                'Asthma attack management with spacers and inhalers',
                'Diabetic emergency assessment and glucose administration',
                'Chest pain and cardiac event management',
                'Recognition and management of shock'
            ]
        },
        {
            'title': 'Multiple Casualty Incident (MCI) Management and Triage',
            'order': 8,
            'description': 'Applying triage principles (e.g., START system), coordinating resources, and directing other first aiders in a simulated incident.',
            'elements': [
                'Incident command and scene leadership',
                'Triage principles and the START system',
                'Triage categories: Immediate, Delayed, Minor, Deceased',
                'Resource allocation and coordination',
                'Communication with emergency services',
                'Patient transport decisions and prioritization',
                'Mass casualty incident management'
            ]
        }
    ]
    
    for skill in practical_skills:
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            module=pm,
            title=skill['title'],
            defaults={
                'order': skill['order'],
                'content': f"""
<h2>{skill['title']}</h2>
<p>{skill['description']}</p>
<h3>Key Skills to Demonstrate:</h3>
<ul>
    {''.join([f'<li>{e}</li>' for e in skill['elements']])}
</ul>
""",
                'duration': 30,
            }
        )
        if created:
            print(f"  ✅ Created Practical Skill: {lesson.title}")
        else:
            print(f"  ℹ️ Practical Skill already exists: {lesson.title}")
    
    # ============================================================
    # 6. QUIZZES FOR KNOWLEDGE MODULE
    # ============================================================
    print("\n[6] Creating Quizzes for Knowledge Module...")
    
    knowledge_lesson = Lesson.objects.filter(course=course, module=km).order_by('order').first()
    quiz_data = {
        'title': 'Advanced Emergency First Aid - Knowledge Assessment',
        'description': 'Comprehensive quiz covering the Concepts and Principles of Advanced Emergency First Aid module. Includes questions on anatomy, physiology, legal principles, and emergency procedures.',
        'passing_score': 70,
        'time_limit': 45,
        'lesson': knowledge_lesson,
    }
    
    quiz, created = Quiz.objects.get_or_create(
        title=quiz_data['title'],
        lesson=knowledge_lesson,
        defaults=quiz_data
    )
    
    if created:
        print(f"  ✅ Created Quiz: {quiz.title}")
    else:
        print(f"  ℹ️ Quiz already exists.")
    
    # ============================================================
    # 7. QUIZ QUESTIONS
    # ============================================================
    print("\n[7] Creating Quiz Questions...")
    
    quiz_questions = [
        {
            'question': 'What does the "A" stand for in the ABCDE primary survey approach?',
            'options': [
                'Assessment',
                'Airway with cervical spine precautions',
                'Analysis',
                'Action plan'
            ],
            'correct': 1,
            'explanation': 'A stands for Airway with cervical spine protection/precautions. This is the first and most critical step in the primary survey of a trauma patient.'
        },
        {
            'question': 'According to the chain of survival, what is the correct sequence of actions for cardiac arrest?',
            'options': [
                'Early CPR, Early defibrillation, Recognition, Advanced life support, Post-arrest care, Recovery',
                'Recognition and activation of EMS, Early CPR, Rapid defibrillation, Advanced life support, Post-cardiac arrest care, Recovery',
                'Early defibrillation, Early CPR, Advanced life support, Recognition, Recovery, Post-arrest care',
                'Recognition, Early defibrillation, Early CPR, Post-arrest care, Advanced life support, Recovery'
            ],
            'correct': 1,
            'explanation': 'The 6 links in the Chain of Survival are: 1) Recognition and activation of EMS, 2) Early CPR, 3) Rapid defibrillation, 4) Advanced life support, 5) Post-cardiac arrest care, 6) Recovery.'
        },
        {
            'question': 'What is the correct compression-to-breath ratio for adult CPR performed by a single rescuer?',
            'options': [
                '15:2',
                '30:2',
                '5:1',
                '20:2'
            ],
            'correct': 1,
            'explanation': 'For adult CPR performed by a single rescuer, the correct ratio is 30 chest compressions to 2 rescue breaths (30:2).'
        },
        {
            'question': 'Which of the following is a sign of a tension pneumothorax?',
            'options': [
                'Bilateral breath sounds',
                'Tracheal deviation to the opposite side',
                'Decreased heart rate',
                'Increased oxygen saturation'
            ],
            'correct': 1,
            'explanation': 'Tracheal deviation to the opposite side of the injury is a late sign of tension pneumothorax, along with decreased breath sounds, hypotension, and distended neck veins.'
        },
        {
            'question': 'What is the primary function of the integumentary system in the context of first aid?',
            'options': [
                'Temperature regulation only',
                'Protection against infection and injury, temperature regulation, and sensory perception',
                'Production of vitamin D only',
                'Blood circulation'
            ],
            'correct': 1,
            'explanation': 'The integumentary system (skin) provides protection against infection and injury, helps regulate body temperature, and provides sensory information about the environment.'
        },
        {
            'question': 'What is the correct depth for chest compressions in an adult during CPR?',
            'options': [
                '1 inch (2.5 cm)',
                'At least 2 inches (5 cm)',
                '3 inches (7.5 cm)',
                '4 inches (10 cm)'
            ],
            'correct': 1,
            'explanation': 'For adult CPR, chest compressions should be at least 2 inches (5 cm) deep, allowing for full chest recoil between compressions, at a rate of 100-120 compressions per minute.'
        },
        {
            'question': 'What does the acronym FAST stand for in stroke assessment?',
            'options': [
                'Face, Arms, Speech, Time',
                'Facial, Assessment, Stroke, Treatment',
                'Find, Assess, Stabilize, Transport',
                'Fever, Agitation, Seizure, Tremor'
            ],
            'correct': 0,
            'explanation': 'FAST stands for Face (drooping), Arms (weakness), Speech (slurred), and Time (to call emergency services). It is a quick screening tool for stroke.'
        },
        {
            'question': 'What is the correct management for a penetrating chest wound with an object still in place?',
            'options': [
                'Remove the object immediately and apply a dressing',
                'Apply pressure to remove the object',
                'Leave the object in place, stabilize it, and apply a dressing around it',
                'Cut the object flush with the skin'
            ],
            'correct': 2,
            'explanation': 'NEVER remove an impaled object from a chest wound. Leave it in place, stabilize it to prevent movement, and apply a dressing around it to control bleeding and prevent contamination.'
        },
        {
            'question': 'What is the function of the cardiovascular system?',
            'options': [
                'To transport oxygen and nutrients to body tissues and remove waste products',
                'To produce hormones',
                'To digest food',
                'To filter waste from the blood'
            ],
            'correct': 0,
            'explanation': 'The cardiovascular system transports oxygen, nutrients, and hormones to body tissues and removes carbon dioxide and other waste products through the blood circulation.'
        },
        {
            'question': 'What is the correct first aid for a person with a suspected spinal injury who is conscious and breathing?',
            'options': [
                'Move them to a comfortable position immediately',
                'Maintain manual in-line stabilization and immobilize the spine, call for emergency help',
                'Apply a cervical collar and let them sit up',
                'Perform CPR immediately'
            ],
            'correct': 1,
            'explanation': 'For suspected spinal injury, maintain manual in-line stabilization, immobilize the spine, and call for emergency help. Do not move the patient unless absolutely necessary.'
        },
        {
            'question': 'What is anaphylaxis and what is the first-line treatment?',
            'options': [
                'A mild allergic reaction treated with antihistamines',
                'A severe life-threatening allergic reaction treated with epinephrine (adrenaline) auto-injector',
                'A local skin reaction treated with topical steroids',
                'A food intolerance treated with dietary changes'
            ],
            'correct': 1,
            'explanation': 'Anaphylaxis is a severe, life-threatening allergic reaction. The first-line treatment is epinephrine (adrenaline) administered via auto-injector (EpiPen).'
        },
        {
            'question': 'What are the 3 Ps of first aid?',
            'options': [
                'Prepare, Practice, Perform',
                'Preserve life, Prevent further injury, Promote recovery',
                'Protect, Position, Provide',
                'Plan, Prepare, Proceed'
            ],
            'correct': 1,
            'explanation': 'The 3 Ps of first aid are: Preserve life, Prevent further injury, and Promote recovery. These are the fundamental aims of all first aid interventions.'
        },
        {
            'question': 'What is the correct treatment for a patient with burns covering more than 20% of total body surface area?',
            'options': [
                'Apply ice packs to all burned areas',
                'Initiate fluid resuscitation, cover burns with clean dry sheet, maintain body temperature, and transport to a burn centre',
                'Apply butter or oil to the burns',
                'Pop all blisters to prevent infection'
            ],
            'correct': 1,
            'explanation': 'For large burns (>20% TBSA), initiate fluid resuscitation, cover burns with clean dry dressings, prevent hypothermia, and transport to a burn centre. DO NOT apply ice directly or use butter/oil.'
        },
        {
            'question': 'What does the term "distal" mean in anatomical terminology?',
            'options': [
                'Closer to the midline of the body',
                'Further from the trunk or point of origin',
                'Closer to the trunk or point of origin',
                'Closer to the skin surface'
            ],
            'correct': 1,
            'explanation': 'Distal means further from the trunk or point of origin. For example, the fingers are distal to the wrist.'
        },
        {
            'question': 'What is the correct procedure for an unconscious patient with no signs of breathing?',
            'options': [
                'Place in recovery position and call for help',
                'Open airway, check for breathing for 10 seconds, and start CPR if no breathing or abnormal breathing is detected',
                'Give water and wait for them to wake up',
                'Slap their face to wake them up'
            ],
            'correct': 1,
            'explanation': 'For an unconscious patient: open the airway, check for breathing for 10 seconds, and start CPR immediately if there is no breathing or only gasping (agonal) breathing.'
        }
    ]
    
    for idx, q_data in enumerate(quiz_questions, 1):
        question, created = QuizQuestion.objects.get_or_create(
            quiz=quiz,
            question_text=q_data['question'],
            defaults={
                'question_type': 'multiple_choice',
                'order': idx,
                'option_a': q_data['options'][0],
                'option_b': q_data['options'][1],
                'option_c': q_data['options'][2],
                'option_d': q_data['options'][3] if len(q_data['options']) > 3 else '',
                'correct_answer': q_data['options'][q_data['correct']],
                'points': 1,
            }
        )
        if created:
            print(f"  ✅ Created Question {idx}: {q_data['question'][:50]}...")
    
    # ============================================================
    # 8. ASSIGNMENTS
    # ============================================================
    print("\n[8] Creating Assignments...")
    
    assignments = [
        {
            'title': 'Principles of Risk-Based First Aid',
            'description': """
Complete this assignment to demonstrate your understanding of the principles of risk-based first aid.

**Tasks:**

1. Explain the role of the advanced emergency first aider within the chain of survival and emergency healthcare system.
2. Describe the legal and ethical principles that guide the provision of advanced first aid (Duty of care, negligence, consent, and recording).
3. Discuss the importance of personal protective equipment (PPE) and universal precautions.
4. Explain the concept of mental health awareness for first aiders and patients.
5. Describe how cultural and gender diversity should be considered when providing advanced first aid care.

**Submission Format:** Written report (1500-2000 words) with references.
**Due Date:** 2 weeks from module start.
""",
            'module': km,
            'max_score': 100,
            'order': 1
        },
        {
            'title': 'Effective Applied Advanced Emergency First Aid',
            'description': """
Complete this assignment to demonstrate your understanding of effective applied advanced emergency first aid.

**Tasks:**

1. Describe the hazard and risk assessment process for an incident scene.
2. Explain the concepts and principles of assessing affected persons using primary and secondary surveys.
3. Discuss the key principles of communication with bystanders, emergency services, and patients.
4. Outline the fundamental concepts that underpin actions required for providing advanced first aid.
5. Explain the importance of ongoing re-assessment and monitoring.
6. Describe the key principles of handover between advanced emergency first aiders and EMS.
7. Discuss the importance of effective record keeping and incident reporting.
8. Explain the principles and practices of post-scene cleanup and post-exposure prophylaxis.

**Submission Format:** Written report (2000-2500 words) with practical scenario analysis.
**Due Date:** 3 weeks from module start.
""",
            'module': km,
            'max_score': 100,
            'order': 2
        },
        {
            'title': 'Human Anatomy and Physiology for First Aid',
            'description': """
Complete this assignment to demonstrate your understanding of human anatomy and physiology as it relates to advanced emergency first aid.

**Tasks:**

1. Explain the principles of anatomical position and directional terms.
2. Describe the surface anatomy relevant to first aid interventions.
3. Identify the location and boundaries of the major body cavities.
4. For each of the following systems, describe the structure and functions and explain how this knowledge applies to first aid:
   - Integumentary system
   - Musculoskeletal system
   - Nervous system
   - Cardiovascular system
   - Respiratory system
5. Explain the relevance of the endocrine, lymphatic, immune, gastrointestinal, renal, and reproductive systems to first aid care.

**Submission Format:** Written report (2500-3000 words) with diagrams and clinical applications.
**Due Date:** 4 weeks from module start.
""",
            'module': km,
            'max_score': 100,
            'order': 3
        },
        {
            'title': 'Advanced Emergency Level First Aid Interventions',
            'description': """
Complete this assignment to demonstrate your understanding of advanced emergency level first aid interventions.

**Tasks:**

1. Describe the ABCDE approach to primary assessment and life-saving treatment.
2. Explain the secondary assessment process including history taking and head-to-toe examination.
3. Describe the management of:
   - Catastrophic bleeding and wounds
   - Breathing difficulties and airway management
   - Cardiac arrest (CPR and AED use)
   - Unconscious patients
   - Shock
   - Head, spinal, chest, abdominal, and pelvic injuries
   - Extremity trauma and fractures
   - Burns (thermal, chemical, radiation, electrical)
4. Explain the management of medical emergencies including:
   - Cardiac arrest/heart attack
   - Stroke
   - Anaphylaxis
   - Diabetic emergencies
   - Seizures
   - Asthma attacks
5. Describe the management of:
   - Thermal stress (hyperthermia/hypothermia)
   - Drowning incidents
   - Poisoning (all routes)
   - Bites and stings
   - Communicable disease exposure
   - Emergency childbirth

**Submission Format:** Comprehensive case study analysis and intervention plan (3000-3500 words).
**Due Date:** 5 weeks from module start.
""",
            'module': km,
            'max_score': 100,
            'order': 4
        }
    ]
    
    for idx, assignment_data in enumerate(assignments, 1):
        assignment, created = Assignment.objects.get_or_create(
            title=assignment_data['title'],
            course=course,
            defaults={
                'description': assignment_data['description'],
                'due_date': timezone.now() + timedelta(weeks=2 + idx),
                'total_points': assignment_data['max_score'],
            }
        )
        if created:
            print(f"  ✅ Created Assignment {idx}: {assignment.title}")
        else:
            print(f"  ℹ️ Assignment already exists: {assignment.title}")
    
    # ============================================================
    # 9. SUMMARY
    # ============================================================
    print("\n" + "="*70)
    print("COURSE CREATION SUMMARY")
    print("="*70)
    print(f"\n✅ Course: {course.title}")
    print(f"   Slug: {course.slug}")
    print(f"   Level: {course.level}")
    print(f"   Status: {course.status}")
    print(f"\n📚 Knowledge Module: {km.title}")
    print(f"   Topics: {knowledge_topics.keys()}")
    print(f"\n🛠️ Practical Module: {pm.title}")
    print(f"   Skills: {len(practical_skills)} practical skills created")
    print(f"\n📝 Quiz: {quiz.title}")
    print(f"   Questions: {len(quiz_questions)} created")
    print(f"\n📄 Assignments: {len(assignments)} created")
    print("\n" + "="*70)
    print("✅ Advanced Emergency First Aid Responder course creation complete!")
    print("="*70)
    
    return course, km, pm, quiz

# ============================================================
# EXECUTION
# ============================================================
if __name__ == "__main__":
    try:
        create_advanced_course()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)