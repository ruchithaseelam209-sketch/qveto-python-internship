
from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_admin_or_hr(user):
    """Check whether the user is Admin, HR, or a superuser."""
    return bool(
        user
        and user.is_authenticated
        and (
            user.is_superuser
            or user.role in ("ADMIN", "HR")
        )
    )


class IsAdminOrHR(BasePermission):
    """Allow only Admin, HR, and superusers."""

    def has_permission(self, request, view):
        return is_admin_or_hr(request.user)


class DepartmentPermission(BasePermission):
    """Authenticated users can read; Admin/HR can modify."""

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return (
            request.method in SAFE_METHODS
            or is_admin_or_hr(user)
        )


class EmployeeProfilePermission(BasePermission):
    """Admin/HR manage all profiles; employees access their own."""

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if is_admin_or_hr(user):
            return True

        return request.method in SAFE_METHODS or request.method in (
            "PUT", "PATCH"
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if is_admin_or_hr(user):
            return True

        return bool(
            user.is_authenticated
            and user.role == "EMPLOYEE"
            and obj.user_id == user.id
            and request.method in SAFE_METHODS + ("PUT", "PATCH")
        )
