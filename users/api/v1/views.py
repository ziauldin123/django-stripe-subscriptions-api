from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, PasswordResetConfirmView
from django.utils import timezone
from django_rest_passwordreset.views import (
    ResetPasswordConfirm,
    ResetPasswordRequestToken,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

# from rest_framework.generics import (
#     ListAPIView,
#     CreateAPIView,
#     RetrieveUpdateAPIView,
#     get_object_or_404,
#     ListCreateAPIView,
# )
from rest_framework.viewsets import ModelViewSet
from users.models import User

from .permissions import IsAdmin, ProfileOwnerORAdmin
from .serializers import (  # PasswordResetTokenSerializer,
    PassRestConfirmSerializer,
    RegisterSerializer,
    SignupSerializer,
)


class PasswordResetView(ResetPasswordRequestToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data["detail"] = "Password reset e-mail has been sent."
        return response


# class PasswordResetConfirmView(ResetPasswordConfirm):
#     serializer_class = PasswordResetTokenSerializer

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         if response.status_code == 200:
#             response.data["detail"] = "Password has been reset successfuly"

#         return response


# class ResetPasswordVerifyToken(ResetPasswordValidateToken):
#     def post(self, request, *args, **kwargs):

#         response = super().post(request, *args, **kwargs)
#         return response


class UserLoginView(LoginView):
    permission_classes = [AllowAny]


class UserRegisterView(RegisterView):
    serializer_class = RegisterSerializer


# class ProfileDetailedView(RetrieveUpdateAPIView):
#     model = Profile
#     serializer_class = ProfileSerializer

#     def get_object(self):
#         obj, created = Profile.objects.get_or_create(user=self.request.user)
#         return obj


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    takes post request with new_password and key which send via email address
    """

    serializer_class = PassRestConfirmSerializer

