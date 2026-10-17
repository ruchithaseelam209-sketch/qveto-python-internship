import json

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


User = get_user_model()


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new employee account.
    Public registration cannot create Admin or HR accounts.
    """

    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip().lower()
    password = request.data.get("password", "")
    first_name = request.data.get("first_name", "").strip()
    last_name = request.data.get("last_name", "").strip()

    if not username or not email or not password:
        return Response(
            {
                "error": "Username, email, and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) < 8:
        return Response(
            {
                "error": "Password must contain at least 8 characters."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(email__iexact=email).exists():
        return Response(
            {"error": "Email is already registered."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=User.Role.EMPLOYEE,
        )
    except IntegrityError:
        return Response(
            {"error": "Unable to create this account."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message": "Registration successful.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        },
        status=status.HTTP_201_CREATED,
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticate a user with username and password.
    """

    username = request.data.get("username", "").strip()
    password = request.data.get("password", "")

    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:
        return Response(
            {"error": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {"error": "This account is inactive."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return Response(
        {
            "message": "Login successful.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_superuser": user.is_superuser,
            },
        },
        status=status.HTTP_200_OK,
    )