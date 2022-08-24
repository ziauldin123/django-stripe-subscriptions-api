from django.contrib import admin

from .models import SubscriptionCatalogue


class SubscriptionCatalogueAdmin(admin.ModelAdmin):
    list_display = [
        "get_price_id",
        "get_price_nickname",
        "human_readable_price",
        "product",
    ]

    def product(self, obj):
        return obj.price.product.name

    product.short_description = "product"

    def get_price_id(self, obj):
        return obj.price.id

    get_price_id.short_description = "price_id"

    def get_price_nickname(self, obj):
        return obj.price.nickname

    get_price_nickname.short_description = "nickname"

    def human_readable_price(self, obj):
        return obj.price.human_readable_price


admin.site.register(SubscriptionCatalogue, SubscriptionCatalogueAdmin)
