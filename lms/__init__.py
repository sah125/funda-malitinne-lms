"""
This file is required when a Django app has a models module as a package
"""

from .celery import app as celery_app

__all__ = ('celery_app',)
