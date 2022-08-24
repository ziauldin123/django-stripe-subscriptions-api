# from django.contrib.postgres.fields import JSONField
from django.db import models
from djstripe.models import Price, Product
from django.db.models import JSONField

class SubscriptionCatalogue(models.Model):

    price = models.ForeignKey(
        "djstripe.Price",
        # null=True,
        # blank=True,
        on_delete=models.CASCADE,
        help_text="The user's Stripe price object, if it exists",
    )

    attributes = JSONField()

    def __str__(self) -> str:
        return self.price.product.name
