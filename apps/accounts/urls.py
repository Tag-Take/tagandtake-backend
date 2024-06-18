from django.urls import path
from apps.accounts.views import (
    SignUpView,
    LogoutView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    PasswordResetView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path(
        "signup/", 
        SignUpView.as_view(), 
        name="signup"
    ),
    path(
        "token/", 
         CustomTokenObtainPairView.as_view(), 
         name="token_obtain_pair"
    ),
    path(
        "token/refresh/", 
        CustomTokenRefreshView.as_view(), 
        name="token_refresh"
    ),
    path(
        "logout/", 
        LogoutView.as_view(), 
        name="logout"
    ),
    path(
        "password_reset/", 
        PasswordResetView.as_view(), 
        name="password_reset"
    ),
    path(
        "password_reset_confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
