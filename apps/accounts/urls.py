from django.urls import path

from apps.accounts.views import (
    MemberSignUpView,
    StoreSignUpView,
    ActivateUserView,
    ResendActivationEmailView,
    LogoutView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    PasswordResetView,
    PasswordResetConfirmView,
    DeleteAccountView,
    get_auth_status
)

urlpatterns = [
    path("signup/member/", MemberSignUpView.as_view(), name="member_signup"),
    path("signup/store/", StoreSignUpView.as_view(), name="store_signup"),
    path("activate/<str:uidb64>/<str:token>/", ActivateUserView.as_view(), name="activate_account"),
    path("activate/resend/", ResendActivationEmailView.as_view(), name="resend_activation"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("auth-status/", get_auth_status, name="auth_status"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("account/delete/", DeleteAccountView.as_view(), name="delete_account"),
]
