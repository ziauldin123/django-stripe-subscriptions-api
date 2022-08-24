"""holy_wind_34364 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from allauth.account.views import confirm_email
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

urlpatterns = [
    path("", include("home.urls")),
    path("accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    path("users/", include("users.urls", namespace="users")),
    # path("rest-auth/", include("dj_rest_auth.urls")),
    # Override email confirm to use allauth's HTML view instead of rest_auth's API view
    path("rest-auth/registration/account-confirm-email/<str:key>/", confirm_email),
    # path("rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("subscriptions/", include("subscriptions.urls", namespace="subscriptions")),
]

admin.site.site_header = "Subscription App"
admin.site.site_title = "Subscription App Admin Portal"
admin.site.index_title = "Subscription App Admin"

# swagger
api_info = openapi.Info(
    title="My Portal API",
    default_version="v1",
    description="API documentation for Holy Wind App",
)

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    path("api-docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api_docs"),

    re_path(
        r"^apis(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
]


urlpatterns += [path("", TemplateView.as_view(template_name="index.html"))]
urlpatterns += [
    re_path(r"^(?:.*)/?$", TemplateView.as_view(template_name="index.html"))
]
