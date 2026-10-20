from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):

    def test_register_employee(self):
        """Test that a new employee can register."""
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
        """Test that registration fails when password is missing."""
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