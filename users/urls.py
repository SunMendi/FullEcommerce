from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import AdminLoginView, ProfileView

urlpatterns = [
    path('auth/login/', AdminLoginView.as_view(), name='login'),
    path('auth/admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
