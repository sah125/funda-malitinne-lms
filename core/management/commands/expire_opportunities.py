from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Opportunity

class Command(BaseCommand):
    help = 'Automatically close expired opportunities'
    
    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # Close expired opportunities
        expired = Opportunity.objects.filter(
            status='published',
            closing_date__lt=today
        ).update(status='closed')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully closed {expired} expired opportunities')
        )