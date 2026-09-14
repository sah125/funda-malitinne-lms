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

COURSE_TITLE = "Occupational Certificate: Small Business Consultant (SP-242101)"
COURSE_SLUG = "small-business-consultant-sp-242101"
COURSE_DESCRIPTION = """Occupational Certificate: Small Business Consultant (SP-242101) is designed to prepare learners to consult, advise and support businesses in developing and improving sustainable ventures. This qualification is intended for school leavers, employed individuals and emerging entrepreneurs who want to contribute to small business growth, resilience and compliance. It equips learners with the practical and theoretical understanding needed to guide business owners, assess opportunities, and support business development in a structured environment.

The curriculum targets those who may work as business consultants, business advisors, business analysts, risk and compliance consultants, and other business support roles in small and medium enterprise support environments. The programme is aligned to NQF Level 5 and supports progression into business support, advisory, and management roles. It is designed to build the capability needed to assess performance, advise on planning and implementation, and support sustainable enterprise development.

This programme has a total of 242 credits and a curriculum code of 242101-000-00-00. It is designed to support the professional development of learners who can work as small business support professionals across a range of environments. The qualification articulates with related learning pathways and aligns with the broader QCTO occupational framework, including ID 63769, 49419, 58341, 59201, and 48874. Learners are expected to develop both business insight and practical competence in advising and supporting business growth.

The curriculum is built around a structured learning model that integrates knowledge, practical skill application and workplace experience. Entry is at NQF Level 4 with Numeracy and Communications, and the learning programme is organised according to 242 credits of total learning time: Theory 91 credits (Knowledge Modules), Practical 55 credits (Practical Skills Modules), and Work Experience 96 credits (Work Experience Modules). It is intended to prepare learners for the demands of professional business consulting and small enterprise support within the South African operating context."""


def lesson_duration_for_credits(credits):
    return max(2, int(round((credits * 10) / 32)))


