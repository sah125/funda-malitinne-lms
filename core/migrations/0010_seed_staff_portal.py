"""Seed the staff portal: Malitinne's bid profile (from the 2024 company profile),
Shared Drive folders, and the sources the tender/grant scanner watches.
Uses get_or_create, so anything edited in the admin is never overwritten."""
from django.db import migrations

CORE = """skills development
training
accredited training
learnership
skills programme
short course
internship
in-service training
work integrated learning
workplace experience
experiential training
graduate development
candidacy programme
workplace readiness
work readiness
capacity building
facilitation
assessor
moderator
mentoring
coaching
EPWP
youth development
unemployed youth
life skills
SMME development
enterprise development
new venture creation
local economic development
first aid
health and safety training
career guidance
placement
human capital development
QCTO"""

RELATED = """consulting
corporate social responsibility
CSI
project management
community development
women empowerment
recruitment
employee wellness
etiquette
emotional intelligence
office administration
end user computing
computer literacy
hairdressing
cookery
municipal finance
integrated development planning
councillor
cooperative
agriculture training
bursary
NYDA"""

EXCLUDE = """construction of
upgrading of
refurbishment
rehabilitation of
road
building works
civil works
electrical installation
plumbing
supply and delivery
supply of
vehicles
fuel
security services
cleaning services
catering services
medical equipment
IT hardware
furniture supply
CIDB"""

FOLDERS = [
    ('company-compliance', 'Company compliance', 'CIPC, tax, B-BBEE, CSD, COIDA, bank letters', 'fa-shield-halved', 1),
    ('letters', 'Referral & appointment letters', 'Referrals, appointments, references, completion certificates', 'fa-envelope-open-text', 2),
    ('accreditation', 'Accreditation', 'QCTO and SETA accreditation letters and scopes', 'fa-award', 3),
    ('tenders-bids', 'Tenders & bids', 'Submitted bids, SBD forms, pricing schedules', 'fa-file-contract', 4),
    ('contracts', 'Contracts & SLAs', 'Signed contracts and service level agreements', 'fa-file-signature', 5),
    ('templates', 'Templates & forms', 'Letterheads, attendance registers, report templates', 'fa-clone', 6),
    ('policies', 'Policies', 'POPIA, HR, quality management and assessment policies', 'fa-scale-balanced', 7),
    ('learner-admin', 'Learner administration', 'Learner files - contains personal information', 'fa-user-lock', 8),
    ('finance', 'Finance', 'Invoices, statements, budgets', 'fa-coins', 9),
    ('marketing', 'Marketing', 'Company profile, brochures, photos', 'fa-bullhorn', 10),
]

SOURCES = [
    ('eTenders - National Treasury open data', 'ocds', 'https://ocds-api.etenders.gov.za/api/OCDSReleases', 'tender', True),
    ('NYDA - funding & opportunities', 'watch_page', 'https://www.nyda.gov.za/', 'grant', True),
    ('National Skills Fund', 'watch_page', 'https://www.nsf.gov.za/', 'grant', True),
    ('Services SETA', 'watch_page', 'https://www.serviceseta.org.za/', 'grant', True),
    ('LGSETA', 'watch_page', 'https://www.lgseta.org.za/', 'grant', True),
    ('AgriSETA', 'watch_page', 'https://www.agriseta.co.za/', 'grant', True),
    ('ETDP SETA', 'watch_page', 'https://www.etdpseta.org.za/', 'grant', True),
    ('W&RSETA', 'watch_page', 'https://www.wrseta.org.za/', 'grant', True),
    ('MICT SETA', 'watch_page', 'https://www.mict.org.za/', 'grant', True),
    ('CATHSSETA', 'watch_page', 'https://www.cathsseta.org.za/', 'grant', True),
]


def seed(apps, schema_editor):
    BidProfile = apps.get_model('core', 'BidProfile')
    DocumentCategory = apps.get_model('core', 'DocumentCategory')
    TenderSource = apps.get_model('core', 'TenderSource')
    if not BidProfile.objects.exists():
        BidProfile.objects.create(
            company_name='Malitinne (Pty) Ltd', core_keywords=CORE, related_keywords=RELATED, exclude_keywords=EXCLUDE,
            home_province='KwaZulu-Natal', target_provinces='Gauteng\nEastern Cape\nMpumalanga',
            accreditations='QCTO\nServices SETA\nLGSETA\nAgriSETA', min_days_to_prepare=5)
    for slug, name, desc, icon, order in FOLDERS:
        DocumentCategory.objects.get_or_create(slug=slug, defaults=dict(name=name, description=desc, icon=icon, order=order))
    for name, kind, url, default_kind, active in SOURCES:
        TenderSource.objects.get_or_create(base_url=url, defaults=dict(
            name=name, source_type=kind, default_kind=default_kind, is_active=active, crawl_frequency_hours=24,
            search_keywords='discretionary grant, funding window, call for proposals, learnership, skills programme'))


class Migration(migrations.Migration):
    dependencies = [('core', '0009_staff_portal_upgrade')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
