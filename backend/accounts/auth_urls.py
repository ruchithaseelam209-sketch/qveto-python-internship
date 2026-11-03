from django.urls import path
from .views import login, register, logout

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
]