LESSONS = [
    {
        "curriculum_code": "KM-01",
        "title": "Regulatory and legislative framework",
        "nqf": 5,
        "credits": 5,
        "order": 1,
        "content": "This knowledge module introduces the learner to the regulatory and legislative environment in which businesses operate. It emphasises that business activities must comply with legal requirements related to employment, labour, taxation, business registration, safety and consumer protection. The purpose of the module is to establish the legal foundation for responsible business practice and to help the learner understand how regulations shape the operating environment of a small enterprise.\n\nThe module covers employment and labour legislation, including the Basic Conditions of Employment Act, labour relations issues, and the relationship between an employer and an employee. It also addresses broader business compliance matters such as skills development, B-BBEE, taxation, UIF, the Companies Act, competition regulation, POPIA, FICA, and workplace safety frameworks. These topics are important because a business consultant must be able to advise an entrepreneur on how to operate legally and responsibly.\n\nThe purpose of the module is therefore to build legal awareness and practical understanding. A learner who understands statutory obligations is better able to guide business owners toward lawful operations, more effective contracts, safer workplaces and stronger governance. This is essential for enterprise support and for reducing the risk of non-compliance in small and emerging businesses.\n\nThe module also helps learners connect legislative obligations to organisational decision-making. In practice, compliance is not only a legal requirement but also a management tool that supports business continuity, trust and efficient operations."
    },
    {
        "curriculum_code": "KM-02",
        "title": "Compliance audit",
        "nqf": 5,
        "credits": 5,
        "order": 2,
        "content": "The compliance audit module prepares the learner to examine organisational practices against relevant legal, policy and risk requirements. It focuses on how a business can be assessed for compliance, how weakness or non-conformance may affect operations, and how problems can be corrected. This is important because businesses often require external or internal review to ensure they are operating legally and efficiently.\n\nA compliance audit is concerned with checking whether systems, processes and actions align with required standards. In the context of small business support, this involves looking at labour practices, documentation, workplace conditions, financial controls, legal obligations and operational procedures. The learner is guided to understand both the purpose of the review and the indicators of poor compliance.\n\nThis module also highlights that compliance is not a once-off exercise. Business requirements change, legislation evolves, and organisations need to monitor their operations regularly. A consultant must therefore understand how to gather evidence, assess risk, and explain compliance gaps in a professional and practical way.\n\nThe module supports learners in becoming more critical and systematic in analysing business practice. It helps them identify areas where compliance is weak and recommend sensible corrective actions that are aligned to legal and organisational requirements."
    },
    {
        "curriculum_code": "KM-03",
        "title": "Fundamentals of entrepreneurial profiles",
        "nqf": 4,
        "credits": 4,
        "order": 3,
        "content": "This module introduces the learner to the traits, motivations and profiles associated with successful entrepreneurial activity. It recognises that business development and consulting are shaped by the personal capabilities of the business owner, founder or leader. The purpose is to help the learner understand how entrepreneurial behaviour, decision-making and personal characteristics influence business growth and performance.\n\nThe content supports understanding of entrepreneurial profiles, personal readiness, and the way individuals respond to opportunity, risk, uncertainty and change. Business consultants need to evaluate both the capacity of the owner and the demands of the environment when advising on business decisions. This means that an understanding of personal motivation, confidence, decision-making and learning orientation is relevant to business support.\n\nThe module therefore helps learners connect entrepreneurship to personal capability and business readiness. It provides a foundation for advising on business formation, growth planning, risk management and strategic action. By understanding entrepreneurial profiles, the consultant can identify strengths, constraints and support needs more clearly.\n\nThis content also positions the learner to assess the quality of entrepreneurial leadership and the factors that influence business sustainability. A business is not only shaped by context, but also by the behaviour and capability of the people driving it."
    },
    {
        "curriculum_code": "KM-04",
        "title": "Business consulting development",
        "nqf": 5,
        "credits": 5,
        "order": 4,
        "content": "The business consulting development module explores what it means to provide consulting support to a business owner or entrepreneur. It lays the foundation for understanding consulting as a professional service that guides decisions, assesses business conditions, and supports action. Through this module, the learner develops awareness of the role of the consultant as an advisor, analyst and support professional.\n\nIt addresses the process of consulting, including how a consultant identifies a client's needs, gathers information, analyses the business context, and presents practical recommendations. A business consultant does not simply offer opinions; they assess the situation, interpret relevant information, and help the client decide on a direction that is realistic, relevant and sustainable.\n\nThe module therefore links consulting practice to practical business improvement. It helps the learner understand the importance of listening, analysis, problem-solving and communication. These capabilities are central to successful business consulting and are essential when supporting entrepreneurs with planning, compliance and growth issues.\n\nThe module also introduces the learner to the professional behaviours expected of a consultant. These include objectivity, clarity, credibility and a strong understanding of the business environment. This gives the learner a grounded view of consulting as a disciplined support service rather than a purely advisory opinion."
    },
    {
        "curriculum_code": "KM-05",
        "title": "Strategic and operational plans",
        "nqf": 4,
        "credits": 5,
        "order": 5,
        "content": "Strategic and operational planning is a core capability in business support. This module introduces learners to the role of plans in guiding business direction and aligning daily activity with longer-term goals. A strategic plan provides a view of where the business is going, while an operational plan turns that direction into actions, responsibilities and timing.\n\nThe module emphasises that a business must be able to connect vision, goals and implementation. Consultants support this by helping owners to clarify objectives, identify priorities, and translate strategic intent into feasible operational steps. This process improves coordination, reduces confusion, and helps the business use resources more effectively.\n\nThe learner is introduced to the planning process as an integrated business tool. It includes assessing the internal and external environment, identifying goals, assigning responsibility, and monitoring progress. Without a clear plan, organisations can operate reactively rather than purposefully, which weakens performance and long-term sustainability.\n\nThis module therefore supports the consultant's role in helping businesses become more organised, focused and measurable. It builds the foundation for better decision-making and stronger implementation of business strategies."
    },
    {
        "curriculum_code": "KM-06",
        "title": "Professional business success factors",
        "nqf": 5,
        "credits": 5,
        "order": 6,
        "content": "This module looks at the factors that support professional success in a business environment. It considers how personal conduct, professional behaviour, communication, planning and consistency contribute to a business's ability to perform well and build trust. The module helps learners see that business success is supported by more than product or price; it is also shaped by professionalism and operational discipline.\n\nThe learner is guided to understand the importance of effectiveness, reliability, accountability and quality in business operations. In a consulting context, professional behaviour helps establish credibility and supports the quality of advice offered to a client. Business success is therefore not based only on market activity but also on how the enterprise is managed and represented.\n\nA strong business environment depends on leadership, process discipline and a clear understanding of responsibilities. The module therefore connects professional behaviour to sustainable performance and long-term trust with customers, employees and partners.\n\nThis content gives the learner a basis for helping small businesses create professional systems that improve service, reliability and long-term stability."
    },
    {
        "curriculum_code": "KM-07",
        "title": "Principles of marketing",
        "nqf": 5,
        "credits": 5,
        "order": 7,
        "content": "The principles of marketing module introduces the learner to the role of marketing in building customer awareness, supporting sales, and establishing business relevance in the market. It explains that marketing is not simply about advertising a product; it is about understanding customer needs, communicating value, and aligning the offer with the target market.\n\nThis module helps the learner understand the importance of product positioning, customer insight, market communication and value delivery. For a small business consultant, marketing knowledge is essential because it informs advice on customer engagement, brand clarity, sales strategy and market readiness.\n\nThe module emphasises that markets are shaped by demand, behaviour, competition and customer expectations. A business that understands its customers and communicates clearly is better placed to win trust and support growth. By building a strong understanding of marketing principles, the learner develops the ability to advise a business on how to attract and retain customers.\n\nThe learning focus is therefore on practical relevance: the learner should be able to explain how marketing decisions support sustainable business development and customer value delivery."
    },
    {
        "curriculum_code": "KM-08",
        "title": "Business finance",
        "nqf": 5,
        "credits": 5,
        "order": 8,
        "content": "This module introduces learners to the financial foundations necessary for managing and advising a business. It focuses on the role of finance in supporting business operations, planning and sustainability. Business finance is central to decision-making because an enterprise cannot function effectively without a sound understanding of income, costs, cash flow and resource allocation.\n\nThe learner is guided to understand that financial management involves more than bookkeeping. It includes planning, monitoring, resource allocation and identifying risks linked to capital, operating costs and growth. For a business consultant, financial understanding is essential because it supports advice on viability, stability and strategic decision-making.\n\nThis module gives context for examining how finance affects business performance, sustainability and decision-making under uncertainty. The learner is expected to connect financial knowledge to real business challenges such as cost control, sales planning and resource prioritisation.\n\nThe content therefore supports a practical understanding of how financial decisions shape the health and performance of a venture."
    },
    {
        "curriculum_code": "KM-09",
        "title": "Principles of costing and pricing to a business venture",
        "nqf": 4,
        "credits": 4,
        "order": 9,
        "content": "This module helps the learner understand the relationship between cost, price and profitability in a business venture. It introduces the concept that pricing must reflect the cost of producing or delivering a product or service while also matching the value expected by the market. For small businesses, pricing decisions are critical because they influence cash flow, competitiveness and viability.\n\nThe learner is introduced to cost structures, pricing logic and the importance of understanding both direct and indirect costs. A consultant must be able to help a business set prices that cover costs and support sustainable operation without alienating the market. This requires a practical understanding of value, cost and commercial context.\n\nThe module therefore connects financial thinking to decision-making in the market. It helps the learner understand why a business needs to examine costs, margins, customer affordability and strategic positioning before setting a selling price.\n\nThis content supports the learner in advising on more informed and commercially sound pricing decisions."
    },
    {
        "curriculum_code": "KM-10",
        "title": "Risk profiling",
        "nqf": 5,
        "credits": 5,
        "order": 10,
        "content": "Risk profiling is a core part of business consultancy because it helps identify the likelihood and impact of threats to business continuity. This module introduces the learner to the concept of risk analysis, including how risk may arise from internal weaknesses, external conditions or operational failure. A consultant must be able to recognise patterns of risk and help a business prioritise action.\n\nThe module covers the importance of identifying risk in terms of impact, likelihood and response. This may include issues such as financial risk, operational disruption, compliance failure, customer risk and strategic risk. The learner is guided to understand that risk management is not only about preventing problems; it is also about preparing for them and making better decisions under uncertainty.\n\nA strong risk profile supports better planning and more resilient business operations. This module therefore helps the learner connect risk analysis to practical business action, particularly when counselling owners on the sustainability and continuity of a venture.\n\nThe content reinforces that risk assessment is a practical management capability and a key part of business consulting support."
    },
    {
        "curriculum_code": "KM-11",
        "title": "Principles of tendering",
        "nqf": 5,
        "credits": 4,
        "order": 11,
        "content": "This module introduces learners to the principles of tendering as part of business opportunity and procurement activity. Tendering is a formal process used when an organisation seeks suppliers, contractors, or service providers. A business consultant may support a client in assessing the relevance, compliance and viability of tender opportunities.\n\nThe learner is introduced to the basic logic of tendering, including the need for accurate documentation, alignment to requirements, and proper evaluation of offers. Tendering is important because poor preparation or weak evaluation can lead to poor outcomes, financial exposure or non-compliance. The module therefore supports understanding of how formal proposals and contracting processes operate.\n\nThis content is relevant to business support because a consultant may need to advise on procurement, project participation or supplier selection. The learner should be able to connect tendering processes to commercial decisions and the broader goals of the enterprise.\n\nThe module provides a foundation for understanding how business opportunities are pursued and evaluated within a formal commercial framework."
    },
    {
        "curriculum_code": "KM-12",
        "title": "Business appraisal",
        "nqf": 5,
        "credits": 5,
        "order": 12,
        "content": "Business appraisal is the process of evaluating a business or enterprise to understand its performance and potential. This module introduces the learner to the reason for appraising a business, including the need to assess operations, resource use, performance, risks and opportunities. It emphasises that business decisions are stronger when supported by a clear understanding of the existing business position.\n\nThe learner is guided to understand how a business can be reviewed in terms of operational effectiveness, customer demand, financial performance and strategic direction. This helps the consultant identify strengths, weaknesses and likely development areas. A good appraisal supports advice that is grounded in evidence and tailored to the particular business context.\n\nThe module therefore supports the consultant’s role in evaluating a business before making recommendations. It helps the learner interpret business information systematically and move from observation to practical advice.\n\nBusiness appraisal is central to effective support because it provides a structured basis for growth planning, risk reduction and transformation of the enterprise."
    },
    {
        "curriculum_code": "KM-13",
        "title": "Business requirements and business rescue strategies",
        "nqf": 5,
        "credits": 4,
        "order": 13,
        "content": "This module focuses on understanding the requirements of a business and the circumstances under which rescue or restructuring may become necessary. It introduces the learner to the fact that organisations may experience distress, underperformance or operational challenges that require intervention. A consultant needs to understand the causes of business difficulty and the tools available to support recovery or restructuring.\n\nThe module addresses the practical importance of assessing operational, financial and strategic requirements before interventions are proposed. It also raises the need to determine whether a business should be restructured, supported, or repositioned to continue operations. This makes the subject relevant to sustainable enterprise support.\n\nA business rescue strategy must be realistic and grounded in the business's circumstances. The learner is therefore encouraged to understand the importance of evidence, analysis and planning before recommending a recovery path.\n\nThis content helps the learner appreciate the role of informed intervention in preserving business value and improving the chances of turnaround."
    },
    {
        "curriculum_code": "KM-14",
        "title": "Effective communication",
        "nqf": 5,
        "credits": 5,
        "order": 14,
        "content": "Effective communication is a cornerstone of business consulting and support. This module helps the learner understand how clear, respectful and purposeful communication improves business relationships, problem-solving and service delivery. In a consulting role, communication shapes how advice is received and how recommendations are implemented.\n\nThe learner is guided to understand that communication involves more than conveying information. It includes listening, interpretation, question-asking, feedback, and making information relevant to the audience. Consultants must be able to explain complex issues in ways that decision-makers can understand and act on.\n\nThis module also acknowledges that communication affects confidence, trust and organisation-wide coordination. A business that communicates clearly is better placed to manage relationships with customers, staff, partners and stakeholders.\n\nThe content therefore supports the learner in developing professional communication capability relevant to business support, strategic advising and client engagement."
    },
    {
        "curriculum_code": "KM-15",
        "title": "Principles of ethics in business",
        "nqf": 6,
        "credits": 3,
        "order": 15,
        "content": "This module introduces the learner to the importance of ethics in business and professional practice. Ethics supports honest behaviour, fairness, accountability and trust in business relationships. In a consulting environment, ethical conduct is critical because the consultant influences decisions that affect a business, its stakeholders and its future.\n\nThe content focuses on principles such as integrity, fairness, responsibility and respect. Learners are encouraged to understand that ethical business practice supports sustainable operations and improves confidence in business relationships. These values also guide how a consultant handles information, advice and decision support.\n\nThis module reinforces that a consultant must provide advice that is honest, responsible and aligned to the best interests of the business and its stakeholders. Business success is stronger when values, governance and conduct are aligned.\n\nThe module therefore supports the professional standards required for sound business support and responsible advice."
    },
    {
        "curriculum_code": "KM-16",
        "title": "Strategies for behaviour change and coaching",
        "nqf": 5,
        "credits": 3,
        "order": 16,
        "content": "This module focuses on behaviour change and coaching as practical tools for supporting business improvement. It recognises that businesses and entrepreneurs often need to change habits, routines, decision patterns or ways of working to improve performance. A consultant may therefore need to guide individuals toward new behaviours, clearer practices and better operational discipline.\n\nThe learner is introduced to the importance of coaching in helping people understand their role, choose improvements, and apply new practices consistently. Coaching is not only about instruction; it is about guiding reflection, accountability and gradual change. This helps the business owner or team move from intention to action.\n\nThe module emphasises that behaviour change is easier when it is purposeful, structured and supported. A consultant who can guide reflection and practical improvement helps the business become more effective and sustainable over time.\n\nThe content therefore connects business development with individual growth and organisational learning."
    },
    {
        "curriculum_code": "KM-17",
        "title": "Principles of change management",
        "nqf": 5,
        "credits": 5,
        "order": 17,
        "content": "This module introduces learners to the nature of change within organisations and the role of structured management in supporting successful transitions. Change may involve new systems, revised processes, new goals, or shifts in business direction. In a consulting role, the learner must understand how to support a business through change without raising avoidable confusion or disruption.\n\nThe module emphasises that change requires planning, communication and support. Businesses that manage transitions poorly often face resistance, confusion and weak implementation. A consultant therefore needs a clear understanding of how to guide an organisation through change in a structured and realistic way.\n\nThis content supports the learner in understanding how change initiatives can be designed, communicated and monitored to improve chances of success. It reinforces the connection between operational planning and long-term business development.\n\nThe module therefore contributes to the business consultant's capacity to support sustainable change and improved performance."
    },
    {
        "curriculum_code": "KM-18",
        "title": "Introductory studies for project managers",
        "nqf": 5,
        "credits": 5,
        "order": 18,
        "content": "This module introduces the learner to the basic principles of project management and their relevance to business support and consulting. It positions project management as a structured way to plan, organise and deliver work within defined objectives, timeframes and resources. A consultant often supports businesses that need to implement new initiatives, improvements or projects.\n\nThe learner is introduced to the value of project thinking, including planning, risk consideration, coordination and review. A project approach helps businesses move from ideas to action in a controlled and accountable way. This is particularly useful in small enterprises that need to implement improvements on limited capacity.\n\nThe module therefore connects business decision-making with practical project structure. It provides a foundation for understanding how objectives are set, tasks are controlled, and outcomes are tracked.\n\nThis is relevant because consultants often work at the intersection of business strategy, implementation and operational performance."
    },
    {
        "curriculum_code": "KM-19",
        "title": "Application of contract documentation",
        "nqf": 5,
        "credits": 4,
        "order": 19,
        "content": "This module introduces the learner to the role of contract documentation in business operations and consulting support. Contracts are a formal mechanism for setting out responsibilities, obligations, deliverables and terms of engagement. A business consultant needs a practical understanding of contract documentation because it underpins service delivery, customer commitments and compliance.\n\nThe learner is guided to understand how documents communicate expectations, define roles, and provide legal clarity. Properly prepared documentation supports accountability and reduces the risk of misunderstanding in business relationships. This is essential for small business support and consulting services.\n\nThe module therefore connects business practice with formal documentation. It supports the understanding that contracts and agreement documents are not merely administrative paperwork; they are part of business governance and risk control.\n\nThis content helps the learner contribute to better planning and communication in business dealings."
    },
    {
        "curriculum_code": "KM-20",
        "title": "Evaluation of influences in value chain",
        "nqf": 5,
        "credits": 5,
        "order": 20,
        "content": "This module introduces the learner to the value chain concept and the factors that influence business efficiency and competitiveness. It recognises that business performance is affected by the interactions between suppliers, producers, service providers, customers and supporting infrastructure. A consultant needs to understand where value is created and where bottlenecks or weaknesses may arise.\n\nThe learner is guided to evaluate the ways in which value chain inputs, processes and outputs influence business performance. This supports more informed advice on efficiency, service quality, supplier relationships and process improvement. It is particularly relevant in small business settings, where operational constraints may be significant.\n\nThe module therefore supports a systematic understanding of how business activities connect to value creation. It helps the learner identify where efficiency can improve and where process, supply or service issues may affect sustainable performance.\n\nThis content makes the value chain concept accessible and relevant to business support and operational improvement."
    },
    {
        "curriculum_code": "PM-01",
        "title": "Evaluate personal capability for performing business consulting services",
        "nqf": 5,
        "credits": 8,
        "order": 21,
        "content": "This practical skill module focuses on the learner's personal capability to perform business consulting services. It emphasises self-assessment, professional readiness, and the ability to match consulting practice to client need. The learner is expected to assess their own skills, strengths and gaps before providing business support or advice.\n\nThe purpose of the module is to help the learner evaluate whether they are equipped to support businesses in a credible and useful way. This includes understanding the consulting role, recognising the boundaries of advice, and deciding when additional support or specialist input is required.\n\nPractical application is built around professional readiness and reflective judgement. The module helps the learner make an informed assessment of their ability to engage with business owners and support improvement in a disciplined and responsible manner.\n\nThis makes it an important foundation for all further consulting work."
    },
    {
        "curriculum_code": "PM-02",
        "title": "Carry out due diligence and check compliance with relevant legislation",
        "nqf": 6,
        "credits": 8,
        "order": 22,
        "content": "This practical skill module develops the learner's ability to perform due diligence and assess compliance with relevant legal requirements. It focuses on the systematic review of business records, controls, evidence and practices to determine whether obligations are being met. This is a core consulting task because accurate review informs advice and risk management.\n\nThe learner is expected to gather evidence, assess the current state of compliance, and identify gaps that require attention. This practical work is essential because consultants must base recommendations on facts and not assumptions.\n\nThe module therefore connects legal compliance to real organisational assessment. It requires the learner to think critically, document findings, and recommend practical corrective action where conditions are not compliant.\n\nThis supports the delivery of effective, evidence-based consulting services."
    },
    {
        "curriculum_code": "PM-03",
        "title": "Monitor methods of appraisal of business owner, business performance and activities",
        "nqf": 5,
        "credits": 8,
        "order": 23,
        "content": "This practical module focuses on the monitoring and appraisal of a business owner, business activities and organisational performance. It helps the learner assess how effectively the business is operating, where weaknesses exist, and how progress can be measured. This supports business improvement and guides practical recommendations.\n\nThe learner is encouraged to evaluate business indicators, organisational behaviour and operational activity in a structured manner. The purpose is to ensure that conclusions are evidence-based and linked to real performance data or observed practice.\n\nThe module therefore connects appraisal and monitoring to business decision-making. It helps the learner understand how to identify the key issues affecting performance and translate observation into useful guidance.\n\nThis is an important practical tool in consulting practice."
    },
    {
        "curriculum_code": "PM-04",
        "title": "Provide strategic and operational consulting service",
        "nqf": 6,
        "credits": 10,
        "order": 24,
        "content": "This practical module develops the learner's capacity to deliver strategic and operational advisory support to an enterprise. It focuses on helping a business define its direction, assess its operational model, and identify practical improvements. The learner is expected to provide advice that is relevant to both strategic planning and day-to-day business functioning.\n\nThe module highlights that consulting should support action, not just diagnosis. Recommendations should be realistic, practical and tied to the needs of the client. This makes the module essential for professional consulting practice in a small business environment.\n\nThe learner is therefore expected to apply analytical and communication skills in a way that supports business improvement. This makes the module central to the programme's practical assessment spine.\n\nThe purpose is to help the learner provide informed, structured support to a business owner or team."
    },
    {
        "curriculum_code": "PM-05",
        "title": "Develop and implement a change management framework",
        "nqf": 5,
        "credits": 5,
        "order": 25,
        "content": "This practical module develops the learner's ability to design and implement a change management framework for a business. It focuses on identifying the need for change, clarifying the approach to change, and supporting organisational transition in a planned way. This is important because businesses often need to adapt to new conditions, revised processes or improved operational practice.\n\nThe learner is expected to support the management of the change process by linking strategy, communication and operational action. This helps the organisation move from awareness to practical implementation without unnecessary disruption.\n\nThe module therefore connects change planning to real operational activity. It gives the learner a practical foundation for supporting improvements that are sustainable and manageable.\n\nThis content is particularly relevant to consultants working with small businesses facing growth, restructuring or process change."
    },
    {
        "curriculum_code": "PM-06",
        "title": "Develop project implementation approach",
        "nqf": 5,
        "credits": 8,
        "order": 26,
        "content": "This practical module introduces the learner to ways of developing a project implementation approach for a business initiative. It supports the learner in translating a plan into activities, responsibilities and delivery steps. The module emphasises that implementation should be structured and realistic if it is to improve business performance.\n\nThe learner is expected to connect strategy to execution by considering tasks, timeline, resources and accountability. This is essential in a consulting environment where support must move beyond recommendations to practical delivery.\n\nThe module therefore strengthens the learner's capacity to support implementation in a controlled and effective way. It helps them turn intentions into manageable steps and monitor the progression of business action.\n\nThis ensures that consulting support is realistic and useful to the client."
    },
    {
        "curriculum_code": "PM-07",
        "title": "Interpret the influences of key components in the value chain on business efficiency",
        "nqf": 5,
        "credits": 8,
        "order": 27,
        "content": "This practical module focuses on the learner's ability to interpret how different value chain components influence business efficiency. It helps the learner examine how suppliers, processes, service delivery and customer relationships affect operational effectiveness. The goal is to identify where value is created and where inefficiencies or constraints occur.\n\nThe module supports the application of analytical thinking to business systems. It helps the learner assess how internal and external components shape quality, speed, cost and customer value.\n\nThis is a practical skill because it requires the learner to apply the value chain concept to real business activity and provide recommendations for improvement.\n\nThe module therefore connects process analysis to business performance and sustainable improvement."
    },
    {
        "curriculum_code": "WM-01",
        "title": "Procedures to evaluate personal capability for performing business consulting services",
        "nqf": 5,
        "credits": 10,
        "order": 28,
        "content": "This work experience module provides the learner with an opportunity to apply the principles of self-evaluation and professional readiness in a practical workplace setting. The purpose is to assess whether the learner can perform business consulting activities in a way that reflects the expected professional standards.\n\nThe learner is expected to demonstrate capability, reflect on performance, and identify areas for further development. This is important because business consulting depends on credible, professional conduct and the ability to support real organisational needs.\n\n# TODO(compliance): expand with learner guide content for observed workplace application and reflective evidence practices."
    },
    {
        "curriculum_code": "WM-02",
        "title": "Processes and procedures for carrying out and checking due diligence compliance with relevant legislation",
        "nqf": 6,
        "credits": 15,
        "order": 29,
        "content": "This work experience module focuses on carrying out due diligence and checking compliance in a real business environment. The learner is expected to apply the relevant methods and procedures to assess whether legal and operational obligations are being met.\n\nThe purpose is to support practical understanding of compliance reviews and their value in improving business governance and risk control.\n\n# TODO(compliance): need a workplace evidence description for actual due diligence checks and corrective follow-up actions."
    },
    {
        "curriculum_code": "WM-03",
        "title": "Process to monitor methods of appraisal of business owner, business performance and activities",
        "nqf": 5,
        "credits": 15,
        "order": 30,
        "content": "This work experience module requires the learner to monitor and appraise business operations in the workplace. The learner is expected to use practical methods to assess performance, identify changes over time, and support evidence-based evaluation of the enterprise.\n\nThis helps the learner connect business appraisal to real operational experience and organisational improvement.\n\n# TODO(compliance): expand with learner-guide observation statements on appraisal methods and evidence collection."
    },
    {
        "curriculum_code": "WM-04",
        "title": "Procedures to provide strategic and operational consulting service",
        "nqf": 6,
        "credits": 20,
        "order": 31,
        "content": "This work experience module allows the learner to apply strategic and operational consulting support in a workplace context. The purpose is to demonstrate the learner's ability to advise, assess and contribute to business improvement in a practical setting.\n\nThe learner is expected to carry out the relevant methods and document the process of giving support in a way that reflects professional consulting behaviour.\n\n# TODO(compliance): expand with learner guide details for workplace client engagement and advisory evidence."
    },
    {
        "curriculum_code": "WM-05",
        "title": "Process to develop and implement a change management framework",
        "nqf": 5,
        "credits": 10,
        "order": 32,
        "content": "This work experience module supports the learner in applying change management approaches in a practical environment. The purpose is to demonstrate how a business can plan and implement a structured change process and monitor its effectiveness.\n\nThe learner is expected to contribute to real intervention, documentation and review activities to show how change can be managed responsibly.\n\n# TODO(compliance): expand with workplace evidence requirements for change interventions and stakeholder communication."
    },
    {
        "curriculum_code": "WM-06",
        "title": "Process and procedures to develop project implementation approach",
        "nqf": 5,
        "credits": 15,
        "order": 33,
        "content": "This work experience module gives the learner practical experience in developing and applying a project implementation approach within a workplace setting. The purpose is to show how a project can be structured, monitored and delivered in a realistic organisational environment.\n\nThe learner is expected to demonstrate the planning and oversight required to move a project from concept through implementation.\n\n# TODO(compliance): add detailed workplace guidance for project planning, coordination and evidence recording."
    },
    {
        "curriculum_code": "WM-07",
        "title": "Procedures to interpret the influences of key components in the value chain on business efficiency",
        "nqf": 5,
        "credits": 11,
        "order": 34,
        "content": "This work experience module focuses on how the learner interprets the influence of value chain components on business efficiency in a live working environment. The objective is to observe, assess and explain how business operations and relationships shape value creation and performance.\n\nThe learner is expected to apply practical analysis to identify weaknesses or opportunities within the value chain and to suggest realistic improvements.\n\n# TODO(compliance): expand with detailed workplace evidence examples for value-chain interpretation and recommendations."
    },
]


