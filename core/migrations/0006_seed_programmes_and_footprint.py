"""Seed the public website with Malitinne's QCTO programmes (from the
accreditation status register) and the places we have worked (from the
2024 company profile). Uses get_or_create, so edits made in the admin are
never overwritten when this runs again."""
from django.db import migrations

ACCREDITED = 'accredited'
IN_PROGRESS = 'in_progress'
PLANNED = 'planned'

PROGRAMMES = [
    # slug, title, code, category, status, credits, hours, nqf, delivery, featured, course-title-hint, summary, audience, outcomes
    ('project-manager', 'Project Manager', '101869', 'business', ACCREDITED, 240, 2400, 5, 'blended', True, 'project manager',
     'An occupational qualification that prepares you to initiate, plan, execute, control and close projects in any sector — the full project life cycle, the way industry runs it.',
     'Supervisors and team leaders who run projects\nGraduates entering project roles\nMunicipal and public-sector officials\nSMME owners delivering contracts',
     'Initiate a project and develop its charter\nPlan scope, schedule, cost, quality and risk\nExecute and control delivery against the plan\nManage stakeholders, procurement and project teams\nClose out a project and capture lessons learned'),
    ('small-business-consultant', 'Small Business Consultant', '118741', 'business', ACCREDITED, 244, 2440, None, 'blended', True, 'small business consultant',
     'Equips you to advise, mentor and support small and emerging businesses — from diagnosing business problems to building plans that help SMMEs grow and stay compliant.',
     'Business advisors and enterprise-development officers\nEntrepreneurs who support other SMMEs\nCooperative and community-project leaders',
     'Assess the health and needs of a small business\nDevelop business, marketing and financial plans with clients\nGuide compliance, funding and growth decisions\nMonitor and report on enterprise-development support'),
    ('new-venture-creation', 'New Venture Creation', 'SP-210401', 'business', ACCREDITED, 32, 320, None, 'blended', True, 'new venture',
     'A practical skills programme for people who want to start or grow their own business — from testing the idea to running day-to-day operations.',
     'Aspiring entrepreneurs and youth\nInformal traders who want to formalise\nEPWP and community-programme beneficiaries',
     'Identify and test a viable business opportunity\nDraft a simple business plan and budget\nManage basic finances, pricing and records\nMarket and sell products or services'),
    ('office-administrator', 'Office Administrator', '102161', 'digital', ACCREDITED, 445, 4450, None, 'blended', False, 'office admin',
     'Prepares you to keep an office running — records, communication, scheduling, finance support and customer service in a modern workplace.',
     'School leavers and graduates seeking office work\nAdministrative staff wanting a formal qualification',
     'Manage records, documents and filing systems\nCoordinate meetings, diaries and travel\nProduce business documents and correspondence\nSupport basic finance and procurement administration'),
    ('management-assistant', 'Management Assistant', '101876', 'digital', ACCREDITED, 316, 3160, None, 'blended', False, 'management assistant',
     'Develops the skills to support managers and executives — coordinating information, people and projects so leaders can focus on decisions.',
     'Personal and executive assistants\nAdministrators moving into management support',
     'Coordinate a manager\'s schedule, meetings and communication\nPrepare reports, minutes and presentations\nSupport projects, events and stakeholder liaison'),
    ('commercial-cleaner', 'Commercial Cleaner', '118709', 'services', ACCREDITED, 120, 1200, None, 'blended', False, 'commercial cleaner',
     'A workplace-ready qualification in professional cleaning for offices, healthcare and commercial facilities, with a strong focus on hygiene and safety.',
     'Facilities and hygiene staff\nUnemployed youth seeking entry-level work\nCleaning-services SMMEs',
     'Apply safe cleaning methods, chemicals and equipment\nClean and sanitise different commercial environments\nFollow health, safety and infection-control procedures'),
    ('basic-emergency-first-aid-responder', 'Basic Emergency First Aid Responder', 'SP-230801', 'health_safety', ACCREDITED, 2, 20, None, 'blended', True, 'basic emergency first aid',
     'A short accredited programme that teaches you to respond safely and confidently to emergencies in the workplace and community until help arrives.',
     'Every workplace that needs appointed first aiders\nEPWP, construction and field teams\nCommunity volunteers',
     'Assess an emergency scene and keep it safe\nPerform basic life support and CPR\nManage bleeding, burns, fractures and shock'),
    ('advanced-emergency-first-aid-responder', 'Advanced Emergency First Aid Responder', 'SP-230803', 'health_safety', ACCREDITED, 6, 60, None, 'blended', True, 'advanced first aid',
     'Builds on basic first aid to manage serious injuries and medical emergencies, lead a response and support emergency services.',
     'Workplace first aiders who need a higher level\nSafety officers and team leaders in high-risk work',
     'Manage multiple casualties and serious trauma\nRecognise and respond to medical emergencies\nLead a first-aid response and hand over to emergency services'),
    # In progress
    ('intermediate-end-user-computing', 'Intermediate End User Computing', 'SP-240202', 'digital', IN_PROGRESS, 20, 200, None, 'online', False, '', 
     'Practical computer skills for the workplace — documents, spreadsheets, presentations, email and safe internet use.', '', ''),
    ('advanced-end-user-computing', 'Advanced End User Computing', 'SP-240203', 'digital', IN_PROGRESS, 20, 200, None, 'online', False, '',
     'Advanced productivity skills for office professionals working with complex documents, data and presentations.', '', ''),
    ('poultry-farmer', 'Poultry Farmer', '99027', 'agriculture', IN_PROGRESS, 226, 2260, None, 'contact', False, '',
     'Prepares farmers to raise poultry productively and safely — housing, feeding, health, biosecurity and selling.', '', ''),
    ('aquaculture-farmer', 'Aquaculture Farmer', '104912', 'agriculture', IN_PROGRESS, 176, 1760, None, 'contact', False, '',
     'Skills to establish and run fish-farming operations, from water quality to harvesting and marketing.', '', ''),
    ('miller', 'Miller', '97204', 'agriculture', IN_PROGRESS, 401, 4010, None, 'contact', False, '',
     'Trains operators to run grain-milling processes safely and to quality standards.', '', ''),
    # Planned (hidden until you publish them in the admin)
    ('workplace-preparation', 'Workplace Preparation', 'SP-201201', 'business', PLANNED, 30, 300, None, 'online', False, '', 'Getting young people ready for the world of work.', '', ''),
    ('pothole-repair-person', 'Pothole Repair Person', 'SP-240504', 'construction', PLANNED, 31, 310, None, 'contact', False, '', 'Road-maintenance skills for municipal and EPWP teams.', '', ''),
    ('hairstylist', 'Hairstylist', 'SP-230305', 'beauty', PLANNED, 56, 560, None, 'blended', False, 'hair', 'Professional hairstyling skills for salons and self-employment.', '', ''),
    ('hair-and-scalp-treatment-attendant', 'Hair and Scalp Treatment Attendant', 'SP-230302', 'beauty', PLANNED, 23, 230, None, 'blended', False, '', 'Hair and scalp care treatments.', '', ''),
    ('forestry-she-representative', 'Forestry SHE Representative', 'SP-220906', 'health_safety', PLANNED, 39, 390, None, 'blended', False, '', 'Safety, health and environment representation in forestry.', '', ''),
    ('forestry-incident-investigator', 'Forestry Incident Investigator', 'SP-220905', 'health_safety', PLANNED, 32, 320, None, 'blended', False, '', 'Investigating incidents in forestry operations.', '', ''),
    ('forestry-hazard-and-risk-assessor', 'Forestry Hazard and Risk Assessor', 'SP-220904', 'health_safety', PLANNED, 35, 350, None, 'blended', False, '', 'Identifying and assessing hazards in forestry work.', '', ''),
    ('basic-end-user-computing', 'Basic End User Computing', 'SP-240201', 'digital', PLANNED, 30, 300, None, 'online', False, '', 'First steps with computers, the internet and email.', '', ''),
    ('barber', 'Barber', 'SP-191215', 'beauty', PLANNED, 36, 360, None, 'contact', False, '', 'Barbering skills for employment or your own business.', '', ''),
    ('aerial-chainsaw-operator', 'Aerial Chainsaw Operator', 'SP-220902', 'agriculture', PLANNED, 36, 360, None, 'contact', False, '', 'Safe aerial chainsaw operation for arboriculture and forestry.', '', ''),
]

