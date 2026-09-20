# core/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Course, Opportunity


class StaticViewSitemap(Sitemap):
    """Top-level pages that should be indexed by search engines."""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # Only include URL names that actually exist in lms/urls.py.
        # Missing names raise NoReverseMatch and kill the whole sitemap.
        return [
            'company_home',   # /
            'programmes',     # /programmes/
            'clients',        # /clients/
            'opportunities',  # /opportunities/
            'about',          # /about/
            'services',       # /services/
            'impact',         # /impact/
            'contact',        # /contact/
        ]

    def location(self, item):
        return reverse(item)


class OpportunitySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Opportunity.objects.filter(status='published')

    def location(self, obj):
        # No dedicated detail URL exists; deep-link to the list page.
        # When you add opportunity detail pages, change this to reverse('opportunity_detail', args=[obj.pk])
        return reverse('opportunities')


class CourseSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Course.objects.filter(status='published')

    def location(self, obj):
        return reverse('course_detail', args=[obj.pk])


sitemaps = {
    'static': StaticViewSitemap,
    'opportunities': OpportunitySitemap,
    'courses': CourseSitemap,
}