"""
Serializers for authentication and user management.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserSettings, NetWorthSnapshot, Insight

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Create default settings
        UserSettings.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    age = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'profile_picture', 'date_of_birth', 'age', 'location', 'timezone',
            'primary_currency', 'date_format', 'fiscal_year_start',
            'email_notifications', 'low_balance_alerts', 'bill_reminders',
            'budget_warnings', 'goal_milestones', 'unusual_spending_alerts',
            'weekly_summary', 'monthly_summary', 'two_factor_enabled',
            'created_at', 'last_login'
        )
        read_only_fields = ('id', 'created_at', 'last_login', 'age')


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user settings."""
    class Meta:
        model = UserSettings
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')


class NetWorthSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for net worth snapshots."""
    class Meta:
        model = NetWorthSnapshot
        fields = '__all__'
        read_only_fields = ('user', 'net_worth', 'created_at')


class InsightSerializer(serializers.ModelSerializer):
    """Serializer for insights."""
    class Meta:
        model = Insight
        fields = '__all__'
        read_only_fields = ('user', 'created_at')
