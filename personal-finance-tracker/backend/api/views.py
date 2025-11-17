"""
API views for authentication and user management.
"""
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import UserSettings, NetWorthSnapshot, Insight
from .serializers import (
    UserRegistrationSerializer, UserSerializer,
    UserSettingsSerializer, NetWorthSnapshotSerializer, InsightSerializer
)
from accounts.models import Account
from transactions.models import Transaction

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile."""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserSettingsView(generics.RetrieveUpdateAPIView):
    """Get and update user settings."""
    serializer_class = UserSettingsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        settings, created = UserSettings.objects.get_or_create(user=self.request.user)
        return settings


class DashboardView(generics.GenericAPIView):
    """
    Main dashboard data endpoint.
    Returns net worth, cash flow, quick stats, upcoming bills, and insights.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # Get latest net worth snapshot
        latest_snapshot = NetWorthSnapshot.objects.filter(user=user).first()

        # Calculate net worth change
        month_ago = today - timedelta(days=30)
        month_ago_snapshot = NetWorthSnapshot.objects.filter(
            user=user, date__lte=month_ago
        ).first()

        net_worth_change = 0
        net_worth_change_pct = 0
        if latest_snapshot and month_ago_snapshot:
            net_worth_change = float(latest_snapshot.net_worth - month_ago_snapshot.net_worth)
            if month_ago_snapshot.net_worth != 0:
                net_worth_change_pct = (net_worth_change / float(month_ago_snapshot.net_worth)) * 100

        # Get current month cash flow
        first_day = today.replace(day=1)
        current_month_income = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__gte=first_day,
            date__lte=today,
            is_pending=False
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        current_month_expenses = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__gte=first_day,
            date__lte=today,
            is_pending=False
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        # Quick stats
        liquid_cash = Account.objects.filter(
            user=user,
            account_type__in=['bank', 'savings'],
            status='active'
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

        total_investments = Account.objects.filter(
            user=user,
            account_type='investment',
            status='active'
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

        total_debt = Account.objects.filter(
            user=user,
            account_type__in=['credit_card', 'loan', 'liability'],
            status='active'
        ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

        # Upcoming bills (next 30 days)
        from transactions.models import RecurringTransaction
        upcoming_bills = RecurringTransaction.objects.filter(
            user=user,
            is_active=True,
            next_due_date__lte=today + timedelta(days=30),
            next_due_date__gte=today
        ).order_by('next_due_date')[:5]

        # Recent insights
        insights = Insight.objects.filter(
            user=user,
            is_dismissed=False
        ).order_by('-created_at')[:5]

        return Response({
            'net_worth': {
                'current': float(latest_snapshot.net_worth) if latest_snapshot else 0,
                'change_amount': net_worth_change,
                'change_percentage': net_worth_change_pct,
                'total_assets': float(latest_snapshot.total_assets) if latest_snapshot else 0,
                'total_liabilities': float(latest_snapshot.total_liabilities) if latest_snapshot else 0,
            },
            'cash_flow': {
                'income': float(current_month_income),
                'expenses': float(current_month_expenses),
                'net': float(current_month_income - current_month_expenses),
            },
            'quick_stats': {
                'liquid_cash': float(liquid_cash),
                'investments': float(total_investments),
                'debt': float(total_debt),
            },
            'upcoming_bills': [
                {
                    'id': bill.id,
                    'description': bill.description,
                    'amount': float(bill.amount),
                    'due_date': bill.next_due_date,
                }
                for bill in upcoming_bills
            ],
            'insights': InsightSerializer(insights, many=True).data,
        })


class NetWorthSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """Net worth snapshots view."""
    serializer_class = NetWorthSnapshotSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return NetWorthSnapshot.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get net worth history with configurable time range."""
        days = int(request.query_params.get('days', 365))
        start_date = timezone.now().date() - timedelta(days=days)

        snapshots = self.get_queryset().filter(date__gte=start_date)
        serializer = self.get_serializer(snapshots, many=True)

        return Response(serializer.data)


class InsightViewSet(viewsets.ModelViewSet):
    """Insights management."""
    serializer_class = InsightSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Insight.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark insight as read."""
        insight = self.get_object()
        insight.is_read = True
        insight.read_at = timezone.now()
        insight.save()
        return Response({'status': 'marked as read'})

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss insight."""
        insight = self.get_object()
        insight.is_dismissed = True
        insight.save()
        return Response({'status': 'dismissed'})
