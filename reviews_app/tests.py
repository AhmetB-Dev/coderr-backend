from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from reviews_app.models import Review

CREATE_REVIEW_DATA = {
    "rating": 5,
    "description": "Excellent",
}


class ReviewApiTests(APITestCase):
    def setUp(self):
        self.customer = self._create_user("customer", "customer")
        self.other_customer = self._create_user("other_customer", "customer")
        self.business = self._create_user("business", "business")
        self.review = Review.objects.create(
            business_user=self.business,
            reviewer=self.customer,
            rating=4,
            description="Good service",
        )

    def _create_user(self, username, profile_type):
        user = User.objects.create_user(
            username=username,
            password="TestPassword123!",
        )
        UserProfile.objects.create(user=user, type=profile_type)
        Token.objects.create(user=user)
        return user

    def _authenticate(self, user):
        token = Token.objects.get(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def _review_url(self):
        return reverse("review-detail", kwargs={"pk": self.review.id})

    def _create_review_payload(self, description="Excellent"):
        return {
            **CREATE_REVIEW_DATA,
            "business_user": self.business.id,
            "description": description,
        }

    def test_review_list_requires_authentication(self):
        response = self.client.get(reverse("review-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_reviews(self):
        self._authenticate(self.customer)
        response = self.client.get(reverse("review-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_customer_can_create_review(self):
        self._authenticate(self.other_customer)
        response = self.client.post(
            reverse("review-list"),
            self._create_review_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["reviewer"], self.other_customer.id)

    def test_business_cannot_create_review(self):
        self._authenticate(self.business)
        response = self.client.post(
            reverse("review-list"),
            self._create_review_payload("Invalid"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_review_is_rejected(self):
        self._authenticate(self.customer)
        response = self.client.post(
            reverse("review-list"),
            self._create_review_payload("Second review"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_business_user(self):
        self._authenticate(self.customer)
        response = self.client.get(
            reverse("review-list"),
            {"business_user_id": self.business.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_reviewer(self):
        self._authenticate(self.customer)
        response = self.client.get(
            reverse("review-list"),
            {"reviewer_id": self.customer.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_owner_can_update_review(self):
        self._authenticate(self.customer)
        response = self.client.patch(
            self._review_url(),
            {"rating": 5, "description": "Updated review"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)

    def test_non_owner_cannot_update_review(self):
        self._authenticate(self.other_customer)
        response = self.client.patch(
            self._review_url(),
            {"rating": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_update_field_is_rejected(self):
        self._authenticate(self.customer)
        response = self.client.patch(
            self._review_url(),
            {"business_user": self.other_customer.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_owner_cannot_delete_review(self):
        self._authenticate(self.other_customer)
        response = self.client.delete(self._review_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_review(self):
        self._authenticate(self.customer)
        response = self.client.delete(self._review_url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=self.review.id).exists())
