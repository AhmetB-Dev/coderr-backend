from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.viewsets import ModelViewSet

from offers_app.models import Offer

from .permissions import IsBusinessUser
from .serializers import OfferCreateSerializer

from auth_app.models import UserProfile


class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)

        return profile is not None and profile.type == UserProfile.UserType.BUSINESS


class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferCreateSerializer
    permission_classes = [IsAuthenticated, IsBusinessUser]
    http_method_names = ["post", "head", "options"]
