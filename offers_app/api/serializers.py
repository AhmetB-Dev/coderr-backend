from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferFilterSerializer(serializers.Serializer):
    creator_id = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    min_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=0,
    )
    max_delivery_time = serializers.IntegerField(
        required=False,
        min_value=0,
    )
    page_size = serializers.IntegerField(
        required=False,
        min_value=1,
    )


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


class OfferDetailUpdateSerializer(OfferDetailSerializer):
    offer_type = serializers.ChoiceField(choices=OfferDetail.OfferType.choices)

    class Meta(OfferDetailSerializer.Meta):
        extra_kwargs = {
            "title": {"required": False},
            "revisions": {"required": False},
            "delivery_time_in_days": {"required": False},
            "price": {"required": False},
            "features": {"required": False},
        }


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
        required_types = {"basic", "standard", "premium"}
        if len(value) != 3:
            raise serializers.ValidationError(
                "An offer must contain exactly three details."
            )
        offer_types = {detail["offer_type"] for detail in value}
        if offer_types != required_types:
            raise serializers.ValidationError(
                "Details must contain basic, standard and premium."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )
        details = [OfferDetail(offer=offer, **data) for data in details_data]
        OfferDetail.objects.bulk_create(details)
        return offer


class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailUpdateSerializer(
        many=True,
        required=False,
    )

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
        offer_types = [detail.get("offer_type") for detail in value]
        if any(offer_type is None for offer_type in offer_types):
            raise serializers.ValidationError(
                "Each detail requires an offer_type."
            )
        if len(offer_types) != len(set(offer_types)):
            raise serializers.ValidationError("Duplicate offer_type values are not allowed.")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", [])

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        self._update_details(instance, details_data)

        return instance

    def _update_details(self, offer, details_data):
        for detail_data in details_data:
            offer_type = detail_data.pop("offer_type")
            detail = offer.details.get(offer_type=offer_type)

            for field, value in detail_data.items():
                setattr(detail, field, value)

            detail.save()


class OfferUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "url",
        ]

    def get_url(self, obj):
        request = self.context.get("request")
        path = f"/api/offerdetails/{obj.id}/"

        if request:
            return request.build_absolute_uri(path)

        return path


class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(
        many=True,
        read_only=True,
    )
    user_details = OfferUserSerializer(
        source="user",
        read_only=True,
    )
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
        read_only=True,
    )
    min_delivery_time = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]


class OfferRetrieveSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(
        many=True,
        read_only=True,
    )
    min_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False,
        read_only=True,
    )
    min_delivery_time = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        ]
