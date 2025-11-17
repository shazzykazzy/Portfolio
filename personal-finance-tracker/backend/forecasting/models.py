"""
Financial forecasting and scenario planning models.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone


class Forecast(models.Model):
    """
    Financial forecast for future periods.
    """
    FORECAST_TYPES = [
        ('cash_flow', 'Cash Flow Forecast'),
        ('net_worth', 'Net Worth Forecast'),
        ('balance', 'Account Balance Forecast'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forecasts')

    forecast_type = models.CharField(max_length=20, choices=FORECAST_TYPES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Date range
    start_date = models.DateField()
    end_date = models.DateField()

    # Forecast method
    based_on_historical = models.BooleanField(default=True)
    include_scheduled = models.BooleanField(default=True)
    include_recurring = models.BooleanField(default=True)
    include_budgets = models.BooleanField(default=True)

    # Assumptions
    expected_income_growth = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text='Annual income growth rate percentage'
    )
    expected_expense_growth = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0'),
        help_text='Annual expense growth rate percentage'
    )
    expected_investment_return = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('7.0'),
        help_text='Expected annual investment return percentage'
    )

    # Status
    is_active = models.BooleanField(default=True)
    last_calculated = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'forecasts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'forecast_type']),
        ]

    def __str__(self):
        return self.name


class ForecastDataPoint(models.Model):
    """
    Individual data points in a forecast.
    """
    forecast = models.ForeignKey(Forecast, on_delete=models.CASCADE, related_name='data_points')
    date = models.DateField()

    # Values
    projected_value = models.DecimalField(max_digits=15, decimal_places=2)
    lower_bound = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Conservative estimate (90% confidence)'
    )
    upper_bound = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Optimistic estimate (90% confidence)'
    )

    # Optional breakdown
    projected_income = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    projected_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    projected_savings = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'forecast_data_points'
        unique_together = ['forecast', 'date']
        ordering = ['date']
        indexes = [
            models.Index(fields=['forecast', 'date']),
        ]

    def __str__(self):
        return f"{self.forecast.name} - {self.date}: {self.projected_value}"


class Scenario(models.Model):
    """
    What-if scenario planning.
    """
    SCENARIO_TYPES = [
        ('base', 'Base Case'),
        ('conservative', 'Conservative'),
        ('optimistic', 'Optimistic'),
        ('custom', 'Custom'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scenarios')

    name = models.CharField(max_length=200)
    description = models.TextField()
    scenario_type = models.CharField(max_length=15, choices=SCENARIO_TYPES, default='custom')

    # Base scenario to clone from
    parent_scenario = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='variants'
    )

    # Date range
    start_date = models.DateField()
    end_date = models.DateField()

    # Assumptions can be stored as JSON for flexibility
    assumptions = models.JSONField(
        default=dict,
        help_text='Scenario assumptions as JSON'
    )

    # Results summary
    projected_net_worth = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    projected_savings = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_favorite = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scenarios'
        ordering = ['-is_favorite', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return self.name


class ScenarioEvent(models.Model):
    """
    Events within a scenario (e.g., 'Buy house', 'Get raise', 'Lose job').
    """
    EVENT_TYPES = [
        ('income_change', 'Income Change'),
        ('expense_change', 'Expense Change'),
        ('major_purchase', 'Major Purchase'),
        ('windfall', 'Windfall'),
        ('debt_payoff', 'Debt Payoff'),
        ('investment', 'Investment'),
        ('market_change', 'Market Change'),
        ('custom', 'Custom Event'),
    ]

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name='events')

    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateField()

    # Impact
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=10,
        choices=[
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        blank=True
    )

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scenario_events'
        ordering = ['date']
        indexes = [
            models.Index(fields=['scenario', 'date']),
        ]

    def __str__(self):
        return f"{self.scenario.name} - {self.name}"


class CashFlowProjection(models.Model):
    """
    Projected cash flow for upcoming periods.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cash_flow_projections')
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='cash_flow_projections',
        null=True,
        blank=True,
        help_text='Null for overall cash flow'
    )

    date = models.DateField()

    # Projected values
    projected_balance = models.DecimalField(max_digits=15, decimal_places=2)
    projected_income = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    projected_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    projected_net = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))

    # Confidence
    confidence_level = models.CharField(
        max_length=10,
        choices=[
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ],
        default='medium'
    )

    # Alert if balance goes below threshold
    is_low_balance_alert = models.BooleanField(default=False)
    low_balance_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cash_flow_projections'
        unique_together = ['user', 'account', 'date']
        ordering = ['date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['account', 'date']),
        ]

    def __str__(self):
        account_name = self.account.name if self.account else 'Overall'
        return f"{account_name} - {self.date}: {self.projected_balance}"

    def check_low_balance(self):
        """Check if projected balance is below threshold."""
        if self.low_balance_threshold:
            if self.projected_balance < self.low_balance_threshold:
                self.is_low_balance_alert = True
                # Create insight
                from api.models import Insight
                Insight.objects.get_or_create(
                    user=self.user,
                    insight_type='forecast',
                    title=f'Low Balance Alert: {self.date}',
                    defaults={
                        'message': f'Your {self.account.name if self.account else "overall"} balance is projected to be ${self.projected_balance} on {self.date}, below your threshold of ${self.low_balance_threshold}.',
                        'priority': 'high',
                        'action_text': 'View Forecast',
                        'action_url': '/forecasting',
                    }
                )
