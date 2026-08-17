from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from orders_app.models import Order

from .permissions import IsCustomerUser
from .serializers import OrderSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]
