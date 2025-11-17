"""
Core User and Profile models for WealthTrack.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from decimal import Decimal


class User(AbstractUser):
    """
    Custom User model with additional fields for personal finance tracking.
    """
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, default='Auckland, New Zealand')
    timezone = models.CharField(max_length=50, default='Pacific/Auckland')

    # Preferences
    primary_currency = models.CharField(max_length=3, default='NZD')
    date_format = models.CharField(max_length=20, default='DD/MM/YYYY')
    fiscal_year_start = models.IntegerField(default=1, help_text='Month number (1-12)')

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    low_balance_alerts = models.BooleanField(default=True)
    bill_reminders = models.BooleanField(default=True)
    budget_warnings = models.BooleanField(default=True)
    goal_milestones = models.BooleanField(default=True)
    unusual_spending_alerts = models.BooleanField(default=True)
    weekly_summary = models.BooleanField(default=True)
    monthly_summary = models.BooleanField(default=True)

    # Security
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def age(self):
        """Calculate user's age from date of birth."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class UserSettings(models.Model):
    """
    Extended user settings and preferences.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')

    # Display preferences
    theme = models.CharField(
        max_length=10,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='auto'
    )
    accent_color = models.CharField(max_length=7, default='#2563EB')
    font_size = models.CharField(
        max_length=10,
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
        default='medium'
    )
    density = models.CharField(
        max_length=15,
        choices=[('compact', 'Compact'), ('comfortable', 'Comfortable'), ('spacious', 'Spacious')],
        default='comfortable'
    )

    # Budget preferences
    budget_period = models.CharField(
        max_length=10,
        choices=[('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')],
        default='monthly'
    )
    rollover_unused_budget = models.BooleanField(default=False)
    budget_start_day = models.IntegerField(default=1, help_text='Day of month (1-31)')

    # Account preferences
    default_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    hide_zero_balance_accounts = models.BooleanField(default=False)

    # Data preferences
    auto_backup_enabled = models.BooleanField(default=True)
    backup_frequency = models.CharField(
        max_length=10,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        default='weekly'
    )

    # Feature flags
    beta_features_enabled = models.BooleanField(default=False)
    developer_mode = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_settings'

    def __str__(self):
        return f"Settings for {self.user.email}"


class NetWorthSnapshot(models.Model):
    """
    Daily snapshot of user's net worth for historical tracking.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='net_worth_snapshots')
    date = models.DateField()

    # Values
    total_assets = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    net_worth = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    # Breakdown
    liquid_cash = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    investments = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    other_assets = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    credit_card_debt = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    loans = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    other_liabilities = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'net_worth_snapshots'
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.date}: {self.net_worth}"

    def save(self, *args, **kwargs):
        """Auto-calculate net worth on save."""
        self.net_worth = self.total_assets - self.total_liabilities
        super().save(*args, **kwargs)


class Insight(models.Model):
    """
    Smart insights and recommendations for users.
    """
    INSIGHT_TYPES = [
        ('spending', 'Spending'),
        ('budget', 'Budget'),
        ('savings', 'Savings'),
        ('income', 'Income'),
        ('investment', 'Investment'),
        ('net_worth', 'Net Worth'),
        ('debt', 'Debt'),
        ('forecast', 'Forecast'),
        ('behavioral', 'Behavioral'),
        ('optimization', 'Optimization'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insights')
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')

    title = models.CharField(max_length=200)
    message = models.TextField()
    action_text = models.CharField(max_length=100, blank=True)
    action_url = models.CharField(max_length=200, blank=True)

    # Metadata
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'insights'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"
