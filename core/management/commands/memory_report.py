import psutil
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Print process memory usage for Django and Celery processes"

    def handle(self, *args, **options):
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                mem_mb = proc.info['memory_info'].rss / 1024 / 1024
                if mem_mb > 50:
                    self.stdout.write(
                        f"PID {proc.info['pid']:>7} {proc.info['name']:<20} {mem_mb:>8.1f} MB"
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass