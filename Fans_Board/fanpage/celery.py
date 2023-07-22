import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Fans_Board.settings')

app = Celery('Fans_Board')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_weekly_notification': {
        'task': 'fanpage.tasks.weekly_notification',
        # 'schedule': crontab(minute='*'), #for test purposes fire EVERY MINUTE
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
        'args': (),
    },
}