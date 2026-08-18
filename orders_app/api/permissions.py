from rest_framework.permissions import BasePermission

from auth_app.models import UserProfile


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        """Allow access only to authenticated customer profiles."""
        profile = getattr(request.user, "profile", None)
        return (
            profile is not None
            and profile.type == UserProfile.UserType.CUSTOMER
        )


class IsOrderBusinessUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        """Allow updates only to the assigned business user."""
        profile = getattr(request.user, "profile", None)
        return (
            profile is not None
            and profile.type == UserProfile.UserType.BUSINESS
            and obj.business_user == request.user
        )


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        """Allow access only to staff users."""
        return request.user.is_staff