def lesson_groups_for_title(title):
    mapping = {
        "Regulatory and legislative framework": [
            ("Labour law fundamentals", "This section focuses on the legal obligations that govern the relationship between employers and employees, including employment status, working conditions and compliance responsibilities."),
            ("Workplace compliance and protection", "This grouping covers workplace protections, leave, overtime, and safety-related duties that must be organised in line with statutory obligations."),
            ("Business governance and statutory compliance", "This grouping looks at the wider compliance environment, including taxation, UIF, registration requirements, data protection, business structure and sector regulation."),
        ],
        "Compliance audit": [
            ("Audit purpose and evidence review", "The learner is guided to understand how a compliance audit begins with evidence gathering and the review of business records, documents and practices."),
            ("Risk and control review", "This section covers how compliance risks are identified, prioritised and linked to operational controls and organisational responsibilities."),
            ("Corrective action and reporting", "The learner learns how to report findings, explain gaps and identify corrective steps in a practical and professional way."),
        ],
        "Fundamentals of entrepreneurial profiles": [
            ("Personal readiness and motivation", "This area focuses on the interpersonal and behavioural traits that influence entrepreneurial decision-making and business ownership."),
            ("Opportunity and risk orientation", "This section examines how entrepreneurs respond to opportunity, uncertainty and change when creating or growing a venture."),
            ("Leadership and growth capability", "The learner is guided to consider how entrepreneurial capability influences planning, growth and organisational direction."),
        ],
        "Business consulting development": [
            ("Consulting role and purpose", "This grouping examines the role and responsibilities of a business consultant as an advisor, analyst and support professional."),
            ("Information gathering and diagnosis", "The learner is introduced to how information is collected and evaluated when supporting a business problem or opportunity."),
            ("Advisory practice and client engagement", "This section looks at professional communication, advice and the practical application of consulting support in a business context."),
        ],
        "Strategic and operational plans": [
            ("Strategic thinking", "This area focuses on how a business defines direction and sets long-term objectives in line with its market and resources."),
            ("Operational execution", "This section addresses the coordination of tasks, responsibilities and resources needed to turn plans into action."),
            ("Planning discipline and review", "The learner is guided to understand how progress is monitored, adjusted and aligned to goals over time."),
        ],
        "Professional business success factors": [
            ("Professional behaviour", "This grouping introduces the behaviours and standards that shape professional performance in business dealings."),
            ("Reliability and accountability", "The learner considers how trust, consistency and accountability support business growth and operational quality."),
            ("Quality and service culture", "This section looks at how business success depends on service quality, communication and disciplined work practice."),
        ],
        "Principles of marketing": [
            ("Customer insight and demand", "This section examines how understanding customer needs helps a business align its offer to real demand."),
            ("Positioning and communication", "This grouping explores how a business shapes its message, value proposition and customer engagement approach."),
            ("Sales and growth drivers", "The learner considers the role of marketing in supporting sales, retention and sustainable business performance."),
        ],
        "Business finance": [
            ("Financial principles", "This grouping introduces the role of income, expenditure, cash flow and capital in maintaining business viability."),
            ("Resource planning", "The learner is guided to understand how funds are allocated and monitored to support operational needs and growth."),
            ("Decision-making and sustainability", "This section looks at how financial knowledge informs business planning and long-term sustainability."),
        ],
        "Principles of costing and pricing to a business venture": [
            ("Cost structures", "The learner examines the direct and indirect costs that must be understood before pricing decisions are made."),
            ("Pricing logic", "This section focuses on value, affordability, margins and how revenue supports business viability."),
            ("Commercial decision-making", "The learner is guided to assess how pricing supports competitiveness and sustainable business operation."),
        ],
        "Risk profiling": [
            ("Risk identification", "This grouping outlines how threats to the business may be identified, assessed and prioritised."),
            ("Impact and response planning", "The learner studies how risk exposure affects planning and how businesses respond to uncertainty."),
            ("Resilience and continuity", "This section focuses on how risk management supports business continuity and strategic resilience."),
        ],
        "Principles of tendering": [
            ("Tender process overview", "This grouping looks at how formal opportunities are identified and structured in a procurement setting."),
            ("Documentation and compliance", "The learner examines the records and requirements that support a credible and compliant tender process."),
            ("Evaluation and commercial decision-making", "This section focuses on how offers and requirements are assessed in a way that supports sound business decisions."),
        ],
        "Business appraisal": [
            ("Assessment framework", "The learner studies how business performance is reviewed in relation to objectives, resources and market conditions."),
            ("Operational and financial review", "This section covers the indicators used to assess how well the business is operating and where the pressure points are."),
            ("Recommendation and improvement planning", "The learner is guided to translate evaluation findings into practical business advice and improvement pathways."),
        ],
        "Business requirements and business rescue strategies": [
            ("Business needs and risk profile", "This grouping focuses on the needs of the business and the conditions that may create stress or operational decline."),
            ("Rescue and recovery options", "The learner reviews how businesses may be stabilised, restructured or supported to recover viability."),
            ("Intervention planning", "This section addresses the practical planning required before and during a business rescue or turnaround process."),
        ],
        "Effective communication": [
            ("Listening and message design", "This section covers how communication is shaped to be clear, relevant and useful to the audience."),
            ("Feedback and engagement", "The learner explores how feedback, clarification and conversation support business relationships and problem-solving."),
            ("Professional communication in practice", "This grouping reinforces the role of communication in advising, negotiating and managing business interactions."),
        ],
        "Principles of ethics in business": [
            ("Integrity and fairness", "This grouping explores how ethical principles guide responsible behaviour in business and consulting situations."),
            ("Trust and accountability", "The learner considers how ethics supports confidence, transparency and organisational credibility."),
            ("Professional standards", "This section emphasises the need for ethical conduct in advice, decision support and client interaction."),
        ],
        "Strategies for behaviour change and coaching": [
            ("Coaching and guidance", "This section examines how support and reflection can help a person adopt better working practices."),
            ("Behavioural change planning", "The learner considers how change is structured so that actions become manageable and sustainable."),
            ("Practice and accountability", "This grouping focuses on review, reinforcement and commitment to improved operational behaviour."),
        ],
        "Principles of change management": [
            ("Change context", "This section helps the learner understand why organisations change and what drives change in the business environment."),
            ("Structured change approach", "This grouping focuses on the planning, communication and management needed for successful transitions."),
            ("Implementation and review", "The learner is guided to consider how a change initiative is monitored and improved over time."),
        ],
        "Introductory studies for project managers": [
            ("Project basics", "This section introduces the logic of project management and why structured work delivery matters."),
            ("Planning and coordination", "The learner examines how objective setting, task organisation and resource control improve delivery."),
            ("Monitoring and accountability", "This grouping focuses on review, performance tracking and maintaining delivery discipline."),
        ],
        "Application of contract documentation": [
            ("Contract purpose", "This section covers why contracts are used and what they are intended to achieve in business relationships."),
            ("Documentation and responsibilities", "The learner looks at how roles, deliverables and obligations are defined in formal documents."),
            ("Governance and risk control", "This grouping ties contract documentation to good governance and reduced misunderstanding or exposure."),
        ],
        "Evaluation of influences in value chain": [
            ("Value chain overview", "This section explains how value is created across the business network from inputs through customer delivery."),
            ("Operational contributors", "The learner is guided to identify the internal and external components that affect efficiency and service quality."),
            ("Improvement opportunities", "This grouping focuses on recognising points of pressure or inefficiency and proposing relevant improvement actions."),
        ],
        "Evaluate personal capability for performing business consulting services": [
            ("Self-assessment", "The learner assesses personal readiness for consulting work by reviewing knowledge, behaviour and professional capacity."),
            ("Role alignment", "This section considers how the learner's capability fits the consulting role and the support expected by a client."),
            ("Professional judgement", "The learner reviews boundaries, confidence and the need for support or specialist referral."),
        ],
        "Carry out due diligence and check compliance with relevant legislation": [
            ("Due diligence process", "This section focuses on reviewing business records, operations and controls to establish the current compliance position."),
            ("Gap assessment", "The learner identifies shortfalls, risks and required corrective actions based on the relevant legal requirements."),
            ("Reporting and support", "This grouping examines how findings are communicated clearly and professionally to support business action."),
        ],
        "Monitor methods of appraisal of business owner, business performance and activities": [
            ("Monitoring approach", "The learner establishes the indicators and methods used to assess business performance and activity."),
            ("Evaluation of business health", "This section focuses on identifying trends in business operations and performance over time."),
            ("Actionable recommendations", "The learner translates findings into useful, practical recommendations to improve business effectiveness."),
        ],
        "Provide strategic and operational consulting service": [
            ("Strategic review", "This section focuses on how a business's strategic direction is assessed and clarified in consultation with the client."),
            ("Operational improvement", "The learner identifies practical operational changes that support business performance and service delivery."),
            ("Client advisory practice", "This grouping reinforces the consulting process of making realistic, evidence-based recommendations."),
        ],
        "Develop and implement a change management framework": [
            ("Change planning", "The learner defines the need for change and the method by which change should be managed in a business setting."),
            ("Implementation support", "This section covers the practical work of rolling out the chosen approach and maintaining operational continuity."),
            ("Review and consolidation", "The learner considers how changes are monitored, adjusted and embedded over time."),
        ],
        "Develop project implementation approach": [
            ("Project design", "The learner outlines the project steps, sequence and responsibilities needed for implementation."),
            ("Resource use and sequencing", "This section focuses on how tasks, timing and resources are aligned for practical delivery."),
            ("Monitoring and delivery control", "This grouping covers progress review and the management of project performance during implementation."),
        ],
        "Interpret the influences of key components in the value chain on business efficiency": [
            ("Value chain analysis", "The learner examines the key components that influence business efficiency and customer value."),
            ("Constraint identification", "This section focuses on recognising weak links, bottlenecks and process issues within the value chain."),
            ("Improvement recommendation", "The learner identifies realistic changes to improve flow, quality and efficiency."),
        ],
        "Procedures to evaluate personal capability for performing business consulting services": [
            ("Capability assessment", "The learner evaluates their own readiness for advising and supporting businesses in practical settings."),
            ("Reflection and improvement", "This section considers professional growth and the development needs that follow assessment."),
            ("Workplace readiness", "The learner confirms the practical standards expected when performing business consulting work."),
        ],
        "Processes and procedures for carrying out and checking due diligence compliance with relevant legislation": [
            ("Workplace due diligence", "The learner applies due diligence methods in a real context to assess compliance and business conditions."),
            ("Evidence and review", "This section focuses on collecting evidence and checking whether current practices meet legal requirements."),
            ("Corrective support", "The learner identifies required corrective action and supports improvement in a professional manner."),
        ],
        "Process to monitor methods of appraisal of business owner, business performance and activities": [
            ("Appraisal practice", "The learner uses practical systems to review the performance of the business and its activities."),
            ("Evidence-based judgement", "This section focuses on collecting and analysing evidence to support conclusions and recommendations."),
            ("Improvement planning", "The learner translates appraisal findings into practical support for business improvement."),
        ],
        "Procedures to provide strategic and operational consulting service": [
            ("Strategic advising", "The learner provides guidance on direction, priorities and business focus in a practical context."),
            ("Operational improvement", "This section focuses on practical service and process improvement in the business environment."),
            ("Professional advisory support", "The learner demonstrates that recommendations are realistic, evidence-based and client-oriented."),
        ],
        "Process to develop and implement a change management framework": [
            ("Change design", "The learner prepares a structured approach for change in a business context."),
            ("Implementation management", "This section focuses on applying the framework in practice with coordination and communication."),
            ("Impact review", "The learner monitors outcomes and adjusts the change process as required."),
        ],
        "Process and procedures to develop project implementation approach": [
            ("Project structure", "The learner plans the implementation approach and sequence of project activity."),
            ("Operational coordination", "This section addresses how work is organised, monitored and aligned to objectives."),
            ("Delivery review", "The learner reviews progress and the quality of implementation against the project plan."),
        ],
        "Procedures to interpret the influences of key components in the value chain on business efficiency": [
            ("Value-chain diagnosis", "The learner identifies the factors influencing efficiency in the business's value chain."),
            ("Constraints and opportunities", "This section assesses where bottlenecks or weaknesses affect performance."),
            ("Improvement support", "The learner proposes practical means to improve operational flow and efficiency."),
        ],
    }
    return mapping.get(title, [
        ("Core understanding", "This section covers the essential concepts required to understand the topic and apply it in a business context."),
        ("Application in practice", "This section focuses on using the concept in a practical workplace or organisational setting."),
        ("Review and action", "This section supports reflection, assessment and the development of practical recommendations."),
    ])


