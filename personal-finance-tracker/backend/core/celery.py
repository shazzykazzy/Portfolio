"""
Celery configuration for WealthTrack.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('wealthtrack')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'daily-net-worth-snapshot': {
        'task': 'api.tasks.create_daily_net_worth_snapshot',
        'schedule': crontab(hour=0, minute=5),  # Run daily at 00:05
    },
    'daily-balance-snapshot': {
        'task': 'accounts.tasks.create_daily_balance_snapshots',
        'schedule': crontab(hour=0, minute=10),  # Run daily at 00:10
    },
    'update-investment-prices': {
        'task': 'investments.tasks.update_investment_prices',
        'schedule': crontab(hour='*/4'),  # Every 4 hours
    },
    'recalculate-forecasts': {
        'task': 'forecasting.tasks.recalculate_all_forecasts',
        'schedule': crontab(hour=1, minute=0),  # Daily at 01:00
    },
    'process-recurring-transactions': {
        'task': 'transactions.tasks.process_recurring_transactions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 02:00
    },
    'send-bill-reminders': {
        'task': 'transactions.tasks.send_bill_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 09:00
    },
    'generate-insights': {
        'task': 'reports.tasks.generate_daily_insights',
        'schedule': crontab(hour=6, minute=0),  # Daily at 06:00
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
