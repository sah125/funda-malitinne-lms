from celery import shared_task
from django.utils import timezone


@shared_task
def close_expired_opportunities():
    from .models import Opportunity

    return Opportunity.objects.filter(
        status='published',
        closing_date__lt=timezone.now().date(),
    ).update(status='closed')
