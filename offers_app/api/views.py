from django.db.models import Min

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from offers_app.models import Offer, OfferDetail

from .filters import OfferFilter
from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import (
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferUpdateSerializer,
)


class OfferDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]


class OfferViewSet(ModelViewSet):
    queryset = (
        Offer.objects.select_related("user")
        .prefetch_related("details")
        .annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )
        .order_by("id")
    )
    serializer_class = OfferListSerializer
    pagination_class = OfferPagination
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_serializer_class(self):
        """Select the serializer required for the current action."""
        serializer_map = {
            "create": OfferCreateSerializer,
            "retrieve": OfferRetrieveSerializer,
            "partial_update": OfferUpdateSerializer,
        }
        return serializer_map.get(self.action, OfferListSerializer)

    def get_permissions(self):
        """Select permissions required for the current action."""
        permission_map = {
            "create": [IsAuthenticated, IsBusinessUser],
            "retrieve": [IsAuthenticated],
            "partial_update": [IsAuthenticated, IsOfferOwner],
            "destroy": [IsAuthenticated, IsOfferOwner],
        }
        classes = permission_map.get(self.action, [AllowAny])
        return [permission() for permission in classes]
