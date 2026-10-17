from django.urls import path
from .views import login, register

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
]