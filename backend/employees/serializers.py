
from rest_framework import serializers

from accounts.models import User
from .models import Department, EmployeeProfile


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


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
        write_only=True,
    )

    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=Department.objects.filter(is_active=True),
        write_only=True,
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
