from django.contrib.auth import get_user_model
from django.db import transaction
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


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class EmployeeCreateSerializer(serializers.Serializer):
    # Existing user workflow
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )

    # New user workflow
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=False,
    )
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
    )
    phone_number = serializers.CharField(
        max_length=15,
        required=False,
        allow_blank=True,
    )
    employee_id = serializers.CharField(
        max_length=20,
        required=False,
    )

    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True),
    )
    job_title = serializers.CharField(max_length=100)

    status = serializers.ChoiceField(
        choices=EmployeeProfile.Status.choices,
        default=EmployeeProfile.Status.ACTIVE,
    )

    date_of_joining = serializers.DateField(
        required=False,
        allow_null=True,
    )

    def validate(self, data):
        existing_user = data.get("user_id")

        if existing_user:
            if EmployeeProfile.objects.filter(user=existing_user).exists():
                raise serializers.ValidationError({
                    "user_id": "This user already has an employee profile."
                })
        else:
            required_fields = ("username", "email", "password", "employee_id")
            missing_fields = [
                field for field in required_fields if not data.get(field)
            ]

            if missing_fields:
                raise serializers.ValidationError({
                    field: "This field is required when creating a new employee account."
                    for field in missing_fields
                })

        return data

    def validate_username(self, value):
        value = value.strip()

        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username already exists."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )

        return value

    def validate_employee_id(self, value):
        value = value.strip()

        if User.objects.filter(employee_id__iexact=value).exists():
            raise serializers.ValidationError(
                "This employee ID already exists."
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        department = validated_data["department_id"]
        existing_user = validated_data.get("user_id")

        if existing_user:
            user = existing_user
        else:
            user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=validated_data.get("first_name", ""),
                last_name=validated_data.get("last_name", ""),
                phone_number=validated_data.get("phone_number", ""),
                employee_id=validated_data["employee_id"],
                department=department.name,
                designation=validated_data["job_title"],
                date_of_joining=validated_data.get("date_of_joining"),
                role=User.Role.EMPLOYEE,
            )

        employee = EmployeeProfile.objects.create(
            user=user,
            department=department,
            job_title=validated_data["job_title"],
            status=validated_data.get(
                "status",
                EmployeeProfile.Status.ACTIVE,
            ),
            date_of_joining=validated_data.get("date_of_joining"),
        )

        return employee


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

    employee_id = serializers.CharField(
        source="user.employee_id",
        read_only=True,
    )

    phone_number = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )

    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True,
    )

    last_name = serializers.CharField(
        source="user.last_name",
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
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "employee_id",
            "department_id",
            "department_name",
            "job_title",
            "status",
            "date_of_joining",
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
                "date_of_joining",
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


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = "__all__"
        read_only_fields = ("id",)


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