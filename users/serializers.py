from allauth.account.models import EmailAddress
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from users.models import  User



class ChangePasswordSerializer(serializers.Serializer):
    """
    Custom serializer used to set the password for a User
    """

    password_1 = serializers.CharField(
        min_length=4, write_only=True, required=True, style={"input_type": "password"}
    )
    password_2 = serializers.CharField(
        min_length=4, write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        pass1 = attrs.get("password_1")
        pass2 = attrs.get("password_2")
        if pass1 != pass2:
            raise serializers.ValidationError({"detail": "Passwords do not match"})
        return super().validate(attrs)


class CustomAuthTokenSerializer(serializers.Serializer):
    """
    Serializer for returning an authenticated User and Token
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False, required=True
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if not user:
            raise serializers.ValidationError(
                {"detail": "Unable to authenticate with provided credentials"}
            )
        attrs["user"] = user
        return attrs
