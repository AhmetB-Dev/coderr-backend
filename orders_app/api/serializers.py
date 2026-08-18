from django.shortcuts import get_object_or_404

from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderStatusSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        """Reject updates to fields other than order status."""
        invalid_fields = set(self.initial_data) - {"status"}

        if invalid_fields:
            raise serializers.ValidationError(
                "Only the status field can be updated."
            )

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True)
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
            "offer_detail_id",
        ]
        read_only_fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        """Create an order snapshot from the selected offer detail."""
        detail = get_object_or_404(
            OfferDetail.objects.select_related("offer__user"),
            pk=validated_data["offer_detail_id"],
        )
        return Order.objects.create(
            customer_user=self.context["request"].user,
            business_user=detail.offer.user,
            **self._snapshot_data(detail),
        )

    @staticmethod
    def _snapshot_data(detail):
        """Build immutable order data from an offer detail."""
        return {
            "title": detail.title,
            "revisions": detail.revisions,
            "delivery_time_in_days": detail.delivery_time_in_days,
            "price": detail.price,
            "features": detail.features,
            "offer_type": detail.offer_type,
        }
