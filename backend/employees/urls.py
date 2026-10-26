from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet,
    EmployeeProfileViewSet,
    AttendanceViewSet,
    LeaveTypeViewSet,
    LeaveRequestViewSet,
)

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="department")
router.register("employees", EmployeeProfileViewSet, basename="employee")
router.register("attendance", AttendanceViewSet, basename="attendance")
router.register("leave-types", LeaveTypeViewSet, basename="leave-type")
router.register("leave-requests", LeaveRequestViewSet, basename="leave-request")

urlpatterns = router.urls