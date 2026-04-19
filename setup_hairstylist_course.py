import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from core.models import User, Course, Lesson, Quiz, QuizQuestion, Assignment, Progress

# Get instructor
instructor = User.objects.filter(username='Phumlani').first()
if not instructor:
    instructor = User.objects.filter(role='instructor').first()

if not instructor:
    print("❌ No instructor found! Creating default instructor...")
    instructor = User.objects.create_user(
        username='hairstylist_instructor',
        email='hairstylist@malitinne.co.za',
        password='Mal@@@123',
        role='instructor',
        first_name='Hairstylist',
        last_name='Trainer'
    )
    print(f"✅ Created instructor: {instructor.username}")

print(f"✅ Using instructor: {instructor.username}")

# ==================== CREATE COURSE ====================
course, created = Course.objects.get_or_create(
    title="Hairstylist Skills Programme - SP-230305 (NQF Level 3)",
    defaults={
        'description': """This Skills Programme is designed for aspiring hairstylists who want to develop professional hairdressing skills.

QUALIFICATION INFORMATION:
• SAQA QUAL ID: 230305
• NQF Level: 3
• Credits: 56
• Curriculum Code: SP-230305 Hairstylist

What you will learn:
• Professional conduct and ethics in hairdressing
• Principles of working with hair and skin
• Hairstyling techniques (dreadlocks, braiding, extensions, thermal styling, up-styles)
• Salon safety and hygiene
• Client consultation and communication

This programme combines knowledge, practical skills, and workplace application for real-world success.""",
        'instructor': instructor,
        'level': 'intermediate',
        'status': 'published',
        'price': 0
    }
)

if created:
    print(f"✅ Created course: {course.title}")
else:
    print(f"📚 Course already exists: {course.title}")

# ==================== KNOWLEDGE MODULE 1: PROFESSIONAL CONDUCT AND ETHICS ====================
# KM-01: Professional conduct and ethics (NQF Level 2, Credits 9)

