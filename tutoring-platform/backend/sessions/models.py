"""
Session booking, scheduling, and management models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, StudentProfile
from core.models import Subject, Topic


class TutorAvailability(models.Model):
    """Tutor's availability schedule"""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, _('Monday')
        TUESDAY = 2, _('Tuesday')
        WEDNESDAY = 3, _('Wednesday')
        THURSDAY = 4, _('Thursday')
        FRIDAY = 5, _('Friday')
        SATURDAY = 6, _('Saturday')
        SUNDAY = 7, _('Sunday')

    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='availability_slots',
        limit_choices_to={'role': 'TUTOR'}
    )
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    # For one-time overrides (e.g., holidays)
    specific_date = models.DateField(
        null=True,
        blank=True,
        help_text="Leave blank for recurring availability"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Set to False to block out time"
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name_plural = 'Tutor Availabilities'

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class BookingRequest(models.Model):
    """Student booking requests"""

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        DECLINED = 'DECLINED', _('Declined')
        CANCELLED = 'CANCELLED', _('Cancelled')

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='booking_requests'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='booking_requests'
    )

    # Session details
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    session_format = models.CharField(
        max_length=20,
        choices=[
            ('IN_PERSON', 'In-Person'),
            ('ONLINE', 'Online'),
        ],
        default='ONLINE'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="For in-person sessions"
    )

    # Request details
    topics_requested = models.ManyToManyField(
        Topic,
        blank=True,
        related_name='booking_requests'
    )
    student_message = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)

    # Trial session
    is_trial_session = models.BooleanField(default=False)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    tutor_response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking Request - {self.student.user.get_full_name()} - {self.preferred_date}"


class Session(models.Model):
    """Tutoring sessions"""

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Scheduled')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        NO_SHOW = 'NO_SHOW', _('No Show')

    class SessionType(models.TextChoices):
        REGULAR = 'REGULAR', _('Regular')
        TRIAL = 'TRIAL', _('Trial')
        EXAM_PREP = 'EXAM_PREP', _('Exam Preparation')
        INTERNAL_ASSESSMENT = 'INTERNAL_ASSESSMENT', _('Internal Assessment')
        HOMEWORK_SUPPORT = 'HOMEWORK_SUPPORT', _('Homework Support')
        REVIEW = 'REVIEW', _('Review')
        GROUP = 'GROUP', _('Group Session')

    # Participants
    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions_as_tutor',
        limit_choices_to={'role': 'TUTOR'}
    )
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    additional_students = models.ManyToManyField(
        StudentProfile,
        blank=True,
        related_name='group_sessions',
        help_text="For group sessions"
    )

    # Session details
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_type = models.CharField(
        max_length=30,
        choices=SessionType.choices,
        default=SessionType.REGULAR
    )

    # Date and time
    scheduled_date = models.DateField()
    scheduled_start_time = models.TimeField()
    scheduled_duration_minutes = models.IntegerField(default=60)
    actual_start_time = models.TimeField(null=True, blank=True)
    actual_end_time = models.TimeField(null=True, blank=True)

    # Format and location
    session_format = models.CharField(
        max_length=20,
        choices=[
            ('IN_PERSON', 'In-Person'),
            ('ONLINE', 'Online'),
        ],
        default='ONLINE'
    )
    location = models.CharField(max_length=200, blank=True)
    online_meeting_url = models.URLField(blank=True)
    online_meeting_id = models.CharField(max_length=100, blank=True)
    online_meeting_password = models.CharField(max_length=100, blank=True)

    # Content
    planned_topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name='planned_sessions'
    )
    topics_covered = models.ManyToManyField(
        Topic,
        blank=True,
        related_name='completed_sessions'
    )
    learning_objectives = models.TextField(blank=True)

    # Session notes (after session)
    session_notes = models.TextField(
        blank=True,
        help_text="What was covered in the session"
    )
    homework_assigned = models.TextField(blank=True)
    student_understanding_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1-5 rating of student's understanding"
    )
    next_session_focus = models.TextField(blank=True)
    concerns_or_highlights = models.TextField(blank=True)

    # Student feedback
    student_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    student_feedback = models.TextField(blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_sessions'
    )

    # Resources shared
    resources_shared = models.JSONField(
        default=list,
        blank=True,
        help_text="List of resource IDs shared during session"
    )

    # Notifications sent
    reminder_24hr_sent = models.BooleanField(default=False)
    reminder_1hr_sent = models.BooleanField(default=False)
    summary_sent_to_parent = models.BooleanField(default=False)

    # Related to booking request
    booking_request = models.OneToOneField(
        BookingRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='session'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date', '-scheduled_start_time']

    def __str__(self):
        return f"{self.subject.name} - {self.student.user.get_full_name()} - {self.scheduled_date}"

    @property
    def is_group_session(self):
        return self.additional_students.exists()

    @property
    def all_students(self):
        """Get all students in the session including main and additional"""
        students = [self.student]
        students.extend(list(self.additional_students.all()))
        return students

    @property
    def actual_duration_minutes(self):
        """Calculate actual session duration"""
        if self.actual_start_time and self.actual_end_time:
            from datetime import datetime, timedelta
            start = datetime.combine(self.scheduled_date, self.actual_start_time)
            end = datetime.combine(self.scheduled_date, self.actual_end_time)
            duration = (end - start).total_seconds() / 60
            return int(duration)
        return None


class SessionAttachment(models.Model):
    """Files attached to sessions (homework uploads, worksheets, etc.)"""

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_session_files'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='session_attachments/')
    file_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., PDF, DOCX, PNG"
    )
    file_size_bytes = models.BigIntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.session}"


class RecurringSession(models.Model):
    """Template for recurring sessions"""

    class Frequency(models.TextChoices):
        WEEKLY = 'WEEKLY', _('Weekly')
        BIWEEKLY = 'BIWEEKLY', _('Every 2 weeks')
        MONTHLY = 'MONTHLY', _('Monthly')

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='recurring_sessions'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='recurring_sessions'
    )
    tutor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recurring_sessions',
        limit_choices_to={'role': 'TUTOR'}
    )

    # Recurrence pattern
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.WEEKLY
    )
    day_of_week = models.IntegerField(
        choices=TutorAvailability.DayOfWeek.choices
    )
    start_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)

    # Session details
    session_format = models.CharField(
        max_length=20,
        choices=[
            ('IN_PERSON', 'In-Person'),
            ('ONLINE', 'Online'),
        ],
        default='ONLINE'
    )
    location = models.CharField(max_length=200, blank=True)

    # Date range
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Leave blank for indefinite"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} ({self.get_frequency_display()})"


class Waitlist(models.Model):
    """Waitlist for fully booked time slots"""

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='waitlist_entries'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='waitlist_entries'
    )

    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    preferred_day_of_week = models.IntegerField(
        choices=TutorAvailability.DayOfWeek.choices,
        null=True,
        blank=True
    )

    notes = models.TextField(blank=True)

    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Waitlist - {self.student.user.get_full_name()} - {self.subject.name}"
