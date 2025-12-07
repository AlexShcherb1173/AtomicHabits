from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import RegisterAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="auth-register"),
    path("login/", obtain_auth_token, name="auth-login"),
]