from django_filters import rest_framework as filters

from offers_app.models import Offer


class OfferFilter(filters.FilterSet):
    """Filter offers by creator, minimum price, and delivery time."""

    creator_id = filters.NumberFilter(field_name="user_id")
    min_price = filters.NumberFilter(
        field_name="min_price",
        lookup_expr="gte",
    )
    max_delivery_time = filters.NumberFilter(
        field_name="min_delivery_time",
        lookup_expr="lte",
    )

    class Meta:
        model = Offer
        fields = []
