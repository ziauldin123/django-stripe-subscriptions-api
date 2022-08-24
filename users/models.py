from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    name = models.CharField(_("Name of User"), blank=True, null=True, max_length=255)
    email = models.EmailField(_("Email of User"), max_length=255, unique=True)
    customer = models.ForeignKey(
        "djstripe.Customer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The user's Stripe Customer object, if it exists",
    )
    subscription = models.ForeignKey(
        "djstripe.Subscription",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The user's Stripe Subscription object, if it exists",
    )

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def has_active_subscription(self):
        if self.customer and self.subscription:
            if self.subscription.status in ("active", "trialing"):
                return True
        return False

    @property
    def subscription_status(self):
        if self.subscription:
            return self.subscription.status
        return "--------"
