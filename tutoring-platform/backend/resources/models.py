"""
Resource library models for study materials and content
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User, StudentProfile
from core.models import Subject, Topic


class ResourceCategory(models.Model):
    """Categories for organizing resources"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    icon = models.CharField(max_length=50, blank=True)
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Resource Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Resource(models.Model):
    """Learning resources and study materials"""

    class ResourceType(models.TextChoices):
        PAST_PAPER = 'PAST_PAPER', _('Past Paper')
        MARK_SCHEME = 'MARK_SCHEME', _('Mark Scheme')
        WORKSHEET = 'WORKSHEET', _('Worksheet')
        STUDY_GUIDE = 'STUDY_GUIDE', _('Study Guide')
        FORMULA_SHEET = 'FORMULA_SHEET', _('Formula Sheet')
        VIDEO = 'VIDEO', _('Video')
        ARTICLE = 'ARTICLE', _('Article')
        PRESENTATION = 'PRESENTATION', _('Presentation')
        PRACTICE_TEST = 'PRACTICE_TEST', _('Practice Test')
        NOTES = 'NOTES', _('Notes')
        OTHER = 'OTHER', _('Other')

    class Curriculum(models.TextChoices):
        NCEA = 'NCEA', _('NCEA')
        CAMBRIDGE = 'CAMBRIDGE', _('Cambridge')
        GENERAL = 'GENERAL', _('General')
        BOTH = 'BOTH', _('Both NCEA & Cambridge')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.WORKSHEET
    )

    # Organization
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name='resources'
    )
    categories = models.ManyToManyField(
        ResourceCategory,
        blank=True,
        related_name='resources'
    )

    # Curriculum and level
    curriculum = models.CharField(
        max_length=20,
        choices=Curriculum.choices,
        default=Curriculum.GENERAL
    )
    year_levels = models.JSONField(
        default=list,
        help_text="List of applicable year levels [9, 10, 11, etc.]"
    )

    # NCEA specific
    ncea_level = models.IntegerField(
        null=True,
        blank=True,
        choices=[(1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3')]
    )

    # Cambridge specific
    cambridge_level = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('IGCSE', 'IGCSE'),
            ('AS', 'AS Level'),
            ('A2', 'A2 Level'),
        ]
    )

    # File or link
    file = models.FileField(
        upload_to='resources/',
        null=True,
        blank=True
    )
    external_url = models.URLField(
        blank=True,
        help_text="For video links or external resources"
    )
    file_size_bytes = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=50, blank=True)

    # Visibility
    is_public = models.BooleanField(
        default=False,
        help_text="Publicly accessible or student-only"
    )
    is_featured = models.BooleanField(default=False)

    # Tracking
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    # Tags for better searchability
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="List of tags for search"
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_resources'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


class StudentResourceAccess(models.Model):
    """Track which students have access to which resources"""

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='resource_access'
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='student_access'
    )

    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='granted_resource_access'
    )

    # Tracking
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['student', 'resource']
        ordering = ['-granted_at']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.resource.title}"


class BlogPost(models.Model):
    """Blog posts for study tips and educational content"""

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PUBLISHED = 'PUBLISHED', _('Published')
        ARCHIVED = 'ARCHIVED', _('Archived')

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()

    # Organization
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_posts'
    )
    categories = models.ManyToManyField(
        ResourceCategory,
        blank=True,
        related_name='blog_posts'
    )
    tags = models.JSONField(default=list, blank=True)

    # Featured image
    featured_image = models.ImageField(
        upload_to='blog_images/',
        null=True,
        blank=True
    )

    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    # Publishing
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    published_date = models.DateTimeField(null=True, blank=True)

    # Tracking
    view_count = models.IntegerField(default=0)

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blog_posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date', '-created_at']

    def __str__(self):
        return self.title


class StudyTool(models.Model):
    """Study tools like flashcards, timers, etc."""

    class ToolType(models.TextChoices):
        FLASHCARD_SET = 'FLASHCARD_SET', _('Flashcard Set')
        STUDY_TIMER = 'STUDY_TIMER', _('Study Timer')
        FORMULA_CALCULATOR = 'FORMULA_CALCULATOR', _('Formula Calculator')
        GRADE_CALCULATOR = 'GRADE_CALCULATOR', _('Grade Calculator')
        MINDMAP = 'MINDMAP', _('Mind Map')
        OTHER = 'OTHER', _('Other')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tool_type = models.CharField(
        max_length=30,
        choices=ToolType.choices
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='study_tools'
    )
    topics = models.ManyToManyField(
        Topic,
        blank=True,
        related_name='study_tools'
    )

    # Tool data (stored as JSON for flexibility)
    tool_data = models.JSONField(
        default=dict,
        help_text="Tool-specific data structure"
    )

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_study_tools'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_tool_type_display()})"


class Flashcard(models.Model):
    """Individual flashcards"""

    tool = models.ForeignKey(
        StudyTool,
        on_delete=models.CASCADE,
        related_name='flashcards',
        limit_choices_to={'tool_type': 'FLASHCARD_SET'}
    )

    question = models.TextField()
    answer = models.TextField()
    hint = models.TextField(blank=True)

    # Optional image for visual learning
    question_image = models.ImageField(
        upload_to='flashcard_images/',
        null=True,
        blank=True
    )
    answer_image = models.ImageField(
        upload_to='flashcard_images/',
        null=True,
        blank=True
    )

    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('EASY', 'Easy'),
            ('MEDIUM', 'Medium'),
            ('HARD', 'Hard'),
        ],
        default='MEDIUM'
    )

    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tool', 'display_order']

    def __str__(self):
        return f"{self.tool.title} - {self.question[:50]}"


class StudentFlashcardProgress(models.Model):
    """Track student progress on flashcard sets"""

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='flashcard_progress'
    )
    flashcard = models.ForeignKey(
        Flashcard,
        on_delete=models.CASCADE,
        related_name='student_progress'
    )

    # Spaced repetition
    times_reviewed = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    times_incorrect = models.IntegerField(default=0)

    last_reviewed = models.DateTimeField(null=True, blank=True)
    next_review_date = models.DateTimeField(null=True, blank=True)

    confidence_level = models.IntegerField(
        default=0,
        choices=[(i, i) for i in range(6)],
        help_text="0 = not reviewed, 5 = fully confident"
    )

    class Meta:
        unique_together = ['student', 'flashcard']
        ordering = ['next_review_date']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.flashcard.question[:30]}"
