"""
Views приложения accounts.
Содержит API эндпоинты:
- RegisterAPIView: регистрация нового пользователя
- TokenLoginAPIView: логин и получение DRF Token для дальнейшей авторизации
Авторизация проекта: Token-based (rest_framework.authtoken).
"""

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer


@extend_schema(
    summary="Регистрация пользователя",
    description=(
        "Создаёт нового пользователя.\n\n"
        "После регистрации можно выполнить логин и получить Token "
        "через `POST /api/auth/login/`."
    ),
    request=RegisterSerializer,
    responses={201: RegisterSerializer},
    tags=["Auth"],
    auth=None,  # endpoint публичный в Swagger
)
class RegisterAPIView(generics.CreateAPIView):
    """
    Регистрация пользователя.
    POST /api/auth/register/
    Пример тела запроса:
    {
      "username": "alex",
      "email": "alex@example.com",
      "password": "qwerty123",
      "password2": "qwerty123"
    }

    Возвращает созданного пользователя (без пароля).
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        """
        Переопределяем create, чтобы явно вернуть 201 и сериализованные данные.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Логин (получить Token)",
    description=(
        "Проверяет логин и пароль и возвращает токен.\n\n"
        "**Использование токена:**\n"
        "`Authorization: Token <token>`\n\n"
        "В Swagger нажми кнопку **Authorize** и вставь значение в формате:\n"
        "`Token <token>`"
    ),
    request=LoginSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {"token": {"type": "string"}},
            "required": ["token"],
        }
    },
    examples=[
        OpenApiExample(
            "Пример запроса",
            value={"username": "alex", "password": "qwerty123"},
            request_only=True,
        ),
        OpenApiExample(
            "Пример ответа",
            value={"token": "1a2b3c4d..."},
            response_only=True,
        ),
    ],
    tags=["Auth"],
    auth=None,  # endpoint публичный в Swagger
)
class TokenLoginAPIView(APIView):
    """
    Логин пользователя и выдача DRF Token.
    POST /api/auth/login/
    Тело запроса:
    {
      "username": "alex",
      "password": "qwerty123"
    }

    Ответ:
    {
      "token": "<token>"
    }
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # убирает SessionAuth/CSRF для этого endpoint

    def post(self, request, *args, **kwargs):
        """
        Валидирует username/password и возвращает (или создаёт) Token.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response({"token": token.key}, status=status.HTTP_200_OK)
