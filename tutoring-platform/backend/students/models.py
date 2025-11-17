"""
Student-specific models for progress tracking, achievements, and goals
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User, StudentProfile
from core.models import Subject, Topic


class StudentSubjectEnrollment(models.Model):
    """Track which subjects each student is enrolled in"""

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='subject_enrollments'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='student_enrollments'
    )

    # Pricing (can override default)
    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave blank to use subject default rate"
    )

    # Academic tracking
    current_grade = models.CharField(max_length=50, blank=True)
    target_grade = models.CharField(max_length=50, blank=True)
    starting_grade = models.CharField(max_length=50, blank=True)

    enrolled_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'subject']
        ordering = ['student', 'subject']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name}"

    @property
    def effective_hourly_rate(self):
        """Get the effective hourly rate (custom or default)"""
        return self.hourly_rate or self.subject.base_hourly_rate


class TopicMastery(models.Model):
    """Track student mastery of individual topics"""

    class MasteryLevel(models.IntegerChoices):
        NOT_STARTED = 0, _('Not Started')
        STRUGGLING = 1, _('Struggling')
        DEVELOPING = 2, _('Developing')
        PROFICIENT = 3, _('Proficient')
        MASTERED = 4, _('Mastered')

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='topic_mastery'
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='student_mastery'
    )
    mastery_level = models.IntegerField(
        choices=MasteryLevel.choices,
        default=MasteryLevel.NOT_STARTED
    )

    # Tracking
    sessions_on_topic = models.IntegerField(default=0)
    last_practiced = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'topic']
        verbose_name_plural = 'Topic Masteries'
        ordering = ['student', 'topic']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.topic.name} ({self.get_mastery_level_display()})"


class PracticeTest(models.Model):
    """Practice test results for tracking progress"""

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='practice_tests'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='practice_tests'
    )

    title = models.CharField(max_length=200)
    test_date = models.DateField()

    # Results
    score_achieved = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage or raw score"
    )
    score_total = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.00,
        help_text="Total possible score (usually 100%)"
    )
    grade = models.CharField(max_length=50, blank=True, help_text="e.g., 'Excellence', 'A*', etc.")

    # Details
    topics_covered = models.ManyToManyField(
        Topic,
        blank=True,
        related_name='practice_tests'
    )
    notes = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-test_date']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title}"

    @property
    def percentage_score(self):
        """Calculate percentage score"""
        if self.score_total > 0:
            return (self.score_achieved / self.score_total) * 100
        return 0


class Goal(models.Model):
    """Student goals and milestones"""

    class GoalStatus(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', _('Not Started')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        ACHIEVED = 'ACHIEVED', _('Achieved')
        ABANDONED = 'ABANDONED', _('Abandoned')

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='student_goals',
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=GoalStatus.choices,
        default=GoalStatus.NOT_STARTED
    )

    achieved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.title}"


class Achievement(models.Model):
    """Gamification achievements/badges for students"""

    class AchievementType(models.TextChoices):
        MILESTONE = 'MILESTONE', _('Milestone')
        GRADE = 'GRADE', _('Grade Achievement')
        STREAK = 'STREAK', _('Study Streak')
        ENGAGEMENT = 'ENGAGEMENT', _('Engagement')
        IMPROVEMENT = 'IMPROVEMENT', _('Improvement')

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    achievement_type = models.CharField(
        max_length=20,
        choices=AchievementType.choices
    )
    icon = models.CharField(max_length=50, default='🏆')
    points = models.IntegerField(default=10)

    # Criteria (stored as JSON for flexibility)
    criteria = models.JSONField(
        default=dict,
        help_text="Criteria for earning this achievement"
    )

    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}"


class StudentAchievement(models.Model):
    """Track achievements earned by students"""

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='student_achievements'
    )
    earned_date = models.DateTimeField(auto_now_add=True)

    # Context
    context_notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['student', 'achievement']
        ordering = ['-earned_date']

    def __str__(self):
        return f"{self.student.user.get_full_name()} earned {self.achievement.name}"


class StudyStreak(models.Model):
    """Track student study streaks for gamification"""

    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='study_streak'
    )

    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    total_sessions = models.IntegerField(default=0)
    total_study_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.current_streak} day streak"


class ProgressReport(models.Model):
    """Generated progress reports for students"""

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='progress_reports'
    )
    report_period_start = models.DateField()
    report_period_end = models.DateField()

    # Content
    summary = models.TextField()
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    tutor_comments = models.TextField(blank=True)

    # Stats
    sessions_attended = models.IntegerField(default=0)
    average_session_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    practice_tests_completed = models.IntegerField(default=0)
    average_test_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    # File
    pdf_file = models.FileField(
        upload_to='reports/',
        null=True,
        blank=True
    )

    sent_to_parent = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports'
    )

    class Meta:
        ordering = ['-report_period_end']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.report_period_start} to {self.report_period_end}"
