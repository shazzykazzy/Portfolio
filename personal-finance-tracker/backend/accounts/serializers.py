"""
Serializers for accounts management.
"""
from rest_framework import serializers
from .models import Account, BalanceHistory, AccountGroup


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for accounts."""
    available_credit = serializers.ReadOnlyField()
    is_asset = serializers.ReadOnlyField()
    is_liability = serializers.ReadOnlyField()

    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class BalanceHistorySerializer(serializers.ModelSerializer):
    """Serializer for balance history."""
    class Meta:
        model = BalanceHistory
        fields = '__all__'
        read_only_fields = ('created_at',)


class AccountGroupSerializer(serializers.ModelSerializer):
    """Serializer for account groups."""
    total_balance = serializers.ReadOnlyField()
    accounts_detail = AccountSerializer(source='accounts', many=True, read_only=True)

    class Meta:
        model = AccountGroup
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')
