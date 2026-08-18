from rest_framework.permissions import BasePermission

from auth_app.models import UserProfile


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)
        return (
            profile is not None
            and profile.type == UserProfile.UserType.CUSTOMER
        )


class IsReviewOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
