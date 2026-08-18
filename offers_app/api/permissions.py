from rest_framework.permissions import BasePermission

from auth_app.models import UserProfile


class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        """Allow access only to authenticated business profiles."""
        profile = getattr(request.user, "profile", None)

        return (
            profile is not None
            and profile.type == UserProfile.UserType.BUSINESS
        )


class IsOfferOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        """Allow object changes only to the offer owner."""
        return obj.user == request.user
