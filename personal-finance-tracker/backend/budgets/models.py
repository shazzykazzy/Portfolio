"""
Budget models for tracking spending limits and goals.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone


class Budget(models.Model):
    """
    Main budget model - can be monthly, weekly, or annual.
    """
    PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    BUDGET_TYPES = [
        ('standard', 'Standard'),
        ('percentage', 'Percentage of Income'),
        ('zero_based', 'Zero-Based'),
        ('envelope', 'Envelope'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Period
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField()

    # Budget type and settings
    budget_type = models.CharField(max_length=15, choices=BUDGET_TYPES, default='standard')
    rollover_unused = models.BooleanField(
        default=False,
        help_text='Rollover unused budget to next period'
    )

    # Targets
    target_income = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Target income for period'
    )
    target_savings = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Target savings for period'
    )
    target_savings_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Target savings rate percentage'
    )

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budgets'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', '-start_date']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

    @property
    def is_current(self):
        """Check if budget is for current period."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    @property
    def days_remaining(self):
        """Calculate days remaining in budget period."""
        if self.is_current:
            today = timezone.now().date()
            return (self.end_date - today).days
        return 0

    @property
    def days_elapsed(self):
        """Calculate days elapsed in budget period."""
        if self.is_current:
            today = timezone.now().date()
            return (today - self.start_date).days
        return (self.end_date - self.start_date).days

    @property
    def total_budgeted(self):
        """Calculate total budgeted amount across all items."""
        return sum(item.amount for item in self.items.all())

    def get_actual_spending(self):
        """Get actual spending for this budget period."""
        from transactions.models import Transaction

        transactions = Transaction.objects.filter(
            user=self.user,
            date__gte=self.start_date,
            date__lte=self.end_date,
            transaction_type='expense',
            is_pending=False
        )

        return sum(t.amount for t in transactions)

    def get_actual_income(self):
        """Get actual income for this budget period."""
        from transactions.models import Transaction

        transactions = Transaction.objects.filter(
            user=self.user,
            date__gte=self.start_date,
            date__lte=self.end_date,
            transaction_type='income',
            is_pending=False
        )

        return sum(t.amount for t in transactions)

    def get_savings_rate(self):
        """Calculate actual savings rate."""
        income = self.get_actual_income()
        spending = self.get_actual_spending()

        if income > 0:
            savings = income - spending
            return (savings / income) * 100
        return 0


class BudgetItem(models.Model):
    """
    Individual category budget within a budget period.
    """
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey('transactions.Category', on_delete=models.CASCADE, related_name='budget_items')

    # Amount
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_percentage = models.BooleanField(
        default=False,
        help_text='Amount is percentage of income'
    )

    # Rollover from previous period
    rollover_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Unused amount from previous period'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budget_items'
        unique_together = ['budget', 'category']
        ordering = ['category__name']

    def __str__(self):
        return f"{self.budget.name} - {self.category.name}: {self.amount}"

    @property
    def effective_amount(self):
        """Get effective budget amount including rollover."""
        return self.amount + self.rollover_amount

    def get_actual_spending(self):
        """Get actual spending for this category in budget period."""
        from transactions.models import Transaction

        transactions = Transaction.objects.filter(
            user=self.budget.user,
            category=self.category,
            date__gte=self.budget.start_date,
            date__lte=self.budget.end_date,
            transaction_type='expense',
            is_pending=False
        )

        # Include subcategories
        subcategories = self.category.subcategories.all()
        if subcategories.exists():
            transactions = transactions | Transaction.objects.filter(
                user=self.budget.user,
                category__in=subcategories,
                date__gte=self.budget.start_date,
                date__lte=self.budget.end_date,
                transaction_type='expense',
                is_pending=False
            )

        return sum(t.amount for t in transactions)

    @property
    def remaining(self):
        """Calculate remaining budget amount."""
        return self.effective_amount - self.get_actual_spending()

    @property
    def percentage_used(self):
        """Calculate percentage of budget used."""
        if self.effective_amount > 0:
            return (self.get_actual_spending() / self.effective_amount) * 100
        return 0

    @property
    def is_overspent(self):
        """Check if over budget."""
        return self.get_actual_spending() > self.effective_amount

    @property
    def pace_indicator(self):
        """
        Calculate if on track, overspending, or underspending.
        Returns: 'on_track', 'overspending', 'underspending'
        """
        if not self.budget.is_current:
            return 'completed'

        days_total = (self.budget.end_date - self.budget.start_date).days
        days_elapsed = self.budget.days_elapsed

        if days_total > 0:
            expected_spending = self.effective_amount * (days_elapsed / days_total)
            actual_spending = self.get_actual_spending()

            # Allow 10% tolerance
            if actual_spending > expected_spending * Decimal('1.1'):
                return 'overspending'
            elif actual_spending < expected_spending * Decimal('0.9'):
                return 'underspending'
            return 'on_track'

        return 'on_track'


class BudgetTemplate(models.Model):
    """
    Reusable budget templates.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budget_templates',
        null=True,
        blank=True,
        help_text='Null for system templates'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_system_template = models.BooleanField(default=False)

    # Default settings
    period = models.CharField(max_length=10, choices=Budget.PERIOD_CHOICES, default='monthly')
    budget_type = models.CharField(max_length=15, choices=Budget.BUDGET_TYPES, default='standard')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'budget_templates'
        ordering = ['name']

    def __str__(self):
        return self.name

    def apply_to_budget(self, budget):
        """Apply template items to a budget."""
        for template_item in self.template_items.all():
            BudgetItem.objects.create(
                budget=budget,
                category=template_item.category,
                amount=template_item.amount,
                is_percentage=template_item.is_percentage
            )


class BudgetTemplateItem(models.Model):
    """
    Items within a budget template.
    """
    template = models.ForeignKey(
        BudgetTemplate,
        on_delete=models.CASCADE,
        related_name='template_items'
    )
    category = models.ForeignKey('transactions.Category', on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_percentage = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'budget_template_items'
        unique_together = ['template', 'category']
        ordering = ['category__name']

    def __str__(self):
        return f"{self.template.name} - {self.category.name}"
