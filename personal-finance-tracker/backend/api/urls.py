"""
API URLs for authentication and user management.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserRegistrationView, UserProfileView, UserSettingsView,
    DashboardView, NetWorthSnapshotViewSet, InsightViewSet
)

router = DefaultRouter()
router.register(r'net-worth', NetWorthSnapshotViewSet, basename='net-worth')
router.register(r'insights', InsightViewSet, basename='insights')

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User profile and settings
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('settings/', UserSettingsView.as_view(), name='settings'),

    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Router URLs
    path('', include(router.urls)),
]
