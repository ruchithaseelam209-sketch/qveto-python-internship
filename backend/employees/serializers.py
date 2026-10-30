
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Department, EmployeeProfile
from .permissions import is_admin_or_hr

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ("id", "created_at")


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

