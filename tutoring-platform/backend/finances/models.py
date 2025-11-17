"""
Financial models for invoicing, payments, and packages
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from decimal import Decimal
from accounts.models import User, StudentProfile
from sessions.models import Session


class Package(models.Model):
    """Session packages with discounts"""

    class PackageType(models.TextChoices):
        FIXED = 'FIXED', _('Fixed Number of Sessions')
        TERM = 'TERM', _('Term Package')
        CUSTOM = 'CUSTOM', _('Custom')

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    package_type = models.CharField(
        max_length=20,
        choices=PackageType.choices,
        default=PackageType.FIXED
    )

    # Sessions
    num_sessions = models.IntegerField(help_text="Number of sessions included")
    session_duration_minutes = models.IntegerField(default=60)

    # Pricing
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    base_price_per_session = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=75.00
    )

    # Validity
    validity_months = models.IntegerField(
        default=3,
        help_text="Number of months package is valid for"
    )

    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'num_sessions']

    def __str__(self):
        return f"{self.name} ({self.num_sessions} sessions)"

    @property
    def discounted_price_per_session(self):
        """Calculate discounted price per session"""
        discount_amount = self.base_price_per_session * (self.discount_percentage / Decimal('100'))
        return self.base_price_per_session - discount_amount

    @property
    def total_package_price(self):
        """Calculate total package price"""
        return self.discounted_price_per_session * self.num_sessions


class StudentPackage(models.Model):
    """Package purchased by a student"""

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        EXPIRED = 'EXPIRED', _('Expired')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='packages'
    )
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name='student_packages'
    )

    # Dates
    purchased_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)

    # Usage tracking
    sessions_total = models.IntegerField()
    sessions_used = models.IntegerField(default=0)
    sessions_remaining = models.IntegerField()

    # Pricing (captured at time of purchase)
    price_paid = models.DecimalField(max_digits=8, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=5, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    # Notifications
    expiry_warning_sent = models.BooleanField(default=False)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchased_date']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.package.name} ({self.sessions_remaining} left)"

    def use_session(self):
        """Mark a session as used from this package"""
        if self.sessions_remaining > 0:
            self.sessions_used += 1
            self.sessions_remaining -= 1
            if self.sessions_remaining == 0:
                self.status = self.Status.COMPLETED
            self.save()


class Invoice(models.Model):
    """Invoices for tutoring sessions"""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        SENT = 'SENT', _('Sent')
        PAID = 'PAID', _('Paid')
        PARTIALLY_PAID = 'PARTIALLY_PAID', _('Partially Paid')
        OVERDUE = 'OVERDUE', _('Overdue')
        CANCELLED = 'CANCELLED', _('Cancelled')

    invoice_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    parent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices_to_pay',
        limit_choices_to={'role': 'PARENT'}
    )

    # Date info
    invoice_date = models.DateField()
    due_date = models.DateField()
    sent_date = models.DateField(null=True, blank=True)

    # Sessions included
    sessions = models.ManyToManyField(
        Session,
        related_name='invoices',
        blank=True
    )

    # Package (if applicable)
    package = models.ForeignKey(
        StudentPackage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )

    # Financial details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    discount_description = models.CharField(max_length=200, blank=True)

    # GST (15% in NZ)
    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15.00')
    )
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # Payment tracking
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)

    # Notes
    notes = models.TextField(blank=True)
    terms = models.TextField(
        blank=True,
        default="Payment due within 7 days. Late cancellations may incur fees."
    )

    # File
    pdf_file = models.FileField(
        upload_to='invoices/',
        null=True,
        blank=True
    )

    # Reminders
    reminder_count = models.IntegerField(default=0)
    last_reminder_sent = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-invoice_date']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.student.user.get_full_name()}"

    def calculate_totals(self):
        """Calculate GST and total amounts"""
        self.gst_amount = (self.subtotal - self.discount_amount) * (self.gst_rate / Decimal('100'))
        self.total_amount = (self.subtotal - self.discount_amount) + self.gst_amount
        self.amount_due = self.total_amount - self.amount_paid

    def save(self, *args, **kwargs):
        # Auto-calculate totals
        self.calculate_totals()

        # Update status based on payment
        if self.amount_paid >= self.total_amount:
            self.status = self.Status.PAID
        elif self.amount_paid > 0:
            self.status = self.Status.PARTIALLY_PAID
        elif self.due_date and self.status == self.Status.SENT:
            from datetime import date
            if date.today() > self.due_date:
                self.status = self.Status.OVERDUE

        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment records"""

    class PaymentMethod(models.TextChoices):
        BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
        CREDIT_CARD = 'CREDIT_CARD', _('Credit Card')
        CASH = 'CASH', _('Cash')
        STRIPE = 'STRIPE', _('Stripe')
        OTHER = 'OTHER', _('Other')

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER
    )

    # Payment gateway reference
    transaction_id = models.CharField(max_length=200, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)

    notes = models.TextField(blank=True)

    # Receipt
    receipt_sent = models.BooleanField(default=False)
    receipt_sent_date = models.DateField(null=True, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)

    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment ${self.amount} - {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice amount paid
        self.invoice.amount_paid = sum(
            self.invoice.payments.values_list('amount', flat=True)
        )
        self.invoice.save()


class Discount(models.Model):
    """Discount codes and special offers"""

    class DiscountType(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', _('Percentage')
        FIXED_AMOUNT = 'FIXED_AMOUNT', _('Fixed Amount')

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)

    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Percentage (e.g., 10.00 for 10%) or fixed amount"
    )

    # Validity
    valid_from = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    max_uses = models.IntegerField(
        null=True,
        blank=True,
        help_text="Leave blank for unlimited uses"
    )
    times_used = models.IntegerField(default=0)

    # Applicability
    applicable_to_packages = models.ManyToManyField(
        Package,
        blank=True,
        related_name='discounts'
    )
    min_sessions = models.IntegerField(
        default=1,
        help_text="Minimum number of sessions required"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.value}{'%' if self.discount_type == self.DiscountType.PERCENTAGE else ' NZD'}"

    def is_valid(self):
        """Check if discount is still valid"""
        from datetime import date
        today = date.today()

        if not self.is_active:
            return False

        if today < self.valid_from:
            return False

        if self.valid_until and today > self.valid_until:
            return False

        if self.max_uses and self.times_used >= self.max_uses:
            return False

        return True

    def calculate_discount(self, amount):
        """Calculate discount amount for given amount"""
        if self.discount_type == self.DiscountType.PERCENTAGE:
            return amount * (self.value / Decimal('100'))
        else:
            return min(self.value, amount)  # Don't discount more than the amount


