from django.urls import path
from apps.core.views import UserSignupView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='user-signup'),
]
