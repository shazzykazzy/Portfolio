"""
Transaction models for tracking income, expenses, and transfers.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal


class Category(models.Model):
    """
    Category and subcategory system for transactions.
    """
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True,
        help_text='Null for system default categories'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )

    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)

    # Display options
    color = models.CharField(max_length=7, default='#6B7280')
    icon = models.CharField(max_length=50, default='tag')
    display_order = models.IntegerField(default=0)

    # Settings
    is_hidden = models.BooleanField(default=False)
    exclude_from_budgets = models.BooleanField(default=False)
    exclude_from_reports = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        ordering = ['display_order', 'name']
        verbose_name_plural = 'categories'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    @property
    def full_path(self):
        """Get full category path."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class Tag(models.Model):
    """
    Custom tags for transactions.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#6B7280')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tags'
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """
    Main transaction model for income, expenses, and transfers.
    """
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
        ('investment_buy', 'Investment Buy'),
        ('investment_sell', 'Investment Sell'),
        ('credit_payment', 'Credit Card Payment'),
        ('loan_payment', 'Loan Payment'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')

    # Basic info
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    # Account info
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    to_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='transfer_in',
        null=True,
        blank=True,
        help_text='For transfers, the destination account'
    )

    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    tags = models.ManyToManyField(Tag, related_name='transactions', blank=True)

    # Payee/Merchant
    payee = models.CharField(max_length=200, blank=True)
    merchant_location = models.CharField(max_length=200, blank=True)

    # Recurring
    is_recurring = models.BooleanField(default=False)
    recurring_transaction = models.ForeignKey(
        'RecurringTransaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_transactions'
    )

    # Split transactions
    is_split = models.BooleanField(default=False)
    parent_transaction = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='split_transactions'
    )

    # Attachments
    receipt = models.ImageField(upload_to='receipts/', null=True, blank=True)

    # Status
    is_pending = models.BooleanField(default=False)
    is_cleared = models.BooleanField(default=True)
    is_reconciled = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['account', '-date']),
            models.Index(fields=['category']),
            models.Index(fields=['payee']),
        ]

    def __str__(self):
        return f"{self.date} - {self.description}: {self.amount}"

    def save(self, *args, **kwargs):
        """Update account balances on save."""
        is_new = self.pk is None
        old_transaction = None if is_new else Transaction.objects.get(pk=self.pk)

        super().save(*args, **kwargs)

        # Update account balances
        if not self.is_pending and not self.parent_transaction:
            self._update_account_balances(old_transaction)

    def _update_account_balances(self, old_transaction=None):
        """Update account balances based on transaction type."""
        from accounts.models import Account

        if old_transaction:
            # Reverse old transaction effect
            self._apply_balance_change(
                old_transaction.account,
                old_transaction.amount,
                old_transaction.transaction_type,
                reverse=True
            )
            if old_transaction.to_account:
                self._apply_balance_change(
                    old_transaction.to_account,
                    old_transaction.amount,
                    old_transaction.transaction_type,
                    reverse=True,
                    is_destination=True
                )

        # Apply new transaction effect
        self._apply_balance_change(self.account, self.amount, self.transaction_type)
        if self.to_account:
            self._apply_balance_change(
                self.to_account,
                self.amount,
                self.transaction_type,
                is_destination=True
            )

    def _apply_balance_change(self, account, amount, trans_type, reverse=False, is_destination=False):
        """Apply balance change to account."""
        multiplier = -1 if reverse else 1

        if trans_type == 'income':
            account.current_balance += amount * multiplier
        elif trans_type == 'expense':
            account.current_balance -= amount * multiplier
        elif trans_type == 'transfer':
            if is_destination:
                account.current_balance += amount * multiplier
            else:
                account.current_balance -= amount * multiplier
        elif trans_type in ['investment_buy', 'credit_payment', 'loan_payment']:
            account.current_balance -= amount * multiplier
        elif trans_type == 'investment_sell':
            account.current_balance += amount * multiplier

        account.save()


class RecurringTransaction(models.Model):
    """
    Template for recurring transactions.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recurring_transactions')

    # Template info (same as Transaction)
    transaction_type = models.CharField(max_length=20, choices=Transaction.TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_variable_amount = models.BooleanField(
        default=False,
        help_text='Amount varies (estimate only)'
    )
    description = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='recurring_from')
    to_account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='recurring_to',
        null=True,
        blank=True
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    payee = models.CharField(max_length=200, blank=True)

    # Recurrence settings
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text='Leave blank for indefinite')
    next_due_date = models.DateField()

    # Status
    is_active = models.BooleanField(default=True)
    auto_create = models.BooleanField(
        default=False,
        help_text='Automatically create transactions or just remind'
    )
    remind_before_days = models.IntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recurring_transactions'
        ordering = ['next_due_date']
        indexes = [
            models.Index(fields=['user', 'next_due_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.description} ({self.get_frequency_display()})"

    def calculate_next_due_date(self):
        """Calculate next due date based on frequency."""
        from dateutil.relativedelta import relativedelta

        current = self.next_due_date

        if self.frequency == 'daily':
            return current + relativedelta(days=1)
        elif self.frequency == 'weekly':
            return current + relativedelta(weeks=1)
        elif self.frequency == 'biweekly':
            return current + relativedelta(weeks=2)
        elif self.frequency == 'monthly':
            return current + relativedelta(months=1)
        elif self.frequency == 'quarterly':
            return current + relativedelta(months=3)
        elif self.frequency == 'yearly':
            return current + relativedelta(years=1)

        return current


class Bill(models.Model):
    """
    Bill tracking and reminders.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bills')

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='bills')

    # Amount
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_variable = models.BooleanField(default=False)

    # Due date
    due_day = models.IntegerField(help_text='Day of month (1-31)')
    remind_before_days = models.IntegerField(default=3)

    # Status
    is_active = models.BooleanField(default=True)
    is_autopay = models.BooleanField(default=False)

    # Linked recurring transaction
    recurring_transaction = models.OneToOneField(
        RecurringTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bill'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bills'
        ordering = ['due_day']
        indexes = [
            models.Index(fields=['user', 'due_day']),
        ]

    def __str__(self):
        return self.name


class TransactionRule(models.Model):
    """
    Auto-categorization rules for transactions.
    """
    FIELD_CHOICES = [
        ('description', 'Description'),
        ('payee', 'Payee'),
        ('amount', 'Amount'),
    ]

    CONDITION_CHOICES = [
        ('contains', 'Contains'),
        ('starts_with', 'Starts with'),
        ('ends_with', 'Ends with'),
        ('equals', 'Equals'),
        ('greater_than', 'Greater than'),
        ('less_than', 'Less than'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transaction_rules')

    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text='Higher priority rules run first')

    # Conditions
    field = models.CharField(max_length=20, choices=FIELD_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    value = models.CharField(max_length=200)

    # Actions
    set_category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    set_payee = models.CharField(max_length=200, blank=True)
    add_tags = models.ManyToManyField(Tag, related_name='+', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transaction_rules'
        ordering = ['-priority', 'name']

    def __str__(self):
        return self.name

    def matches(self, transaction):
        """Check if transaction matches this rule."""
        field_value = getattr(transaction, self.field, '')

        if self.condition == 'contains':
            return self.value.lower() in str(field_value).lower()
        elif self.condition == 'starts_with':
            return str(field_value).lower().startswith(self.value.lower())
        elif self.condition == 'ends_with':
            return str(field_value).lower().endswith(self.value.lower())
        elif self.condition == 'equals':
            return str(field_value).lower() == self.value.lower()
        elif self.condition == 'greater_than':
            return float(field_value) > float(self.value)
        elif self.condition == 'less_than':
            return float(field_value) < float(self.value)

        return False

    def apply(self, transaction):
        """Apply rule actions to transaction."""
        if self.set_category:
            transaction.category = self.set_category
        if self.set_payee:
            transaction.payee = self.set_payee

        transaction.save()

        if self.add_tags.exists():
            transaction.tags.add(*self.add_tags.all())
