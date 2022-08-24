from unittest.util import _MAX_LENGTH

import sesame.utils
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import ResetPasswordForm
from allauth.account.utils import setup_user_email
from allauth.utils import (
    email_address_exists,
    generate_unique_username,
    get_username_max_length,
)
from dj_rest_auth.serializers import PasswordResetSerializer
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.http import HttpRequest
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from users.models import User

# from django_rest_passwordreset.serializers import PasswordTokenSerializer
# from ...service import onsignal_hashed_auth
# from notifyme.models import Notify


class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password", "placeholder": "Password"},
    )

    class Meta:
        model = User
        fields = ("email", "username", "password", "password2")
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "email": {
                "required": True,
                "allow_blank": False,
            },
        }

    def _get_request(self):
        request = self.context.get("request")
        if (
            request
            and not isinstance(request, HttpRequest)
            and hasattr(request, "_request")
        ):
            request = request._request
        return request

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address.")
                )
        return email

    # def validate_terms_privacy(self, terms_privacy):
    #     if terms_privacy == False:
    #         raise serializers.ValidationError(
    #             _("Can not signup without accept terms and privacy ")
    #         )
    #     else:
    #         return terms_privacy

    # def validate(self, data):
    #     if data["password"] != data["password2"]:
    #         raise serializers.ValidationError(
    #             _("The two password fields didn't match.")
    #         )
    #     return data

    def create(self, validated_data):
        user = User(
            email=validated_data.get("email"),
            # name=validated_data.get('name'),
            username=generate_unique_username(
                [validated_data.get("name"), validated_data.get("email"), "user"]
            ),
        )
        user.set_password(validated_data.get("password"))
        user.save()
        request = self._get_request()
        setup_user_email(request, user, [])
        return user

    def save(self, request=None):
        """rest_auth passes request so we must override to accept it"""
        return super().save()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=True,  # allauth_settings.USERNAME_REQUIRED,
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password = serializers.CharField(write_only=True)

    photo = serializers.ImageField(required=False)

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("A user is already registered with this e-mail address."),
                )
        return email

    def validate_photo(self, photo):
        return photo

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("username", ""),
            "password": self.validated_data.get("password", ""),
            "email": self.validated_data.get("email", ""),
            "photo": self.validated_data.get("photo", None),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if "password" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data["password"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        if self.cleaned_data.get("photo", None):
            user.photo = self.cleaned_data.get("photo")
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name"]


class PasswordSerializer(PasswordResetSerializer):
    """Custom serializer for rest_auth to solve reset password error"""

    password_reset_form_class = ResetPasswordForm


class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """

    is_admin = serializers.BooleanField(source="is_superuser")

    class Meta:
        model = User
        fields = ("id", "username", "email", "name", "is_admin", "photo")
        read_only_fields = (
            "id",
            "email",
        )


# class PasswordResetTokenSerializer(PasswordTokenSerializer):
#     password2 = serializers.CharField(
#         label=_("Password2"), style={"input_type": "password"}
#     )

#     def validate(self, data):
#         if data["password"] != data["password2"]:
#             raise ValidationError("The Two passwords don't match")
#         return super().validate(data)


# todo here make sure the city is apart of county is apart stat


class PassRestConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a password reset attempt.
    """

    new_password = serializers.CharField(max_length=128)
    key = serializers.CharField(max_length=255)

    user = None

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        UserModel = User
        if "allauth" in settings.INSTALLED_APPS:
            from allauth.account.forms import default_token_generator
            from allauth.account.utils import url_str_to_user_pk as uid_decoder
        else:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_decode as uid_decoder

        # Decode the uidb64 (allauth use base36) to uid to get User object
        key = attrs["key"]
        if "-" in key:
            # check if key contains two parts one for string and other for token
            key_list = key.split("-", 1)
            uid = key_list[0]
            token = key_list[1]
        else:
            raise ValidationError({"key": ["Invalid key"]})
        try:
            uid = force_str(uid_decoder(uid))
            self.user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({"key": ["Invalid key "]})

        if not default_token_generator.check_token(self.user, token):
            raise ValidationError({"key": ["Invalid key"]})

        self.custom_validation(attrs)
        ## validate password
        get_adapter().clean_password(attrs["new_password"])
        self.user.set_password(attrs["new_password"])
        return attrs

    def save(self):
        return self.user.save()

