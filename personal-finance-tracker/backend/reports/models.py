"""
Reports and analytics models.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class SavedReport(models.Model):
    """
    User-saved custom reports.
    """
    REPORT_TYPES = [
        ('income_vs_expenses', 'Income vs Expenses'),
        ('spending_by_category', 'Spending by Category'),
        ('cash_flow', 'Cash Flow'),
        ('net_worth', 'Net Worth Over Time'),
        ('budget_performance', 'Budget Performance'),
        ('income_analysis', 'Income Analysis'),
        ('expense_analysis', 'Expense Analysis'),
        ('investment_performance', 'Investment Performance'),
        ('debt_progress', 'Debt Payoff Progress'),
        ('merchant_analysis', 'Merchant Analysis'),
        ('tag_analysis', 'Tag Analysis'),
        ('tax_summary', 'Tax Summary'),
        ('custom', 'Custom Report'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_reports')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)

    # Filters and configuration stored as JSON
    config = models.JSONField(
        default=dict,
        help_text='Report configuration including filters, date ranges, grouping, etc.'
    )

    # Display
    is_favorite = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'saved_reports'
        ordering = ['-is_favorite', '-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return self.name


class ScheduledReport(models.Model):
    """
    Scheduled email delivery of reports.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_reports')
    saved_report = models.ForeignKey(SavedReport, on_delete=models.CASCADE, related_name='schedules')

    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    email_to = models.EmailField(help_text='Email address to send report to')

    # Schedule settings
    next_send_date = models.DateField()
    last_sent_date = models.DateField(null=True, blank=True)

    # Format
    format = models.CharField(
        max_length=10,
        choices=[
            ('pdf', 'PDF'),
            ('csv', 'CSV'),
            ('excel', 'Excel'),
        ],
        default='pdf'
    )

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'scheduled_reports'
        ordering = ['next_send_date']
        indexes = [
            models.Index(fields=['user', 'next_send_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.saved_report.name} - {self.get_frequency_display()}"

    def calculate_next_send_date(self):
        """Calculate next send date based on frequency."""
        from dateutil.relativedelta import relativedelta

        current = self.next_send_date

        if self.frequency == 'daily':
            return current + relativedelta(days=1)
        elif self.frequency == 'weekly':
            return current + relativedelta(weeks=1)
        elif self.frequency == 'monthly':
            return current + relativedelta(months=1)
        elif self.frequency == 'quarterly':
            return current + relativedelta(months=3)
        elif self.frequency == 'yearly':
            return current + relativedelta(years=1)

        return current


class SpendingPattern(models.Model):
    """
    Detected spending patterns and trends.
    """
    PATTERN_TYPES = [
        ('daily', 'Daily Pattern'),
        ('weekly', 'Weekly Pattern'),
        ('monthly', 'Monthly Pattern'),
        ('seasonal', 'Seasonal Pattern'),
        ('anomaly', 'Anomaly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spending_patterns')

    pattern_type = models.CharField(max_length=15, choices=PATTERN_TYPES)
    category = models.ForeignKey(
        'transactions.Category',
        on_delete=models.CASCADE,
        related_name='spending_patterns',
        null=True,
        blank=True
    )

    # Pattern details
    description = models.TextField()
    average_amount = models.DecimalField(max_digits=15, decimal_places=2)
    frequency = models.CharField(max_length=100, blank=True)

    # Detection date
    detected_at = models.DateTimeField(auto_now_add=True)

    # Confidence score (0-100)
    confidence_score = models.IntegerField(default=0)

    # Data
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'spending_patterns'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['user', '-detected_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_pattern_type_display()}"


class FinancialHealthScore(models.Model):
    """
    Overall financial health score calculated periodically.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='health_scores')
    date = models.DateField()

    # Overall score (0-100)
    total_score = models.IntegerField()

    # Component scores
    savings_rate_score = models.IntegerField(help_text='Based on savings rate')
    debt_score = models.IntegerField(help_text='Based on debt-to-income ratio')
    emergency_fund_score = models.IntegerField(help_text='Based on months of expenses covered')
    budget_adherence_score = models.IntegerField(help_text='Based on budget performance')
    net_worth_growth_score = models.IntegerField(help_text='Based on net worth trend')
    diversification_score = models.IntegerField(help_text='Based on investment diversification')

    # Recommendations
    recommendations = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'financial_health_scores'
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.date}: {self.total_score}/100"

    def calculate_total_score(self):
        """Calculate total score from component scores."""
        self.total_score = (
            self.savings_rate_score * 0.25 +
            self.debt_score * 0.20 +
            self.emergency_fund_score * 0.20 +
            self.budget_adherence_score * 0.15 +
            self.net_worth_growth_score * 0.15 +
            self.diversification_score * 0.05
        )
        return int(self.total_score)
