from dj_rest_auth.registration.views import ResendEmailVerificationView, VerifyEmailView
from dj_rest_auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.conf import settings
from django.urls import include, path

from .views import (
    CustomPasswordResetConfirmView,
    UserLoginView,
    UserRegisterView,
)

urlpatterns = [
    path("signup/", UserRegisterView.as_view(), name="api-signup"),
    path("login/", UserLoginView.as_view(), name="api-login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    # incase of token reset password required #
    # path('password-reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    # path('password/reset/', PasswordResetView.as_view(), name='api-rest_password'),
    #     path('password/reset/confirm/', PasswordResetConfirmView.as_view(),
    #          name='api-rest_password_confirm'),
    #     path('password/reset/verify-token/',
    #          ResetPasswordVerifyToken.as_view(), name='api-rest_password'),
    path("verify-email/", VerifyEmailView.as_view(), name="rest_verify_email"),
    path(
        "resend-email/", ResendEmailVerificationView.as_view(), name="rest_resend_email"
    ),
    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="api-rest_password_change",
    ),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "password/reset/confirm-key/",
        CustomPasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
]


if getattr(settings, "REST_USE_JWT", False):
    from dj_rest_auth.jwt_auth import get_refresh_view
    from rest_framework_simplejwt.views import TokenVerifyView

    urlpatterns += [
        path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
        path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    ]