km01_lessons = [
    {
        'order': 1,
        'title': 'KM-01-KT01: Introduction to the Hairdressing Industry',
        'content': """# Introduction to the Hairdressing Industry

## What is Hairdressing?

Hairdressing is the profession of cutting, styling, coloring, and treating hair. It is a creative and technical field that requires both artistic vision and scientific knowledge.

## Career Opportunities for Qualified Hairdressers:

### 1. Salon Owner
- Run your own salon business
- Manage staff and operations
- Create your brand identity

### 2. Technical Advisor
- Work with product companies
- Train other stylists
- Develop new techniques

### 3. Product Consultant
- Advise salons on product usage
- Demonstrate new products
- Build client relationships

### 4. Competition Judge
- Judge hairdressing competitions
- Set industry standards
- Recognize talent

### 5. Film and Theatre Stylist
- Work on movie sets
- Create period hairstyles
- Collaborate with costume departments

### 6. Educator/Facilitator
- Train new hairdressers
- Develop curriculum
- Assess student work

## Industry Trends:

### Post-COVID-19 Industry Recovery
- 16.9% growth expected in 2022
- Increased demand for salon services
- New safety protocols

### Technology in Hairdressing
- Online booking systems
- Digital consultation tools
- Social media marketing

### Natural & Organic Products
- Growing demand for eco-friendly products
- Chemical-free alternatives
- Sustainable packaging

### Expanded Service Offerings
- Keratin treatments
- Makeup services
- Bridal packages

## Employment Outlook
- Projected growth: 20% faster than average
- 349,210 jobs in the industry
- Many self-employed opportunities""",
        'duration': 60
    },
    {
        'order': 2,
        'title': 'KM-01-KT02: Hazards, Risks, Safety, Health and Environmental Protection',
        'content': """# Safety, Health and Environmental Protection in the Salon

## Common Safety and Health Risks in a Salon:

### 1. Poor Cleanliness
- Cross-contamination risks
- Germ spread between clients
- Prevention: Regular disinfection of all surfaces

### 2. Hazardous Chemicals
- Hair dyes, bleaches, chemical peels
- Risks: Dermatitis, asthma, eye irritation
- Prevention: Use gloves, proper ventilation

### 3. Trips and Falls
- Wet floors from shampooing
- Spilled products
- Prevention: Clean spills immediately, secure electrical leads

### 4. Unqualified Staff
- Risk of injuries and poor service
- Prevention: Verify qualifications and experience

### 5. Fire Hazards
- Overloaded electrical sockets
- Chemical storage
- Prevention: Regular safety checks, proper storage

## Types of Safety Signs:

### Emergency Signs
- Exit signs (green, photoluminescent)
- Fire equipment location

### Warning Signs
- Yellow triangles with black pictograms
- "Slippery surface", "High voltage"

### Mandatory Safety Signs
- "Safety goggles must be worn"
- "Gloves required"

## Safe Handling of Hazardous Substances:

### Storage Requirements:
- Cool, well-ventilated areas
- Away from heat and sunlight
- Separate incompatible chemicals

### Personal Protective Equipment (PPE):
- Gloves for chemical handling
- Safety goggles
- Aprons

## Cleaning, Sanitation and Disinfection:

### Sanitation:
- Removing visible debris
- Washing with soap and water

### Disinfection:
- Killing microorganisms on surfaces
- Using approved disinfectants

### Sterilization:
- Complete elimination of all microorganisms
- For tools that may cause bleeding

## Waste Management:

### Types of Salon Waste:
- Chemical waste (hair dyes, cleaning products)
- Metal waste (scissors, aerosol cans)
- Plastic recycling (bottles)
- Clinical waste (wax strips, cotton wool)
- Sanitary waste

### Proper Disposal:
- Separate hazardous waste
- Use approved disposal services
- Follow environmental regulations""",
        'duration': 75
    },
    {
        'order': 3,
        'title': 'KM-01-KT03: Basic Principles of Firefighting',
        'content': """# Basic Principles of Firefighting

## Causes of Fire in the Workplace:

### 1. Faulty Electrical Equipment
- Loose wires
- Overloaded plugs
- Damaged connections

### 2. Flammable and Combustible Materials
- Hairsprays, alcohol-based products
- Improper storage of chemicals

### 3. Lack of Staff Training
- Not knowing fire procedures
- Improper use of equipment

### 4. Lack of Resources
- No fire extinguishers
- Non-functional smoke detectors

## The Fire Triangle:

Fire requires three elements:
1. **Heat** - ignition source
2. **Fuel** - combustible material
3. **Oxygen** - from the air

Remove any one element to extinguish the fire.

## Classes of Fire and Firefighting Equipment:

### Class A (Ordinary combustibles)
- Wood, paper, textiles, plastic
- **Equipment**: Water extinguisher, hose, sand bucket

### Class B (Flammable liquids)
- Petrol, diesel, oils, solvents, propane
- **Equipment**: Fire blanket, foam extinguisher, CO2 extinguisher, Dry Chemical Powder

### Class C (Electrical fires)
- Electrical equipment, wiring
- **Equipment**: CO2 extinguisher, Dry Chemical Powder (DCP)

### Class D (Metal fires)
- Specialized extinguishers

### Class F (Cooking oils and fats)
- Deep fat fryers
- **Equipment**: Wet chemical extinguisher

## Fire Extinguisher Types:

### Water Fire Extinguisher (9L)
- For Class A fires only
- NOT for electrical or liquid fires

### CO2 Fire Extinguisher (2kg, 5kg)
- For Class B and electrical fires
- Leaves no residue

### Dry Chemical Powder (DCP) (1kg, 1.5kg, 2.5kg, 4.5kg, 9kg)
- Multipurpose for A, B, C fires
- Most common type

### Foam Fire Extinguisher (9L)
- For Class A and B fires
- Smothers flames

### Wet Chemical Extinguisher (6L)
- For Class F fires (cooking oils)
- For restaurant kitchens

## Fire Blanket:
- Smothers small fires
- For pan fires, clothing fires

## Emergency Procedures:

### R.A.C.E. Protocol:
- **R**escue anyone in danger
- **A**larm - activate the fire alarm
- **C**ontain the fire (close doors)
- **E**vacuate / Extinguish

### P.A.S.S. for Fire Extinguishers:
- **P**ull the pin
- **A**im at the base of the fire
- **S**queeze the handle
- **S**weep side to side

## First Aid for Burns:
1. Cool the burn with cool running water for 20 minutes
2. Remove jewelry and clothing from the area
3. Cover with a clean, non-stick dressing
4. Seek medical attention for severe burns""",
        'duration': 60
    },
    {
        'order': 4,
        'title': 'KM-01-KT04: Basic Concepts of First Aid and Emergencies',
        'content': """# Basic Concepts of First Aid and Emergencies

## Legal Requirements for a First Aid Box:

Under the Occupational Health and Safety Act, first aid boxes are required when more than 5 people are employed.

### Minimum Contents:
- Wound cleaner / antiseptic (100ml)
- Swabs for cleaning wounds
- Cotton wool for padding (100g)
- Sterile gauze (minimum 10)
- Forceps (for splinters)
- Scissors (minimum 100mm)
- Safety pins
- 4 triangular bandages
- 4 roller bandages (75mm x 5m)
- 4 roller bandages (100mm x 5m)
- Elastic adhesive (25mm x 3m)
- Non-allergenic adhesive strip
- Adhesive dressing strips (minimum 10)
- 4 First aid dressings (75mm x 100mm)
- 4 First aid dressings (150mm x 200mm)
- 2 Straight splints
- 2 Large and 2 medium disposable latex gloves
- 2 CPR mouth pieces

## DRSABCD Action Plan:

### D - Danger
Check for danger to yourself, bystanders, and the casualty

### R - Response
Is the person conscious?
- Squeeze shoulders
- Ask "Are you okay?"

### S - Send for help
Call emergency services (10177 or 112)

### A - Airway
Open the mouth and check for obstructions

### B - Breathing
Look, listen, and feel for breathing (10 seconds)

### C - CPR (Cardiopulmonary Resuscitation)
If not breathing normally:
- 30 chest compressions (rate 100-120 per minute)
- 2 rescue breaths
- Continue until help arrives or person responds

### D - Defibrillator
Apply AED if available

## Basic First Aid for Common Injuries:

### Cuts and Abrasions:
1. Clean the wound
2. Apply pressure to stop bleeding
3. Cover with sterile dressing

### Burns and Scalds:
1. Cool under running water for 20 minutes
2. Remove jewelry from the area
3. Cover with non-stick dressing
4. DO NOT apply creams or ice

### Electrical Shock:
1. Turn off power source
2. If unsafe, use non-conductive object to separate
3. Check for responsiveness
4. Call emergency services

### Chemical Ingestion:
1. Do NOT induce vomiting
2. Identify the chemical
3. Call poison control
4. Give water if advised

### Choking (Heimlich Maneuver):
1. Stand behind the person
2. Make a fist above the navel
3. Grasp fist with other hand
4. Give quick upward thrusts
5. Repeat until object is expelled

## Infection Control:
- Use gloves when dealing with blood/body fluids
- Use CPR mask for rescue breaths
- Wash hands before and after treatment""",
        'duration': 60
    },
    {
        'order': 5,
        'title': 'KM-01-KT05: Business Etiquette',
        'content': """# Business Etiquette

## What is Etiquette?

Etiquette is the intricate network of rules that govern good behavior and our social interactions. It reflects society's customs, history, ethical codes, and group rules.

## Benefits of Proper Etiquette:

### 1. First Impressions Count
- First 5-7 seconds are crucial
- Positive impression leads to trust

### 2. Confidence Boost
- Knowing correct etiquette reduces anxiety
- More comfortable in social situations

### 3. Stronger Friendships
- Treating people with kindness builds relationships
- Respect creates loyalty

### 4. Career Opportunities
- Good manners give you an advantage
- Professionals with etiquette stand out

## Positive Attitude at Work:

### Characteristics:
- Cheerful and optimistic
- Resilient
- Encouraging to others

### How to Demonstrate:
- Avoid negativity and gossip
- Practice gratitude
- Set and achieve goals
- Make friends with colleagues
- Give yourself breaks
- Focus on positives
- Prioritize wellbeing
- Show kindness
- Stay organized
- Smile!

## Professional Image - The 3 Key Elements:

### 1. Appearance
- What you wear and how you look
- First thing people judge
- Online image matters too

### 2. Professional Behavior
- Respectful communication
- Courteous conduct
- Proper workplace etiquette

### 3. Professional Conduct
- Ethics and morals
- Integrity and reputation
- Standards of behavior

## Dress Code:

### Formal Business Attire
- Suits, dress shirts/blouses
- Professional shoes
- No casual clothing

### Business Casual
- Less formal than business attire
- No shorts, torn jeans, tank tops
- Clean and neat

### Salon Dress Code:
- Clean uniforms
- Professional appearance
- Proper hygiene
- Neat hairstyle

## Email Etiquette Rules:

1. Use clear, professional subject lines
2. Proofread every email
3. Write before entering recipient address
4. Double-check recipient
5. CC all relevant recipients
6. Don't always "reply all"
7. Reply to your emails
8. Include a signature block
9. Use appropriate formality
10. Keep emails brief and to the point

## Telephone Etiquette:

1. Always speak clearly
2. Do not yell
3. Don't use slang
4. Never eat or drink
5. Always listen actively
6. Use proper titles (Mr., Mrs., Dr.)
7. Have patience with difficult callers
8. Focus on the task
9. Ask permission before placing on hold

## Closing an Interaction:

### Types of Customer Interactions:
1. **Requests** - Be helpful and efficient
2. **Questions** - Provide accurate information
3. **Complaints** - Listen actively, apologize, solve
4. **Compliments** - Thank sincerely

### Tips for Successful Closures:
- Use customer's name
- Empathize with their needs
- Anticipate other needs
- Keep protocols consistent
- Personalize every interaction""",
        'duration': 75
    },
    {
        'order': 6,
        'title': 'KM-01-KT06: Customer Service and Communication',
        'content': """# Customer Service and Communication

## Effective Listening Skills:

### Benefits of Effective Listening:
- Better problem solving
- Improved accuracy
- Stronger relationships
- Ensured understanding
- Less wasted time
- Fewer errors

### Barriers to Effective Listening:

#### Physical and Environmental
- Noise, distance, obstructions
- Temperature, lighting

#### Cultural Barriers
- Different backgrounds
- Different communication styles

#### Emotional and Psychological
- Mood and energy level
- Prejudgments and assumptions

#### Language Barriers
- Different native languages
- Accents and expressions

## Verbal Communication:

### Functions of Verbal Communication:
1. **Define reality** - Label and describe experiences
2. **Organize ideas** - Create meaningful categories
3. **Enable thinking** - Reflect on past, present, future
4. **Shape attitudes** - Language influences worldview

## Non-Verbal Communication:

### Types of Non-Verbal Communication:

1. **Facial Expressions**
   - Smile, frown, surprise
   - Universal across cultures

2. **Gestures**
   - Waving, pointing, thumbs up
   - Can vary by culture

3. **Paralinguistics**
   - Tone of voice
   - Loudness, inflection, pitch

4. **Body Language and Posture**
   - Open vs closed positions
   - Leaning forward shows interest

5. **Proxemics (Personal Space)**
   - Casual conversation: 18 inches - 4 feet
   - Public speaking: 10-12 feet

6. **Eye Gaze**
   - Eye contact shows honesty
   - Blinking rate indicates interest

7. **Haptics (Touch)**
   - Conveys affection, familiarity, sympathy
   - Communicates status and power

8. **Appearance**
   - Clothing, hairstyle
   - First impressions matter

## Internal vs External Customers:

### Internal Customers
- Employees within your organization
- Coworkers, other departments
- Happy employees = happy external customers

### External Customers
- Pay for products/services
- The end user
- Revenue source

## Dealing with Difficult Customers:

### The Contentious Customer
- Ready to argue
- Solution: Understand what's bothering them

### The Challenging Customer
- Doesn't trust your suggestions
- Solution: Show you value their insights

### The Impatient Customer
- Wants immediate solution
- Solution: Communicate often and clearly

### The Vague Customer
- Doesn't know what they need
- Solution: Ask clarifying questions

### The Demanding Customer
- Hard to please
- Solution: Identify concerns early, set boundaries

## The Psychology of Selling:

### Cialdini's 6 Principles of Persuasion:

1. **Reciprocity** - People feel obliged to give back
2. **Scarcity** - Desire for limited availability
3. **Authority** - Follow credible experts
4. **Consistency** - Drive to be consistent
5. **Liking** - Say "yes" to people we like
6. **Consensus** - Follow others' actions

## Ethical Selling:
- Understand your leads better
- Build connections
- Strengthen through positive influence
- Focus on solving problems, not manipulating""",
        'duration': 90
    },
    {
        'order': 7,
        'title': 'KM-01-KT07: Principles of Numeracy',
        'content': """# Principles of Numeracy

## Reading a Payslip:

### Key Terms:
- **Basic Pay** - Agreed set pay without bonuses
- **Gross Pay** - Amount earned before deductions
- **Net Pay** - Amount paid into bank account (take-home)
- **Cost to Company** - Total package including benefits
- **PAYE** - Pay As You Earn (income tax)
- **UIF** - Unemployment Insurance Fund (1% employee + 1% employer)
- **IRP5** - Tax certificate at end of tax year

## Basic Calculations:

### 1. Net Income Formula
Example: R25,000 revenue - R30,000 expenses = -R5,000 (net loss)

### 2. Accounting Equation

### 3. Cost of Goods Sold (COGS)
Example: R2,500 ÷ (R2.95 - R1.40) = 1,613 cups of coffee

### 5. Return on Investment (ROI)

### 6. Profit Margin

### 7. Current Ratio
Should be greater than 1

### 8. Markup Formula
OR

## Financial Ratios:

### Leverage Ratios:
- **Debt-to-Equity** = Total liabilities ÷ Shareholders' equity
- **Debt-to-Asset** = Total liabilities ÷ Total assets

### Liquidity Ratios:
- **Working Capital Ratio** = Current assets ÷ Current liabilities
- **Cash Ratio** = Liquid assets ÷ Current liabilities

### Profitability Ratios:
- **Net Profit Margin** = After tax net profit ÷ Net sales
- **Return on Equity** = Net income ÷ Shareholders' equity

### Operations Ratios:
- **Accounts Receivable Turnover** = Net sales ÷ Average accounts receivable
- **Inventory Turnover** = Cost of goods sold ÷ Average inventory

## Percentages:

To calculate percentage change:

Example: Sales increased from 25 to 35 units
Difference = 10, Original = 25
(10 ÷ 25) × 100 = 40% increase

## VAT (Value Added Tax):

### Current VAT Rate in South Africa: 15%

### Adding VAT:

### Removing VAT:

### Example:
Product costs R100
VAT = R100 × 0.15 = R15
Total including VAT = R115

## VAT Registration:
- Register if taxable turnover > R1 million per year
- Can voluntarily register if turnover < R1 million

### VAT Responsibilities:
- Include VAT at correct rate
- Keep VAT records
- Submit VAT returns (usually every 2 months)
- Pay VAT owed to SARS""",
        'duration': 60
    }
]

