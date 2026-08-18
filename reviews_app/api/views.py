from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from reviews_app.models import Review

from .permissions import IsCustomerUser, IsReviewOwner
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_serializer_class(self):
        if self.action == "partial_update":
            return ReviewUpdateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]
        if self.action in ["partial_update", "destroy"]:
            return [IsAuthenticated(), IsReviewOwner()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Review.objects.all()
        queryset = self._filter_business(queryset)
        return self._filter_reviewer(queryset)

    def _filter_business(self, queryset):
        business_id = self.request.query_params.get("business_user_id")
        if business_id:
            queryset = queryset.filter(business_user_id=business_id)
        return queryset

    def _filter_reviewer(self, queryset):
        reviewer_id = self.request.query_params.get("reviewer_id")
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
