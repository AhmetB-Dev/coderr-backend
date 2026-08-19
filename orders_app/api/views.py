from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from auth_app.models import UserProfile
from orders_app.models import Order

from .permissions import (
    IsCustomerUser,
    IsOrderBusinessUser,
    IsStaffUser,
)
from .serializers import OrderSerializer, OrderStatusSerializer


class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the number of in-progress orders for a business user."""
        business_user = get_object_or_404(
            User.objects.filter(profile__type=UserProfile.UserType.BUSINESS),
            pk=business_user_id,
        )
        count = Order.objects.filter(
            business_user=business_user,
            status=Order.Status.IN_PROGRESS,
        ).count()
        return Response({"order_count": count})


class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Return the number of completed orders for a business user."""
        business_user = get_object_or_404(
            User.objects.filter(profile__type=UserProfile.UserType.BUSINESS),
            pk=business_user_id,
        )
        count = Order.objects.filter(
            business_user=business_user,
            status=Order.Status.COMPLETED,
        ).count()
        return Response({"completed_order_count": count})


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_serializer_class(self):
        """Use the status serializer for partial order updates."""
        if self.action == "partial_update":
            return OrderStatusSerializer
        return OrderSerializer

    def get_permissions(self):
        """Select permissions required for the current order action."""
        permission_map = {
            "create": [IsAuthenticated, IsCustomerUser],
            "partial_update": [IsAuthenticated, IsOrderBusinessUser],
            "destroy": [IsAuthenticated, IsStaffUser],
        }
        classes = permission_map.get(self.action, [IsAuthenticated])
        return [permission() for permission in classes]

    def get_queryset(self):
        """Return the queryset appropriate for the current order action."""
        if self.action == "partial_update":
            return Order.objects.all()
        if self.action == "destroy" and self.request.user.is_staff:
            return Order.objects.all()
        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        ).order_by("-created_at")
