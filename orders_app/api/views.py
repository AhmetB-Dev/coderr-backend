from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from orders_app.models import Order

from .permissions import (
    IsBusinessUser,
    IsCustomerUser,
    IsOrderBusinessUser,
    IsStaffUser,
)

from .serializers import OrderSerializer, OrderStatusSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import UserProfile


class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
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
        if self.action == "partial_update":
            return OrderStatusSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]

        if self.action == "partial_update":
            return [
                IsAuthenticated(),
                IsBusinessUser(),
                IsOrderBusinessUser(),
            ]

        if self.action == "destroy":
            return [IsAuthenticated(), IsStaffUser()]

        return [IsAuthenticated()]

    def get_queryset(self):
        if self.action == "destroy" and self.request.user.is_staff:
            return Order.objects.all()

        user = self.request.user
        return Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        ).order_by("-created_at")
