"""Convert a face-to-face learner guide (Word) into online lessons.

Example (the KM-01 Project Manager material):

  python manage.py import_learner_guide "KM01_Learner_Guide.docx" \
      --course "Project Manager" --module "KM-01 Introductory studies for Project Managers" \
      --assessment "KM-01-Learner_Assessment.docx" --instructor admin

If the course does not exist it is created as a *draft* so learners cannot see
it until you publish it.
"""
from django.core.management.base import BaseCommand, CommandError

from core.importers import import_into_course
from core.models import Course, User


class Command(BaseCommand):
    help = 'Import a Word learner guide (and optional learner assessment) into an LMS course.'

    def add_arguments(self, parser):
        parser.add_argument('guide', help='Path to the learner guide .docx')
        parser.add_argument('--course', required=True, help='Course title (existing or new)')
        parser.add_argument('--module', default='', help='Knowledge module title, e.g. "KM-01 Introductory studies"')
        parser.add_argument('--assessment', help='Path to the learner assessment .docx (activities -> assignments)')
        parser.add_argument('--instructor', help='Username of the facilitator for a new course')
        parser.add_argument('--replace', action='store_true', help='Replace lessons previously imported into this module')
        parser.add_argument('--publish', action='store_true', help='Publish the course immediately')

    def handle(self, *args, **opts):
        course = Course.objects.filter(title__iexact=opts['course']).first()
        if course is None:
            instructor = User.objects.filter(username=opts.get('instructor')).first() if opts.get('instructor') else \
                User.objects.filter(role__in=['instructor', 'admin']).order_by('id').first()
            if instructor is None:
                raise CommandError('No instructor found. Pass --instructor <username>.')
            course = Course.objects.create(title=opts['course'], instructor=instructor, status='draft',
                                           description=f"Online delivery of {opts['course']}.")
            self.stdout.write(f'Created draft course "{course.title}" (id {course.id}).')
        result = import_into_course(course, opts['guide'], opts.get('assessment'), module_title=opts['module'],
                                    replace=opts['replace'])
        if opts['publish']:
            course.status = 'published'
            course.save(update_fields=['status'])
        self.stdout.write(self.style.SUCCESS(
            f"Imported {result['lessons']} lessons (~{result['minutes']} min of reading) and "
            f"{result['assignments']} assessment activities into '{course.title}' / {result['module']}."))
