from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import (
    Course,
    LearningModule,
    Lesson,
    LessonModule,
    ObservationChecklistItem,
    SummativeAssessment,
)

User = get_user_model()

COURSE_TITLE = "New Venture Creation (SP-210401)"
COURSE_SLUG = "new-venture-creation-sp-210401"
COURSE_DESCRIPTION = """New Venture Creation (SP-210401) is designed to prepare learners to start, manage, grow and sustain a small business. It introduces the entrepreneurial mindset, helps learners understand themselves and their opportunities, and builds practical business decision-making skills for a real-world venture.

This programme is aligned to Grade 9 entry requirements and NQF Level 2, with 32 credits and 320 notional hours. It is structured over 40 working days, with Theory for 20 days, Practical for 6 days, FISA for 10 days, and Self-study for 4 days. The focus is on building the confidence, knowledge and practical ability required to identify opportunities, plan a venture, and work in a small business environment.

Learners are guided through the fundamentals of entrepreneurship, customer service, market awareness, marketing, financial management, pricing, and business planning. The programme supports both the understanding and practice of running a business in a realistic environment, helping learners move from idea generation to operational decision-making.

By the end of the programme, learners should be able to recognise a business opportunity, understand the needs of a market, think creatively, manage basic finances, and contribute to a small business in a structured and responsible way. It combines personal development, business awareness, and practical planning so that learners can begin to operate or support a venture with confidence."""