LESSON_MODULES = {}
for lesson in LESSONS:
    title = lesson["title"]
    groups = lesson_groups_for_title(title)
    LESSON_MODULES[title] = [
        {"title": group_title, "content": group_content}
        for group_title, group_content in groups
    ]


CHECKLIST_PATTERNS = {
    "theory": [
        "Defines the purpose and scope of the topic clearly.",
        "Explains the key concepts and relevant business context.",
        "Applies the concept to a realistic business or organisational scenario.",
        "Identifies the main risks, requirements or decisions associated with the topic.",
        "Communicates findings and recommendations clearly and professionally.",
    ],
    "practical": [
        "Carries out the required practical task in a structured manner.",
        "Collects and reviews relevant evidence before making a conclusion.",
        "Uses the relevant method or procedure correctly.",
        "Identifies gaps, risks or improvement areas in the business context.",
        "Reports findings and recommendations clearly for action.",
    ],
    "work_experience": [
        "Applies the relevant workplace method in a real business setting.",
        "Exercises the required skill with attention to process and evidence.",
        "Demonstrates professional conduct in carrying out the work.",
        "Reflects on workplace outcomes and identifies improvement actions.",
        "Records and communicates findings clearly for review and assessment.",
    ],
}


def make_checklist_items_for_lesson(lesson_title, module_type):
    prefix_map = {
        "KM-01": "Regulatory and legislative framework",
        "KM-02": "Compliance audit",
        "KM-03": "Entrepreneurial profile",
        "KM-04": "Business consulting development",
        "KM-05": "Strategic and operational planning",
        "KM-06": "Professional business factors",
        "KM-07": "Marketing principles",
        "KM-08": "Business finance",
        "KM-09": "Costing and pricing",
        "KM-10": "Risk management",
        "KM-11": "Tendering principles",
        "KM-12": "Business appraisal",
        "KM-13": "Business rescue and requirements",
        "KM-14": "Effective communication",
        "KM-15": "Business ethics",
        "KM-16": "Behaviour change and coaching",
        "KM-17": "Change management",
        "KM-18": "Project management basics",
        "KM-19": "Contract documentation",
        "KM-20": "Value chain evaluation",
    }
    label = prefix_map.get(lesson_title.split(": ", 1)[0], lesson_title)
    base = [
        f"Defines the purpose and scope of {label} in a business context.",
        f"Explains the key concepts and issues associated with {label}.",
        f"Applies {label} to a realistic organisational scenario or case.",
        f"Uses evidence to assess the relevance of {label} for business improvement.",
        f"Communicates findings and recommendations clearly and professionally.",
    ]
    return base if module_type != "practical" and module_type != "work_experience" else [
        f"Carries out the required task for {label} in a structured and professional manner.",
        f"Collects and reviews relevant evidence for {label}.",
        f"Uses the relevant method or procedure correctly for {label}.",
        f"Identifies gaps, risks or opportunities linked to {label}.",
        f"Reports findings and recommendations clearly for action and review.",
    ]


