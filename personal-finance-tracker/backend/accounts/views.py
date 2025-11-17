"""
API views for accounts management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import Account, BalanceHistory, AccountGroup
from .serializers import AccountSerializer, BalanceHistorySerializer, AccountGroupSerializer


class AccountViewSet(viewsets.ModelViewSet):
    """CRUD operations for accounts."""
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get account summary statistics."""
        accounts = self.get_queryset().filter(status='active')

        summary = {
            'total_assets': accounts.filter(
                account_type__in=['bank', 'savings', 'investment', 'asset']
            ).aggregate(total=Sum('current_balance'))['total'] or 0,
            'total_liabilities': abs(accounts.filter(
                account_type__in=['credit_card', 'loan', 'liability']
            ).aggregate(total=Sum('current_balance'))['total'] or 0),
            'liquid_cash': accounts.filter(
                account_type__in=['bank', 'savings']
            ).aggregate(total=Sum('current_balance'))['total'] or 0,
            'investments': accounts.filter(
                account_type='investment'
            ).aggregate(total=Sum('current_balance'))['total'] or 0,
            'debt': abs(accounts.filter(
                account_type__in=['credit_card', 'loan', 'liability']
            ).aggregate(total=Sum('current_balance'))['total'] or 0),
        }

        return Response(summary)

    @action(detail=True, methods=['get'])
    def balance_history(self, request, pk=None):
        """Get balance history for an account."""
        account = self.get_object()
        days = int(request.query_params.get('days', 90))
        start_date = timezone.now().date() - timedelta(days=days)

        history = BalanceHistory.objects.filter(
            account=account,
            date__gte=start_date
        )

        serializer = BalanceHistorySerializer(history, many=True)
        return Response(serializer.data)


class AccountGroupViewSet(viewsets.ModelViewSet):
    """CRUD operations for account groups."""
    serializer_class = AccountGroupSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return AccountGroup.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
