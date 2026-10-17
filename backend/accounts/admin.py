from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "department",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "department",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "employee_id",
    )

    ordering = ("username",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Employee Information",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "employee_id",
                    "department",
                    "designation",
                    "date_of_joining",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Employee Information",
            {
                "fields": (
                    "role",
                    "phone_number",
                    "employee_id",
                    "department",
                    "designation",
                    "date_of_joining",
                )
            },
        ),
    )