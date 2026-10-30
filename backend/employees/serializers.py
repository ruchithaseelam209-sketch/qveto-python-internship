
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Department,
    EmployeeProfile,
    Attendance,
    LeaveType,
    LeaveRequest,
)

from .employee_permissions import is_admin_or_hr

User = get_user_model()


# DEPARTMENT SERIALIZER
class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ("id", "created_at")


# EMPLOYEE PROFILE SERIALIZER
class EmployeeProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        required=True,
    )

    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=Department.objects.all(),
    )

    class Meta:
        model = EmployeeProfile
        fields = [
            "id",
            "user_id",
            "username",
            "email",
            "department_id",
            "department_name",
            "job_title",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def to_internal_value(self, data):
        request = self.context.get("request")

        if (
            request
            and request.user.is_authenticated
            and not is_admin_or_hr(request.user)
        ):
            protected_fields = {
                "user_id",
                "username",
                "email",
                "department_id",
                "department_name",
                "status",
                "job_title",
                "id",
                "created_at",
                "updated_at",
            }

            attempted = protected_fields.intersection(data.keys())

            if attempted:
                raise serializers.ValidationError({
                    field: "This field cannot be changed by an employee."
                    for field in sorted(attempted)
                })

        return super().to_internal_value(data)

    def validate_user(self, user):
        request = self.context.get("request")

        if (
            request
            and request.user.is_authenticated
            and not is_admin_or_hr(request.user)
        ):
            raise serializers.ValidationError(
                "Employees cannot assign profiles to users."
            )

        return user

    def validate_department_id(self, department):
        if not department.is_active:
            raise serializers.ValidationError(
                "Select an active department."
            )

        return department

    def validate_job_title(self, value):
        request = self.context.get("request")

        if (
            request
            and request.user.is_authenticated
            and not is_admin_or_hr(request.user)
        ):
            raise serializers.ValidationError(
                "Only Admin and HR can change job titles."
            )

        return value


# ATTENDANCE SERIALIZER
class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


# LEAVE TYPE SERIALIZER
class LeaveTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveType
        fields = "__all__"
        read_only_fields = (
            "id",
        )


# LEAVE REQUEST SERIALIZER
class LeaveRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LeaveRequest
        fields = "__all__"
        read_only_fields = (
            "id",
            "employee",
            "status",
            "reviewed_by",
            "review_remarks",
            "reviewed_at",
            "created_at",
            "updated_at",
        )

    def validate(self, data):
        start_date = data.get(
            "start_date",
            getattr(self.instance, "start_date", None),
        )

        end_date = data.get(
            "end_date",
            getattr(self.instance, "end_date", None),
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                "End date cannot be before start date."
            )

        return data