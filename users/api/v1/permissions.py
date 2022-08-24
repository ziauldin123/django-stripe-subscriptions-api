from rest_framework import permissions


class ProfileOwnerORAdmin(permissions.BasePermission):
    message = "You don't have access to view this profile"  # custom error message

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if obj == request.user or request.user.is_superuser or request.user.is_staff:
            return True
        return False


class IsAdmin(permissions.BasePermission):
    # custom error message
    message = "You don't have access to change this need admin rights"

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
