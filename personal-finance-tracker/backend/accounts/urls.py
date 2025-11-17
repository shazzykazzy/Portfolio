"""
URLs for accounts API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, AccountGroupViewSet

router = DefaultRouter()
router.register(r'', AccountViewSet, basename='accounts')
router.register(r'groups', AccountGroupViewSet, basename='account-groups')

urlpatterns = [
    path('', include(router.urls)),
]
