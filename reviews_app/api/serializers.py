from django.contrib.auth.models import User

from rest_framework import serializers

from auth_app.models import UserProfile
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            profile__type=UserProfile.UserType.BUSINESS
        )
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reviewer",
            "created_at",
            "updated_at",
        ]

    def validate_business_user(self, business_user):
        reviewer = self.context["request"].user
        exists = Review.objects.filter(
            reviewer=reviewer,
            business_user=business_user,
        ).exists()

        if exists:
            raise serializers.ValidationError(
                "You have already reviewed this business user."
            )

        return business_user


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "business_user",
            "reviewer",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        invalid_fields = set(self.initial_data) - {
            "rating",
            "description",
        }

        if invalid_fields:
            raise serializers.ValidationError(
                "Only rating and description can be updated."
            )

        return attrs
