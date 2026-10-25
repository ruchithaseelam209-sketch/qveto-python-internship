
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Department, EmployeeProfile
from .serializers import (
    DepartmentSerializer,
    EmployeeProfileSerializer,
)
from .permissions import (
    DepartmentPermission,
    EmployeeProfilePermission,
    is_admin_or_hr,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [DepartmentPermission]


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.select_related(
        "user",
        "department",
    ).all()

    serializer_class = EmployeeProfileSerializer
    permission_classes = [EmployeeProfilePermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Admin and HR can access all employee profiles.
        if is_admin_or_hr(user):
            return queryset

        # Employees can access only their own profiles.
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        # Only Admin and HR can create employee profiles.
        if not is_admin_or_hr(self.request.user):
            raise PermissionDenied(
                "Only Admin and HR can create employee profiles."
            )

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user

        # Admin and HR can update any employee profile.
        if is_admin_or_hr(user):
            serializer.save()
            return

        # Employees can update only their own profiles.
        if serializer.instance.user_id != user.id:
            raise PermissionDenied(
                "You can only update your own employee profile."
            )

        serializer.save()
