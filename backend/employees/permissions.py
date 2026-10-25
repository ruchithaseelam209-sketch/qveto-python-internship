from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_admin_or_hr(user):
    return (
        user.is_authenticated
        and user.role in ("ADMIN", "HR")
    )


class IsAdminOrHR(BasePermission):
    """Allow only Admin and HR users."""

    def has_permission(self, request, view):
        return is_admin_or_hr(request.user)


class DepartmentPermission(BasePermission):
    """Allow authenticated users to read departments.
    Only Admin and HR can modify them.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return is_admin_or_hr(request.user)


class EmployeeProfilePermission(BasePermission):
    """Restrict employees to their own profile."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if is_admin_or_hr(request.user):
            return True

        # Employees can read/update their own profile,
        # but cannot create or delete profiles.
        return request.method in SAFE_METHODS or request.method in (
            "PUT",
            "PATCH",
        )

    def has_object_permission(self, request, view, obj):
        if is_admin_or_hr(request.user):
            return True

        return (
            request.user.role == "EMPLOYEE"
            and obj.user_id == request.user.id
            and request.method in SAFE_METHODS + ("PUT", "PATCH")
        )
