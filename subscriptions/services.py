import djstripe
import stripe
from django.conf import settings
from djstripe import settings as djstripe_settings
from djstripe.models import Customer


def get_or_create_customer(user, dj_stripe_api=False):

    if dj_stripe_api:
        customer = Customer.get_or_create(subscriber=user)
        user.customer = customer
        user.save()
        return customer
    else:
        if user.customer:
            return user.customer
        else:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            customer = stripe.Customer.create(
                email=user.email,
                name=user.username,
                # livemode=False,#djstripe_settings.STRIPE_LIVE_MODE,
            )
            customer = djstripe.models.Customer.sync_from_stripe_data(customer)
            user.customer = customer
            user.save()
            return customer
