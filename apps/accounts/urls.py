from django.urls import path

from apps.accounts.views import (
    SignUpView,
    ActivateUserView,
    ResendActivationEmailView,
    LogoutView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    PasswordResetView,
    PasswordResetConfirmView,
    DeleteAccountView,
)

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path(
        "activate/<str:uidb64>/<str:token>/",
        ActivateUserView.as_view(),
        name="activate",
    ),
    path(
        "resend-activation/",
        ResendActivationEmailView.as_view(),
        name="resend_activation_email",
    ),
    path("tokens/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("tokens/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/confirm",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("", DeleteAccountView.as_view(), name="delete_account"),
]


