import djstripe
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from djstripe.models import Subscription
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from rest_framework.views import APIView
from subscriptions.models import SubscriptionCatalogue
from subscriptions.services import get_or_create_customer

from .permissions import ActiveSubscription, NotActiveSubscription
from .serializers import (
    CancelSubscriptionSerializer,
    CreateSubscriptionSerializer,
    PriceIdSerializer,
    SubscriptionCatalogueSerializer,
    SubscriptionSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionPriceView(ListAPIView):
    serializer_class = SubscriptionCatalogueSerializer

    def get_queryset(self):
        return SubscriptionCatalogue.objects.all()


class CreateSubscriptionView(APIView):
    """
    after choosing price you want to subscripe  you must not have active subscriptions
    """

    permission_classes = [NotActiveSubscription]
    serializer_class = CreateSubscriptionSerializer

    @swagger_auto_schema(
        operation_description="description", request_body=CreateSubscriptionSerializer
    )
    def post(self, request, *args, **kwargs):
        """ "
        passing the price id you want to subscripe to
        """
        # validate Price_id
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            price_id = serializer.validated_data["price_id"]
            user = request.user
            customer = get_or_create_customer(user)
            # delete in-completed subscriptions to prevent doublicated payment
            if user.subscription:
                # delete incompleted subscription
                # this voiding the invoice to prevent invoice doublication
                stripe.Subscription.delete(user.subscription.id)
            try:
                # Create the subscription. Note we're using
                # expand here so that the API will return the Subscription's related
                # latest invoice, and that latest invoice's payment_intent
                # so we can collect payment information and confirm the payment on the front end.

                # Create the subscription
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[
                        {
                            "price": price_id,
                        }
                    ],
                    payment_behavior="default_incomplete",
                    expand=["latest_invoice.payment_intent"],
                )
                user.subscription = Subscription.sync_from_stripe_data(subscription)
                user.save()
                return Response(
                    data={
                        "subscriptionId": subscription.id,
                        "clientSecret": subscription.latest_invoice.payment_intent.client_secret,
                    },
                    status=HTTP_201_CREATED,
                )

            except Exception as e:
                print("subscription error message")
                return Response(
                    data={"error": e.user_message}, status=HTTP_400_BAD_REQUEST
                )

        return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)


class ReactivateSubscriptionView(APIView):
    """
    reactivate subscription only when subscription cancelled
    and still valid till period end
    """

    def post(self, request, **kwargs):
        """
        the user must have subscription and subscription status must be active or trial.
        Subscription to be reactivated must be cancelled at period end

        """
        try:
            subscription = request.user.subscription
            if not (subscription):
                return Response(
                    {"detail": "You don not have any subscription"},
                    status=HTTP_404_NOT_FOUND,
                )
            if subscription.status in ("active", "trialing"):
                if subscription.cancel_at_period_end == True:
                    sub = subscription.reactivate()
                    subscription = stripe.Subscription.retrieve(subscription.id)
                    return Response(data=subscription, status=HTTP_201_CREATED)
                else:
                    return Response(
                        data={"detail": "Your subscription already active"},
                        status=HTTP_200_OK,
                    )

            else:
                return Response(
                    data={
                        "detail": "You Don not have any subscription, please subscripe!!"
                    },
                    status=HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            print("errror", e)
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)


# alternative solution
class CancelSubscriptionView1(APIView):
    serializer_class = CancelSubscriptionSerializer

    @swagger_auto_schema(
        operation_description="description", request_body=CancelSubscriptionSerializer
    )
    def post(self, request, *args, **kwargs):
        """cancelling subscription will cancel subsription at period end
        this will prevente further disputes
        """
        user = request.user
        serializer = self.serializer_class(data=request.data, context={"user": user})
        if serializer.is_valid():
            try:
                # make sure the user deleting his own subscriptions
                subscription_id = serializer.validated_data("subscription_id")
                stripe.api_key = settings.STRIPE_SECRET_KEY
                # Cancel the subscription by deleting it
                # deletedSubscription = stripe.Subscription.delete(data['subscriptionId'], "cancel_at_period_end"=True)
                # another way to cancel @period end
                updatedSubscription = stripe.Subscription.modify(
                    subscription_id, cancel_at_period_end=True
                )

                djstripe.models.Subscription.sync_from_stripe_data(updatedSubscription)
                # if you want to use djstripe
                # sub = user.subscription.cancel(cancel_at_period_end =True)
                return Response(data=updatedSubscription, status=HTTP_201_CREATED)
            except Exception as e:
                print("errror", e)
                return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
        return Response(data=serializer.error, status=HTTP_400_BAD_REQUEST)


