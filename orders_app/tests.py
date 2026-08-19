from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from offers_app.models import Offer, OfferDetail
from orders_app.models import Order


class OrderApiTests(APITestCase):
    def setUp(self):
        self.customer = self._create_user("customer", "customer")
        self.business = self._create_user("business", "business")
        self.other = self._create_user("other", "customer")
        self.staff = self._create_staff()
        self.detail = self._create_detail()
        self.order = self._create_order()

    def _create_user(self, username, profile_type):
        user = User.objects.create_user(
            username=username,
            password="TestPassword123!",
        )
        UserProfile.objects.create(user=user, type=profile_type)
        Token.objects.create(user=user)
        return user

    def _create_staff(self):
        user = User.objects.create_user(
            username="staff",
            password="TestPassword123!",
            is_staff=True,
        )
        Token.objects.create(user=user)
        return user

    def _authenticate(self, user):
        token = Token.objects.get(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def _create_offer(self):
        return Offer.objects.create(
            user=self.business,
            title="Logo Offer",
            description="Description",
        )

    def _create_detail(self):
        return OfferDetail.objects.create(
            offer=self._create_offer(),
            title="Basic Logo",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo", "Business Card"],
            offer_type="basic",
        )

    def _create_order(self, status_value="in_progress"):
        return Order.objects.create(
            customer_user=self.customer,
            business_user=self.business,
            title="Basic Logo",
            revisions=3,
            delivery_time_in_days=5,
            price=150,
            features=["Logo"],
            offer_type="basic",
            status=status_value,
        )

    def _order_url(self):
        return reverse("order-detail", kwargs={"pk": self.order.id})

    def test_order_list_requires_authentication(self):
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_sees_own_orders(self):
        self._authenticate(self.customer)
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_business_sees_related_orders(self):
        self._authenticate(self.business)
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_unrelated_user_does_not_see_order(self):
        self._authenticate(self.other)
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_customer_can_create_order(self):
        self._authenticate(self.customer)
        response = self.client.post(
            reverse("order-list"),
            {"offer_detail_id": self.detail.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["business_user"], self.business.id)
        self.assertEqual(response.data["status"], "in_progress")

    def test_business_cannot_create_order(self):
        self._authenticate(self.business)
        response = self.client.post(
            reverse("order-list"),
            {"offer_detail_id": self.detail.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_offer_detail_is_rejected(self):
        self._authenticate(self.customer)
        response = self.client.post(reverse("order-list"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_offer_detail_returns_404(self):
        self._authenticate(self.customer)
        response = self.client.post(
            reverse("order-list"),
            {"offer_detail_id": 99999},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_business_can_update_order_status(self):
        self._authenticate(self.business)
        response = self.client.patch(
            self._order_url(),
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_customer_cannot_update_order_status(self):
        self._authenticate(self.customer)
        response = self.client.patch(
            self._order_url(),
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unknown_order_update_returns_404(self):
        self._authenticate(self.customer)
        url = reverse("order-detail", kwargs={"pk": 99999})
        response = self.client.patch(url, {"status": "completed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_order_status_is_rejected(self):
        self._authenticate(self.business)
        response = self.client.patch(
            self._order_url(),
            {"status": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_price_cannot_be_updated(self):
        self._authenticate(self.business)
        response = self.client.patch(
            self._order_url(),
            {"price": 999},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_staff_cannot_delete_order(self):
        self._authenticate(self.business)
        response = self.client.delete(self._order_url())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_delete_order(self):
        self._authenticate(self.staff)
        response = self.client.delete(self._order_url())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(pk=self.order.id).exists())

    def test_order_count_returns_in_progress_count(self):
        self._authenticate(self.customer)
        url = reverse(
            "order-count",
            kwargs={"business_user_id": self.business.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_count"], 1)

    def test_completed_order_count(self):
        self._create_order(status_value="completed")
        self._authenticate(self.customer)
        url = reverse(
            "completed-order-count",
            kwargs={"business_user_id": self.business.id},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["completed_order_count"], 1)
