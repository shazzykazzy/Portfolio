"""
User and authentication models
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'TUTOR')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with role-based access"""

    class Role(models.TextChoices):
        STUDENT = 'STUDENT', _('Student')
        PARENT = 'PARENT', _('Parent')
        TUTOR = 'TUTOR', _('Tutor/Admin')

    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True, default='Auckland')
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_parent(self):
        return self.role == self.Role.PARENT

    @property
    def is_tutor(self):
        return self.role == self.Role.TUTOR


class StudentProfile(models.Model):
    """Extended profile for students"""

    class YearLevel(models.IntegerChoices):
        YEAR_9 = 9, _('Year 9')
        YEAR_10 = 10, _('Year 10')
        YEAR_11 = 11, _('Year 11')
        YEAR_12 = 12, _('Year 12')
        YEAR_13 = 13, _('Year 13')

    class Curriculum(models.TextChoices):
        NCEA = 'NCEA', _('NCEA')
        CAMBRIDGE = 'CAMBRIDGE', _('Cambridge')

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    school = models.CharField(max_length=200)
    year_level = models.IntegerField(choices=YearLevel.choices)
    curriculum = models.CharField(
        max_length=20,
        choices=Curriculum.choices,
        default=Curriculum.NCEA,
    )
    parent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        limit_choices_to={'role': User.Role.PARENT}
    )

    # Academic info
    subjects_enrolled = models.JSONField(default=list, blank=True)  # List of subject IDs
    learning_needs = models.TextField(blank=True, help_text="Any special learning needs or accommodations")
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    goals = models.TextField(blank=True)

    # Preferences
    preferred_session_times = models.TextField(blank=True)
    preferred_format = models.CharField(
        max_length=20,
        choices=[
            ('IN_PERSON', 'In-Person'),
            ('ONLINE', 'Online'),
            ('HYBRID', 'Hybrid'),
        ],
        default='HYBRID'
    )

    # Engagement
    referral_code = models.CharField(max_length=20, unique=True, blank=True)
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - Year {self.year_level}"


class ParentProfile(models.Model):
    """Extended profile for parents"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile'
    )
    occupation = models.CharField(max_length=200, blank=True)
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('EMAIL', 'Email'),
            ('PHONE', 'Phone'),
            ('SMS', 'SMS'),
        ],
        default='EMAIL'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Parent: {self.user.get_full_name()}"


class TutorProfile(models.Model):
    """Extended profile for tutor"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='tutor_profile'
    )
    bio = models.TextField(blank=True)
    qualifications = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    specializations = models.TextField(blank=True)
    hourly_rate_default = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=75.00
    )

    # Social proof
    total_students_taught = models.IntegerField(default=0)
    success_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Percentage of students achieving their goals"
    )

    # Availability
    available_for_bookings = models.BooleanField(default=True)
    max_students = models.IntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tutor: {self.user.get_full_name()}"
