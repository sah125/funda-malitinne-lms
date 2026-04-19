import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms.settings')
django.setup()

from core.models import User, Course, Lesson

# Get instructor
instructor = User.objects.filter(role='instructor').first()

if not instructor:
    print("❌ No instructor found! Please create an instructor first in admin panel.")
    print("   Go to: http://127.0.0.1:8000/admin/core/user/add/")
    print("   Create a user with role='instructor'")
else:
    print(f"✅ Using instructor: {instructor.username}")
    
    # Create New Venture Creation Course
    course, created = Course.objects.get_or_create(
        title="New Venture Creation - NQF Level 2 (SAQA ID: 2110010232)",
        defaults={
            'description': """This qualification is designed for aspiring entrepreneurs and small business owners.

Learn to start, manage, and grow your own successful venture.

What you will learn:
• Being an entrepreneur and knowing yourself
• Understanding your industry and market opportunities
• Innovation and customer service excellence
• Financial management and cash flow
• Business planning and SMART goals
• Marketing strategies and pricing

This course combines knowledge, practical skills, and workplace application for real-world success.""",
            'instructor': instructor,
            'level': 'intermediate',
            'price': 0
        }
    )
    
    if created:
        print(f"✅ Created course: {course.title}")
    else:
        print(f"📚 Course already exists: {course.title}")
    
    # Add all topics as lessons
    topics = [
        (1, "Being an Entrepreneur", "Learn what it takes to be a successful entrepreneur. Understand the entrepreneurial mindset, characteristics, and success factors."),
        (2, "Know Yourself", "Self-assessment and personal development for entrepreneurs. Identify your strengths, weaknesses, and areas for growth."),
        (3, "Know Your Industry", "Research and analyze your industry. Understand market trends, competitors, and opportunities."),
        (4, "Identifying Market Opportunities", "Learn how to spot and evaluate business opportunities. Market research techniques and validation."),
        (5, "Innovation", "Creative thinking and innovation in business. How to develop unique products and services."),
        (6, "Customer Service", "Excellence in customer service. Building customer relationships and loyalty."),
        (7, "Financial and Cash Flow Management", "Understanding cash flow, budgeting, and financial planning for small businesses."),
        (8, "Basic Business Financial Statements", "Learn to read and prepare income statements, balance sheets, and cash flow statements."),
        (9, "Pricing of Goods and Services", "Pricing strategies, cost analysis, and profit calculation."),
        (10, "Marketing", "Marketing fundamentals, digital marketing, and promotional strategies."),
        (11, "SMART Goals", "Setting Specific, Measurable, Achievable, Relevant, Time-bound goals for business success."),
        (12, "Business Planning", "Creating a comprehensive business plan that attracts investors and guides operations."),
    ]
    
    print("\n📚 Adding lessons:")
    for order, title, content in topics:
        lesson, created = Lesson.objects.get_or_create(
            course=course,
            title=title,
            defaults={
                'content': content,
                'order': order,
                'duration': 45
            }
        )
        if created:
            print(f"  ✅ Added lesson {order}: {title}")
        else:
            print(f"  📖 Lesson already exists: {title}")
    
    print(f"\n🎉 Course setup complete! Total lessons: {course.lessons.count()}")
    print(f"\n🔗 View course at: http://127.0.0.1:8000/course/{course.id}/")