LOCATIONS = [
    # name, kind, town, lat, lng, beneficiaries, period, programmes
    ('Malitinne Head Office', 'office', 'Durban CBD', -29.8587, 31.0218, None, 'Since 2014',
     'Office 1138, 11th Floor, Commercial City, 40 Dr A B Xuma Rd\nTraining, placements and project management hub'),
    ('iSimangaliso Wetland Park', 'project', 'St Lucia', -28.3833, 32.4167, 2575, '2022 – 2024',
     'Skills Programme: Bush Clearing\nHealth and Safety\nBasic First Aid Levels 1–4\nFire Awareness\nFire Marshal'),
    ('uMgungundlovu District Municipality', 'project', 'Pietermaritzburg', -29.6006, 30.3794, 2500, '2015',
     'Project management & placement of graduates\nSourcing funds for training and development'),
    ('uMfolozi TVET College', 'project', 'Richards Bay', -28.7807, 32.0383, 880, '2015 – 2021',
     'Apprenticeships: Bricklaying, Electrical Engineering, Welding, Plumbing\nCoordination, placement and project management'),
    ('Okhahlamba Local Municipality', 'project', 'Bergville', -28.7333, 29.3500, 550, '2021 – current',
     'TETA Programme: Project Management\nCETA Apprenticeship: Bricklaying\nLGSETA: New Venture Creation\nHealth & Safety\nTVET Placement: Civil Engineering'),
    ('KZN Department of Arts & Culture', 'project', 'Pietermaritzburg', -29.6168, 30.3928, 545, '2015',
     'EPWP Project Management\nRecruitment\nPayroll administration'),
    ('uPhongolo Local Municipality', 'project', 'Pongola', -27.3833, 31.6167, 185, '2022 – current',
     'Silviculture: Brush-cutting Operator (EPWP)\nCandidacy: Quantity Surveying & Civil Engineering\nInternships (CETA + FP&M SETA)\nLearnership: Community House Building'),
    ('uMshwathi Local Municipality', 'project', 'Wartburg', -29.4333, 30.5833, 155, 'Current',
     'Skills Programme: Conservation Farming\nTender Processing for SMMEs\nHairdressing'),
    ('Ulundi Local Municipality', 'project', 'Ulundi', -28.3333, 31.4167, 90, '2019',
     'Councillor Development\nFirst Aid'),
    ('Abaqulusi Local Municipality', 'project', 'Vryheid', -27.7667, 30.8000, 50, '2021',
     'Funding for internships and TVET placements (FASSET & CETA)'),
    ('Mkhambathini Local Municipality', 'project', 'Camperdown', -29.7333, 30.5333, 37, '2019',
     'Skills Development: Landscaping\nNew Venture Creation'),
    ('Hlabisa Local Municipality', 'project', 'Hlabisa', -28.1500, 31.8667, 30, '2022',
     'Placement of graduates and undergraduates'),
    ('Dr Nkosazana Dlamini Zuma Municipality', 'project', 'Bulwer', -29.8000, 29.7667, 20, '2023',
     'Skills Programme: Leather Manufacturing Processes'),
    ('Nkandla Local Municipality', 'project', 'Nkandla', -28.6167, 31.0833, 20, '2023 – current',
     'Learnership: Horticulture'),
    ('Zululand Chamber of Commerce & Industry', 'partner', 'Richards Bay', -28.7450, 32.0500, 16, '2023',
     'Skills Programme: Basic manicure and pedicure'),
    ('Ndwedwe Local Municipality', 'project', 'Ndwedwe', -29.5167, 30.9333, 10, '2022',
     'Internship Programme: TVET Placement'),
    ('uMfolozi Local Municipality', 'project', 'KwaMbonambi', -28.6000, 32.0833, 10, '2022',
     'TVET placement for graduates and undergraduates'),
]


def seed(apps, schema_editor):
    Programme = apps.get_model('core', 'Programme')
    ServiceLocation = apps.get_model('core', 'ServiceLocation')
    Course = apps.get_model('core', 'Course')

    for order, row in enumerate(PROGRAMMES):
        (slug, title, code, category, status, credits, hours, nqf, delivery, featured, hint,
         summary, audience, outcomes) = row
        course = Course.objects.filter(title__icontains=hint).first() if hint else None
        Programme.objects.get_or_create(slug=slug, defaults=dict(
            title=title, code=code, category=category, status=status, credits=credits, notional_hours=hours,
            nqf_level=nqf, delivery_mode=delivery, is_featured=featured, summary=summary,
            who_is_it_for=audience, outcomes=outcomes, quality_partner='QCTO', course=course,
            is_published=status != PLANNED, order=order,
        ))

    for order, (name, kind, town, lat, lng, people, period, progs) in enumerate(LOCATIONS):
        ServiceLocation.objects.get_or_create(name=name, defaults=dict(
            kind=kind, town=town, latitude=lat, longitude=lng, beneficiaries=people,
            period=period, programmes=progs, order=order,
        ))


class Migration(migrations.Migration):
    dependencies = [('core', '0005_approvals_programmes_enquiries')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
