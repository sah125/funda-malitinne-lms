# create_new_venture_course.py
import os
import django
from django.contrib.auth import get_user_model
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from core.models import Course, Lesson, User, Progress, Quiz, QuizQuestion, Assignment

User = get_user_model()

def create_new_venture_course():
    """Create the complete New Venture Creation course with all lessons"""
    
    # Get the instructor (assuming Phumlani exists, or create one)
    instructor, created = User.objects.get_or_create(
        username='phumlani',
        defaults={
            'email': 'phumlani@malitinne.co.za',
            'first_name': 'Phumlani',
            'last_name': 'Phakathi',
            'role': 'instructor',
            'is_approved': True,
            'is_active': True
        }
    )
    
    if created:
        instructor.set_password('Phumlani@123')
        instructor.save()
        print(f"✓ Created instructor: {instructor.username}")
    else:
        print(f"✓ Found instructor: {instructor.username}")
    
    # Delete existing "New Venture Creation" course if it exists
    existing_course = Course.objects.filter(title__icontains='New Venture Creation').first()
    if existing_course:
        existing_course.delete()
        print("✓ Removed existing New Venture Creation course")
    
    # Create the main course
    course = Course.objects.create(
        title='New Venture Creation - NQF Level 2 (SAQA ID: 2110010232)',
        description="""This qualification is designed for aspiring entrepreneurs and small business owners. Learn to start, manage, and grow your own successful venture.

What you will learn:
• Being an entrepreneur and knowing yourself
• Understanding your industry and market opportunities  
• Innovation and customer service excellence
• Financial management and cash flow
• Business planning and SMART goals
• Marketing strategies and pricing

This course combines knowledge, practical skills, and workplace application for real-world success.""",
        instructor=instructor,
        level='intermediate',
        price=Decimal('0.00'),
        status='published'
    )
    print(f"✓ Created course: {course.title}")
    
    # ==================== LESSON 1: Being an Entrepreneur ====================
    lesson1 = Lesson.objects.create(
        course=course,
        title='Being an Entrepreneur',
        content="""What is an Entrepreneur?

An entrepreneur is an individual who identifies a business opportunity, organizes resources, and takes on the financial risk to create and manage a new venture. Entrepreneurs are the driving force behind economic growth, innovation, and job creation.

Key Characteristics of Successful Entrepreneurs:

• Risk-taking: Willing to take calculated financial and personal risks
• Innovation: Creates new products, services, or processes
• Proactive: Takes initiative rather than waiting for opportunities
• Resilience: Bounces back from failures and setbacks
• Vision: Has a clear picture of future business goals
• Self-confidence: Believes in their ability to succeed
• Adaptability: Responds effectively to changing conditions

The Entrepreneurial Process:
Opportunity Identification → Resource Gathering → Business Launch → Growth Management → Exit/Scaling

Myths About Entrepreneurs:
• Myth: Entrepreneurs are born, not made → Reality: Entrepreneurship can be learned through education and experience
• Myth: Entrepreneurs are gamblers → Reality: Successful entrepreneurs take calculated, researched risks
• Myth: Entrepreneurs work alone → Reality: Most successful ventures are built with teams and networks
• Myth: Entrepreneurs need a unique idea → Reality: Execution and improvement of existing ideas often leads to success

Why Entrepreneurship Matters for South Africa:
• Contributes to GDP growth
• Creates employment opportunities (youth unemployment crisis)
• Reduces poverty through wealth creation
• Drives innovation in communities
• Builds self-reliance and economic independence

📌 SAQA Note: This lesson aligns with US 263474/S01/AC1 - Understanding financial concepts for new ventures.""",
        duration=45,
        order=1
    )
    print(f"✓ Created Lesson 1: {lesson1.title}")
    
    # Quiz for Lesson 1
    quiz1 = Quiz.objects.create(
        lesson=lesson1,
        title='Being an Entrepreneur - Quiz',
        description='Test your understanding of entrepreneurship fundamentals',
        passing_score=70
    )
    
    # Quiz Questions for Lesson 1
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text="Which of the following BEST defines an entrepreneur?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="Someone who works for a large corporation",
        option_b="Someone who identifies opportunities, organizes resources, and takes financial risk to create a venture",
        option_c="Someone who only invests money but doesn't work",
        option_d="Someone who manages an existing business inherited from family",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text="Which characteristic is MOST important for entrepreneurs when facing business failure?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Arrogance",
        option_b="Resilience",
        option_c="Perfectionism",
        option_d="Impulsiveness",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text="According to the lesson, which statement about entrepreneurs is TRUE?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="Entrepreneurs are born, not made",
        option_b="Entrepreneurs work alone and never build teams",
        option_c="Entrepreneurship can be learned through education and experience",
        option_d="Entrepreneurs need completely unique ideas to succeed",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text="How does entrepreneurship benefit South Africa's economy?",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="Only benefits the entrepreneur personally",
        option_b="Creates employment opportunities and reduces poverty",
        option_c="Increases government debt",
        option_d="Reduces competition in markets",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text="What is the FIRST step in the entrepreneurial process?",
        question_type="multiple_choice",
        points=10,
        order=5,
        option_a="Business Launch",
        option_b="Exit/Scaling",
        option_c="Opportunity Identification",
        option_d="Growth Management",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text="True or False: Successful entrepreneurs take blind, uncalculated risks.",
        question_type="true_false",
        points=10,
        order=6,
        option_a="True",
        option_b="False (They take calculated, researched risks)",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text="True or False: Innovation is NOT important for entrepreneurs.",
        question_type="true_false",
        points=10,
        order=7,
        option_a="True",
        option_b="False (Innovation is critical for entrepreneurs)",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text="True or False: Entrepreneurs contribute to GDP growth in South Africa.",
        question_type="true_false",
        points=10,
        order=8,
        option_a="True",
        option_b="False",
        correct_answer="A"
    )
    print(f"  ✓ Added 8 quiz questions for Lesson 1")
    
    # ==================== LESSON 2: Know Yourself ====================
    lesson2 = Lesson.objects.create(
        course=course,
        title='Know Yourself',
        content="""Self-Assessment for Entrepreneurs

Before starting a venture, you must understand your own strengths, weaknesses, opportunities, and threats as an individual. This is called a Personal SWOT Analysis.

Entrepreneurial Competency Framework:
• Opportunity recognition: Ability to spot business gaps
• Financial literacy: Understanding money management
• Marketing skills: Promoting products/services
• Leadership: Guiding and motivating others
• Time management: Prioritizing tasks effectively
• Negotiation: Getting favorable agreements
• Digital literacy: Using technology for business

Simon Sinek's "Golden Circle" for Entrepreneurs:
• WHY (Center): Your purpose, cause, belief
• HOW (Middle): Your unique process, values
• WHAT (Outer): Your products, services

Example:
WHY: To help small businesses in townships succeed
HOW: By providing affordable training and mentorship
WHAT: Business skills workshops and coaching sessions

Personal Development Plan (PDP) for Entrepreneurs:
1. Identify skill gaps - Month 1
2. Find training/resources - Month 1-2
3. Schedule learning activities - Ongoing
4. Apply new skills in business - Ongoing
5. Review and adjust - Quarterly

📌 SAQA Note: This lesson supports understanding of personal readiness before financial management (US 263474/S01).""",
        duration=45,
        order=2
    )
    print(f"✓ Created Lesson 2: {lesson2.title}")
    
    quiz2 = Quiz.objects.create(
        lesson=lesson2,
        title='Know Yourself - Quiz',
        description='Test your understanding of self-assessment for entrepreneurs',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz2,
        question_text="What does the 'S' in a personal SWOT analysis stand for?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="Strategy",
        option_b="Strengths",
        option_c="Solutions",
        option_d="Sales",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz2,
        question_text="In Simon Sinek's Golden Circle, what comes at the CENTER (most important)?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="What (Products)",
        option_b="How (Process)",
        option_c="Why (Purpose)",
        option_d="When (Timing)",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz2,
        question_text="Which of the following is an example of an EXTERNAL factor in personal analysis?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="Your marketing skills",
        option_b="Your financial knowledge",
        option_c="Market competition",
        option_d="Your time management",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz2,
        question_text="A personal development plan (PDP) helps entrepreneurs to:",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="Only track their income",
        option_b="Identify and address skill gaps",
        option_c="Automatically grow their business",
        option_d="Avoid all business risks",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz2,
        question_text="Which entrepreneurial competency involves understanding money management?",
        question_type="multiple_choice",
        points=10,
        order=5,
        option_a="Marketing skills",
        option_b="Leadership",
        option_c="Financial literacy",
        option_d="Negotiation",
        correct_answer="C"
    )
    print(f"  ✓ Added 5 quiz questions for Lesson 2")
    
    # ==================== LESSON 3: Know Your Industry ====================
    lesson3 = Lesson.objects.create(
        course=course,
        title='Know Your Industry',
        content="""Industry Analysis Fundamentals

Before launching a venture, you must understand the industry you are entering. An industry is a group of businesses that offer similar products or services.

Why Industry Knowledge Matters:
• Identifies opportunities and threats
• Helps position your business effectively
• Informs pricing and marketing strategies
• Reduces risk of business failure

PESTLE Analysis for External Factors:
• Political: Government stability, policies, tax laws, trade regulations
• Economic: Interest rates, inflation, unemployment, cost of borrowing
• Social: Demographics, lifestyle trends, youth unemployment in SA
• Technological: New tech affecting industry (AI, e-commerce, mobile payments)
• Legal: Laws and regulations, business licensing, labor laws
• Environmental: Climate impact, sustainability, eco-friendly products

Market Research Methods:
• Surveys: Questionnaires to potential customers - Low cost - Quantitative data
• Interviews: One-on-one conversations - Medium cost - Deep insights
• Focus Groups: Small group discussions - Medium-High cost - Product feedback
• Observation: Watching customer behavior - Low cost - Understanding real behavior
• Secondary Research: Using existing reports/data - Low cost - Industry trends

📌 SAQA Note: Industry knowledge is essential for realistic financial planning (US 263474/S01).""",
        duration=45,
        order=3
    )
    print(f"✓ Created Lesson 3: {lesson3.title}")
    
    quiz3 = Quiz.objects.create(
        lesson=lesson3,
        title='Know Your Industry - Quiz',
        description='Test your understanding of industry analysis',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz3,
        question_text="What does the 'E' in PESTLE analysis stand for?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="Employment",
        option_b="Economic",
        option_c="Evaluation",
        option_d="External",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz3,
        question_text="Which market research method is BEST for collecting numerical data from many people?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Focus groups",
        option_b="One-on-one interviews",
        option_c="Surveys",
        option_d="Observation",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz3,
        question_text="In PESTLE analysis, 'interest rates' and 'inflation' fall under which category?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="Political",
        option_b="Social",
        option_c="Economic",
        option_d="Technological",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz3,
        question_text="Why is competitor analysis important for a new venture?",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="To copy exactly what competitors do",
        option_b="To reduce prices below cost",
        option_c="To identify market gaps and positioning opportunities",
        option_d="To avoid selling any products",
        correct_answer="C"
    )
    print(f"  ✓ Added 4 quiz questions for Lesson 3")
    
    # ==================== LESSON 4: Identifying Market Opportunities ====================
    lesson4 = Lesson.objects.create(
        course=course,
        title='Identifying Market Opportunities',
        content="""What is a Market Opportunity?

A market opportunity is a favorable set of circumstances that creates a need or want for a product or service that is not being adequately met by existing businesses.

Sources of Market Opportunities:
• PROBLEMS: What frustrates people? What is inconvenient?
• CHANGES: What is changing? What trends are emerging?
• GAPS: What is missing? What do people want that they can't find?
• SKILLS: What can you do well? What expertise do you have?
• RESOURCES: What do you have access to? What assets are available?
• NETWORKS: Who do you know? What connections can help you?

Opportunity Evaluation Criteria (Score 1-5 each):
• Market Size: Is the market large enough?
• Growth Potential: Is the market growing?
• Profitability: Can you make enough profit?
• Competition: Can you compete effectively?
• Your Resources: Do you have what you need?
• Risk Level: Is the risk acceptable?
• Timing: Is now the right time?

Total Score: ___ / 35
Interpretation: 30+ = Excellent opportunity; 20-29 = Good opportunity, address weaknesses; Below 20 = Reconsider

Township Economy Opportunities in South Africa:
• Spaza shop modernization: Digital inventory, delivery - Low-Medium cost
• Mobile car wash: On-demand services - Low cost
• Hair and beauty: Mobile app booking - Low cost
• Food delivery: Local restaurant partnerships - Medium cost
• Tutoring services: After-school programs - Low cost
• Laundry services: Pick-up and delivery - Medium cost
• Event planning: Parties, weddings, funerals - Medium-High cost

📌 SAQA Note: Opportunity identification relates to US 263474/S01 - Understanding the financial foundation of a new venture.""",
        duration=45,
        order=4
    )
    print(f"✓ Created Lesson 4: {lesson4.title}")
    
    quiz4 = Quiz.objects.create(
        lesson=lesson4,
        title='Identifying Market Opportunities - Quiz',
        description='Test your understanding of market opportunity identification',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz4,
        question_text="What is a market opportunity?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="A guaranteed way to make money",
        option_b="A favorable set of circumstances creating unmet need for a product/service",
        option_c="A government grant for businesses",
        option_d="A type of marketing strategy",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz4,
        question_text="Which of the following is a VALID source of market opportunities?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Copying an existing business exactly",
        option_b="Problems and frustrations people experience",
        option_c="Ignoring market trends",
        option_d="Only doing what you already know",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz4,
        question_text="What is market segmentation?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="Charging different prices to different customers",
        option_b="Dividing the total market into smaller groups with similar characteristics",
        option_c="Removing competitors from the market",
        option_d="Selling products in different countries",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz4,
        question_text="When evaluating an opportunity, a score below 20 out of 35 suggests:",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="Excellent opportunity, launch immediately",
        option_b="Good opportunity with minor issues",
        option_c="Reconsider the opportunity; it may not be viable",
        option_d="The scoring is incorrect",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz4,
        question_text="True or False: Market opportunities can only come from completely new ideas.",
        question_type="true_false",
        points=10,
        order=5,
        option_a="True",
        option_b="False (Opportunities can come from improving existing products/services)",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz4,
        question_text="True or False: Customer frustrations and complaints can be sources of business opportunities.",
        question_type="true_false",
        points=10,
        order=6,
        option_a="True",
        option_b="False",
        correct_answer="A"
    )
    print(f"  ✓ Added 6 quiz questions for Lesson 4")
    
    # ==================== LESSON 5: Innovation ====================
    lesson5 = Lesson.objects.create(
        course=course,
        title='Innovation',
        content="""What is Innovation?

Innovation is the process of creating new or significantly improved products, services, processes, or business models. It is NOT the same as invention (creating something completely new) - innovation often involves improving existing ideas.

Types of Innovation:
• Product Innovation: Creating new or improved products (Example: Smartphone with better camera)
• Process Innovation: Improving how products are made or delivered (Example: Faster checkout system)
• Business Model Innovation: Changing how value is created and captured (Example: Subscription instead of one-time fee)
• Service Innovation: Improving customer experience (Example: 24/7 customer support chatbot)
• Social Innovation: Creating social or environmental impact (Example: Recycling program that employs youth)

The Innovation Funnel:
Many Ideas (100) → Screening (20) → Development (5) → Testing (2) → One Launch (1)

Design Thinking Process (5 steps):
1. EMPATHIZE: Understand user needs and pain points
2. DEFINE: Define the core problem to solve
3. IDEATE: Generate many potential solutions
4. PROTOTYPE: Create simple versions to test
5. TEST: Get feedback and refine

Simple Innovation Techniques - SCAMPER:
• Substitute: Change delivery method
• Combine: Combine two products
• Adapt: Modify for new use
• Modify: Change characteristics
• Put to other use: Find new applications
• Eliminate: Remove unnecessary features
• Reverse: Do the opposite

📌 SAQA Note: Innovation relates to financial efficiency and profitability (US 263474/S06).""",
        duration=45,
        order=5
    )
    print(f"✓ Created Lesson 5: {lesson5.title}")
    
    quiz5 = Quiz.objects.create(
        lesson=lesson5,
        title='Innovation - Quiz',
        description='Test your understanding of innovation for entrepreneurs',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz5,
        question_text="What is the difference between invention and innovation?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="They are the same thing",
        option_b="Invention creates something completely new; innovation improves existing ideas",
        option_c="Innovation creates something completely new; invention improves existing ideas",
        option_d="Both create completely new things",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz5,
        question_text="Which type of innovation changes how products are made or delivered?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Product innovation",
        option_b="Process innovation",
        option_c="Business model innovation",
        option_d="Social innovation",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz5,
        question_text="What is the FIRST step in the Design Thinking process?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="Ideate",
        option_b="Test",
        option_c="Empathize",
        option_d="Prototype",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz5,
        question_text="What does the 'C' in SCAMPER stand for?",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="Create",
        option_b="Combine",
        option_c="Compete",
        option_d="Calculate",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz5,
        question_text="True or False: Innovation is only for large corporations with big budgets.",
        question_type="true_false",
        points=10,
        order=5,
        option_a="True",
        option_b="False (Small businesses can innovate with minimal resources)",
        correct_answer="B"
    )
    print(f"  ✓ Added 5 quiz questions for Lesson 5")
    
    # ==================== LESSON 6: Customer Service ====================
    lesson6 = Lesson.objects.create(
        course=course,
        title='Customer Service',
        content="""Why Customer Service Matters

Customer service is the support and assistance provided to customers before, during, and after they purchase a product or service. It is often the KEY differentiator between successful and failed businesses.

The Cost of Poor Customer Service:
• 1 unhappy customer tells 11-15 people
• 91% of unhappy customers will NOT buy from you again
• It costs 5-7x MORE to get a new customer than keep an old one
• A 5% increase in retention can increase profit by 25-95%

Handling Customer Complaints - The HEAT Method:
• H - Hear them out (listen without interrupting)
• E - Empathize (show you understand their frustration)
• A - Apologize (sincerely, even if not your fault)
• T - Take action (solve the problem quickly)

Building Customer Loyalty:
• Thank you notes with purchases
• Small discounts for repeat customers
• Birthday specials
• Referral rewards ("bring a friend, get R50 off")
• Ask for feedback and act on it

Customer Service in the South African Context:
• Language diversity: Learn basic greetings in local languages
• Cash vs digital: Offer payment options (cash, SnapScan, Zapper, EFT)
• Township accessibility: Consider delivery, flexible hours
• Trust building: Be consistent, visible, and keep promises

📌 SAQA Note: Customer retention affects recurring revenue and cash flow stability (US 263474/S02).""",
        duration=45,
        order=6
    )
    print(f"✓ Created Lesson 6: {lesson6.title}")
    
    quiz6 = Quiz.objects.create(
        lesson=lesson6,
        title='Customer Service - Quiz',
        description='Test your understanding of customer service for entrepreneurs',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz6,
        question_text="How many people does one unhappy customer typically tell?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="1-2 people",
        option_b="5-7 people",
        option_c="11-15 people",
        option_d="50+ people",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz6,
        question_text="What does the 'A' stand for in the HEAT method for handling complaints?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Ask questions",
        option_b="Apologize",
        option_c="Analyze",
        option_d="Approve",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz6,
        question_text="How much more does it cost to acquire a new customer compared to retaining an existing one?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="2-3x more",
        option_b="5-7x more",
        option_c="10-12x more",
        option_d="Same cost",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz6,
        question_text="Which of the following is a simple way to build customer loyalty for a small business?",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="Ignore customer feedback",
        option_b="Never offer discounts",
        option_c="Send thank you notes with purchases",
        option_d="Make it difficult to contact you",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz6,
        question_text="List the FOUR steps of the HEAT method for handling complaints.",
        question_type="multiple_choice",
        points=10,
        order=5,
        option_a="Help, Evaluate, Ask, Thank",
        option_b="Hear, Empathize, Apologize, Take action",
        option_c="Hello, Explain, Answer, Terminate",
        option_d="Hold, Execute, Advance, Teach",
        correct_answer="B"
    )
    print(f"  ✓ Added 5 quiz questions for Lesson 6")
    
    # ==================== LESSON 7: Financial and Cash Flow Management ====================
    lesson7 = Lesson.objects.create(
        course=course,
        title='Financial and Cash Flow Management',
        content="""Key Financial Concepts for New Ventures

Start-up Capital vs. Working Capital:
• Start-up Capital: One-time investment needed to launch the business (business registration, initial stock, equipment deposit)
• Fixed Capital: Long-term assets used repeatedly (property, vehicles, machinery, computers)
• Working Capital: Funds for day-to-day operations (stock, salaries, rent, utilities)

Formula: Working Capital = Current Assets - Current liabilities

Short-term vs. Long-term Finance:
• Short-term: Repayment under 12 months (stock, salaries, seasonal needs) - Bank overdraft, trade credit
• Long-term: Repayment over 1 year (property, vehicles, major equipment) - Mortgage, business loan

Cash Flow vs. Profit - The #1 confusion!
• Cash Flow: Actual money moving in/out - Shows if you can pay bills
• Profit: Accounting concept - Revenue minus expenses
• Critical: A business can be PROFITABLE but RUN OUT OF CASH and FAIL!

Cash Flow Warning Signs:
• Always waiting for customer payments before paying suppliers
• Using overdraft every month
• Delaying payments to creditors
• Unable to take advantage of discounts
• Owner delaying salary

📌 SAQA Note: This lesson aligns with US 263474/S01 and US 263474/S02.""",
        duration=45,
        order=7
    )
    print(f"✓ Created Lesson 7: {lesson7.title}")
    
    quiz7 = Quiz.objects.create(
        lesson=lesson7,
        title='Financial and Cash Flow Management - Quiz',
        description='Test your understanding of financial management',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz7,
        question_text="Define start-up capital.",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="Money needed for daily operations like salaries",
        option_b="One-time investment needed to launch the business before trading",
        option_c="Profit the business makes in first year",
        option_d="Loan from bank with high interest",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz7,
        question_text="What is the key difference between fixed capital and working capital?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Fixed capital is for daily expenses; working capital for long-term assets",
        option_b="Fixed capital is for long-term assets; working capital for daily operations",
        option_c="Fixed capital is a liability; working capital is an asset",
        option_d="There is no difference",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz7,
        question_text="Which is an example of LONG-TERM finance?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="Bank overdraft",
        option_b="12-month trade credit",
        option_c="5-year business loan",
        option_d="Payday loan",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz7,
        question_text="True or False: A business can have high profit but still run out of cash and fail.",
        question_type="true_false",
        points=10,
        order=4,
        option_a="True",
        option_b="False",
        correct_answer="A"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz7,
        question_text="Why is cash flow management critical?",
        question_type="multiple_choice",
        points=10,
        order=5,
        option_a="To calculate exact tax amount",
        option_b="To ensure business can pay bills, salaries, and suppliers on time",
        option_c="To determine resale value of fixed assets",
        option_d="To measure customer satisfaction",
        correct_answer="B"
    )
    print(f"  ✓ Added 5 quiz questions for Lesson 7")
    
    # ==================== LESSON 8: Basic Business Financial Statements ====================
    lesson8 = Lesson.objects.create(
        course=course,
        title='Basic Business Financial Statements',
        content="""Three Essential Financial Statements

Every new venture needs these three statements to manage finances effectively:

1. Cash Flow Forecast: Shows CASH moving in and out - "Will I have money to pay bills?"

2. Income & Expenditure Statement (Profit & Loss): Shows PROFIT/LOSS over time - "Am I making money?"

3. Balance Sheet: Shows NET WORTH at a moment in time - "What is my business worth today?"

Cash Flow Forecast Template:
• Opening Balance + Inflows - Outflows = Closing Balance

Income & Expenditure Statement:
• TOTAL INCOME - TOTAL EXPENDITURE = PROFIT/(LOSS)

Balance Sheet Equation:
• ASSETS = LIABILITIES + OWNER'S EQUITY
• OR: Owner's Equity = Assets - Liabilities (Net Worth)

Sources of Information:
• Income sources: Sales invoices, bank deposits, service fees
• Expense sources: Purchase receipts, salary records, utility bills

📌 SAQA Note: This lesson covers US 263474/S02, S04, S05.""",
        duration=45,
        order=8
    )
    print(f"✓ Created Lesson 8: {lesson8.title}")
    
    quiz8 = Quiz.objects.create(
        lesson=lesson8,
        title='Basic Business Financial Statements - Quiz',
        description='Test your understanding of financial statements',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz8,
        question_text="What is the purpose of an Income and Expenditure Statement?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="Show value of what business owns and owes on one day",
        option_b="Track cash in and out over a period",
        option_c="Summarize income and expenses to see profit or loss",
        option_d="List names of all shareholders",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz8,
        question_text="What is the purpose of a Balance Sheet?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Show cash flow for the next year",
        option_b="Provide snapshot of assets, liabilities, and equity on a specific date",
        option_c="Record every single transaction in detail",
        option_d="Calculate income tax owed",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz8,
        question_text="Which is a CURRENT LIABILITY?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="Long-term bank loan",
        option_b="Delivery vehicle",
        option_c="Supplier invoice due in 30 days",
        option_d="Owner's personal house",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz8,
        question_text="How do you determine financial net worth from the balance sheet?",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="Total Assets + Total Liabilities",
        option_b="Total Liabilities - Total Assets",
        option_c="Total Assets - Total Liabilities",
        option_d="Total Cash - Total Expenses",
        correct_answer="C"
    )
    print(f"  ✓ Added 4 quiz questions for Lesson 8")
    
    # ==================== LESSON 9: Pricing of Goods and Services ====================
    lesson9 = Lesson.objects.create(
        course=course,
        title='Pricing of Goods and Services',
        content="""What is Pricing?

Pricing is the process of determining what to charge customers for products or services. It directly affects profitability, cash flow, customer perception, and competitive position.

Pricing Strategies for New Ventures:
• Cost-Plus: Cost + Markup % (Example: Cost R50 + 50% = R75 price)
• Competitive: Match or beat competitors
• Penetration: Low price to gain market share
• Premium: High price = high quality
• Psychological: R99 instead of R100
• Value-Based: Price based on customer value

Cost-Plus Pricing Formula:
Cost of product (materials + labour + overhead) + Markup (profit %) = Selling Price

Break-Even Analysis:
Break-Even Units = Fixed Costs ÷ (Selling Price - Variable Cost per Unit)
• Fixed costs: Rent, salaries (don't change with units sold)
• Variable costs: Materials, packaging (change with each unit)
• Contribution margin = Selling Price - Variable Cost per unit

Factors Affecting Pricing:
• Costs: Must cover all costs + profit target
• Customers: What price can they afford?
• Competition: What are others charging?
• Value: What is the perceived benefit?
• Business goals: Growth vs profit focus

📌 SAQA Note: Pricing directly affects cash flow and viability (US 263474/S02, S04).""",
        duration=45,
        order=9
    )
    print(f"✓ Created Lesson 9: {lesson9.title}")
    
    quiz9 = Quiz.objects.create(
        lesson=lesson9,
        title='Pricing of Goods and Services - Quiz',
        description='Test your understanding of pricing strategies',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz9,
        question_text="What is the break-even point?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="When total revenue is maximum",
        option_b="When total revenue equals total costs (no profit, no loss)",
        option_c="When total costs are zero",
        option_d="When profit is 50%",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz9,
        question_text="Which pricing strategy sets prices lower than competitors to gain market share?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Premium pricing",
        option_b="Penetration pricing",
        option_c="Cost-plus pricing",
        option_d="Psychological pricing",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz9,
        question_text="A product costs R40 to make. You want a 60% markup. What is the selling price?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="R40",
        option_b="R64",
        option_c="R80",
        option_d="R100",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz9,
        question_text="Why is psychological pricing (e.g., R99 instead of R100) effective?",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="It significantly reduces cost",
        option_b="Customers perceive it as cheaper",
        option_c="It doubles profit",
        option_d="It guarantees sales",
        correct_answer="B"
    )
    print(f"  ✓ Added 4 quiz questions for Lesson 9")
    
    # ==================== LESSON 10: Marketing ====================
    lesson10 = Lesson.objects.create(
        course=course,
        title='Marketing',
        content="""What is Marketing?

Marketing is the process of identifying, anticipating, and satisfying customer needs profitably. It's NOT just advertising - it's everything from product design to after-sales service.

The 7 Ps of Marketing:
1. PRODUCT: What are you selling? Quality? Features?
2. PRICE: How much? Payment terms? Discounts?
3. PLACE: Where do customers access it? Location?
4. PROMOTION: How do customers know about it? Advertising?
5. PEOPLE: Staff, customer service, delivery team
6. PROCESS: Ordering, delivery, payment process
7. PHYSICAL EVIDENCE: Packaging, store appearance, uniforms

Low-Cost Marketing Strategies:
• Word of mouth: Happy customers tell others (R0 cost)
• WhatsApp marketing: Broadcast lists, groups, status (R0-R100)
• Social media: Facebook, Instagram, TikTok posts (R0-R500)
• Referral program: Discount for referrals (Low cost)
• Flyers/posters: Put in high-traffic areas (R200-R500)
• Collaborations: Partner with complementary businesses (R0)

SMART Marketing Goals:
• Specific: Clear, detailed, no confusion
• Measurable: Can track progress and completion
• Achievable: Realistic with available resources
• Relevant: Aligns with business purpose/values
• Time-bound: Has a deadline or timeframe

Example: "Gain 50 new customers in first 3 months"

📌 SAQA Note: Marketing effectiveness affects income and cash flow (US 263474/S02, S04).""",
        duration=45,
        order=10
    )
    print(f"✓ Created Lesson 10: {lesson10.title}")
    
    quiz10 = Quiz.objects.create(
        lesson=lesson10,
        title='Marketing - Quiz',
        description='Test your understanding of marketing for entrepreneurs',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz10,
        question_text="Which of the following is NOT one of the 7 Ps of Marketing?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="Product",
        option_b="Price",
        option_c="Profit",
        option_d="Promotion",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz10,
        question_text="What does USP stand for?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Universal Sales Price",
        option_b="Unique Selling Point",
        option_c="Under Sales Protection",
        option_d="Ultimate Service Plan",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz10,
        question_text="Which marketing strategy typically has the LOWEST cost?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="TV advertising",
        option_b="Radio advertising",
        option_c="Word of mouth",
        option_d="Billboards",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz10,
        question_text="Why is WhatsApp considered an effective marketing tool for South African small businesses?",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="It's expensive so only serious businesses use it",
        option_b="Most South Africans have WhatsApp and use it daily",
        option_c="It automatically creates advertisements",
        option_d="Government requires all businesses to use it",
        correct_answer="B"
    )
    print(f"  ✓ Added 4 quiz questions for Lesson 10")
    
    # ==================== LESSON 11: SMART Goals ====================
    lesson11 = Lesson.objects.create(
        course=course,
        title='SMART Goals',
        content="""What are SMART Goals?

SMART is an acronym that helps create effective, achievable goals for business and personal success.

The SMART Framework:
• S - SPECIFIC: Clear, detailed, no confusion - "WHAT exactly do I want?"
• M - MEASURABLE: Can track progress and completion - "HOW MUCH or HOW MANY?"
• A - ACHIEVABLE: Realistic with available resources - "CAN I actually do this?"
• R - RELEVANT: Aligns with business purpose/values - "DOES this matter to my business?"
• T - TIME-BOUND: Has a deadline or timeframe - "WHEN will I complete this?"

Examples:
• Non-SMART: "Make more money"
• SMART: "Increase monthly sales revenue by 20% (from R50,000 to R60,000) by 31 December"

Financial Ratios for Goal Setting:
• Current Ratio = Current Assets ÷ Current Liabilities (Target: Above 1.5)
• Gross Profit Margin = (Revenue - Cost of Goods Sold) ÷ Revenue × 100
• Net Profit Margin = Net Profit ÷ Revenue × 100 (Target: 10-20%)

To INCREASE INCOME:
• Raise prices 5-10%
• Add new products/services
• Upsell to existing customers
• Expand customer base

To REDUCE COSTS:
• Negotiate with suppliers
• Reduce waste
• Energy efficiency
• Outsource non-core tasks

📌 SAQA Note: This lesson covers US 263474/S05/AC5 and US 263474/S06/AC2.""",
        duration=45,
        order=11
    )
    print(f"✓ Created Lesson 11: {lesson11.title}")
    
    quiz11 = Quiz.objects.create(
        lesson=lesson11,
        title='SMART Goals - Quiz',
        description='Test your understanding of SMART goal setting',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz11,
        question_text="What does the 'M' in SMART goals stand for?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="Meaningful",
        option_b="Measurable",
        option_c="Monetary",
        option_d="Manageable",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz11,
        question_text="Which of the following is a SMART goal?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="Make more sales",
        option_b="Get rich",
        option_c="Increase monthly sales by 15% (from R40,000 to R46,000) by 31 December",
        option_d="Be better than competitors",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz11,
        question_text="The Current Ratio measures:",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="How much profit the business makes",
        option_b="The ability to pay short-term debts",
        option_c="Customer satisfaction levels",
        option_d="Employee productivity",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz11,
        question_text="Which strategy would increase income?",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="Reducing prices below cost",
        option_b="Adding complementary products/services",
        option_c="Closing earlier each day",
        option_d="Reducing marketing",
        correct_answer="B"
    )
    print(f"  ✓ Added 4 quiz questions for Lesson 11")
    
    # ==================== LESSON 12: Business Planning ====================
    lesson12 = Lesson.objects.create(
        course=course,
        title='Business Planning',
        content="""What is a Business Plan?

A business plan is a written document that describes your business, its objectives, strategies, market, financial forecasts, and operations. It serves as a roadmap and is essential for securing funding, guiding business decisions, measuring progress, and attracting partners.

Business Plan Structure:
1. Executive Summary: One-page overview of the entire plan (Write this LAST)
2. Business Description: What business does, mission, vision, legal structure
3. Products/Services: What you sell, features, benefits, pricing
4. Market Analysis: Industry, target market, competition, size
5. Marketing & Sales Strategy: How you will attract and retain customers
6. Operations Plan: Location, equipment, suppliers, processes
7. Management & Organization: Owners, staff, roles, advisors
8. Financial Plan: Start-up capital, cash flow forecast, income statement, balance sheet, break-even analysis
9. Risk Assessment: Potential problems and solutions
10. Appendices: Supporting documents (licenses, quotes, resumes)

Accounting System Requirements:
• Choose the right system (Excel, QuickBooks, Wave, or manual)
• Set up chart of accounts
• Open separate business bank account
• Schedule regular record-keeping (daily/weekly/monthly)
• File receipts and invoices

Taxation Requirements for South Africa:
• Income Tax: 27% on profit (companies)
• VAT: 15% (if revenue > R1 million/year)
• PAYE: 18-45% (deduct from employee salaries)
• UIF: 1% employee + 1% employer

📌 SAQA Note: This lesson integrates ALL US 263474 learning outcomes.""",
        duration=45,
        order=12
    )
    print(f"✓ Created Lesson 12: {lesson12.title}")
    
    quiz12 = Quiz.objects.create(
        lesson=lesson12,
        title='Business Planning - Quiz',
        description='Test your understanding of business planning',
        passing_score=70
    )
    
    QuizQuestion.objects.create(
        quiz=quiz12,
        question_text="Which is the BEST accounting system for a brand new small venture with very few transactions?",
        question_type="multiple_choice",
        points=10,
        order=1,
        option_a="Enterprise ERP system (R20,000+)",
        option_b="Excel spreadsheet or simple paper records",
        option_c="Complex multi-company software",
        option_d="No system at all",
        correct_answer="B"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz12,
        question_text="At what annual revenue must a business register for VAT in South Africa?",
        question_type="multiple_choice",
        points=10,
        order=2,
        option_a="R100,000",
        option_b="R500,000",
        option_c="R1,000,000",
        option_d="R5,000,000",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz12,
        question_text="How often should a small business reconcile its bank statements?",
        question_type="multiple_choice",
        points=10,
        order=3,
        option_a="Never",
        option_b="Once a year",
        option_c="Monthly",
        option_d="Every 5 years",
        correct_answer="C"
    )
    
    QuizQuestion.objects.create(
        quiz=quiz12,
        question_text="Why should the Executive Summary be written LAST when creating a business plan?",
        question_type="multiple_choice",
        points=10,
        order=4,
        option_a="Because it's least important",
        option_b="Because it's a summary of the ENTIRE plan - you must write everything else first",
        option_c="Because it requires special software",
        option_d="Because only accountants can write it",
        correct_answer="B"
    )
    print(f"  ✓ Added 4 quiz questions for Lesson 12")
    
    # Summary
    print("\n" + "="*60)
    print("✅ COURSE CREATION COMPLETE!")
    print("="*60)
    print(f"\n📚 Course: {course.title}")
    print(f"📖 Total Lessons: 12")
    print(f"❓ Total Quiz Questions: 54")
    print(f"👨‍🏫 Instructor: {instructor.get_full_name() or instructor.username}")
    print(f"\n🔗 Course URL: http://127.0.0.1:8000/course/{course.id}/")
    print("\n✨ Students can now enroll and start learning!")
    
    return course

if __name__ == '__main__':
    print("🚀 Starting New Venture Creation Course Creation...")
    print("-" * 40)
    create_new_venture_course()