from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoApiTests(APITestCase):
    def setUp(self):
        self.business = self._create_user(
            "business",
            UserProfile.UserType.BUSINESS,
        )
        self.customer = self._create_user(
            "customer",
            UserProfile.UserType.CUSTOMER,
        )

    def _create_user(self, username, profile_type):
        user = User.objects.create_user(
            username=username,
            password="TestPassword123!",
        )
        UserProfile.objects.create(
            user=user,
            type=profile_type,
        )
        return user

    def test_base_info_is_public(self):
        response = self.client.get(reverse("base-info"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_base_info_returns_correct_counts(self):
        Offer.objects.create(
            user=self.business,
            title="Test Offer",
            description="Description",
        )

        response = self.client.get(reverse("base-info"))

        self.assertEqual(response.data["review_count"], 0)
        self.assertEqual(response.data["business_profile_count"], 1)
        self.assertEqual(response.data["offer_count"], 1)

    def test_base_info_calculates_average_rating(self):
        Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description="Good",
        )

        response = self.client.get(reverse("base-info"))

        self.assertEqual(response.data["review_count"], 1)
        self.assertEqual(response.data["average_rating"], 4.0)
