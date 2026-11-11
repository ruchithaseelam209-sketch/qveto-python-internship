from django.urls import path

from . import views
from .csrf_views import csrf_token

app_name = "accounts"

urlpatterns = [
    path("csrf/", csrf_token, name="csrf_token"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
]