from django.urls import include, path
from users.views import user_detail_view, user_redirect_view, user_update_view

app_name = "subscriptions"

urlpatterns = [
    path("api/", include("subscriptions.api.v1.urls")),
]
