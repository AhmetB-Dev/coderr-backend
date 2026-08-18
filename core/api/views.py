from django.db.models import Avg

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import UserProfile
from offers_app.models import Offer
from reviews_app.models import Review


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Return aggregate public statistics for the platform."""
        average = Review.objects.aggregate(average=Avg("rating"))["average"]

        return Response(
            {
                "review_count": Review.objects.count(),
                "average_rating": round(average or 0, 1),
                "business_profile_count": UserProfile.objects.filter(
                    type=UserProfile.UserType.BUSINESS
                ).count(),
                "offer_count": Offer.objects.count(),
            }
        )
