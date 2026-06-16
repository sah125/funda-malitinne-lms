# core/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Opportunity, Course, TenderOpportunity


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'company_home',
            'programmes',
            'clients',
            'opportunities',
            'lms_portal',
            'login',
            'register',
        ]

    def location(self, item):
        return reverse(item)


class OpportunitySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Opportunity.objects.filter(status='published')


class CourseSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Course.objects.filter(status='published')


class TenderSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return TenderOpportunity.objects.filter(status__in=['new', 'viewed', 'active'])


sitemaps = {
    'static': StaticViewSitemap,
    'opportunities': OpportunitySitemap,
    'courses': CourseSitemap,
    'tenders': TenderSitemap,
}