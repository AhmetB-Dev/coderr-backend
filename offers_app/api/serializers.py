from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ["id"]

    def validate_revisions(self, value):
        if value < -1:
            raise serializers.ValidationError("Revisions must be -1 or greater.")
        return value

    def validate_features(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Features must be a list.")

        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("Every feature must be a string.")

        return value


class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]
        read_only_fields = ["id"]

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError(
                "An offer must contain exactly three details."
            )

        offer_types = {detail["offer_type"] for detail in value}
        required_types = {"basic", "standard", "premium"}

        if offer_types != required_types:
            raise serializers.ValidationError(
                "Details must contain basic, standard and premium."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop("details")
        user = self.context["request"].user

        offer = Offer.objects.create(
            user=user,
            **validated_data,
        )

        for detail_data in details_data:
            OfferDetail.objects.create(
                offer=offer,
                **detail_data,
            )

        return offer


class OfferDetailSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
    )

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
