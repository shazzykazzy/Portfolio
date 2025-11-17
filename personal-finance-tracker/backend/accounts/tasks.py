"""
Celery tasks for accounts.
"""
from celery import shared_task
from django.utils import timezone
from .models import Account, BalanceHistory


@shared_task
def create_daily_balance_snapshots():
    """Create daily balance snapshots for all active accounts."""
    today = timezone.now().date()
    accounts = Account.objects.filter(status='active')

    created_count = 0
    for account in accounts:
        # Check if snapshot already exists
        if not BalanceHistory.objects.filter(account=account, date=today).exists():
            BalanceHistory.objects.create(
                account=account,
                date=today,
                balance=account.current_balance,
                available_balance=account.available_balance
            )
            created_count += 1

    return f"Created {created_count} balance snapshots"
