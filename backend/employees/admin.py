from django.contrib import admin
from .models import Department, EmployeeProfile, Attendance, LeaveType, LeaveRequest


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department", "job_title", "status")
    search_fields = ("user__username", "job_title")
    list_filter = ("department", "status")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "check_in", "check_out", "status")
    list_filter = ("date", "status")
    search_fields = ("employee__user__username",)


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "annual_allowance", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "reviewed_by",
    )
    list_filter = ("status", "leave_type")
    search_fields = ("employee__user__username", "reason")