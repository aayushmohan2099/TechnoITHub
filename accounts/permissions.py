from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Custom permission class to restrict access to Admin only.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated and has the role of 'Admin'
        return bool(request.user and request.user.is_authenticated and request.user.role == 'Admin')