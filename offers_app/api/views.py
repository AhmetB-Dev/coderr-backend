from django.db.models import Min
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from offers_app.models import Offer, OfferDetail

from .pagination import OfferPagination
from .permissions import IsBusinessUser, IsOfferOwner
from .serializers import (
    OfferCreateSerializer,
    OfferDetailSerializer,
    OfferFilterSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
    OfferUpdateSerializer,
)


class OfferDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]


class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferListSerializer
    pagination_class = OfferPagination
    filter_backends = [SearchFilter, OrderingFilter]
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
        if self.action == "create":
            return OfferCreateSerializer

        if self.action == "retrieve":
            return OfferRetrieveSerializer

        if self.action == "partial_update":
            return OfferUpdateSerializer

        return OfferListSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsBusinessUser()]

        if self.action == "retrieve":
            return [IsAuthenticated()]

        if self.action in ["partial_update", "destroy"]:
            return [IsAuthenticated(), IsOfferOwner()]

        return [AllowAny()]

    def get_queryset(self):
        params = OfferFilterSerializer(data=self.request.query_params)
        params.is_valid(raise_exception=True)
        self.filter_params = params.validated_data

        queryset = self._base_queryset()
        queryset = self._filter_creator(queryset)
        queryset = self._filter_min_price(queryset)
        return self._filter_delivery_time(queryset)

    def _base_queryset(self):
        return (
            Offer.objects.select_related("user")
            .prefetch_related("details")
            .annotate(
                min_price=Min("details__price"),
                min_delivery_time=Min("details__delivery_time_in_days"),
            )
            .order_by("id")
        )

    def _filter_creator(self, queryset):
        creator_id = self.filter_params.get("creator_id")
        if creator_id:
            queryset = queryset.filter(user_id=creator_id)
        return queryset

    def _filter_min_price(self, queryset):
        min_price = self.filter_params.get("min_price")
        if min_price is not None:
            queryset = queryset.filter(min_price__gte=min_price)
        return queryset

    def _filter_delivery_time(self, queryset):
        max_time = self.filter_params.get("max_delivery_time")
        if max_time is not None:
            queryset = queryset.filter(min_delivery_time__lte=max_time)
        return queryset
