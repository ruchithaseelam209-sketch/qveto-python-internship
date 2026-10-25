from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from accounts.permissions import IsAdmin, IsHR, IsEmployee

User = get_user_model()


class AuthenticationTests(APITestCase):
    """Tests for authentication and registration APIs."""

    def test_register_employee(self):
        """Test successful employee registration."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "testemployee",
                "email": "testemployee@example.com",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )
        self.assertTrue(
            User.objects.filter(username="testemployee").exists()
        )

    def test_duplicate_registration(self):
        """Test that duplicate usernames cannot register."""
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="SecurePass123!",
        )

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "existinguser",
                "email": "new@example.com",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

    def test_login_with_valid_credentials(self):
        """Test login with correct credentials."""
        User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="SecurePass123!",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "loginuser",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

    def test_login_with_invalid_password(self):
        """Test login with an incorrect password."""
        User.objects.create_user(
            username="loginuser2",
            email="login2@example.com",
            password="SecurePass123!",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "loginuser2",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            response.data,
        )

    def test_registration_without_password(self):
        """Test registration without a password."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "nopassworduser",
                "email": "nopassword@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

    def test_registration_without_username(self):
        """Test registration without a username."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "email": "nousername@example.com",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

    def test_login_without_password(self):
        """Test login without a password."""
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "loginuser",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

    def test_login_with_inactive_account(self):
        """Test that inactive accounts cannot log in."""
        user = User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="SecurePass123!",
        )
        user.is_active = False
        user.save()

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "inactiveuser",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            response.data,
        )

    def test_public_registration_creates_employee_role(self):
        """Test that public registration creates an employee account."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "roleemployee",
                "email": "roleemployee@example.com",
                "password": "SecurePass123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        user = User.objects.get(username="roleemployee")
        self.assertEqual(user.role, User.Role.EMPLOYEE)

    def test_public_registration_cannot_assign_admin_role(self):
        """Test that public registration cannot assign the admin role."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "publicadmin",
                "email": "publicadmin@example.com",
                "password": "SecurePass123!",
                "role": "ADMIN",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        user = User.objects.get(username="publicadmin")
        self.assertEqual(user.role, User.Role.EMPLOYEE)


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
        """Test permissions granted to Admin users."""
        admin = User.objects.create_user(
            username="permission_admin",
            password="SecurePass123!",
            role="ADMIN",
        )

        self.assertTrue(self.check_permission(IsAdmin, admin))
        self.assertTrue(self.check_permission(IsHR, admin))
        self.assertFalse(self.check_permission(IsEmployee, admin))

    def test_hr_permissions(self):
        """Test permissions granted to HR users."""
        hr = User.objects.create_user(
            username="permission_hr",
            password="SecurePass123!",
            role="HR",
        )

        self.assertFalse(self.check_permission(IsAdmin, hr))
        self.assertTrue(self.check_permission(IsHR, hr))
        self.assertFalse(self.check_permission(IsEmployee, hr))

    def test_employee_permissions(self):
        """Test permissions granted to Employee users."""
        employee = User.objects.create_user(
            username="permission_employee",
            password="SecurePass123!",
            role="EMPLOYEE",
        )

        self.assertFalse(self.check_permission(IsAdmin, employee))
        self.assertFalse(self.check_permission(IsHR, employee))
        self.assertTrue(self.check_permission(IsEmployee, employee))

    def test_anonymous_user_permissions(self):
        """Test that anonymous users have no role-based permissions."""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        for permission_class in (IsAdmin, IsHR, IsEmployee):
            with self.subTest(permission=permission_class.__name__):
                self.assertFalse(
                    permission_class().has_permission(request, None)
                )
