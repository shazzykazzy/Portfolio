"""
Investment tracking models for portfolio management.
"""
from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone


class InvestmentHolding(models.Model):
    """
    Individual stock or ETF holding within an investment account.
    """
    ASSET_TYPES = [
        ('stock', 'Stock'),
        ('etf', 'ETF'),
        ('mutual_fund', 'Mutual Fund'),
        ('bond', 'Bond'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other'),
    ]

    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='holdings'
    )

    # Asset info
    ticker_symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=15, choices=ASSET_TYPES, default='stock')
    exchange = models.CharField(max_length=50, blank=True, help_text='e.g., NZX, NYSE, NASDAQ')

    # Holdings
    shares = models.DecimalField(max_digits=15, decimal_places=6, default=Decimal('0'))
    average_cost = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=Decimal('0'),
        help_text='Average cost per share/unit'
    )
    current_price = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        default=Decimal('0'),
        help_text='Current market price'
    )

    # Currency
    currency = models.CharField(max_length=3, default='NZD')

    # Metadata
    last_price_update = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'investment_holdings'
        unique_together = ['account', 'ticker_symbol']
        ordering = ['ticker_symbol']
        indexes = [
            models.Index(fields=['account', 'ticker_symbol']),
        ]

    def __str__(self):
        return f"{self.ticker_symbol} - {self.shares} shares"

    @property
    def total_cost(self):
        """Calculate total cost basis."""
        return self.shares * self.average_cost

    @property
    def current_value(self):
        """Calculate current market value."""
        return self.shares * self.current_price

    @property
    def gain_loss(self):
        """Calculate total gain/loss."""
        return self.current_value - self.total_cost

    @property
    def gain_loss_percentage(self):
        """Calculate gain/loss percentage."""
        if self.total_cost > 0:
            return (self.gain_loss / self.total_cost) * 100
        return Decimal('0')

    @property
    def weight_in_portfolio(self):
        """Calculate weight in overall portfolio."""
        portfolio_value = sum(h.current_value for h in self.account.holdings.all())
        if portfolio_value > 0:
            return (self.current_value / portfolio_value) * 100
        return Decimal('0')


class InvestmentTransaction(models.Model):
    """
    Buy/sell transactions for investments.
    """
    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('dividend', 'Dividend'),
        ('split', 'Stock Split'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
    ]

    holding = models.ForeignKey(
        InvestmentHolding,
        on_delete=models.CASCADE,
        related_name='investment_transactions'
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='investment_transactions')

    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    date = models.DateField()

    # Transaction details
    shares = models.DecimalField(max_digits=15, decimal_places=6)
    price_per_share = models.DecimalField(max_digits=15, decimal_places=4)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    # Fees
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))

    # Tax (for realized gains)
    capital_gain = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Capital gain for tax reporting'
    )

    # Linked to main transaction
    transaction = models.OneToOneField(
        'transactions.Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='investment_transaction'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'investment_transactions'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['holding', '-date']),
            models.Index(fields=['user', '-date']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.shares} @ {self.price_per_share}"

    def save(self, *args, **kwargs):
        """Update holding on save."""
        super().save(*args, **kwargs)
        self._update_holding()

    def _update_holding(self):
        """Update holding shares and average cost."""
        holding = self.holding

        if self.transaction_type == 'buy':
            # Update average cost
            old_value = holding.shares * holding.average_cost
            new_value = self.shares * self.price_per_share
            holding.shares += self.shares
            if holding.shares > 0:
                holding.average_cost = (old_value + new_value) / holding.shares

        elif self.transaction_type == 'sell':
            holding.shares -= self.shares
            # Calculate capital gain
            cost_basis = self.shares * holding.average_cost
            proceeds = self.shares * self.price_per_share - self.commission - self.fees
            self.capital_gain = proceeds - cost_basis

        elif self.transaction_type == 'split':
            # shares field contains split ratio (e.g., 2 for 2:1 split)
            holding.shares *= self.shares
            holding.average_cost /= self.shares

        elif self.transaction_type == 'transfer_in':
            holding.shares += self.shares

        elif self.transaction_type == 'transfer_out':
            holding.shares -= self.shares

        holding.save()


class Dividend(models.Model):
    """
    Dividend payments from investments.
    """
    holding = models.ForeignKey(InvestmentHolding, on_delete=models.CASCADE, related_name='dividends')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dividends')

    # Payment details
    payment_date = models.DateField()
    ex_dividend_date = models.DateField(null=True, blank=True)
    amount_per_share = models.DecimalField(max_digits=10, decimal_places=4)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    shares_held = models.DecimalField(max_digits=15, decimal_places=6)

    # Tax
    withholding_tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    net_amount = models.DecimalField(max_digits=15, decimal_places=2)

    # Reinvestment
    is_reinvested = models.BooleanField(default=False)
    reinvestment_transaction = models.ForeignKey(
        InvestmentTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )

    # Linked to main transaction
    transaction = models.OneToOneField(
        'transactions.Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dividend'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dividends'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['holding', '-payment_date']),
            models.Index(fields=['user', '-payment_date']),
        ]

    def __str__(self):
        return f"{self.holding.ticker_symbol} - {self.payment_date}: {self.total_amount}"

    @property
    def dividend_yield(self):
        """Calculate dividend yield."""
        if self.holding.current_price > 0:
            annual_dividend = self.amount_per_share * 4  # Assume quarterly
            return (annual_dividend / self.holding.current_price) * 100
        return Decimal('0')


class PortfolioSnapshot(models.Model):
    """
    Daily snapshot of portfolio value and performance.
    """
    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='portfolio_snapshots'
    )
    date = models.DateField()

    # Values
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)
    total_gain_loss = models.DecimalField(max_digits=15, decimal_places=2)
    gain_loss_percentage = models.DecimalField(max_digits=8, decimal_places=3)

    # Daily change
    day_change = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    day_change_percentage = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('0'))

    # Dividend info
    total_dividends_ytd = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'portfolio_snapshots'
        unique_together = ['account', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['account', '-date']),
        ]

    def __str__(self):
        return f"{self.account.name} - {self.date}: {self.total_value}"


class AssetAllocation(models.Model):
    """
    Target asset allocation for portfolio.
    """
    ASSET_CLASSES = [
        ('nz_stocks', 'NZ Stocks'),
        ('us_stocks', 'US Stocks'),
        ('intl_stocks', 'International Stocks'),
        ('bonds', 'Bonds'),
        ('cash', 'Cash'),
        ('real_estate', 'Real Estate'),
        ('commodities', 'Commodities'),
        ('crypto', 'Cryptocurrency'),
        ('other', 'Other'),
    ]

    account = models.ForeignKey(
        'accounts.Account',
        on_delete=models.CASCADE,
        related_name='asset_allocations'
    )

    asset_class = models.CharField(max_length=20, choices=ASSET_CLASSES)
    target_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'asset_allocations'
        unique_together = ['account', 'asset_class']
        ordering = ['asset_class']

    def __str__(self):
        return f"{self.account.name} - {self.get_asset_class_display()}: {self.target_percentage}%"

    @property
    def current_percentage(self):
        """Calculate current allocation percentage."""
        # This would need to sum up holdings by asset class
        # Simplified for now
        return Decimal('0')

    @property
    def rebalance_needed(self):
        """Check if rebalancing is needed (>5% deviation)."""
        deviation = abs(self.current_percentage - self.target_percentage)
        return deviation > Decimal('5')
