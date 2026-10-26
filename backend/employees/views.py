from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsHR
from .models import (
    Department,
    EmployeeProfile,
    Attendance,
    LeaveType,
    LeaveRequest,
)
from .serializers import (
    DepartmentSerializer,
    EmployeeProfileSerializer,
    AttendanceSerializer,
    LeaveTypeSerializer,
    LeaveRequestSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsHR()]


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.select_related(
        "user", "department"
    ).all()
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated, IsHR]


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Attendance.objects.select_related(
            "employee", "employee__user"
        )

        if user.is_superuser or user.role in ["ADMIN", "HR"]:
            return queryset

        return queryset.filter(employee__user=user)

    def get_permissions(self):
        if self.action in [
            "create", "update", "partial_update", "destroy"
        ]:
            return [IsAuthenticated(), IsHR()]
        return [IsAuthenticated()]

    def get_employee(self):
        try:
            return EmployeeProfile.objects.get(user=self.request.user)
        except EmployeeProfile.DoesNotExist:
            raise PermissionDenied(
                "Your account does not have an employee profile."
            )

    @action(detail=False, methods=["post"], url_path="check-in")
    def check_in(self, request):
        employee = self.get_employee()
        now = timezone.now()
        today = timezone.localdate()

        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                "check_in": now,
                "status": Attendance.Status.PRESENT,
            },
        )

        if not created:
            if attendance.check_in:
                raise ValidationError(
                    {"detail": "You have already checked in today."}
                )
            attendance.check_in = now
            attendance.status = Attendance.Status.PRESENT
            attendance.save(
                update_fields=["check_in", "status", "updated_at"]
            )

        return Response(
            AttendanceSerializer(attendance).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="check-out")
    def check_out(self, request):
        employee = self.get_employee()

        try:
            attendance = Attendance.objects.get(
                employee=employee,
                date=timezone.localdate(),
            )
        except Attendance.DoesNotExist:
            raise ValidationError(
                {"detail": "Check in before checking out."}
            )

        if not attendance.check_in:
            raise ValidationError(
                {"detail": "Check in before checking out."}
            )

        if attendance.check_out:
            raise ValidationError(
                {"detail": "You have already checked out today."}
            )

        attendance.check_out = timezone.now()
        attendance.save(update_fields=["check_out", "updated_at"])

        return Response(AttendanceSerializer(attendance).data)


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated, IsHR]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = LeaveRequest.objects.select_related(
            "employee",
            "employee__user",
            "leave_type",
            "reviewed_by",
        )

        if user.is_superuser or user.role in ["ADMIN", "HR"]:
            return queryset

        return queryset.filter(employee__user=user)

    def get_permissions(self):
        if self.action in ["approve", "reject", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsHR()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        try:
            employee = EmployeeProfile.objects.get(user=self.request.user)
        except EmployeeProfile.DoesNotExist:
            raise PermissionDenied(
                "Your account does not have an employee profile."
            )

        serializer.save(employee=employee)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        leave_request = self.get_object()

        if leave_request.status != LeaveRequest.Status.PENDING:
            raise ValidationError(
                {"detail": "Only pending leave requests can be approved."}
            )

        leave_request.status = LeaveRequest.Status.APPROVED
        leave_request.reviewed_by = request.user
        leave_request.reviewed_at = timezone.now()
        leave_request.review_remarks = request.data.get(
            "review_remarks", ""
        )
        leave_request.save()

        return Response(LeaveRequestSerializer(leave_request).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        leave_request = self.get_object()

        if leave_request.status != LeaveRequest.Status.PENDING:
            raise ValidationError(
                {"detail": "Only pending leave requests can be rejected."}
            )

        leave_request.status = LeaveRequest.Status.REJECTED
        leave_request.reviewed_by = request.user
        leave_request.reviewed_at = timezone.now()
        leave_request.review_remarks = request.data.get(
            "review_remarks", ""
        )
        leave_request.save()

        return Response(LeaveRequestSerializer(leave_request).data)