LESSONS = [
    {
        "title": "Being an Entrepreneur",
        "duration": 12,
        "order": 1,
        "content": "Entrepreneurship is the process of identifying an opportunity, gathering the resources needed to act on it, and taking calculated risk to create and manage a new enterprise. An entrepreneur is not only a business owner; they are also a decision-maker, planner, innovator and risk-taker who turns an idea into an operating business. The lesson frames business creation as a practical process that begins with self-awareness, opportunity recognition and deliberate action.\n\nSuccessful entrepreneurs are usually recognised by their initiative, resilience, willingness to learn, and ability to adapt. They are able to evaluate the environment in which they operate, consider what the market needs, and choose a direction that matches their skills and goals. Entrepreneurship contributes to economic growth, job creation and self-reliance, which is especially relevant to developing communities and small business environments.\n\nThe journey of an entrepreneur includes identifying an opportunity, organising resources, launching the business, managing growth and reviewing performance. It is important to understand that entrepreneurship is not simply about having a unique idea; it is about using knowledge, planning and practical effort to create value. Entrepreneurs often work with partners, customers, suppliers and support networks, and they are expected to make responsible decisions in uncertain conditions.\n\nThis lesson emphasises that entrepreneurship can be learned and developed through exposure, training and experience. A person can become more effective as a business owner by building personal confidence, understanding risk, and improving the ability to act on opportunities in a structured way."
    },
    {
        "title": "Know Yourself",
        "duration": 12,
        "order": 2,
        "content": "Before starting a venture, a learner must understand their own strengths, weaknesses, motivations and personal qualities. Self-awareness is a foundation for entrepreneurship because a business grows best when the owner knows how they think, work and respond to challenges. This lesson encourages learners to evaluate personal strengths, identify gaps in skills, and recognise the habits that support business growth.\n\nA personal SWOT analysis can help a learner reflect on areas such as opportunity recognition, leadership, confidence, communication, time management and financial literacy. These competencies support the ability to make smart decisions and handle responsibilities in a business environment. Understanding personal purpose is also important, because a business should align with the values and goals of the owner.\n\nThe lesson also introduces the idea of a business purpose through the Golden Circle model: why the business exists, how it creates value, and what it offers. This helps learners connect personal vision to practical business action. By clarifying why they want to operate a venture, learners can become more focused, resilient and intentional in their decision-making.\n\nA practical self-development plan supports this process by identifying gaps, seeking relevant learning, applying new knowledge and reviewing results over time. This shows that personal growth is part of business readiness and that success is built through ongoing practice and reflection."
    },
    {
        "title": "Know Your Industry",
        "duration": 12,
        "order": 3,
        "content": "Understanding the industry in which a business will operate is essential before launching or expanding a venture. Learners are introduced to the idea that different industries have different customer needs, trends, risks and operating conditions. A business owner must understand the environment in which they compete so that decisions about products, services, prices and marketing are based on evidence and not guesswork.\n\nThis lesson helps learners look at the industry context, identify key players, understand demand patterns and assess where opportunities exist. It also teaches that a business should respond to the needs of customers and the realities of the market. By understanding industry conditions, a learner can make better choices about the type of venture to start and the kind of value they can provide.\n\nEnvironmental scanning and market awareness are crucial for this process. Learners are encouraged to look at current conditions, competition, customer preferences and changes in the market so that the venture remains relevant. An entrepreneur who understands the industry can make more realistic plans and adapt more quickly when conditions change.\n\nThe lesson therefore connects business knowledge with commercial thinking: knowing the industry helps the entrepreneur make informed choices about products, pricing, delivery, and long-term sustainability."
    },
    {
        "title": "Identifying Market Opportunities",
        "duration": 12,
        "order": 4,
        "content": "Market opportunities arise when there is a gap between what customers need and what is currently available in the market. This lesson teaches learners to recognise business opportunities by observing customer problems, unmet needs, weaknesses in existing products or services, and changing trends. Seeing an opportunity requires curiosity, analysis and a willingness to look beyond what already exists.\n\nAn entrepreneur may identify an opportunity by listening to customer complaints, noticing common frustrations, or seeing a pattern in the behaviour of the market. A clear opportunity is not only a good idea; it is an idea that matches a genuine need and can be delivered in a practical and sustainable way. Learning to recognise opportunities is therefore an important part of business planning.\n\nThe lesson also highlights the importance of comparing likely demand with available resources. A good opportunity should be realistic, achievable and aligned with the entrepreneur's strengths and the local market. It should consider whether customers will buy, whether the price is right, and whether the venture can deliver consistently.\n\nThis practical way of thinking prepares learners to evaluate ideas before investing time and money. It helps them move from intuition to evidence-based business decisions."
    },
    {
        "title": "Innovation",
        "duration": 10,
        "order": 5,
        "content": "Innovation is the process of improving or creating a product, service, method or process in a way that adds value. A business that wants to stand out in a competitive market must often find ways to do things differently, more effectively or more conveniently. This lesson introduces learners to innovation as a way of solving practical problems and meeting customer needs in a creative way.\n\nInnovation does not always mean inventing something completely new. It can also mean improving an existing product, offering a better customer experience, simplifying a process, or adapting a service to a local market. In small businesses, innovation may be small but still valuable, especially when it improves efficiency or provides a better customer experience.\n\nThe lesson explains that customer demand, market gaps and business realities often create opportunities for innovation. Entrepreneurs who observe customer behaviour, compare competitors and think creatively are better able to design solutions that are practical and valuable. Innovation is therefore a tool for competitiveness, growth and sustainability.\n\nFor a new venture, innovation is not just about creativity; it is also about problem-solving and business usefulness. The most effective ideas are often those that solve a real problem in a simple, affordable and relevant way."
    },
    {
        "title": "Customer Service",
        "duration": 14,
        "order": 6,
        "content": "Customer service is essential to any venture because customers decide whether a business will succeed, grow and remain competitive. The lesson explains that a good customer experience builds trust, loyalty and repeat business. When customers feel respected, listened to and served well, they are more likely to return and recommend the business to others.\n\nGood customer service includes listening carefully, being polite, understanding customer needs and responding professionally. A small business that communicates clearly, solves problems quickly and treats people with respect is more likely to build strong relationships. Customer service is not only about selling a product; it is about creating a positive experience from first contact to after-sale support.\n\nThis lesson also shows that customer service affects reputation, word-of-mouth marketing and long-term viability. A business with poor service may lose customers even if the product is acceptable. By contrast, excellent service can strengthen loyal relationships and support long-term business sustainability.\n\nIn practice, entrepreneurs need to train staff, monitor service quality and continuously improve how customers are treated. This makes customer service part of the business strategy, not a separate afterthought."
    },
    {
        "title": "Financial and Cash Flow Management",
        "duration": 16,
        "order": 7,
        "content": "Financial management is one of the most important responsibilities of an entrepreneur. This lesson helps learners understand the flow of money into and out of a business, including income, expenses, debt, savings and cash available for daily operations. Cash flow is the money moving through the business and it must be managed carefully to keep the venture operational.\n\nA business can make sales and still struggle if it does not manage its cash flow well. Costs such as stock, rent, wages, utilities and supplies must be planned for in advance, and income must be monitored consistently. Learning to manage cash flow means knowing when money comes in, when it goes out and whether the business is able to cover its obligations.\n\nThe lesson introduces learners to simple financial planning concepts, including budgeting, forecasting and monitoring expenditure. It teaches that small businesses need clear decisions about spending, saving and pricing so that they can remain sustainable. Good financial management helps prevent shortfalls, supports growth and reduces the risk of business failure.\n\nThis topic underlines the importance of financial discipline for new ventures. Even a promising business can struggle if its owner does not understand cash flow and basic financial decisions."
    },
    {
        "title": "Basic Business Financial Statements",
        "duration": 16,
        "order": 8,
        "content": "Basic financial statements help a business understand its financial position and performance. These statements are tools used by owners, managers and stakeholders to review cash movement, profit, expenses and overall business health. The lesson introduces the main financial records that support informed decisions in a small venture.\n\nLearners are guided through the purpose of basic statements such as the income statement, cash flow statement and balance sheet. Each statement provides different information: one shows how much profit or loss was made over a period, another tracks money moving in and out of the business, and another reflects what the business owns and owes at a given point in time. These tools are essential for decision-making and planning.\n\nA sound understanding of financial statements helps an entrepreneur monitor business performance and identify problems early. For example, if expenses rise faster than income, the owner can take corrective action before the business becomes unsustainable. Similarly, cash flow statements make it easier to anticipate shortages and prepare for future obligations.\n\nBy learning to read and use basic business financial statements, entrepreneurs are better prepared to manage their venture with confidence and make informed business choices."
    },
    {
        "title": "Pricing of Goods and Services",
        "duration": 14,
        "order": 9,
        "content": "Pricing is a vital part of a business strategy because it affects profitability, customer perception and competitiveness. The lesson explains that the selling price of a product or service must reflect more than just the cost of producing it; it should also consider the value delivered to the customer, the target market and the competitive environment. A price that is too low may damage profitability, while a price that is too high may reduce demand.\n\nThe lesson introduces practical pricing methods such as cost-plus pricing, competitor-based pricing and value-based pricing. Learners are encouraged to calculate costs carefully, include overheads where relevant, and consider which price would be sustainable and still attractive to customers. Pricing decisions also influence marketing, sales and customer loyalty.\n\nThe ability to set an appropriate price is essential for a small business because it supports cash flow, revenue generation and business continuity. Entrepreneurs must decide whether they are trying to compete on affordability, quality, convenience or premium value, and their pricing approach should support that strategy.\n\nThis lesson highlights that pricing is not a one-time decision; it should be reviewed regularly as costs, market conditions and customer expectations change."
    },
    {
        "title": "Marketing",
        "duration": 16,
        "order": 10,
        "content": "Marketing is the process of understanding customer needs and communicating the value of a product or service in a way that encourages demand. For a new venture, marketing helps create awareness, build trust and attract customers. This lesson explains that marketing is not only advertising; it also includes understanding the market, choosing the right message, and communicating effectively with the target audience.\n\nThe learning focus includes promotion, customer engagement, sales communication and the use of available channels such as social media, community networks and local word-of-mouth. A business may need to use a mix of tools to reach the right customers. The success of a marketing plan depends on knowing who the customer is, what they want and where they are likely to respond.\n\nThis lesson also emphasises that businesses must market in a way that is honest, clear and relevant. A strong marketing message helps the customer understand the value of the offering and why it is useful. In a small business, marketing often relies heavily on relationships, trust and consistent communication.\n\nMarketing is therefore a core business function that supports sales, growth and sustainability. It helps the entrepreneur convert opportunity into demand and demand into income."
    },
    {
        "title": "SMART Goals",
        "duration": 10,
        "order": 11,
        "content": "Planning is essential for any business, and clear goals help an entrepreneur focus effort and measure progress. The lesson introduces SMART goals, which are goals that are Specific, Measurable, Achievable, Relevant and Time-bound. These criteria make it easier to turn a general intention into a practical plan that can be followed and reviewed.\n\nWhen goals are vague, they are difficult to act on and difficult to evaluate. SMART goals help the entrepreneur define what success looks like, how it will be measured, and by when it should be achieved. A simple, realistic goal is easier to implement than a broad ambition.\n\nThis lesson shows that planning is connected to execution. A good business plan includes realistic targets related to sales, costs, customer acquisition, service quality and growth. SMART goals provide a framework for managing operations and setting priorities so that the entrepreneur works consistently toward the venture's objectives.\n\nBy using clear goals, a learner can monitor progress, identify delays or weaknesses and make better decisions over time. This improves accountability and makes business planning more effective."
    },
    {
        "title": "Business Planning",
        "duration": 18,
        "order": 12,
        "content": "Business planning is the process of deciding how a venture will operate, what it will offer, how it will reach customers and how it will sustain itself. A basic business plan helps the entrepreneur clarify the idea, define costs, set objectives and assess whether the venture is realistic. It is a practical document that supports decision-making and helps the entrepreneur organise their thinking.\n\nThis lesson teaches that a business plan should cover key issues such as the business idea, customer needs, operations, pricing, marketing, staffing, and financial requirements. Even a simple business plan is useful because it creates structure and helps the owner identify risks early. Without planning, a venture may be built on assumptions rather than evidence.\n\nThe planning process also helps the entrepreneur decide what resources are required and how they will be used. This may include start-up capital, equipment, materials, labour, time, and marketing activity. Clear planning supports resource management and helps reduce the likelihood of avoidable mistakes.\n\nBy the end of this lesson, learners should understand that a business plan is a practical management tool. It helps translate an idea into action, supports ongoing decision-making and creates a foundation for growth and sustainability."
    },
    {
        "title": "Calculations and Pricing",
        "duration": 10,
        "order": 13,
        "content": "This practical lesson focuses on using calculations to support pricing decisions and basic business operations. Entrepreneurs must be able to estimate costs, understand mark-up, set selling prices and assess whether a business activity is financially viable. Good calculation skills help the owner avoid under-pricing and ensure that the venture remains sustainable.\n\nLearners are expected to work with simple cost calculations such as total cost, unit cost, selling price and profit. These calculations can be used to compare different options, test assumptions and support decisions about what to sell and at what price. The lesson makes it clear that financial decision-making is a daily business skill, not only an accounting function.\n\nThe ability to calculate accurately is also important for sales planning and cash management. A small business needs to know whether a product or service covers its costs and contributes to profit. This helps the entrepreneur judge whether a venture is viable in practice and whether it can support growth or ongoing operations.\n\nThe lesson therefore links mathematics with entrepreneurship by showing that price-setting and financial planning are practical tasks that require careful calculation and sound judgement."
    },
    {
        "title": "Basic Bookkeeping",
        "duration": 12,
        "order": 14,
        "content": "Basic bookkeeping is the process of recording and organising the money-related transactions of a business. These records help the entrepreneur track income, expenses, assets and liabilities, and they make it easier to understand the business's financial status over time. Effective bookkeeping supports planning, control and accountability.\n\nThis practical lesson covers the importance of maintaining simple books, recording sales and expenses, and keeping financial records orderly. A clear record of transactions helps owners monitor cash flow, identify trends, prepare for taxes or obligations, and make informed decisions. In small businesses, this discipline often determines whether the owner has reliable information for action.\n\nBookkeeping is not only a compliance task; it is also a business management tool. When records are accurate and up to date, the entrepreneur can see which activities are profitable, which costs are rising and where money is being lost. This improves the ability to control the venture and to plan for future growth.\n\nThe lesson reinforces that consistent record-keeping underpins good financial management and gives the business a stronger foundation for operation and decision-making."
    },
    {
        "title": "Marketing Project",
        "duration": 12,
        "order": 15,
        "content": "The marketing project allows learners to apply the principles of marketing in a practical way. This may involve planning a simple marketing campaign, identifying a target customer, choosing a message, and deciding how to communicate the value of the product or service. The purpose is to turn theory into a real business activity that demonstrates understanding of the market.\n\nA practical marketing project helps the learner practise customer analysis, promotional planning and communication. It may include identifying the business offering, research into the target audience, selection of channels and a basic strategy for attracting customers. This creates a realistic business learning experience and develops confidence in marketing decisions.\n\nThe lesson highlights that learners need to test assumptions about customer demand and communication. A marketing plan should be grounded in actual customer needs and the realities of the market. It should make clear how the offer will be communicated and why customers would choose it.\n\nThis project-based learning style builds practical competence and helps the learner understand that marketing must be planned, measured and adjusted over time."
    },
    {
        "title": "Customer Service (Practical)",
        "duration": 10,
        "order": 16,
        "content": "This practical lesson focuses on applying customer service skills in a real business context. Learners practise how to greet customers, listen to their needs, respond professionally, handle objections and resolve concerns in a respectful way. These are essential activities in any small business because service quality strongly affects customer retention and reputation.\n\nThis lesson shows that customer service is not only a mindset but also a set of actions. Responding promptly, showing interest, using courteous communication, and solving small problems effectively all contribute to a positive customer experience. A business benefits when staff are trained to behave consistently and professionally.\n\nThe practical component helps learners put theory into action by role-playing scenarios, responding to customer needs and evaluating whether the service met expectations. This builds communication confidence, professionalism and the ability to think on one's feet in a customer-facing environment.\n\nThe lesson therefore connects service quality to customer loyalty and business sustainability. Good customer service helps the venture retain customers, strengthen its reputation and improve its commercial performance."
    },
]

