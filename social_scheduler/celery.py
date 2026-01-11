import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_scheduler.settings')

app = Celery("social_scheduler")

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-scheduled-posts-every-minute': {
        'task': 'poster.tasks.check_for_scheduled_posts', 
        'schedule': 60.0, 
    },
}