# Create lessons for KM-01
for lesson_data in km01_lessons:
    lesson, created = Lesson.objects.get_or_create(
        course=course,
        title=lesson_data['title'],
        defaults={
            'content': lesson_data['content'],
            'order': lesson_data['order'],
            'duration': lesson_data['duration']
        }
    )
    if created:
        print(f"  ✅ Added lesson {lesson_data['order']}: {lesson_data['title']}")

# ==================== QUIZZES FOR KM-01 ====================

km01_quizzes = [
    {
        'lesson_title': 'KM-01-KT01: Introduction to the Hairdressing Industry',
        'questions': [
            ('What percentage growth is expected for the hair salon industry in 2022?', 'multiple_choice', 10, 'B', 'A) 10%|B) 16.9%|C) 25%|D) 50%'),
            ('Which of the following is a career opportunity for qualified hairdressers?', 'multiple_choice', 10, 'A', 'A) Salon Owner|B) Accountant|C) Lawyer|D) Engineer'),
            ('True or False: Social media marketing is NOT important for hair salons.', 'true_false', 5, 'False', ''),
            ('How many jobs are in the hairdressing industry in the US?', 'multiple_choice', 10, 'C', 'A) 100,000|B) 200,000|C) 349,210|D) 500,000'),
            ('What is the projected growth rate for hairdressing employment?', 'multiple_choice', 10, 'A', 'A) 20% faster than average|B) 5% slower|C) No growth|D) 50% decline'),
        ]
    },
    {
        'lesson_title': 'KM-01-KT02: Hazards, Risks, Safety, Health and Environmental Protection',
        'questions': [
            ('What is the first step in preventing cross-contamination in a salon?', 'multiple_choice', 10, 'A', 'A) Regular disinfection|B) Wearing gloves only|C) Using air freshener|D) Opening windows'),
            ('Which type of safety sign uses yellow triangles with black pictograms?', 'multiple_choice', 10, 'B', 'A) Emergency signs|B) Warning signs|C) Mandatory signs|D) Information signs'),
            ('What does PPE stand for?', 'short_answer', 10, 'Personal Protective Equipment', ''),
            ('True or False: Chemical waste can be disposed of in regular trash bins.', 'true_false', 5, 'False', ''),
            ('Which of the following is NOT a hazardous chemical found in salons?', 'multiple_choice', 10, 'D', 'A) Hair dyes|B) Bleaches|C) Chemical peels|D) Water'),
        ]
    },
    {
        'lesson_title': 'KM-01-KT03: Basic Principles of Firefighting',
        'questions': [
            ('What are the three elements of the fire triangle?', 'short_answer', 15, 'Heat, fuel, oxygen', ''),
            ('Which fire extinguisher is best for electrical fires?', 'multiple_choice', 10, 'A', 'A) CO2 extinguisher|B) Water extinguisher|C) Foam extinguisher|D) Wet chemical'),
            ('What does P.A.S.S. stand for in fire extinguisher use?', 'short_answer', 15, 'Pull, Aim, Squeeze, Sweep', ''),
            ('Class A fires involve which materials?', 'multiple_choice', 10, 'A', 'A) Wood, paper, textiles|B) Flammable liquids|C) Electrical equipment|D) Cooking oils'),
            ('True or False: Water extinguishers can be used on electrical fires.', 'true_false', 5, 'False', ''),
        ]
    },
    {
        'lesson_title': 'KM-01-KT04: Basic Concepts of First Aid and Emergencies',
        'questions': [
            ('What does D stand for in DRSABCD?', 'multiple_choice', 10, 'A', 'A) Danger|B) Doctor|C) Dressing|D) Defibrillator'),
            ('How long should you cool a burn with running water?', 'multiple_choice', 10, 'B', 'A) 5 minutes|B) 20 minutes|C) 1 hour|D) Until pain stops'),
            ('What is the correct compression to breath ratio in CPR for adults?', 'multiple_choice', 10, 'A', 'A) 30:2|B) 15:2|C) 5:1|D) 100:1'),
            ('True or False: You should induce vomiting if someone swallows chemicals.', 'true_false', 5, 'False', ''),
            ('What should you use to protect yourself when giving CPR?', 'multiple_choice', 10, 'A', 'A) CPR mask|B) Bandage|C) Gloves only|D) No protection needed'),
        ]
    },
    {
        'lesson_title': 'KM-01-KT05: Business Etiquette',
        'questions': [
            ('How many seconds does it take to form a first impression?', 'multiple_choice', 10, 'B', 'A) 30 seconds|B) 5-7 seconds|C) 1 minute|D) 10 seconds'),
            ('Which of the following is NOT a benefit of proper etiquette?', 'multiple_choice', 10, 'D', 'A) Confidence boost|B) Stronger friendships|C) Career opportunities|D) Lower salary'),
            ('What are the three key elements of a professional image?', 'short_answer', 15, 'Appearance, professional behavior, professional conduct', ''),
            ('True or False: Email subject lines are not important.', 'true_false', 5, 'False', ''),
            ('Which of the following demonstrates a positive attitude at work?', 'multiple_choice', 10, 'A', 'A) Smiling|B) Gossiping|C) Being late|D) Complaining'),
        ]
    },
    {
        'lesson_title': 'KM-01-KT06: Customer Service and Communication',
        'questions': [
            ('What percentage of communication is non-verbal according to some researchers?', 'multiple_choice', 10, 'B', 'A) 20%|B) 80%|C) 50%|D) 100%'),
            ('Which is NOT a type of non-verbal communication?', 'multiple_choice', 10, 'D', 'A) Facial expressions|B) Gestures|C) Eye gaze|D) Written words'),
            ('What is the recommended distance for casual conversation?', 'multiple_choice', 10, 'A', 'A) 18 inches - 4 feet|B) 10-12 feet|C) 6 inches|D) 20 feet'),
            ('True or False: Internal customers are employees within your organization.', 'true_false', 5, 'True', ''),
            ('Which principle of persuasion involves people feeling obliged to give back?', 'multiple_choice', 10, 'A', 'A) Reciprocity|B) Scarcity|C) Authority|D) Consistency'),
        ]
    },
    {
        'lesson_title': 'KM-01-KT07: Principles of Numeracy',
        'questions': [
            ('What is the current VAT rate in South Africa?', 'multiple_choice', 10, 'B', 'A) 10%|B) 15%|C) 20%|D) 25%'),
            ('If a product costs R100 excluding VAT, what is the price including VAT?', 'short_answer', 15, 'R115', ''),
            ('Calculate net income if revenue is R50,000 and expenses are R35,000.', 'short_answer', 15, 'R15,000', ''),
            ('What does PAYE stand for?', 'short_answer', 10, 'Pay As You Earn', ''),
            ('True or False: Net pay is the amount before deductions.', 'true_false', 5, 'False', ''),
        ]
    }
]

# Create quizzes for KM-01
for quiz_data in km01_quizzes:
    lesson = Lesson.objects.filter(course=course, title=quiz_data['lesson_title']).first()
    if lesson:
        quiz, created = Quiz.objects.get_or_create(
            lesson=lesson,
            defaults={
                'title': f'Quiz: {lesson.title}',
                'description': f'Test your knowledge on {lesson.title}',
                'passing_score': 70
            }
        )
        if created:
            print(f"  ✅ Created quiz for: {lesson.title}")
        
        for q in quiz_data['questions']:
            question_text, q_type, points, correct, options = q[0], q[1], q[2], q[3], q[4] if len(q) > 4 else ''
            
            option_a = option_b = option_c = option_d = ''
            if q_type == 'multiple_choice' and '|' in options:
                parts = options.split('|')
                if len(parts) >= 1: option_a = parts[0]
                if len(parts) >= 2: option_b = parts[1]
                if len(parts) >= 3: option_c = parts[2]
                if len(parts) >= 4: option_d = parts[3]
            
            QuizQuestion.objects.get_or_create(
                quiz=quiz,
                question_text=question_text,
                defaults={
                    'question_type': q_type,
                    'points': points,
                    'correct_answer': correct,
                    'option_a': option_a,
                    'option_b': option_b,
                    'option_c': option_c,
                    'option_d': option_d,
                    'order': quiz.questions.count() + 1
                }
            )
        print(f"     📝 Added {len(quiz_data['questions'])} questions")

print("\n" + "="*60)
print("🎉 HAIRSTYLIST COURSE SETUP COMPLETE!")
print("="*60)
print(f"\n📚 Course: {course.title}")
print(f"📖 Lessons: {course.lessons.count()}")
print(f"❓ Quizzes: {Quiz.objects.filter(lesson__course=course).count()}")
print(f"\n🔗 View course at: http://127.0.0.1:8000/course/{course.id}/")    
print("\n✅ Ready for students to enroll and learn!")
