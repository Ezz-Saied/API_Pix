from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    ProfileView,
    RegisterView,
    RequestPasswordResetView,
    ResetPasswordView,
    VerifyEmailView,
    VerifyResetTokenView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/<uuid:token>/", VerifyEmailView.as_view(), name="verify"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("password/reset/request/", RequestPasswordResetView.as_view(), name="password_reset_request"),
    path(
        "password/reset/verify/<uuid:token>/",
        VerifyResetTokenView.as_view(),
        name="password_reset_verify",
    ),
    path("password/reset/", ResetPasswordView.as_view(), name="password_reset"),
]
