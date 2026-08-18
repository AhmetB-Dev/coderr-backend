from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from reviews_app.models import Review

from .filters import ReviewFilter
from .permissions import IsCustomerUser, IsReviewOwner
from .serializers import ReviewSerializer, ReviewUpdateSerializer


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ReviewFilter
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
        """Use the restricted serializer for partial updates."""
        if self.action == "partial_update":
            return ReviewUpdateSerializer
        return ReviewSerializer

    def get_permissions(self):
        """Select permissions required for the current review action."""
        permission_map = {
            "create": [IsAuthenticated, IsCustomerUser],
            "partial_update": [IsAuthenticated, IsReviewOwner],
            "destroy": [IsAuthenticated, IsReviewOwner],
        }
        classes = permission_map.get(self.action, [IsAuthenticated])
        return [permission() for permission in classes]

    def perform_create(self, serializer):
        """Store the authenticated user as the review author."""
        serializer.save(reviewer=self.request.user)
