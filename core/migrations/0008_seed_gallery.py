"""Seed the gallery with Malitinne's own project photos. Captions can be
edited in the admin (Gallery photos). get_or_create never overwrites edits."""
from django.db import migrations

PHOTOS = [
    # file, title, caption, category, show_on_home
    ('epwp-furniture-team', 'EPWP furniture-making cohort', 'Learners and supervisors celebrate an office desk built during the EPWP furniture-making programme.', 'furniture', True),
    ('furniture-office-installed', 'Finished office furniture', 'A desk and cabinet made by learners, installed in a client office.', 'furniture', True),
    ('leather-products-showcase', 'Leather & skins products', 'Bags, cushions, wallets and accessories handmade by learners in the leather & skins programme.', 'leather', True),
    ('leather-learner-pattern', 'Pattern work', 'A learner lays out a pattern on cowhide during a leather & skins workshop.', 'leather', True),
    ('nyda-youth-session', 'Youth entrepreneurship session', 'Facilitating a youth development session alongside the National Youth Development Agency (NYDA).', 'community', True),
    ('classroom-assessment', 'Learners at work', 'Learners complete written activities and assessments during a contact session.', 'classroom', True),
    ('epwp-furniture-handover', 'Programme handover day', 'The EPWP furniture-making team with stakeholders at the programme handover.', 'furniture', False),
    ('furniture-workshop-build', 'In the workshop', 'Assembling a desk frame in the training workshop.', 'furniture', False),
    ('furniture-installation', 'On-site installation', 'Learners install a desk on site, gaining real workplace experience.', 'furniture', False),
    ('furniture-shelving-units', 'Shelving units', 'Shelving and storage units produced by the furniture-making learners.', 'furniture', False),
    ('epwp-team-briefing', 'Team briefing', 'A facilitator briefs EPWP learners before a practical session.', 'community', False),
    ('leather-exhibition-stand', 'Exhibition stand', 'Malitinne learners showcase and sell their leather products at a market exhibition.', 'leather', False),
    ('leather-learner-cutting', 'Cutting and shaping', 'Hands-on practice cutting and shaping hide.', 'leather', False),
    ('leather-learner-measuring', 'Measuring and marking', 'Precise measuring and marking before cutting leather.', 'leather', False),
    ('leather-clutch-product', 'Finished clutch', 'A suede-and-leather clutch made by a learner.', 'leather', False),
]


def seed(apps, schema_editor):
    GalleryPhoto = apps.get_model('core', 'GalleryPhoto')
    for order, (name, title, caption, category, home) in enumerate(PHOTOS):
        GalleryPhoto.objects.get_or_create(static_path=f'images/gallery/{name}.jpg', defaults=dict(
            title=title, caption=caption, category=category, show_on_home=home, order=order))


class Migration(migrations.Migration):
    dependencies = [('core', '0007_gallery')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
