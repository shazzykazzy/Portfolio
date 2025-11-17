"""
Core business models for subjects, topics, and foundational data
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Subject(models.Model):
    """Subjects offered for tutoring"""

    class SubjectType(models.TextChoices):
        PHYSICS = 'PHYSICS', _('Physics')
        MATHEMATICS = 'MATHEMATICS', _('Mathematics')
        ENGLISH_LIT = 'ENGLISH_LIT', _('English Literature')
        GENERAL_SCIENCE = 'GENERAL_SCIENCE', _('General Science')

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    subject_type = models.CharField(
        max_length=20,
        choices=SubjectType.choices
    )
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    color = models.CharField(max_length=7, default='#1E40AF', help_text="Hex color code")

    # Curriculum applicability
    available_for_ncea = models.BooleanField(default=True)
    available_for_cambridge = models.BooleanField(default=True)

    # Year level range
    min_year_level = models.IntegerField(default=9)
    max_year_level = models.IntegerField(default=13)

    # Pricing
    base_hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=75.00
    )

    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Topic(models.Model):
    """Topics within each subject"""

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='topics'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Curriculum and level
    curriculum = models.CharField(
        max_length=20,
        choices=[
            ('NCEA', 'NCEA'),
            ('CAMBRIDGE', 'Cambridge'),
            ('BOTH', 'Both'),
        ],
        default='BOTH'
    )
    year_levels = models.JSONField(
        default=list,
        help_text="List of applicable year levels [9, 10, 11, etc.]"
    )

    # Difficulty and prerequisites
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('FOUNDATION', 'Foundation'),
            ('INTERMEDIATE', 'Intermediate'),
            ('ADVANCED', 'Advanced'),
        ],
        default='INTERMEDIATE'
    )
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='unlocks'
    )

    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject', 'display_order', 'name']
        unique_together = ['subject', 'name']

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


class ExamPeriod(models.Model):
    """NCEA and Cambridge exam periods"""

    name = models.CharField(max_length=200)
    curriculum = models.CharField(
        max_length=20,
        choices=[
            ('NCEA', 'NCEA'),
            ('CAMBRIDGE', 'Cambridge'),
        ]
    )
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'start_date']

    def __str__(self):
        return f"{self.curriculum} {self.year} - {self.name}"


class PricingTier(models.Model):
    """Pricing tiers by year level and curriculum"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    year_level = models.IntegerField()
    curriculum = models.CharField(
        max_length=20,
        choices=[
            ('NCEA', 'NCEA'),
            ('CAMBRIDGE', 'Cambridge'),
            ('GENERAL', 'General'),
        ],
        default='GENERAL'
    )

    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['year_level', 'curriculum']
        unique_together = ['year_level', 'curriculum']

    def __str__(self):
        return f"{self.name} - ${self.hourly_rate}/hr"


class FAQ(models.Model):
    """Frequently Asked Questions"""

    class Category(models.TextChoices):
        GENERAL = 'GENERAL', _('General')
        BOOKING = 'BOOKING', _('Booking & Scheduling')
        PRICING = 'PRICING', _('Pricing & Payments')
        NCEA = 'NCEA', _('NCEA')
        CAMBRIDGE = 'CAMBRIDGE', _('Cambridge')
        SESSIONS = 'SESSIONS', _('Sessions')

    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL
    )
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'display_order']

    def __str__(self):
        return self.question


class Testimonial(models.Model):
    """Student and parent testimonials"""

    name = models.CharField(max_length=200)
    relationship = models.CharField(
        max_length=50,
        choices=[
            ('STUDENT', 'Student'),
            ('PARENT', 'Parent'),
        ]
    )
    content = models.TextField()
    rating = models.IntegerField(
        default=5,
        choices=[(i, i) for i in range(1, 6)]
    )

    # Optional details
    student_year_level = models.IntegerField(blank=True, null=True)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='testimonials'
    )
    grade_improvement = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., 'Achieved to Excellence' or 'C to A*'"
    )

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'display_order', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating}⭐"


class SiteSettings(models.Model):
    """Global site settings"""

    # Business hours
    business_hours_weekday = models.CharField(
        max_length=100,
        default='3:00 PM - 7:00 PM'
    )
    business_hours_weekend = models.CharField(
        max_length=100,
        default='9:00 AM - 5:00 PM'
    )

    # Booking settings
    min_booking_notice_hours = models.IntegerField(
        default=24,
        help_text="Minimum hours notice required for booking"
    )
    max_advance_booking_weeks = models.IntegerField(
        default=8,
        help_text="Maximum weeks in advance for booking"
    )
    default_session_duration_minutes = models.IntegerField(default=60)
    buffer_time_minutes = models.IntegerField(
        default=15,
        help_text="Buffer time between sessions"
    )

    # Cancellation policy
    cancellation_notice_hours = models.IntegerField(
        default=48,
        help_text="Hours notice required for free cancellation"
    )
    cancellation_fee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.00,
        help_text="Percentage fee for late cancellations"
    )

    # Trial session
    trial_session_enabled = models.BooleanField(default=True)
    trial_session_duration_minutes = models.IntegerField(default=30)
    trial_session_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        help_text="0 for free trial"
    )

    # Package deals
    package_5_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=3.00
    )
    package_10_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.00
    )
    package_20_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00
    )
    package_30_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.00
    )

    # Discounts
    sibling_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00
    )
    group_session_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20.00
    )

    # Contact info (displayed on site)
    contact_email = models.EmailField(default='contact@yourtutoring.co.nz')
    contact_phone = models.CharField(max_length=20, default='+64 21 XXX XXXX')
    contact_address = models.TextField(default='Auckland, New Zealand')

    # Social media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    # SEO
    site_title = models.CharField(max_length=200, default='Auckland Tutoring Services')
    site_description = models.TextField(
        default='Expert NCEA and Cambridge tutoring in Physics, Mathematics, English Literature, and Science.'
    )
    meta_keywords = models.TextField(
        default='NCEA tutoring, Cambridge tutoring, Auckland tutor, physics tutor, maths tutor'
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
