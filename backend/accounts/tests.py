from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.permissions import IsAdmin, IsHR, IsEmployee

User = get_user_model()


class RolePermissionTests(TestCase):
    """Tests for role-based permission classes."""

    def setUp(self):
        self.factory = APIRequestFactory()

    def check_permission(self, permission_class, user):
        request = self.factory.get("/")
        request.user = user
        permission = permission_class()
        return permission.has_permission(request, None)

    def test_admin_permissions(self):
        admin = User.objects.create_user(
            username="permission_admin",
            password="SecurePass123!",
            role="ADMIN",
        )
        self.assertTrue(self.check_permission(IsAdmin, admin))
        self.assertTrue(self.check_permission(IsHR, admin))
        self.assertFalse(self.check_permission(IsEmployee, admin))

    def test_hr_permissions(self):
        hr = User.objects.create_user(
            username="permission_hr",
            password="SecurePass123!",
            role="HR",
        )
        self.assertFalse(self.check_permission(IsAdmin, hr))
        self.assertTrue(self.check_permission(IsHR, hr))
        self.assertFalse(self.check_permission(IsEmployee, hr))

    def test_employee_permissions(self):
        employee = User.objects.create_user(
            username="permission_employee",
            password="SecurePass123!",
            role="EMPLOYEE",
        )
        self.assertFalse(self.check_permission(IsAdmin, employee))
        self.assertFalse(self.check_permission(IsHR, employee))
        self.assertTrue(self.check_permission(IsEmployee, employee))

    def test_anonymous_user_permissions(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        for permission_class in (IsAdmin, IsHR, IsEmployee):
            with self.subTest(permission=permission_class.__name__):
                self.assertFalse(
                    permission_class().has_permission(request, None)
                )