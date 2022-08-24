from django.urls import include, path, re_path

from .views import (
    CancelSubscriptionView,
    CreateSubscriptionView,
    MySubscriptionView,
    PaymentMethodView,
    PreviewInvoiceView,
    ReactivateSubscriptionView,
    SubscriptionPriceView,
    UpcommingInvoiceView,
    UpdateSubcriptionView,
)

urlpatterns = [
    path("planes/", SubscriptionPriceView.as_view(), name="prices"),
    path("create/", CreateSubscriptionView.as_view(), name="create"),
    path("cancel/", CancelSubscriptionView.as_view(), name="cancel"),
    path("reactivate/", ReactivateSubscriptionView.as_view(), name="reactivate"),
    path("update/", UpdateSubcriptionView.as_view(), name="update"),
    path("preview-plan-change/", PreviewInvoiceView.as_view(), name="preview-invoice"),
    path("my-subscription/", MySubscriptionView.as_view(), name="my-subscription"),
    path(
        "upcomming-invoice/", UpcommingInvoiceView.as_view(), name="upcomming-invoice"
    ),
    path("my-payment-list/", PaymentMethodView.as_view(), name="payment-list"),
]
