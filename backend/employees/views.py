
from django.utils import timezone
from django.utils.dateparse import parse_date

from django.db.models import Count, Q

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

from .employee_permissions import (
    DepartmentPermission,
    EmployeeProfilePermission,
    is_admin_or_hr,
)


# DEPARTMENT MANAGEMENT
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [DepartmentPermission]


# EMPLOYEE PROFILE MANAGEMENT
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

        if is_admin_or_hr(user):
            return queryset

        return queryset.filter(user=user)

    def perform_create(self, serializer):
        if not is_admin_or_hr(self.request.user):
            raise PermissionDenied(
                "Only Admin and HR can create employee profiles."
            )

        serializer.save()


# ATTENDANCE MANAGEMENT
class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = Attendance.objects.select_related(
            "employee",
            "employee__user",
        )

        # Employees can access only their own records
        if not is_admin_or_hr(user):
            queryset = queryset.filter(employee__user=user)

        # Date-wise filtering
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            start_date = parse_date(start_date)

            if not start_date:
                raise ValidationError({
                    "start_date": (
                        "Enter a valid date in YYYY-MM-DD format."
                    )
                })

            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)

            if not end_date:
                raise ValidationError({
                    "end_date": (
                        "Enter a valid date in YYYY-MM-DD format."
                    )
                })

            queryset = queryset.filter(date__lte=end_date)

        if start_date and end_date and start_date > end_date:
            raise ValidationError({
                "detail": (
                    "Start date cannot be later than end date."
                )
            })

        # Employee filtering (HR/Admin only)
        employee_id = self.request.query_params.get("employee_id")

        if employee_id:
            if not is_admin_or_hr(user):
                raise PermissionDenied(
                    "Only HR or Admin can filter by employee."
                )

            try:
                employee_id = int(employee_id)

                if employee_id <= 0:
                    raise ValueError

            except ValueError:
                raise ValidationError({
                    "employee_id": "Enter a valid employee ID."
                })

            queryset = queryset.filter(
                employee_id=employee_id
            )

        return queryset

    def get_permissions(self):
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [IsAuthenticated(), IsHR()]

        if self.action == "report":
            return [IsAuthenticated(), IsHR()]

        return [IsAuthenticated()]

    def get_employee(self):
        try:
            return EmployeeProfile.objects.get(
                user=self.request.user
            )
        except EmployeeProfile.DoesNotExist:
            raise PermissionDenied(
                "Your account does not have an employee profile."
            )

    # EMPLOYEE CHECK-IN
    @action(
        detail=False,
        methods=["post"],
        url_path="check-in",
    )
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
                update_fields=[
                    "check_in",
                    "status",
                    "updated_at",
                ]
            )

        return Response(
            AttendanceSerializer(attendance).data,
            status=(
                status.HTTP_201_CREATED
                if created
                else status.HTTP_200_OK
            ),
        )

    # EMPLOYEE CHECK-OUT
    @action(
        detail=False,
        methods=["post"],
        url_path="check-out",
    )
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

        attendance.save(
            update_fields=[
                "check_out",
                "updated_at",
            ]
        )

        return Response(
            AttendanceSerializer(attendance).data
        )

    # MONTHLY ATTENDANCE SUMMARY
    @action(
        detail=False,
        methods=["get"],
        url_path="monthly-summary",
    )
    def monthly_summary(self, request):
        today = timezone.localdate()

        year = request.query_params.get("year", today.year)
        month = request.query_params.get("month", today.month)

        try:
            year = int(year)
            month = int(month)

            if year < 2000 or year > 9999:
                raise ValueError

            if month < 1 or month > 12:
                raise ValueError

        except (TypeError, ValueError):
            raise ValidationError({
                "detail": "Provide a valid year and month."
            })

        queryset = self.get_queryset().filter(
            date__year=year,
            date__month=month,
        )

        summary = queryset.aggregate(
            total_days=Count("id"),
            present=Count(
                "id",
                filter=Q(status=Attendance.Status.PRESENT),
            ),
            absent=Count(
                "id",
                filter=Q(status=Attendance.Status.ABSENT),
            ),
            half_day=Count(
                "id",
                filter=Q(status=Attendance.Status.HALF_DAY),
            ),
            on_leave=Count(
                "id",
                filter=Q(status=Attendance.Status.ON_LEAVE),
            ),
        )

        return Response({
            "year": year,
            "month": month,
            **summary,
        })

    # HR ATTENDANCE REPORT
    @action(
        detail=False,
        methods=["get"],
        url_path="report",
    )
    def report(self, request):
        queryset = self.get_queryset()

        return Response(
            AttendanceSerializer(
                queryset,
                many=True,
            ).data
        )


# LEAVE TYPE MANAGEMENT
class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated, IsHR]


# LEAVE REQUEST MANAGEMENT
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

        if is_admin_or_hr(user):
            return queryset

        return queryset.filter(
            employee__user=user
        )

    def get_permissions(self):
        if self.action in [
            "approve",
            "reject",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [
                IsAuthenticated(),
                IsHR(),
            ]

        return [IsAuthenticated()]

    def perform_create(self, serializer):
        try:
            employee = EmployeeProfile.objects.get(
                user=self.request.user
            )
        except EmployeeProfile.DoesNotExist:
            raise PermissionDenied(
                "Your account does not have an employee profile."
            )

        serializer.save(employee=employee)

    @action(
        detail=True,
        methods=["post"],
        url_path="approve",
    )
    def approve(self, request, pk=None):
        leave_request = self.get_object()

        if leave_request.status != LeaveRequest.Status.PENDING:
            raise ValidationError({
                "detail": (
                    "Only pending leave requests can be approved."
                )
            })

        leave_request.status = LeaveRequest.Status.APPROVED
        leave_request.reviewed_by = request.user
        leave_request.reviewed_at = timezone.now()

        leave_request.review_remarks = request.data.get(
            "review_remarks",
            "",
        )

        leave_request.save()

        return Response(
            LeaveRequestSerializer(leave_request).data
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="reject",
    )
    def reject(self, request, pk=None):
        leave_request = self.get_object()

        if leave_request.status != LeaveRequest.Status.PENDING:
            raise ValidationError({
                "detail": (
                    "Only pending leave requests can be rejected."
                )
            })

        leave_request.status = LeaveRequest.Status.REJECTED
        leave_request.reviewed_by = request.user
        leave_request.reviewed_at = timezone.now()

        leave_request.review_remarks = request.data.get(
            "review_remarks",
            "",
        )

        leave_request.save()

        return Response(
            LeaveRequestSerializer(leave_request).data
        )
