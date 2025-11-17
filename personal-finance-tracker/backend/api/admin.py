"""
Admin configuration for API app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserSettings, NetWorthSnapshot, Insight


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('profile_picture', 'date_of_birth', 'location', 'timezone', 'primary_currency')
        }),
        ('Preferences', {
            'fields': (
                'date_format', 'fiscal_year_start', 'email_notifications',
                'low_balance_alerts', 'bill_reminders', 'budget_warnings',
                'goal_milestones', 'unusual_spending_alerts', 'weekly_summary', 'monthly_summary'
            )
        }),
        ('Security', {
            'fields': ('two_factor_enabled', 'last_login_ip')
        }),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'budget_period', 'created_at')
    list_filter = ('theme', 'budget_period')
    search_fields = ('user__email',)


@admin.register(NetWorthSnapshot)
class NetWorthSnapshotAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'net_worth', 'total_assets', 'total_liabilities')
    list_filter = ('date',)
    search_fields = ('user__email',)
    date_hierarchy = 'date'


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'insight_type', 'priority', 'is_read', 'created_at')
    list_filter = ('insight_type', 'priority', 'is_read', 'is_dismissed')
    search_fields = ('user__email', 'title', 'message')
    date_hierarchy = 'created_at'