LESSON_MODULES = {
    "Being an Entrepreneur": [
        {
            "title": "Sole Trader",
            "content": "A sole trader is a business owned and managed by one person. The owner controls the venture, takes on the risks and receives the rewards. This form of business is common for small enterprises because it is simple to establish and allows direct decision-making."
        },
        {
            "title": "Partnership",
            "content": "A partnership is formed when two or more people share ownership and responsibility for the business. Partners contribute capital, skills or labour and share the risks and benefits of the venture. Clear agreements are important to avoid conflict and to define responsibilities."
        },
        {
            "title": "Company",
            "content": "A company is a separate legal entity from its owners. This structure allows the business to continue operating even if ownership changes. A company can be more formal in structure and may have greater compliance requirements than a sole trader or a partnership."
        },
        {
            "title": "Legal Registrations",
            "content": "Legal registration is a part of formalising the business. Depending on the chosen structure, a venture may need to register with the relevant authority and meet legal requirements before trading. Proper registration supports compliance and builds professionalism."
        },
    ],
    "Know Yourself": [
        {
            "title": "Self-Assessment",
            "content": "Self-assessment helps the learner identify strengths, weaknesses, opportunities and obstacles. By reflecting on skills, work habits and personal qualities, the learner can make realistic decisions about business readiness."
        },
        {
            "title": "Personal SWOT",
            "content": "A personal SWOT analysis helps the entrepreneur evaluate internal strengths and weaknesses as well as external opportunities and threats. This reflection is useful when deciding on a business idea or a development path."
        },
        {
            "title": "Purpose, Values and Vision",
            "content": "Purpose and values give the business direction. Learners should think about why they want to start the venture, what they believe in and what kind of impact they want to create. This gives the idea shape and meaning."
        },
    ],
    "Know Your Industry": [
        {
            "title": "Industry Awareness",
            "content": "Industry awareness means understanding the market, the players, and the conditions under which a business must operate. This helps the entrepreneur make better decisions about entry, growth and risk."
        },
        {
            "title": "Customer Needs",
            "content": "A business must understand what customers need, how they behave and what influences their purchasing decisions. Customer insight is a key foundation for correctly positioning a product or service."
        },
        {
            "title": "Market Trends",
            "content": "Market trends provide information about changes in demand, customer preferences and competitor activity. Tracking trends helps the entrepreneur adjust products, pricing and communication in a timely way."
        },
    ],
    "Identifying Market Opportunities": [
        {
            "title": "Customer Problems",
            "content": "Many business opportunities begin with identifying a recurring problem or frustration experienced by customers. Entrepreneurs should observe pain points and look for ways to improve the experience or solve the issue."
        },
        {
            "title": "Gap Analysis",
            "content": "Gap analysis helps compare what customers want with what is currently available. Where a clear mismatch exists, there may be a viable business opportunity."
        },
        {
            "title": "Feasibility Check",
            "content": "An opportunity must be realistic to pursue. Entrepreneurs should consider whether the need is genuine, whether resources are available, and whether the venture can offer a practical solution."
        },
    ],
    "Innovation": [
        {
            "title": "Improving Existing Solutions",
            "content": "Innovation can involve improving an existing product or process rather than inventing something entirely new. Small changes in service quality, convenience or efficiency can create meaningful value."
        },
        {
            "title": "Problem Solving",
            "content": "Innovation is often the result of applying creative thinking to a real problem. The best solutions are useful, practical and relevant to the customer."
        },
    ],
    "Customer Service": [
        {
            "title": "Listening and Response",
            "content": "Listening carefully to customer needs is a core part of strong service. A business benefits when staff respond with empathy, clarity and professionalism."
        },
        {
            "title": "Loyalty and Reputation",
            "content": "Good customer service supports repeat business and word-of-mouth promotion. It helps build trust and develops a reputation that supports long-term sustainability."
        },
    ],
    "Financial and Cash Flow Management": [
        {
            "title": "Income and Expenses",
            "content": "Understanding sales income and business expenses is essential to cash flow management. The entrepreneur must know what money is coming in and what must be paid out."
        },
        {
            "title": "Budgeting and Forecasting",
            "content": "Budgeting and forecasting help the business prepare for future cash needs. These planning tools reduce the risk of shortages and improve financial control."
        },
        {
            "title": "Cash Flow Control",
            "content": "Cash flow control means monitoring the movement of money and managing it deliberately. This supports daily operations and helps prevent financial stress."
        },
    ],
    "Basic Business Financial Statements": [
        {
            "title": "Income Statement",
            "content": "The income statement summarises revenue and expenses to show whether the business made a profit or a loss during a period. It helps the entrepreneur assess performance."
        },
        {
            "title": "Cash Flow Statement",
            "content": "The cash flow statement tracks money moving into and out of the business. It is important for understanding liquidity and day-to-day operations."
        },
        {
            "title": "Balance Sheet",
            "content": "The balance sheet reflects what the business owns and owes at a point in time. It supports a stronger understanding of the financial position of the venture."
        },
    ],
    "Pricing of Goods and Services": [
        {
            "title": "Cost-Based Pricing",
            "content": "Cost-based pricing starts with the cost of producing or delivering the good or service and then adds a margin. This helps ensure the price covers expenses and supports profit."
        },
        {
            "title": "Market-Based Pricing",
            "content": "Market-based pricing responds to what customers are prepared to pay and what competitors charge. This helps the entrepreneur stay competitive while protecting profitability."
        },
    ],
    "Marketing": [
        {
            "title": "Target Market",
            "content": "A target market is the group of people most likely to buy the product or service. Identifying the right customer segment improves the effectiveness of marketing messages."
        },
        {
            "title": "Communication Channels",
            "content": "Different channels such as social media, local networks and direct communication can be used to reach customers. Choosing the right channel helps the entrepreneur promote effectively."
        },
        {
            "title": "Sales Messaging",
            "content": "Messaging explains the value of the offering in a clear and relevant way. Good marketing communication helps people understand what they gain by buying from the business."
        },
    ],
    "SMART Goals": [
        {
            "title": "Specific and Measurable",
            "content": "Specific goals define exactly what is to be achieved, while measurable goals show how success will be tracked. Together, they create clarity and accountability."
        },
        {
            "title": "Achievable and Time-Bound",
            "content": "Goals should be realistic and linked to a time frame. This helps the entrepreneur focus effort and review progress in a practical way."
        },
    ],
    "Business Planning": [
        {
            "title": "Idea and Market Fit",
            "content": "A business plan begins by clarifying the offer and the needs it serves. The entrepreneur should explain who the customer is and why the venture is relevant."
        },
        {
            "title": "Operations and Resources",
            "content": "The plan should also describe how the business will operate, what resources are needed and how they will be managed. This includes staffing, equipment, materials and time."
        },
        {
            "title": "Financial Planning",
            "content": "Financial planning connects the business idea to practical feasibility. It helps the entrepreneur estimate costs, revenue and sustainability before committing to operations."
        },
    ],
    "Calculations and Pricing": [
        {
            "title": "Cost Calculations",
            "content": "Cost calculations help the entrepreneur understand the amount required to produce or deliver a product or service. This forms the basis for realistic pricing decisions."
        },
        {
            "title": "Profit and Margin",
            "content": "Profit and margin calculations show whether the business is generating enough return to remain sustainable. This is a critical part of commercial thinking."
        },
    ],
    "Basic Bookkeeping": [
        {
            "title": "Record Keeping",
            "content": "Accurate record keeping ensures that each financial transaction is captured and tracked consistently. This allows the business to monitor performance and reduce error."
        },
        {
            "title": "Expenses and Sales",
            "content": "Tracking expenses and sales helps the entrepreneur understand whether the business is making progress and where money is being used. These records support planning and control."
        },
    ],
    "Marketing Project": [
        {
            "title": "Campaign Planning",
            "content": "A marketing project requires a clear plan for reaching and engaging customers. This includes deciding the message, audience and channels to use."
        },
        {
            "title": "Evaluation",
            "content": "Marketing should be reviewed after action is taken so the entrepreneur can learn what worked, what did not, and what should be improved next time."
        },
    ],
    "Customer Service (Practical)": [
        {
            "title": "Greeting and Listening",
            "content": "Professional customer service begins with greeting customers respectfully and listening carefully to their needs. This helps the business respond with confidence and relevance."
        },
        {
            "title": "Problem Resolution",
            "content": "A practical service interaction often involves resolving a complaint or concern. A calm, respectful response helps build trust and preserve the relationship."
        },
    ],
}

