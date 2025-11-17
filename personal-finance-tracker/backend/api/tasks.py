"""
Celery tasks for user and net worth management.
"""
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal

from .models import NetWorthSnapshot
from accounts.models import Account

User = get_user_model()


@shared_task
def create_daily_net_worth_snapshot():
    """Create daily net worth snapshot for all users."""
    today = timezone.now().date()
    users = User.objects.filter(is_active=True)

    for user in users:
        # Check if snapshot already exists
        if NetWorthSnapshot.objects.filter(user=user, date=today).exists():
            continue

        # Calculate totals
        assets = Account.objects.filter(
            user=user,
            status='active',
            is_excluded_from_totals=False
        ).filter(
            account_type__in=['bank', 'savings', 'investment', 'asset']
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

        liabilities = Account.objects.filter(
            user=user,
            status='active',
            is_excluded_from_totals=False
        ).filter(
            account_type__in=['credit_card', 'loan', 'liability']
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

        # Get breakdowns
        liquid_cash = Account.objects.filter(
            user=user,
            account_type__in=['bank', 'savings'],
            status='active'
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

        investments = Account.objects.filter(
            user=user,
            account_type='investment',
            status='active'
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

        other_assets = assets - liquid_cash - investments

        credit_card_debt = Account.objects.filter(
            user=user,
            account_type='credit_card',
            status='active'
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

        loans = Account.objects.filter(
            user=user,
            account_type='loan',
            status='active'
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

        other_liabilities = liabilities - credit_card_debt - loans

        # Create snapshot
        NetWorthSnapshot.objects.create(
            user=user,
            date=today,
            total_assets=assets,
            total_liabilities=abs(liabilities),
            liquid_cash=liquid_cash,
            investments=investments,
            other_assets=other_assets,
            credit_card_debt=abs(credit_card_debt),
            loans=abs(loans),
            other_liabilities=abs(other_liabilities)
        )

    return f"Created net worth snapshots for {users.count()} users"
