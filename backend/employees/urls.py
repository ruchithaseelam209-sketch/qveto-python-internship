

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DepartmentViewSet, EmployeeProfileViewSet

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="department")
router.register("employees", EmployeeProfileViewSet, basename="employee")

urlpatterns = [
    path("", include(router.urls)),
]