ELO_MODULES = [
    {
        "title": "Gather and analyse information for an industry",
        "module_type": "knowledge",
        "short_title": "Gather and analyse information",
        "description": "Gather and analyse information for an industry. Learners must use relevant sources to understand market conditions, customer needs and business opportunities before acting."
    },
    {
        "title": "Determine market requirements relevant for marketing and selling goods and services",
        "module_type": "knowledge",
        "short_title": "Determine market requirements",
        "description": "Determine market requirements relevant for marketing and selling goods and services. Learners must identify customer needs, target markets and value propositions for goods or services."
    },
    {
        "title": "Determine financial, human and infrastructure requirements",
        "module_type": "knowledge",
        "short_title": "Determine resource requirements",
        "description": "Determine financial, human and infrastructure requirements. Learners must analyse the resources needed to operate a small enterprise effectively."
    },
    {
        "title": "Manage financial, human and infrastructure resources of a business",
        "module_type": "practical",
        "short_title": "Manage business resources",
        "description": "Manage financial, human and infrastructure resources of a business. Learners must allocate and control resources to support efficient operations and sustainability."
    },
    {
        "title": "Plan for the establishment of business",
        "module_type": "practical",
        "short_title": "Plan for establishment",
        "description": "Plan for the establishment of business. Learners must organise the steps required to launch a viable venture and prepare for its operation."
    },
    {
        "title": "Organise and conduct business activities",
        "module_type": "practical",
        "short_title": "Organise business activities",
        "description": "Organise and conduct business activities. Learners must coordinate operations, customer activity and day-to-day business functions in a structured way."
    },
]

