"""
Account models for managing bank accounts, credit cards, investments, assets, and liabilities.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal
from cryptography.fernet import Fernet


class Account(models.Model):
    """
    Main Account model supporting multiple account types.
    """
    ACCOUNT_TYPES = [
        ('bank', 'Bank Account'),
        ('savings', 'Savings Account'),
        ('credit_card', 'Credit Card'),
        ('investment', 'Investment Account'),
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('loan', 'Loan'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')

    # Basic Info
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    institution = models.CharField(max_length=200, blank=True, help_text='Bank or institution name')
    account_number = models.CharField(max_length=255, blank=True, help_text='Encrypted account number')
    currency = models.CharField(max_length=3, default='NZD')

    # Balance Info
    current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    available_balance = models.DecimalField(
        max_digits=15, decimal_places=2,
        null=True,
        blank=True,
        help_text='Available balance (for credit cards and overdrafts)'
    )

    # Credit Card Specific
    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Credit card limit'
    )
    statement_date = models.IntegerField(
        null=True,
        blank=True,
        help_text='Day of month for statement (1-31)'
    )
    payment_due_date = models.IntegerField(
        null=True,
        blank=True,
        help_text='Day of month for payment (1-31)'
    )

    # Loan Specific
    original_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Original loan amount'
    )
    interest_rate = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Annual interest rate percentage'
    )
    monthly_payment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Monthly payment amount'
    )
    payoff_date = models.DateField(null=True, blank=True, help_text='Expected payoff date')

    # Asset Specific
    purchase_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Original purchase price for assets'
    )
    purchase_date = models.DateField(null=True, blank=True)
    depreciation_rate = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Annual depreciation rate percentage'
    )

    # Display Options
    color = models.CharField(max_length=7, default='#2563EB', help_text='Hex color code')
    icon = models.CharField(max_length=50, default='bank', help_text='Icon name')
    display_order = models.IntegerField(default=0)
    is_hidden = models.BooleanField(default=False)

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_excluded_from_totals = models.BooleanField(
        default=False,
        help_text='Exclude from net worth calculations (e.g., business accounts)'
    )

    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts'
        ordering = ['display_order', '-created_at']
        indexes = [
            models.Index(fields=['user', 'account_type']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

    @property
    def available_credit(self):
        """Calculate available credit for credit cards."""
        if self.account_type == 'credit_card' and self.credit_limit:
            return self.credit_limit + self.current_balance  # Balance is negative for debt
        return None

    @property
    def is_asset(self):
        """Check if account is an asset (positive contribution to net worth)."""
        return self.account_type in ['bank', 'savings', 'investment', 'asset']

    @property
    def is_liability(self):
        """Check if account is a liability (negative contribution to net worth)."""
        return self.account_type in ['credit_card', 'liability', 'loan']

    def calculate_current_value(self):
        """Calculate current value for depreciating assets."""
        if self.account_type == 'asset' and self.purchase_price and self.depreciation_rate:
            from django.utils import timezone
            from dateutil.relativedelta import relativedelta

            if self.purchase_date:
                months_owned = relativedelta(timezone.now().date(), self.purchase_date).months
                years_owned = months_owned / 12
                depreciation = self.purchase_price * (self.depreciation_rate / 100) * Decimal(str(years_owned))
                return max(Decimal('0.00'), self.purchase_price - depreciation)
        return self.current_balance


class BalanceHistory(models.Model):
    """
    Historical balance tracking for accounts.
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='balance_history')
    date = models.DateField()
    balance = models.DecimalField(max_digits=15, decimal_places=2)

    # Optional breakdown
    available_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'balance_history'
        unique_together = ['account', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['account', '-date']),
        ]

    def __str__(self):
        return f"{self.account.name} - {self.date}: {self.balance}"


class AccountGroup(models.Model):
    """
    Group accounts together (e.g., 'Emergency Fund' = multiple savings accounts).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account_groups')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#2563EB')
    icon = models.CharField(max_length=50, default='folder')

    accounts = models.ManyToManyField(Account, related_name='groups', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'account_groups'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_balance(self):
        """Calculate total balance of all accounts in group."""
        return sum(account.current_balance for account in self.accounts.all())
