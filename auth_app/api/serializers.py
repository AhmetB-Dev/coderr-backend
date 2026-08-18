from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from auth_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
        allow_blank=True,
    )
    email = serializers.EmailField(
        source="user.email",
        required=False,
    )

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["type", "created_at"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        user = instance.user

        for field, value in user_data.items():
            setattr(user, field, value)

        user.save()
        return super().update(instance, validated_data)


class UserProfileListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(
        source="user.id",
        read_only=True,
    )
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )
    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid username or password."}
            )

        attrs["user"] = user
        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=UserProfile.UserType.choices,
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "repeated_password",
            "type",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        profile_type = validated_data.pop("type")
        validated_data.pop("repeated_password")

        user = User.objects.create_user(**validated_data)

        UserProfile.objects.create(
            user=user,
            type=profile_type,
        )

        Token.objects.create(user=user)

        return user