CHECKLIST_SAMPLES = {
    "Gather and analyse information for an industry": [
        "Identifies relevant industry data sources",
        "Collects information systematically",
        "Analyses information to draw conclusions",
        "Records findings clearly for decision-making",
        "Links information to business opportunity selection",
    ],
    "Determine market requirements relevant for marketing and selling goods and services": [
        "Identifies target customers for a product or service",
        "Determines market needs and buying behaviour",
        "Analyses customer demand and preferences",
        "Matches a product or service to customer requirements",
        "Describes how to market effectively to the target market",
    ],
    "Determine financial, human and infrastructure requirements": [
        "Identifies financial resources required to start or run a business",
        "Considers labour and skills needed for the venture",
        "Assesses infrastructure and equipment needs",
        "Links resource requirements to business operations",
        "Explains the implications of resource planning for sustainability",
    ],
    "Manage financial, human and infrastructure resources of a business": [
        "Allocates funds according to operational needs",
        "Monitors expenditure against planned budgets",
        "Coordinates human resources effectively",
        "Maintains workplace and operational infrastructure",
        "Uses resources to support business continuity",
    ],
    "Plan for the establishment of business": [
        "Develops a basic business plan or launch approach",
        "Identifies required actions before opening the venture",
        "Plans resources, tasks and responsibilities",
        "Sets realistic objectives for the start-up stage",
        "Explains readiness for business establishment",
    ],
    "Organise and conduct business activities": [
        "Organises work tasks and daily business activities",
        "Coordinates customer or service activities effectively",
        "Implements operational plans in a structured way",
        "Monitors day-to-day business performance",
        "Adjusts tasks or activities to improve outcomes",
    ],
}


