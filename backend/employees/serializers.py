from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Department, EmployeeProfile

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


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
        queryset=Department.objects.filter(is_active=True),
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
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def to_internal_value(self, data):
        request = self.context.get("request")

        if (
            request
            and request.user.is_authenticated
            and request.user.role == User.Role.EMPLOYEE
            and "user_id" in data
        ):
            raise serializers.ValidationError({
                "user_id": (
                    "Employees cannot assign or change profile ownership."
                )
            })

        return super().to_internal_value(data)

    def validate_user(self, user):
        request = self.context.get("request")

        if (
            request
            and request.user.is_authenticated
            and request.user.role == User.Role.EMPLOYEE
        ):
            raise serializers.ValidationError(
                "Employees cannot assign profiles to users."
            )

        return user