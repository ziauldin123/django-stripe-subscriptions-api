from django.urls import path, include
from rest_framework.routers import DefaultRouter

from home.api.v1.viewsets import (
    #SignupViewSet,
    LoginViewSet,
)
from users.viewsets import UserViewSet


router = DefaultRouter()
#router.register("signup", SignupViewSet, basename="signup")
#router.register("login", LoginViewSet, basename="login")
#router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