class Command(BaseCommand):
    help = "Seed the New Venture Creation skills programme into the LMS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be created without writing to the database.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete the existing course and dependent records before reseeding.",
        )
        parser.add_argument(
            "--instructor",
            help="Assign the course to a specific instructor username.",
        )
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Skip confirmation prompts for destructive actions.",
        )

    def _resolve_instructor(self, username=None):
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist as exc:
                raise CommandError(f"Instructor '{username}' does not exist. Create the account or pass a valid --instructor value.") from exc

        instructor = User.objects.filter(role='admin', is_approved=True).order_by('id').first()
        if not instructor:
            raise CommandError("No approved admin user exists. Create an admin account or pass --instructor <username>.")
        return instructor

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run: no changes will be written to the database."))
            self.stdout.write(f"Would create: 1 course, 16 lessons, {sum(len(v) for v in LESSON_MODULES.values())} modules, 6 learning modules, {sum(len(v) for v in CHECKLIST_SAMPLES.values())} checklist items, 6 FISA assessments")
            self.stdout.write(f"Course: {COURSE_TITLE}")
            return

        instructor = self._resolve_instructor(options.get("instructor"))
        self.stdout.write(f"Using instructor: {instructor.username}")

        existing_course = Course.objects.filter(slug=COURSE_SLUG).first()
        if options["reset"] and existing_course:
            if not options["noinput"] and not self.confirm(
                "Delete the existing New Venture Creation course and all cascaded dependent records and reseed it?",
                default=False,
            ):
                raise CommandError("Reset cancelled.")
            self.stdout.write("Deleting existing New Venture Creation course...")
            existing_course.delete()

        course_exists = Course.objects.filter(slug=COURSE_SLUG).exists()
        has_all_lessons = Lesson.objects.filter(course__slug=COURSE_SLUG).count() == len(LESSONS)
        has_all_modules = LessonModule.objects.filter(lesson__course__slug=COURSE_SLUG).count() == sum(len(v) for v in LESSON_MODULES.values())
        has_all_learning_modules = LearningModule.objects.filter(course__slug=COURSE_SLUG).count() == len(ELO_MODULES)
        has_all_checklists = ObservationChecklistItem.objects.filter(module__course__slug=COURSE_SLUG).count() == sum(len(v) for v in CHECKLIST_SAMPLES.values())
        has_all_assessments = SummativeAssessment.objects.filter(course__slug=COURSE_SLUG).count() == len(ELO_MODULES)

        if course_exists and has_all_lessons and has_all_modules and has_all_learning_modules and has_all_checklists and has_all_assessments:
            self.stdout.write(self.style.WARNING("Everything already exists; no new records were created."))
            return

        try:
            with transaction.atomic():
                course, course_created = Course.objects.update_or_create(
                    slug=COURSE_SLUG,
                    defaults={
                        "title": COURSE_TITLE,
                        "description": COURSE_DESCRIPTION,
                        "instructor": instructor,
                        "level": "beginner",
                        "price": 0,
                        "status": "published",
                    },
                )

                if course_created:
                    self.stdout.write("Creating course...")
                else:
                    self.stdout.write("Course already exists; updating metadata...")
                course.instructor = instructor
                course.title = COURSE_TITLE
                course.description = COURSE_DESCRIPTION
                course.level = "beginner"
                course.price = 0
                course.status = "published"
                course.save()

                created_records = 0
                lesson_count = len(LESSONS)
                for index, lesson_data in enumerate(LESSONS, start=1):
                    self.stdout.write(f"Creating lesson {index}/{lesson_count}: {lesson_data['title']}")
                    lesson, lesson_created = Lesson.objects.update_or_create(
                        course=course,
                        title=lesson_data["title"],
                        defaults={
                            "content": lesson_data["content"],
                            "duration": lesson_data["duration"],
                            "order": lesson_data["order"],
                        },
                    )
                    if lesson_created:
                        created_records += 1

                    modules = LESSON_MODULES.get(lesson_data["title"], [])
                    self.stdout.write(f"Creating {len(modules)} modules for lesson {index}")
                    for module_index, module_data in enumerate(modules, start=1):
                        module, module_created = LessonModule.objects.update_or_create(
                            lesson=lesson,
                            title=module_data["title"],
                            defaults={
                                "content": module_data["content"],
                                "content_type": "text",
                                "points": 10,
                                "time_estimate": 30,
                                "order": module_index,
                            },
                        )
                        if module_created:
                            created_records += 1

                self.stdout.write("Creating 6 learning modules...")
                for elo_index, elo in enumerate(ELO_MODULES, start=1):
                    learning_module, learning_created = LearningModule.objects.update_or_create(
                        course=course,
                        title=elo["title"],
                        defaults={
                            "description": elo["description"],
                            "order": elo_index,
                            "module_type": elo["module_type"],
                            "is_visible": True,
                        },
                    )
                    if learning_created:
                        created_records += 1

                    checklist_items = CHECKLIST_SAMPLES.get(elo["title"], [])
                    self.stdout.write(f"Creating {len(checklist_items)} checklist items for ELO {elo_index}")
                    for item_index, item_description in enumerate(checklist_items, start=1):
                        item, item_created = ObservationChecklistItem.objects.update_or_create(
                            module=learning_module,
                            description=item_description,
                            defaults={"order": item_index},
                        )
                        if item_created:
                            created_records += 1

                self.stdout.write("Creating 6 FISA assessments...")
                assessment_due_date = timezone.now() + timedelta(days=90)
                for elo_index, elo in enumerate(ELO_MODULES, start=1):
                    assessment_title = f"FISA: ELO {elo_index} — {elo['short_title']}"
                    instructions = (
                        f"{elo['description']} "
                        "The learner must submit evidence in their Portfolio of Evidence. "
                        "Prepare evidence showing the relevant work and reflection for this outcome."
                    )
                    assessment, assessment_created = SummativeAssessment.objects.update_or_create(
                        course=course,
                        title=assessment_title,
                        defaults={
                            "instructions": instructions,
                            "due_date": assessment_due_date,
                            "created_by": instructor,
                        },
                    )
                    if assessment_created:
                        created_records += 1

                total_lessons = Lesson.objects.filter(course=course).count()
                total_modules = LessonModule.objects.filter(lesson__course=course).count()
                total_learning_modules = LearningModule.objects.filter(course=course).count()
                total_checklist_items = ObservationChecklistItem.objects.filter(module__course=course).count()
                total_fisa = SummativeAssessment.objects.filter(course=course).count()

                if created_records == 0:
                    self.stdout.write(self.style.WARNING("Everything already exists; no new records were created."))
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: 1 course, {total_lessons} lessons, {total_modules} modules, "
                        f"{total_learning_modules} learning modules, {total_checklist_items} checklist items, "
                        f"{total_fisa} FISA assessments"
                    )
                )

        except Exception as exc:  # pragma: no cover - transaction rollback path
            self.stderr.write(f"Error while seeding New Venture Creation course: {exc}")
            raise
