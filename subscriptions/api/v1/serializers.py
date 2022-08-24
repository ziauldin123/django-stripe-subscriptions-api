from operator import sub

from djstripe.models import Price, Product, Subscription
from rest_framework import serializers
from subscriptions.models import SubscriptionCatalogue


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name"]


class PriceSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Price
        fields = [
            "id",
            "human_readable_price",
            "currency",
            "product",
            "recurring",
            "unit_amount_decimal",
        ]


class SubscriptionCatalogueSerializer(serializers.ModelSerializer):
    price = PriceSerializer()

    class Meta:
        model = SubscriptionCatalogue
        fields = ["price", "attributes"]


class CreateSubscriptionSerializer(serializers.Serializer):
    price_id = serializers.CharField(required=True)


class PriceIdSerializer(serializers.Serializer):
    new_price_id = serializers.CharField(required=True)

    def validate_price_id(self, new_price_id):
        return new_price_id.upper()


class CancelSubscriptionSerializer(serializers.Serializer):
    subscribtion_id = serializers.CharField(required=True)

    def validate_subscribtion_id(self, sub_id):
        user = self.context.get("user", None)
        if user:
            if user.subscription:
                if not sub_id != user.subscription.id:
                    raise serializers.ValidationError("not valid subscription id")
        return sub_id


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
