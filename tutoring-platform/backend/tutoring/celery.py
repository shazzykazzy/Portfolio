"""
Celery configuration for background tasks
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutoring.settings')

app = Celery('tutoring')

# Load task modules from all registered Django apps
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks schedule
app.conf.beat_schedule = {
    # Send session reminders 24 hours before
    'send-24hr-session-reminders': {
        'task': 'communications.tasks.send_session_reminders_24hr',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
    # Send session reminders 1 hour before
    'send-1hr-session-reminders': {
        'task': 'communications.tasks.send_session_reminders_1hr',
        'schedule': crontab(minute='*/15'),  # Run every 15 minutes
    },
    # Send payment reminders for overdue invoices
    'send-payment-reminders': {
        'task': 'finances.tasks.send_payment_reminders',
        'schedule': crontab(hour=10, minute=0, day_of_week=1),  # Mondays at 10 AM
    },
    # Generate and send monthly progress reports
    'send-monthly-progress-reports': {
        'task': 'students.tasks.send_monthly_progress_reports',
        'schedule': crontab(hour=9, minute=0, day_of_month=1),  # 1st of each month at 9 AM
    },
    # Send exam preparation reminders
    'send-exam-prep-reminders': {
        'task': 'communications.tasks.send_exam_prep_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    # Check for package expiry and send notifications
    'check-package-expiry': {
        'task': 'finances.tasks.check_package_expiry',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
    # Re-engage inactive students
    'reengage-inactive-students': {
        'task': 'communications.tasks.reengage_inactive_students',
        'schedule': crontab(hour=10, minute=0, day_of_week=3),  # Wednesdays at 10 AM
    },
    # Generate weekly business summary
    'weekly-business-summary': {
        'task': 'analytics.tasks.send_weekly_business_summary',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Mondays at 8 AM
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