class Command(BaseCommand):
    help = "Seed the Occupational Certificate: Small Business Consultant (SP-242101) into the LMS."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Print what would be created without writing to the database.")
        parser.add_argument("--reset", action="store_true", help="Delete the existing SBC course and cascade before reseeding.")
        parser.add_argument("--instructor", help="Assign the course to a specific instructor username.")
        parser.add_argument("--noinput", action="store_true", help="Skip confirmation prompts.")

    def _resolve_instructor(self, username=None):
        match = None
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist as exc:
                raise CommandError(f"Instructor '{username}' does not exist. Create the account or pass a valid --instructor value.") from exc

        candidate = User.objects.filter(first_name='F.P.S.', last_name='Mdlalose').order_by('id').first()
        if candidate:
            return candidate

        instructor = User.objects.filter(role='admin', is_approved=True).order_by('id').first()
        if not instructor:
            raise CommandError("No approved admin user exists. Create an admin account or pass --instructor <username>.")
        return instructor

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            total_modules = sum(len(v) for v in LESSON_MODULES.values())
            total_checklists = sum(len(make_checklist_items_for_lesson(lesson["curriculum_code"] + ": " + lesson["title"], "theory" if lesson["curriculum_code"].startswith("KM") else "practical" if lesson["curriculum_code"].startswith("PM") else "work_experience")) for lesson in LESSONS)
            self.stdout.write(self.style.WARNING("Dry run: no changes will be written to the database."))
            self.stdout.write(f"Would create: 1 course, 34 lessons, {total_modules} modules, 34 learning modules, {total_checklists} checklist items, 7 FISA assessments")
            self.stdout.write(f"Course: {COURSE_TITLE}")
            return

        instructor = self._resolve_instructor(options.get("instructor"))
        self.stdout.write(f"Using instructor: {instructor.username}")

        existing_course = Course.objects.filter(slug=COURSE_SLUG).first()
        if options["reset"] and existing_course:
            if not options["noinput"] and not self.confirm(
                "Delete the existing Small Business Consultant course and cascade all dependent records before reseeding?",
                default=False,
            ):
                raise CommandError("Reset cancelled.")
            self.stdout.write("Deleting existing Small Business Consultant course...")
            existing_course.delete()

        course_exists = Course.objects.filter(slug=COURSE_SLUG).exists()
        has_all_lessons = Lesson.objects.filter(course__slug=COURSE_SLUG).count() == len(LESSONS)
        has_all_modules = LessonModule.objects.filter(lesson__course__slug=COURSE_SLUG).count() == sum(len(v) for v in LESSON_MODULES.values())
        has_all_learning_modules = LearningModule.objects.filter(course__slug=COURSE_SLUG).count() == len(LESSONS)
        has_all_checklists = ObservationChecklistItem.objects.filter(module__course__slug=COURSE_SLUG).count() >= 170
        has_all_assessments = SummativeAssessment.objects.filter(course__slug=COURSE_SLUG).count() == 7

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
                        "level": "intermediate",
                        "price": 0,
                        "status": "published",
                    },
                )

                if course_created:
                    self.stdout.write("Creating course...")
                else:
                    self.stdout.write("Course already exists; updating metadata...")
                course.title = COURSE_TITLE
                course.description = COURSE_DESCRIPTION
                course.instructor = instructor
                course.level = "intermediate"
                course.price = 0
                course.status = "published"
                course.save()

                lesson_count = len(LESSONS)
                for index, lesson_data in enumerate(LESSONS, start=1):
                    lesson_title = f"{lesson_data['curriculum_code']}: {lesson_data['title']}"
                    self.stdout.write(f"Creating lesson {index}/{lesson_count}: {lesson_title}")
                    lesson, _ = Lesson.objects.update_or_create(
                        course=course,
                        title=lesson_title,
                        defaults={
                            "content": lesson_data["content"],
                            "duration": lesson_duration_for_credits(lesson_data["credits"]),
                            "order": lesson_data["order"],
                        },
                    )

                    modules = LESSON_MODULES.get(lesson_data["title"], [])
                    self.stdout.write(f"Creating {len(modules)} modules for lesson {index}")
                    for module_order, module_data in enumerate(modules, start=1):
                        LessonModule.objects.update_or_create(
                            lesson=lesson,
                            title=module_data["title"],
                            defaults={
                                "content": module_data["content"],
                                "content_type": "text",
                                "points": 10,
                                "time_estimate": 30,
                                "order": module_order,
                            },
                        )

                self.stdout.write("Creating 34 learning modules...")
                for lesson_order, lesson_data in enumerate(LESSONS, start=1):
                    lesson_title = f"{lesson_data['curriculum_code']}: {lesson_data['title']}"
                    lesson = Lesson.objects.get(course=course, title=lesson_title)
                    module_type = "theory" if lesson_data["curriculum_code"].startswith("KM") else "practical" if lesson_data["curriculum_code"].startswith("PM") else "work_experience"
                    LearningModule.objects.update_or_create(
                        course=course,
                        title=lesson_title,
                        defaults={
                            "description": lesson_data["content"][:300],
                            "order": lesson_order,
                            "module_type": module_type,
                            "is_visible": True,
                        },
                    )

                    checklist_items = make_checklist_items_for_lesson(lesson_data["curriculum_code"], module_type)
                    self.stdout.write(f"Creating {len(checklist_items)} checklist items for {lesson_data['curriculum_code']}")
                    learning_module = LearningModule.objects.get(course=course, title=lesson_title)
                    for item_order, item_description in enumerate(checklist_items, start=1):
                        ObservationChecklistItem.objects.update_or_create(
                            module=learning_module,
                            description=item_description,
                            defaults={"order": item_order},
                        )

                self.stdout.write("Creating 7 FISA assessments...")
                assessment_due_date = timezone.now() + timedelta(days=120)
                pm_lessons = [lesson for lesson in LESSONS if lesson["curriculum_code"].startswith("PM")]
                for lesson in pm_lessons:
                    title = f"FISA: {lesson['curriculum_code']} — {lesson['title']}"
                    instructions = (
                        f"Purpose of the Practical Skill Module: {lesson['content']} "
                        "The learner must submit evidence in their Portfolio of Evidence and demonstrate the required practical capability for this outcome."
                    )
                    SummativeAssessment.objects.update_or_create(
                        course=course,
                        title=title,
                        defaults={
                            "instructions": instructions,
                            "due_date": assessment_due_date,
                            "created_by": instructor,
                        },
                    )

                total_lessons = Lesson.objects.filter(course=course).count()
                total_modules = LessonModule.objects.filter(lesson__course=course).count()
                total_learning_modules = LearningModule.objects.filter(course=course).count()
                total_checklist_items = ObservationChecklistItem.objects.filter(module__course=course).count()
                total_fisa = SummativeAssessment.objects.filter(course=course).count()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: 1 course, {total_lessons} lessons, {total_modules} modules, "
                        f"{total_learning_modules} learning modules, {total_checklist_items} checklist items, "
                        f"{total_fisa} FISA assessments"
                    )
                )
        except Exception as exc:  # pragma: no cover - transaction rollback path
            self.stderr.write(f"Error while seeding Small Business Consultant course: {exc}")
            raise
