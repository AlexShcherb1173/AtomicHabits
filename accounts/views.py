from rest_framework import generics, permissions
from .serializers import RegisterSerializer


class RegisterAPIView(generics.CreateAPIView):
    """
    Регистрация пользователя.
    POST /api/auth/register/
    {
      "username": "alex",
      "email": "alex@example.com",
      "password": "qwerty123",
      "password2": "qwerty123"
    }
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
