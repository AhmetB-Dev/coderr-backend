from django_filters import rest_framework as filters

from reviews_app.models import Review


class ReviewFilter(filters.FilterSet):
    """Filter reviews by business user or reviewer."""

    business_user_id = filters.NumberFilter(field_name="business_user_id")
    reviewer_id = filters.NumberFilter(field_name="reviewer_id")

    class Meta:
        model = Review
        fields = []
