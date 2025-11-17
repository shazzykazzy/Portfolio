"""
Analytics and reporting models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class BusinessMetrics(models.Model):
    """Daily/weekly/monthly business metrics snapshot"""

    class Period(models.TextChoices):
        DAILY = 'DAILY', _('Daily')
        WEEKLY = 'WEEKLY', _('Weekly')
        MONTHLY = 'MONTHLY', _('Monthly')
        YEARLY = 'YEARLY', _('Yearly')

    period_type = models.CharField(
        max_length=20,
        choices=Period.choices
    )
    period_start = models.DateField()
    period_end = models.DateField()

    # Student metrics
    active_students = models.IntegerField(default=0)
    new_students = models.IntegerField(default=0)
    churned_students = models.IntegerField(default=0)
    total_students = models.IntegerField(default=0)

    # Session metrics
    sessions_scheduled = models.IntegerField(default=0)
    sessions_completed = models.IntegerField(default=0)
    sessions_cancelled = models.IntegerField(default=0)
    sessions_no_show = models.IntegerField(default=0)
    total_teaching_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )

    # Financial metrics
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    outstanding_invoices = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Booking metrics
    booking_requests = models.IntegerField(default=0)
    booking_requests_approved = models.IntegerField(default=0)
    booking_requests_declined = models.IntegerField(default=0)
    trial_sessions = models.IntegerField(default=0)
    trial_conversion_count = models.IntegerField(default=0)

    # Subject breakdown (stored as JSON)
    revenue_by_subject = models.JSONField(default=dict, blank=True)
    sessions_by_subject = models.JSONField(default=dict, blank=True)
    students_by_subject = models.JSONField(default=dict, blank=True)

    # Curriculum breakdown
    revenue_by_curriculum = models.JSONField(default=dict, blank=True)
    sessions_by_curriculum = models.JSONField(default=dict, blank=True)

    # Average ratings
    average_student_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    average_understanding_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['period_type', 'period_start']
        ordering = ['-period_start']
        verbose_name_plural = 'Business Metrics'

    def __str__(self):
        return f"{self.get_period_type_display()} - {self.period_start} to {self.period_end}"


class SubjectPerformance(models.Model):
    """Track performance metrics by subject"""

    subject = models.ForeignKey(
        'core.Subject',
        on_delete=models.CASCADE,
        related_name='performance_metrics'
    )
    period_start = models.DateField()
    period_end = models.DateField()

    # Student metrics
    total_students = models.IntegerField(default=0)
    new_students = models.IntegerField(default=0)

    # Session metrics
    total_sessions = models.IntegerField(default=0)
    total_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    # Academic metrics
    average_grade_improvement = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    excellence_count = models.IntegerField(
        default=0,
        help_text="Number of students achieving Excellence/A* grade"
    )
    pass_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Financial
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_start', 'subject']

    def __str__(self):
        return f"{self.subject.name} - {self.period_start} to {self.period_end}"


class StudentEngagement(models.Model):
    """Track student engagement metrics"""

    student = models.ForeignKey(
        'accounts.StudentProfile',
        on_delete=models.CASCADE,
        related_name='engagement_metrics'
    )
    period_start = models.DateField()
    period_end = models.DateField()

    # Session attendance
    sessions_scheduled = models.IntegerField(default=0)
    sessions_attended = models.IntegerField(default=0)
    sessions_cancelled = models.IntegerField(default=0)
    sessions_no_show = models.IntegerField(default=0)
    attendance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )

    # Platform engagement
    login_count = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    resources_accessed = models.IntegerField(default=0)
    practice_tests_completed = models.IntegerField(default=0)

    # Study metrics
    total_study_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    current_study_streak = models.IntegerField(default=0)

    # Academic progress
    topics_mastered = models.IntegerField(default=0)
    achievements_earned = models.IntegerField(default=0)
    goals_achieved = models.IntegerField(default=0)

    # Ratings
    average_session_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'period_start']
        ordering = ['-period_start', 'student']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.period_start}"


class WebsiteAnalytics(models.Model):
    """Track website visitor analytics"""

    date = models.DateField(unique=True)

    # Traffic
    total_visitors = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    page_views = models.IntegerField(default=0)

    # Engagement
    average_session_duration_seconds = models.IntegerField(default=0)
    bounce_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )

    # Conversions
    booking_requests_submitted = models.IntegerField(default=0)
    contact_forms_submitted = models.IntegerField(default=0)
    trial_sessions_requested = models.IntegerField(default=0)
    resource_downloads = models.IntegerField(default=0)

    # Traffic sources (JSON)
    traffic_sources = models.JSONField(
        default=dict,
        blank=True,
        help_text="Breakdown by source (direct, organic, social, etc.)"
    )

    # Popular pages (JSON)
    top_pages = models.JSONField(
        default=list,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Website Analytics'

    def __str__(self):
        return f"Analytics - {self.date}"


class RevenueGoal(models.Model):
    """Revenue goals and targets"""

    class Period(models.TextChoices):
        WEEKLY = 'WEEKLY', _('Weekly')
        MONTHLY = 'MONTHLY', _('Monthly')
        QUARTERLY = 'QUARTERLY', _('Quarterly')
        YEARLY = 'YEARLY', _('Yearly')

    name = models.CharField(max_length=100)
    period_type = models.CharField(
        max_length=20,
        choices=Period.choices
    )
    period_start = models.DateField()
    period_end = models.DateField()

    target_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    actual_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    target_sessions = models.IntegerField(null=True, blank=True)
    actual_sessions = models.IntegerField(default=0)

    target_new_students = models.IntegerField(null=True, blank=True)
    actual_new_students = models.IntegerField(default=0)

    notes = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.name} ({self.period_start} - {self.period_end})"

    @property
    def revenue_achievement_percentage(self):
        if self.target_revenue > 0:
            return (self.actual_revenue / self.target_revenue) * Decimal('100')
        return Decimal('0')
