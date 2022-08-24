from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (
            "User",
            {"fields": ("name", "customer", "subscription")},
        ),
    ) + auth_admin.UserAdmin.fieldsets
    list_display = ["id", "username", "name", "is_superuser", "subscription_status"]
    search_fields = ["name", "username", "email"]
    # inlines = (ProfileInline, UserServiceInline, CredentialsInline)
    # list_select_related = ('profile', 'credential')
