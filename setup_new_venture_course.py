import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from core.models import User, Course, Lesson, Quiz, QuizQuestion, Assignment, Progress

# Get instructor (Phumlani)
instructor = User.objects.filter(username='Phumlani').first()
if not instructor:
    instructor = User.objects.filter(role='instructor').first()

if not instructor:
    print("❌ No instructor found! Please create an instructor first.")
    exit()

print(f"✅ Using instructor: {instructor.username}")

# ==================== CREATE COURSE ====================
course, created = Course.objects.get_or_create(
    title="Manage Finances of a New Venture - NQF Level 4 (US 263474)",
    defaults={
        'description': """This unit standard enables learners to manage the finances of a new venture.

What you will learn:
• Start-up Capital and Working Capital
• Cash Flow Management
• Income and Expenditure Statements
• Balance Sheets
• Financial Ratios Analysis
• Accounting Systems for Small Business

This qualification is essential for entrepreneurs and small business managers.""",
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

# ==================== CREATE LESSONS ====================
lessons_data = [
    {
        'order': 1,
        'title': 'Being an Entrepreneur',
        'content': """Being an Entrepreneur - Learning Objectives:

1. Define what an entrepreneur is
2. Understand the characteristics of successful entrepreneurs
3. Identify entrepreneurial opportunities
4. Understand the risks and rewards of entrepreneurship

Key Concepts:
• Entrepreneurship is the process of starting and operating a business
• Entrepreneurs take calculated risks to create value
• Successful entrepreneurs are innovative, persistent, and adaptable

Success Factors:
• Clear vision and mission
• Strong work ethic
• Financial literacy
• Marketing knowledge
• Customer focus""",
        'duration': 60
    },
    {
        'order': 2,
        'title': 'Know Yourself (Self-Assessment)',
        'content': """Know Yourself - Learning Objectives:

1. Conduct a personal SWOT analysis
2. Identify your strengths and weaknesses as an entrepreneur
3. Understand your skills and competencies
4. Develop a personal development plan

SWOT Analysis:
• Strengths: What are you good at?
• Weaknesses: What areas need improvement?
• Opportunities: What market opportunities exist?
• Threats: What challenges might you face?

Entrepreneurial Skills Assessment:
• Leadership
• Communication
• Problem-solving
• Financial management
• Time management
• Networking""",
        'duration': 45
    },
    {
        'order': 3,
        'title': 'Know Your Industry',
        'content': """Know Your Industry - Learning Objectives:

1. Research your target industry
2. Understand industry trends and dynamics
3. Identify key competitors
4. Analyze market size and growth potential

Industry Analysis Framework:
• Industry size and growth rate
• Key players and market share
• Entry barriers
• Supplier and buyer power
• Substitute products

Research Methods:
• Industry reports
• Trade associations
• Government statistics
• Competitor websites
• Customer surveys""",
        'duration': 50
    },
    {
        'order': 4,
        'title': 'Identifying Market Opportunities',
        'content': """Identifying Market Opportunities - Learning Objectives:

1. Spot market gaps and opportunities
2. Evaluate business opportunities
3. Conduct market research
4. Validate business ideas

Opportunity Identification Methods:
• Problem-solving approach
• Gap analysis
• Trend spotting
• Customer feedback
• Competitor analysis

Market Research Techniques:
• Surveys and questionnaires
• Focus groups
• Interviews
• Observation
• Secondary research""",
        'duration': 55
    },
    {
        'order': 5,
        'title': 'Innovation in Business',
        'content': """Innovation - Learning Objectives:

1. Understand the importance of innovation
2. Identify different types of innovation
3. Develop innovative products and services
4. Create a culture of innovation

Types of Innovation:
• Product innovation
• Process innovation
• Business model innovation
• Service innovation

Innovation Techniques:
• Brainstorming
• Design thinking
• Reverse engineering
• Blue ocean strategy""",
        'duration': 50
    },
    {
        'order': 6,
        'title': 'Customer Service Excellence',
        'content': """Customer Service - Learning Objectives:

1. Understand the importance of customer service
2. Develop customer service standards
3. Handle customer complaints effectively
4. Build customer loyalty

Customer Service Principles:
• Responsiveness
• Empathy
• Reliability
• Assurance
• Tangibles

Service Excellence Strategies:
• Personalization
• Follow-up
• Exceeding expectations
• Customer feedback systems""",
        'duration': 45
    },
    {
        'order': 7,
        'title': 'Financial and Cash Flow Management',
        'content': """Financial and Cash Flow Management - Learning Objectives:

1. Understand cash flow concepts
2. Create a cash flow forecast
3. Manage working capital
4. Interpret bank statements

Key Terms:
• Start-up Capital: Initial funds to start business
• Working Capital: Funds for daily operations
• Cash Flow: Money moving in and out of business
• Profit: Revenue minus expenses

Cash Flow Management Tips:
• Monitor cash flow regularly
• Invoice promptly
• Manage inventory
• Negotiate payment terms
• Build cash reserves""",
        'duration': 70
    },
    {
        'order': 8,
        'title': 'Basic Business Financial Statements',
        'content': """Basic Business Financial Statements - Learning Objectives:

1. Understand the purpose of financial statements
2. Read and interpret income statements
3. Read and interpret balance sheets
4. Read and interpret cash flow statements

Income Statement (Profit & Loss):
• Revenue - Sales income
• Cost of Goods Sold - Direct costs
• Gross Profit - Revenue minus COGS
• Operating Expenses - Rent, salaries, utilities
• Net Profit - Final profit after all expenses

Balance Sheet:
• Assets - What you own
• Liabilities - What you owe
• Equity - Owner's investment

Cash Flow Statement:
• Operating activities
• Investing activities
• Financing activities""",
        'duration': 60
    },
    {
        'order': 9,
        'title': 'Pricing of Goods and Services',
        'content': """Pricing of Goods and Services - Learning Objectives:

1. Understand pricing strategies
2. Calculate pricing using cost-plus method
3. Determine profit mark-up
4. Calculate break-even point

Pricing Methods:
• Cost-plus pricing = Cost + Markup
• Value-based pricing = Customer perceived value
• Competitive pricing = Market rates
• Penetration pricing = Low initial price

Break-even Calculation:
• Fixed Costs ÷ (Selling Price - Variable Cost)
• Example: R10,000 ÷ (R100 - R40) = 167 units

Mark-up Calculation:
• Markup % = (Selling Price - Cost) ÷ Cost × 100
• Example: (R120 - R80) ÷ R80 × 100 = 50% markup""",
        'duration': 55
    },
    {
        'order': 10,
        'title': 'Marketing Fundamentals',
        'content': """Marketing - Learning Objectives:

1. Understand the 4 Ps of marketing
2. Develop a marketing plan
3. Use digital marketing effectively
4. Measure marketing ROI

The 4 Ps of Marketing:
• Product - What you sell
• Price - How much you charge
• Place - Where you sell
• Promotion - How you communicate

Marketing Channels:
• Social media (Facebook, Instagram, LinkedIn)
• Email marketing
• Content marketing
• Search engine optimization (SEO)
• Traditional advertising
• Word of mouth

Marketing Metrics:
• Customer acquisition cost (CAC)
• Customer lifetime value (CLV)
• Conversion rate
• Return on investment (ROI)""",
        'duration': 50
    },
    {
        'order': 11,
        'title': 'SMART Goals for Business Success',
        'content': """SMART Goals - Learning Objectives:

1. Understand SMART goal framework
2. Set business goals using SMART criteria
3. Track and measure goal progress
4. Adjust goals as needed

SMART Criteria:
• Specific - Clear and specific goal
• Measurable - Trackable metrics
• Achievable - Realistic and attainable
• Relevant - Aligned with business objectives
• Time-bound - Deadline for completion

Example SMART Goals:
• "Increase sales by 20% within 6 months"
• "Acquire 100 new customers by December 31"
• "Reduce operating costs by 15% in Q3"

Goal Tracking Methods:
• Key Performance Indicators (KPIs)
• Weekly progress reviews
• Dashboard reporting""",
        'duration': 40
    },
    {
        'order': 12,
        'title': 'Business Planning',
        'content': """Business Planning - Learning Objectives:

1. Understand the purpose of a business plan
2. Identify key sections of a business plan
3. Write an effective business plan
4. Use the business plan to secure funding

Business Plan Sections:
1. Executive Summary
2. Company Description
3. Market Analysis
4. Organization and Management
5. Products and Services
6. Marketing and Sales
7. Funding Request
8. Financial Projections
9. Appendix

Business Plan Uses:
• Secure loans and investment
• Guide business operations
• Attract partners and employees
• Measure progress""",
        'duration': 60
    }
]

# Create lessons
for lesson_data in lessons_data:
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
    else:
        print(f"  📖 Lesson exists: {lesson_data['title']}")

# ==================== CREATE QUIZZES FOR EACH LESSON ====================

# Quiz questions based on Learner Workbook
quiz_questions_data = [
    # Lesson 1 Quiz
    {'lesson_title': 'Being an Entrepreneur', 'questions': [
        ('What is an entrepreneur?', 'multiple_choice', 10, 'A', 'A person who starts and operates a business|B person who works for salary|C person who invests only|D person who retired'),
        ('Which is a characteristic of successful entrepreneurs?', 'multiple_choice', 10, 'A', 'Persistence|B Laziness|C Fear of risk|D Indecision'),
        ('True or False: Entrepreneurs avoid all risks.', 'true_false', 5, 'False', ''),
    ]},
    # Lesson 2 Quiz
    {'lesson_title': 'Know Yourself', 'questions': [
        ('What does SWOT stand for?', 'multiple_choice', 10, 'B', 'Strengths, Work, Opportunities, Time|B Strengths, Weaknesses, Opportunities, Threats|C Sales, Work, Orders, Tasks|D Skills, Weaknesses, Objectives, Targets'),
        ('Which is a personal strength?', 'multiple_choice', 10, 'A', 'Good communication skills|B Poor time management|C Lack of knowledge|D Fear of public speaking'),
        ('True or False: Self-assessment is important for entrepreneurs.', 'true_false', 5, 'True', ''),
    ]},
    # Lesson 7 Quiz (Financial)
    {'lesson_title': 'Financial and Cash Flow Management', 'questions': [
        ('What is start-up capital?', 'multiple_choice', 10, 'A', 'Funds needed to start the business|B Funds for daily operations|C Profit from sales|D Money for marketing'),
        ('What is working capital?', 'multiple_choice', 10, 'A', 'Funds for day-to-day operations|B Money for equipment|C Building purchase|D Tax payments'),
        ('What is the difference between profit and cash flow?', 'short_answer', 15, '', 'Profit is accounting surplus; cash flow is actual money movement'),
        ('True or False: A business can be profitable but still run out of cash.', 'true_false', 5, 'True', ''),
        ('What is a cash flow forecast?', 'short_answer', 10, '', 'Prediction of money inflows and outflows over a period'),
    ]},
    # Lesson 8 Quiz (Financial Statements)
    {'lesson_title': 'Basic Business Financial Statements', 'questions': [
        ('What does an income statement show?', 'multiple_choice', 10, 'A', 'Revenue and expenses|B Assets and liabilities|C Cash movements|D Employee salaries'),
        ('What is the accounting equation?', 'multiple_choice', 10, 'A', 'Assets = Liabilities + Equity|B Assets = Revenue - Expenses|C Liabilities = Assets + Equity|D Equity = Assets + Liabilities'),
        ('What are assets?', 'short_answer', 10, '', 'Resources owned by the business that have value'),
        ('True or False: A balance sheet shows financial position at a point in time.', 'true_false', 5, 'True', ''),
    ]},
    # Lesson 9 Quiz (Pricing)
    {'lesson_title': 'Pricing of Goods and Services', 'questions': [
        ('What is cost-plus pricing?', 'multiple_choice', 10, 'A', 'Cost + Markup = Price|B Price - Cost = Markup|C Cost × 2 = Price|D Market price only'),
        ('How do you calculate break-even point?', 'short_answer', 15, '', 'Fixed Costs ÷ (Selling Price - Variable Cost per unit)'),
        ('If cost is R50 and markup is 40%, what is selling price?', 'short_answer', 15, '', 'R70'),
        ('True or False: Pricing only depends on costs.', 'true_false', 5, 'False', ''),
    ]},
    # Lesson 12 Quiz (Business Planning)
    {'lesson_title': 'Business Planning', 'questions': [
        ('What is the first section of a business plan?', 'multiple_choice', 10, 'A', 'Executive Summary|B Financial Projections|C Market Analysis|D Company Description'),
        ('Why is a business plan important?', 'short_answer', 15, '', 'Guides operations, secures funding, measures progress'),
        ('True or False: A business plan is only needed for loans.', 'true_false', 5, 'False', ''),
    ]},
]

# Create quizzes
for quiz_data in quiz_questions_data:
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
        
        # Add questions
        for q in quiz_data['questions']:
            question_text, q_type, points, correct, options = q[0], q[1], q[2], q[3], q[4] if len(q) > 4 else ''
            
            # Parse options for multiple choice
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

# ==================== CREATE ASSIGNMENTS ====================
assignments_data = [
    {
        'title': 'Task 1 - Accounting Glossary',
        'description': """Compile a glossary of accounting terms for your new venture.

Include the following terms with their meanings:
• Start-up Capital
• Working Capital
• Cash Flow Forecast
• Profit
• Short-term finance
• Long-term finance
• Fixed Capital

Add 8 more terms of your choice (total 15 terms).

Format: Create a table with Term and Meaning columns.
Submit as PDF or Word document.""",
        'due_days': 7,
        'points': 100
    },
    {
        'title': 'Task 2 - Cash Flow Statement',
        'description': """Create a simple cash flow statement for a new venture of your choice.

Then explain:
1. The importance of managing cash flow
2. Using cash flow as a budgeting tool
3. Using cash flow to determine working capital
4. The importance of reconciling bank statements

Include a 6-month cash flow forecast with realistic figures.
Submit as Excel or PDF document.""",
        'due_days': 14,
        'points': 100
    },
    {
        'title': 'Task 3 - Accounting System Analysis',
        'description': """Research an accounting system for your new venture.

Answer:
1. Why did you choose this system?
2. What makes this system effective for your business?
3. Does this system make provisions for tax calculations?

Include a brochure or screenshot of the system.
Submit as PDF document (2-3 pages).""",
        'due_days': 10,
        'points': 100
    },
    {
        'title': 'Task 4 - Balance Sheet',
        'description': """Create a simple balance sheet for your new venture.

Answer:
1. How often would you draw up a balance sheet?
2. List the assets and liabilities on your balance sheet
3. How would you use the balance sheet to determine financial net worth?

Include a sample balance sheet with at least 5 assets and 5 liabilities.
Submit as Excel or PDF.""",
        'due_days': 10,
        'points': 100
    },
    {
        'title': 'Task 5 - Financial Ratios',
        'description': """Use your balance sheet and income statement to calculate:

1. Current Ratio
2. Gross Profit Margin
3. Net Profit Margin
4. Business rate of income

Show all calculations and formulas.
Explain what each ratio tells about your business.
Submit as PDF or Word document.""",
        'due_days': 12,
        'points': 100
    },
    {
        'title': 'Workplace Practical - Wimpy Contract',
        'description': """Wimpy is considering your business for a contract. Prepare:

1. Cash flow statement for six months
2. Income and expenditure statement for past six months
3. Balance sheet for past six months
4. Current financial system explanation

Attach all evidence and explain each task.
Submit as PDF with supporting documents.""",
        'due_days': 21,
        'points': 150
    }
]

for assign_data in assignments_data:
    due_date = timezone.now() + timedelta(days=assign_data['due_days'])
    assignment, created = Assignment.objects.get_or_create(
        course=course,
        title=assign_data['title'],
        defaults={
            'description': assign_data['description'],
            'due_date': due_date,
            'total_points': assign_data['points']
        }
    )
    if created:
        print(f"  ✅ Created assignment: {assign_data['title']}")
    else:
        print(f"  📋 Assignment exists: {assign_data['title']}")

print("\n" + "="*60)
print("🎉 COURSE SETUP COMPLETE!")
print("="*60)
print(f"\n📚 Course: {course.title}")
print(f"📖 Lessons: {course.lessons.count()}")
print(f"❓ Quizzes: {Quiz.objects.filter(lesson__course=course).count()}")
print(f"📝 Assignments: {course.assignments.count()}")
print(f"\n🔗 View course at: http://127.0.0.1:8000/course/{course.id}/")
print("\n✅ Ready for students to enroll and learn!")