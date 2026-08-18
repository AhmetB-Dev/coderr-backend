from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import UserProfile
from offers_app.models import Offer, OfferDetail


class OfferApiTests(APITestCase):
    def setUp(self):
        self.business = self._create_user(
            "business_test",
            UserProfile.UserType.BUSINESS,
        )
        self.customer = self._create_user(
            "customer_test",
            UserProfile.UserType.CUSTOMER,
        )
        self.offer = self._create_offer(self.business)

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

    def _create_offer(self, user, title="Test Offer"):
        offer = Offer.objects.create(
            user=user,
            title=title,
            description="Test description",
        )
        self._create_details(offer)
        return offer

    def _create_details(self, offer):
        detail_data = [
            ("Basic", 100, 5, "basic"),
            ("Standard", 200, 7, "standard"),
            ("Premium", 500, 10, "premium"),
        ]

        for title, price, delivery, offer_type in detail_data:
            OfferDetail.objects.create(
                offer=offer,
                title=title,
                revisions=2,
                delivery_time_in_days=delivery,
                price=price,
                features=["Feature"],
                offer_type=offer_type,
            )

    def _offer_payload(self):
        return {
            "title": "New Offer",
            "description": "New description",
            "details": [
                {
                    "title": "Basic",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Logo"],
                    "offer_type": "basic",
                },
                {
                    "title": "Standard",
                    "revisions": 5,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Logo", "Flyer"],
                    "offer_type": "standard",
                },
                {
                    "title": "Premium",
                    "revisions": 10,
                    "delivery_time_in_days": 10,
                    "price": 500,
                    "features": ["Logo", "Flyer", "Website"],
                    "offer_type": "premium",
                },
            ],
        }

    def test_offer_list_is_public(self):
        response = self.client.get(reverse("offer-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_business_can_create_offer(self):
        self._authenticate(self.business)

        response = self.client.post(
            reverse("offer-list"),
            self._offer_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["details"]), 3)

    def test_customer_cannot_create_offer(self):
        self._authenticate(self.customer)

        response = self.client.post(
            reverse("offer-list"),
            self._offer_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_requires_exactly_three_details(self):
        self._authenticate(self.business)
        payload = self._offer_payload()
        payload["details"] = payload["details"][:2]

        response = self.client.post(
            reverse("offer-list"),
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_detail_requires_authentication(self):
        response = self.client.get(
            reverse(
                "offer-detail",
                kwargs={"pk": self.offer.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_retrieve_offer(self):
        self._authenticate(self.customer)

        response = self.client.get(
            reverse(
                "offer-detail",
                kwargs={"pk": self.offer.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["min_price"], 100)
        self.assertEqual(response.data["min_delivery_time"], 5)

    def test_owner_can_update_offer_detail_without_changing_id(self):
        self._authenticate(self.business)
        basic = self.offer.details.get(offer_type="basic")

        response = self.client.patch(
            reverse(
                "offer-detail",
                kwargs={"pk": self.offer.id},
            ),
            {
                "details": [
                    {
                        "offer_type": "basic",
                        "price": 150,
                    }
                ]
            },
            format="json",
        )

        basic.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(basic.price, 150)
        self.assertEqual(
            basic.id,
            self.offer.details.get(offer_type="basic").id,
        )

    def test_non_owner_cannot_update_offer(self):
        self._authenticate(self.customer)

        response = self.client.patch(
            reverse(
                "offer-detail",
                kwargs={"pk": self.offer.id},
            ),
            {"title": "Forbidden change"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_offer(self):
        self._authenticate(self.business)

        response = self.client.delete(
            reverse(
                "offer-detail",
                kwargs={"pk": self.offer.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(pk=self.offer.id).exists())

    def test_offerdetail_requires_authentication(self):
        detail = self.offer.details.first()

        response = self.client.get(
            reverse(
                "offerdetail-detail",
                kwargs={"pk": detail.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_get_offerdetail(self):
        self._authenticate(self.customer)
        detail = self.offer.details.first()

        response = self.client.get(
            reverse(
                "offerdetail-detail",
                kwargs={"pk": detail.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], detail.id)

    def test_offer_update_requires_offer_type_for_details(self):
        self._authenticate(self.business)
        response = self.client.patch(
            reverse("offer-detail", kwargs={"pk": self.offer.id}),
            {"details": [{"price": 150}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_update_rejects_invalid_offer_type(self):
        self._authenticate(self.business)
        response = self.client.patch(
            reverse("offer-detail", kwargs={"pk": self.offer.id}),
            {"details": [{"offer_type": "gold", "price": 150}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offer_update_rejects_invalid_revisions(self):
        self._authenticate(self.business)
        response = self.client.patch(
            reverse("offer-detail", kwargs={"pk": self.offer.id}),
            {"details": [{"offer_type": "basic", "revisions": -2}]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