class CancelSubscriptionView(APIView):
    def post(self, request, *args, **kwargs):
        """cancelling subscription will cancel subsription at period end
        this will prevent further disputes and user can reactive his
        subscription during this period
        """
        user = request.user
        try:
            subscription = user.subscription
            # make sure the user deleting his own subscriptions
            if subscription:
                if subscription.status == "active" or subscription.status == "trialing":
                    # sub_object = subscription.cancel(at_period_end=True)
                    updatedSubscription = stripe.Subscription.modify(
                        subscription.id, cancel_at_period_end=True
                    )

                    Subscription.sync_from_stripe_data(updatedSubscription)
                    return Response(data=updatedSubscription, status=HTTP_201_CREATED)
            return Response(
                data={"detail": "you don not have active subscription "},
                status=HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            print("errror", e)
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)


class UpdateSubcriptionView(APIView):

    serializer_class = PriceIdSerializer

    @swagger_auto_schema(
        operation_description="description", request_body=PriceIdSerializer
    )
    def post(self, request, *args, **kwargs):
        """
        Upgrade or downgrade the subscription plans
        by send new price you want it will be updated
        and here we will run som properation
        refer to following link to know more about proprations
        https://stripe.com/docs/billing/subscriptions/prorations
        """
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                stripe.api_key = settings.STRIPE_SECRET_KEY
                current_subscription = self.request.user.subscription
                if current_subscription:
                    subscription = stripe.Subscription.retrieve(current_subscription.id)
                    new_subscription = stripe.Subscription.modify(
                        current_subscription.id,
                        cancel_at_period_end=False,
                        proration_behavior="create_prorations",
                        items=[
                            {
                                "id": subscription["items"]["data"][0].id,
                                "price": serializer.validated_data["new_price_id"],
                            }
                        ],
                    )
                    new_sub = Subscription.sync_from_stripe_data(new_subscription)
                    return Response(
                        data={"detail": "your plan has been changed"},
                        status=HTTP_200_OK,
                    )

                return Response(
                    data={"detail": "You don not have active subscription"},
                    status=HTTP_400_BAD_REQUEST,
                )
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(data={"error": str(e)}, status=403)


class PreviewInvoiceView(APIView):
    # Simulating authenticated user. Lookup the logged in user in your
    # database, and set customer_id to the Stripe Customer ID of that user.
    """
    preview price change before upgrade or downgrade
    """
    serializer_class = PriceIdSerializer
    permission_classes = [ActiveSubscription]

    @swagger_auto_schema(
        operation_description="description", request_body=serializer_class
    )
    def post(self, request, *args, **kwargs):
        """
        This API call doesn’t modify the subscription, it returns the upcoming invoice
        based only on the parameters that you pass.
        Changing the price  result in a proration.
        do you will see invoice preview if you want to change subscriptions

        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            customer_id = request.user.customer.id
            subscription_id = request.user.subscription.id
            new_price_id = serializer.validated_data["new_price_id"]
            try:
                # Retrieve the subscription
                subscription = stripe.Subscription.retrieve(subscription_id)
                # Retrive the Invoice
                invoice = stripe.Invoice.upcoming(
                    customer=customer_id,
                    subscription=subscription_id,
                    subscription_items=[
                        {
                            "id": subscription["items"]["data"][0].id,
                            "price": new_price_id,
                        }
                    ],
                )
                return Response(data=invoice, status=HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, 403)


class MySubscriptionView(APIView):
    """
    get user active subscription
    """

    serializer_class = SubscriptionSerializer

    def get(self, request, *args, **kwargs):
        """
        View current loged on user subscription if found
        """
        user = self.request.user
        if user.subscription:
            # retrieve subscription just to update subscription
            subscription = stripe.Subscription.retrieve(user.subscription.id)
            Subscription.sync_from_stripe_data(subscription)
            # serializer = self.serializer_class(instance=user.subscription)
            return Response(data=subscription, status=HTTP_200_OK)

        return Response(
            data={"detail": "No Subscription found"}, status=HTTP_404_NOT_FOUND
        )


class UpcommingInvoiceView(APIView):
    """
    check what is invoice of next billing cycle
    """

    permission_classes = [ActiveSubscription]

    def get(self, request, *args, **kwargs):
        """
        preview the upcomming invoice which not created yet
        """
        customer_id = request.user.customer.id
        subscription_id = request.user.subscription.id

        try:
            # Retrive the upcomming Invoice for subscription
            invoice = stripe.Invoice.upcoming(
                customer=customer_id,
                subscription=subscription_id,
            )
            return Response(data=invoice, status=HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, 403)


class PaymentMethodView(APIView):
    def get(self, request, *args, **kwargs):
        """
        View all saved payment attached to user so he can select from them later on
        """
        try:
            customer = request.user.customer
            if customer:
                payments_list = stripe.Customer.list_payment_methods(
                    customer.id,
                    type="card",
                )
                # paymentMethod = stripe.PaymentMethod.retrieve(
                #     data['paymentMethodId'],
                # )
                return Response(data=payments_list, status=HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, 403)

        return Response(
            data={"detail": "No payment methods attached to user"},
            status=HTTP_404_NOT_FOUND,
        )
