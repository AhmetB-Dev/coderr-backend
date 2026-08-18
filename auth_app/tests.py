from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile


class AuthApiTests(APITestCase):
    def setUp(self):
        self.customer = self._create_user(
            "customer_test",
            "customer",
        )
        self.business = self._create_user(
            "business_test",
            "business",
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
        Token.objects.create(user=user)
        return user

    def _authenticate(self, user):
        token = Token.objects.get(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_registration_creates_user_profile_and_token(self):
        response = self.client.post(
            reverse("registration"),
            {
                "username": "new_customer",
                "email": "new@example.com",
                "password": "Password123!",
                "repeated_password": "Password123!",
                "type": "customer",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(User.objects.filter(username="new_customer").exists())
        self.assertEqual(
            response.data["username"],
            "new_customer",
        )
        self.assertIn("token", response.data)

    def test_registration_rejects_different_passwords(self):
        response = self.client.post(
            reverse("registration"),
            {
                "username": "new_customer",
                "email": "new@example.com",
                "password": "Password123!",
                "repeated_password": "WrongPassword123!",
                "type": "customer",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_returns_token(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "customer_test",
                "password": "TestPassword123!",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["user_id"],
            self.customer.id,
        )
        self.assertIn("token", response.data)

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "customer_test",
                "password": "wrong",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_profile_requires_authentication(self):
        response = self.client.get(
            reverse(
                "profile-detail",
                kwargs={"pk": self.customer.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_profile_owner_can_update_profile(self):
        self._authenticate(self.customer)

        response = self.client.patch(
            reverse(
                "profile-detail",
                kwargs={"pk": self.customer.id},
            ),
            {
                "first_name": "Ahmet",
                "location": "Siegen",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["first_name"],
            "Ahmet",
        )
        self.assertEqual(
            response.data["location"],
            "Siegen",
        )

    def test_other_user_cannot_update_profile(self):
        self._authenticate(self.business)

        response = self.client.patch(
            reverse(
                "profile-detail",
                kwargs={"pk": self.customer.id},
            ),
            {
                "first_name": "Changed",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_business_list_contains_business_only(self):
        self._authenticate(self.customer)

        response = self.client.get(reverse("business-profiles"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["type"],
            "business",
        )

    def test_customer_list_contains_customer_only(self):
        self._authenticate(self.business)

        response = self.client.get(reverse("customer-profiles"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["type"],
            "customer",
        )

    def test_profile_empty_fields_are_not_null(self):
        self._authenticate(self.customer)

        response = self.client.get(
            reverse(
                "profile-detail",
                kwargs={"pk": self.customer.id},
            )
        )

        fields = [
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
        ]

        for field in fields:
            self.assertEqual(
                response.data[field],
                "",
            )

    def test_profile_list_empty_fields_are_not_null(self):
        self._authenticate(self.business)

        response = self.client.get(reverse("customer-profiles"))

        profile = response.data[0]

        fields = [
            "first_name",
            "last_name",
            "location",
            "tel",
            "description",
            "working_hours",
        ]

        for field in fields:
            self.assertEqual(
                profile[field],
                "",
            )
