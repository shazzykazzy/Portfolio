"""
Financial goals and milestones tracking.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone


class Goal(models.Model):
    """
    Financial goals and targets.
    """
    GOAL_TYPES = [
        ('savings', 'Savings Goal'),
        ('debt_payoff', 'Debt Payoff'),
        ('net_worth', 'Net Worth Goal'),
        ('investment', 'Investment Goal'),
        ('purchase', 'Purchase Goal'),
        ('income', 'Income Goal'),
        ('emergency_fund', 'Emergency Fund'),
        ('custom', 'Custom Goal'),
    ]

    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals')

    # Basic info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')

    # Target
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    target_date = models.DateField(null=True, blank=True)

    # Tracking
    linked_accounts = models.ManyToManyField(
        'accounts.Account',
        related_name='goals',
        blank=True,
        help_text='Accounts to auto-track progress'
    )
    auto_track = models.BooleanField(
        default=False,
        help_text='Automatically update current_amount from linked accounts'
    )

    # Display
    icon = models.CharField(max_length=50, default='target')
    color = models.CharField(max_length=7, default='#10B981')

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'goals'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return self.name

    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.target_amount > 0:
            return min((self.current_amount / self.target_amount) * 100, 100)
        return 0

    @property
    def remaining_amount(self):
        """Calculate remaining amount to reach goal."""
        return max(self.target_amount - self.current_amount, Decimal('0'))

    @property
    def days_until_target(self):
        """Calculate days until target date."""
        if self.target_date:
            today = timezone.now().date()
            if self.target_date > today:
                return (self.target_date - today).days
        return None

    @property
    def is_on_track(self):
        """Check if goal is on track."""
        if not self.target_date or self.target_amount == 0:
            return True

        today = timezone.now().date()
        if self.target_date <= today:
            return self.current_amount >= self.target_amount

        # Calculate expected progress
        total_days = (self.target_date - self.created_at.date()).days
        days_elapsed = (today - self.created_at.date()).days

        if total_days > 0:
            expected_amount = self.target_amount * (days_elapsed / total_days)
            # Allow 10% tolerance
            return self.current_amount >= expected_amount * Decimal('0.9')

        return True

    @property
    def required_monthly_savings(self):
        """Calculate required monthly savings to reach goal."""
        if self.target_date and self.remaining_amount > 0:
            today = timezone.now().date()
            if self.target_date > today:
                months_remaining = (
                    (self.target_date.year - today.year) * 12 +
                    (self.target_date.month - today.month)
                )
                if months_remaining > 0:
                    return self.remaining_amount / months_remaining

        return Decimal('0')

    @property
    def projected_completion_date(self):
        """Estimate completion date based on current progress."""
        if self.current_amount == 0 or self.remaining_amount == 0:
            return None

        # Calculate average monthly progress
        from dateutil.relativedelta import relativedelta

        today = timezone.now().date()
        months_elapsed = relativedelta(today, self.created_at.date()).months or 1

        monthly_average = self.current_amount / months_elapsed

        if monthly_average > 0:
            months_to_complete = self.remaining_amount / monthly_average
            return today + relativedelta(months=int(months_to_complete))

        return None

    def update_from_linked_accounts(self):
        """Update current_amount from linked accounts."""
        if self.auto_track and self.linked_accounts.exists():
            self.current_amount = sum(
                account.current_balance for account in self.linked_accounts.all()
            )
            self.save()

    def check_completion(self):
        """Check if goal is completed and update status."""
        if self.status == 'active' and self.current_amount >= self.target_amount:
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()

            # Create milestone
            Milestone.objects.create(
                user=self.user,
                goal=self,
                name=f"Completed: {self.name}",
                description=f"Reached {self.goal_type} goal of ${self.target_amount}",
                milestone_type='goal_completed',
                amount=self.target_amount
            )


class GoalContribution(models.Model):
    """
    Manual contributions to goals.
    """
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='contributions')
    date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    notes = models.TextField(blank=True)

    # Linked transaction
    transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goal_contribution'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'goal_contributions'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['goal', '-date']),
        ]

    def __str__(self):
        return f"{self.goal.name} - {self.date}: {self.amount}"

    def save(self, *args, **kwargs):
        """Update goal current_amount on save."""
        super().save(*args, **kwargs)
        self.goal.current_amount += self.amount
        self.goal.save()
        self.goal.check_completion()


class Milestone(models.Model):
    """
    Financial milestones and achievements.
    """
    MILESTONE_TYPES = [
        ('net_worth', 'Net Worth Milestone'),
        ('debt_free', 'Debt Free'),
        ('investment', 'Investment Milestone'),
        ('savings', 'Savings Milestone'),
        ('goal_completed', 'Goal Completed'),
        ('first_investment', 'First Investment'),
        ('budget_perfect', 'Perfect Budget Month'),
        ('savings_streak', 'Savings Streak'),
        ('custom', 'Custom Milestone'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='milestones')

    name = models.CharField(max_length=200)
    description = models.TextField()
    milestone_type = models.CharField(max_length=20, choices=MILESTONE_TYPES)

    # Amount (if applicable)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Linked goal (if applicable)
    goal = models.ForeignKey(
        Goal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milestones'
    )

    # Display
    icon = models.CharField(max_length=50, default='trophy')
    color = models.CharField(max_length=7, default='#F59E0B')

    # Status
    is_celebrated = models.BooleanField(default=False)
    celebrated_at = models.DateTimeField(null=True, blank=True)

    achieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'milestones'
        ordering = ['-achieved_at']
        indexes = [
            models.Index(fields=['user', '-achieved_at']),
        ]

    def __str__(self):
        return self.name

    def celebrate(self):
        """Mark milestone as celebrated."""
        if not self.is_celebrated:
            self.is_celebrated = True
            self.celebrated_at = timezone.now()
            self.save()
