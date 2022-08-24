from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, BasePermission

# edit_methods = ("PUT", "PATCH", "POST", "DELETE")


class ActiveSubscription(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.has_active_subscription:
                return True
            raise PermissionDenied(
                {"detail": "You don't have any active subscriptions"}
            )
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.subscription and user.customer:
            if user.subscription.status in ("active", "trialing"):
                print("user has active subscription")
                return True
        raise PermissionDenied({"detail": "You don't have any active subscriptions"})
        return False


class NotActiveSubscription(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.has_active_subscription:
                raise PermissionDenied(
                    {
                        "detail": "You already have active subscriptions upgrade or downgrade it"
                    }
                )
            return True
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.subscription and user.customer:
            if user.subscription.status in ("active", "trialing"):
                print("user has active subscription")
                return True
        raise PermissionDenied({"detail": "You don't have any active subscriptions"})
        return False
