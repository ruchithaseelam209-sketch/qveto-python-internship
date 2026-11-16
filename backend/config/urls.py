from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # Authentication: Login, Logout, Register, CSRF
    path("api/auth/", include("accounts.auth_urls")),

    # Employee Management, Departments, Attendance and Leave
    path("api/", include("employees.urls")),
]