class ReferralReward(models.Model):
    """Track referral rewards"""

    referrer = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='referrals_made'
    )
    referred = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='referred_by_student'
    )

    reward_amount = models.DecimalField(max_digits=8, decimal_places=2)
    reward_type = models.CharField(
        max_length=50,
        default='CREDIT',
        help_text="e.g., CREDIT, FREE_SESSION, DISCOUNT"
    )

    # Status
    is_redeemed = models.BooleanField(default=False)
    redeemed_date = models.DateField(null=True, blank=True)

    # Applied to invoice
    applied_to_invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referral_rewards_applied'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.referrer.user.get_full_name()} referred {self.referred.user.get_full_name()}"


class Expense(models.Model):
    """Track business expenses"""

    class ExpenseCategory(models.TextChoices):
        MATERIALS = 'MATERIALS', _('Teaching Materials')
        TRAVEL = 'TRAVEL', _('Travel')
        MARKETING = 'MARKETING', _('Marketing')
        SOFTWARE = 'SOFTWARE', _('Software/Subscriptions')
        EQUIPMENT = 'EQUIPMENT', _('Equipment')
        PROFESSIONAL_DEV = 'PROFESSIONAL_DEV', _('Professional Development')
        OTHER = 'OTHER', _('Other')

    description = models.CharField(max_length=200)
    category = models.CharField(
        max_length=30,
        choices=ExpenseCategory.choices,
        default=ExpenseCategory.OTHER
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()

    # GST
    gst_inclusive = models.BooleanField(default=True)
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    # Receipt
    receipt_file = models.FileField(
        upload_to='expense_receipts/',
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_expenses'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.description} - ${self.amount}"
