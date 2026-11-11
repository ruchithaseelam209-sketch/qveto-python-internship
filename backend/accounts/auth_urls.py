
from django.urls import path
from .views import login, register, logout, csrf, current_user

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("csrf/", csrf, name="csrf"),
    path("me/", current_user, name="current-user"),
]