from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from auth_app.models import UserProfile

from .permissions import IsProfileOwnerOrReadOnly
from .serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserProfileListSerializer,
    UserProfileSerializer,
)


def _auth_payload(user, token):
    """Build the authentication response payload for a user."""
    return {
        "token": token.key,
        "username": user.username,
        "email": user.email,
        "user_id": user.id,
    }


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.select_related("user")
    serializer_class = UserProfileSerializer
    permission_classes = [
        IsAuthenticated,
        IsProfileOwnerOrReadOnly,
    ]
    lookup_field = "user_id"
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "head", "options"]


class BusinessProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.filter(
        type=UserProfile.UserType.BUSINESS
    ).select_related("user")
    serializer_class = UserProfileListSerializer
    permission_classes = [IsAuthenticated]


class CustomerProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.filter(
        type=UserProfile.UserType.CUSTOMER
    ).select_related("user")
    serializer_class = UserProfileListSerializer
    permission_classes = [IsAuthenticated]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate a user and return the existing or new token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(_auth_payload(user, token))


class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a user and return the created authentication token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response(
            _auth_payload(user, token),
            status=status.HTTP_201_CREATED,
        )
