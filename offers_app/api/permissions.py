from rest_framework.permissions import BasePermission

from auth_app.models import UserProfile


class IsBusinessUser(BasePermission):
    def has_permission(self, request, view):
        profile = getattr(request.user, "profile", None)

        return profile is not None and profile.type == UserProfile.UserType.BUSINESS
