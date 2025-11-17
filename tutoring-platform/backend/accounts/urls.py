"""
URL configuration for accounts app
"""
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = 'accounts'

urlpatterns = [
    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User management endpoints will be added here
    # path('register/', views.RegisterView.as_view(), name='register'),
    # path('profile/', views.ProfileView.as_view(), name='profile'),
    # path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
]
