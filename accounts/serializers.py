"""
Сериализаторы для аутентификации и регистрации пользователей.
Содержит:
- RegisterSerializer — регистрация нового пользователя
- LoginSerializer — проверка логина и пароля для получения токена
"""

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации пользователя.
    Используется для:
    POST /api/auth/register/
    Особенности:
    - требует подтверждение пароля (password + password2)
    - пароль сохраняется в захешированном виде
    """

    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Пароль пользователя (минимум 6 символов).",
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Повтор пароля для подтверждения.",
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2")
        read_only_fields = ("id",)

    def validate(self, attrs):
        """
        Проверяет совпадение паролей.
        """
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Пароли не совпадают."}
            )
        return attrs

    def create(self, validated_data):
        """
        Создаёт пользователя с захешированным паролем.
        """
        validated_data.pop("password2")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор авторизации пользователя.
    Используется для:
    POST /api/auth/login/
    Проверяет:
    - корректность username + password
    - возвращает объект пользователя для выдачи Token
    """

    username = serializers.CharField(
        help_text="Имя пользователя.",
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Пароль пользователя.",
    )

    def validate(self, attrs):
        """
        Проверяет логин и пароль через Django authenticate().
        """
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError(
                "Неверный логин или пароль."
            )

        attrs["user"] = user
        return attrs