from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allow access only to Admin users."""

    message = "Only Admin users can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.role == "ADMIN"
                or request.user.is_superuser
            )
        )


class IsHR(BasePermission):
    """Allow access only to HR and Admin users."""

    message = "Only HR or Admin users can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in ["ADMIN", "HR"]
                or request.user.is_superuser
            )
        )


class IsEmployee(BasePermission):
    """Allow access only to Employee users."""

    message = "Only Employee users can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "EMPLOYEE"
            and not request.user.is_superuser
        )