"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from .models import Account, BalanceHistory, AccountGroup


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'account_type', 'current_balance', 'currency', 'status')
    list_filter = ('account_type', 'status', 'currency')
    search_fields = ('name', 'user__email', 'institution')
    ordering = ('user', 'display_order')


@admin.register(BalanceHistory)
class BalanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('account', 'date', 'balance')
    list_filter = ('date',)
    search_fields = ('account__name',)
    date_hierarchy = 'date'


@admin.register(AccountGroup)
class AccountGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__email')
