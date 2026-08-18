from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        """Allow safe access to all users and writes only to the owner."""
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user
