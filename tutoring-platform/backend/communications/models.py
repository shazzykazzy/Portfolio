"""
Communication models for messaging and email templates
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User


class EmailTemplate(models.Model):
    """Templates for automated emails"""

    class TemplateType(models.TextChoices):
        BOOKING_CONFIRMATION = 'BOOKING_CONFIRMATION', _('Booking Confirmation')
        SESSION_REMINDER_24HR = 'SESSION_REMINDER_24HR', _('Session Reminder (24hr)')
        SESSION_REMINDER_1HR = 'SESSION_REMINDER_1HR', _('Session Reminder (1hr)')
        SESSION_SUMMARY = 'SESSION_SUMMARY', _('Session Summary')
        INVOICE = 'INVOICE', _('Invoice')
        PAYMENT_REMINDER = 'PAYMENT_REMINDER', _('Payment Reminder')
        PAYMENT_RECEIPT = 'PAYMENT_RECEIPT', _('Payment Receipt')
        CANCELLATION_CONFIRMATION = 'CANCELLATION_CONFIRMATION', _('Cancellation Confirmation')
        PROGRESS_REPORT = 'PROGRESS_REPORT', _('Progress Report')
        TRIAL_SESSION_FOLLOWUP = 'TRIAL_SESSION_FOLLOWUP', _('Trial Session Follow-up')
        PACKAGE_EXPIRING = 'PACKAGE_EXPIRING', _('Package Expiring Soon')
        EXAM_PREP_REMINDER = 'EXAM_PREP_REMINDER', _('Exam Preparation Reminder')
        INACTIVE_STUDENT_REENGAGEMENT = 'INACTIVE_STUDENT_REENGAGEMENT', _('Inactive Student Re-engagement')
        WELCOME_STUDENT = 'WELCOME_STUDENT', _('Welcome Student')
        WELCOME_PARENT = 'WELCOME_PARENT', _('Welcome Parent')
        WAITLIST_NOTIFICATION = 'WAITLIST_NOTIFICATION', _('Waitlist Notification')

    name = models.CharField(max_length=100)
    template_type = models.CharField(
        max_length=50,
        choices=TemplateType.choices,
        unique=True
    )
    subject = models.CharField(max_length=200)
    body_html = models.TextField(help_text="HTML email body with template variables")
    body_text = models.TextField(help_text="Plain text version")

    # Template variables documentation
    available_variables = models.JSONField(
        default=list,
        help_text="List of available template variables"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['template_type']

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class EmailLog(models.Model):
    """Log of all emails sent"""

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SENT = 'SENT', _('Sent')
        FAILED = 'FAILED', _('Failed')
        BOUNCED = 'BOUNCED', _('Bounced')
        OPENED = 'OPENED', _('Opened')
        CLICKED = 'CLICKED', _('Clicked')

    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )

    recipient_email = models.EmailField()
    recipient_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_emails'
    )

    subject = models.CharField(max_length=200)
    body_html = models.TextField(blank=True)
    body_text = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # External service reference
    sendgrid_message_id = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Email to {self.recipient_email} - {self.status}"


class Message(models.Model):
    """Internal messaging between users"""

    class MessageType(models.TextChoices):
        DIRECT = 'DIRECT', _('Direct Message')
        SYSTEM = 'SYSTEM', _('System Message')
        ANNOUNCEMENT = 'ANNOUNCEMENT', _('Announcement')

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )

    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.DIRECT
    )

    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()

    # Attachments
    has_attachments = models.BooleanField(default=False)

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Parent message for threading
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.get_full_name()} to {self.recipient.get_full_name()}"


class MessageAttachment(models.Model):
    """File attachments for messages"""

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    file = models.FileField(upload_to='message_attachments/')
    file_name = models.CharField(max_length=255)
    file_size_bytes = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=50, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"{self.file_name} - {self.message}"


class Notification(models.Model):
    """In-app notifications"""

    class NotificationType(models.TextChoices):
        SESSION_REMINDER = 'SESSION_REMINDER', _('Session Reminder')
        SESSION_CANCELLED = 'SESSION_CANCELLED', _('Session Cancelled')
        NEW_MESSAGE = 'NEW_MESSAGE', _('New Message')
        BOOKING_REQUEST = 'BOOKING_REQUEST', _('Booking Request')
        PAYMENT_RECEIVED = 'PAYMENT_RECEIVED', _('Payment Received')
        INVOICE_SENT = 'INVOICE_SENT', _('Invoice Sent')
        PROGRESS_REPORT = 'PROGRESS_REPORT', _('Progress Report')
        ACHIEVEMENT_EARNED = 'ACHIEVEMENT_EARNED', _('Achievement Earned')
        GOAL_ACHIEVED = 'GOAL_ACHIEVED', _('Goal Achieved')
        RESOURCE_SHARED = 'RESOURCE_SHARED', _('Resource Shared')
        EXAM_UPCOMING = 'EXAM_UPCOMING', _('Exam Upcoming')
        OTHER = 'OTHER', _('Other')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices
    )

    title = models.CharField(max_length=200)
    message = models.TextField()

    # Link to related object
    action_url = models.CharField(max_length=500, blank=True)

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.get_full_name()} - {self.title}"


class SMSLog(models.Model):
    """Log of SMS messages sent (optional feature)"""

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        SENT = 'SENT', _('Sent')
        FAILED = 'FAILED', _('Failed')
        DELIVERED = 'DELIVERED', _('Delivered')

    recipient_phone = models.CharField(max_length=20)
    recipient_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_sms'
    )

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Twilio reference
    twilio_sid = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"SMS to {self.recipient_phone} - {self.status}"


class AutomationRule(models.Model):
    """Rules for automated communications"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Trigger
    trigger_event = models.CharField(
        max_length=50,
        choices=[
            ('SESSION_BOOKED', 'Session Booked'),
            ('SESSION_24HR_BEFORE', '24 Hours Before Session'),
            ('SESSION_1HR_BEFORE', '1 Hour Before Session'),
            ('SESSION_COMPLETED', 'Session Completed'),
            ('INVOICE_CREATED', 'Invoice Created'),
            ('PAYMENT_RECEIVED', 'Payment Received'),
            ('PAYMENT_OVERDUE', 'Payment Overdue'),
            ('PACKAGE_EXPIRING', 'Package Expiring Soon'),
            ('STUDENT_INACTIVE', 'Student Inactive'),
            ('EXAM_UPCOMING', 'Exam Upcoming'),
        ]
    )

    # Actions
    email_template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='automation_rules'
    )
    send_sms = models.BooleanField(default=False)
    sms_message = models.TextField(blank=True)
    create_notification = models.BooleanField(default=True)

    # Conditions (stored as JSON)
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions that must be met for rule to fire"
    )

    # Timing
    delay_minutes = models.IntegerField(
        default=0,
        help_text="Delay before sending (in minutes)"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
