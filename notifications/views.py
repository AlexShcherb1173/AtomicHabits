"""
API views for Telegram integration.
Этот модуль содержит endpoint(ы), связанные с интеграцией Telegram:
- выдача одноразовой deep-link ссылки для привязки Telegram-аккаунта к пользователю.
"""

from django.conf import settings
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TelegramLinkToken
from .serializers import TelegramLinkSerializer


@extend_schema(
    tags=["Telegram"],
    summary="Получить ссылку для привязки Telegram",
    description=(
        "Возвращает одноразовую ссылку для привязки Telegram-аккаунта.\n\n"
        "Ссылка имеет вид:\n"
        "`https://t.me/<BOT_USERNAME>?start=<token>`\n\n"
        "Пользователь переходит по ссылке, бот получает `/start <token>` "
        "и по этому токену связывает Telegram chat_id с аккаунтом в системе."
    ),
    responses={
        200: OpenApiResponse(
            response=TelegramLinkSerializer,
            description="Deep-link ссылка для Telegram",
            examples=[
                OpenApiExample(
                    name="Пример ответа",
                    value={"link": "https://t.me/AtomicHabitsBot?start=abcdef"},
                    response_only=True,
                )
            ],
        )
    },
)
class TelegramLinkAPIView(APIView):
    """
    Возвращает одноразовую deep-link ссылку для привязки Telegram.
    Endpoint:
        GET /api/telegram/link/
    Требования:
    - Пользователь должен быть аутентифицирован.
    - Для пользователя создаётся новый токен привязки Telegram.
    - Старые неиспользованные токены можно очищать (чтобы не плодить активные ссылки).
    Ответ:
        {"link": "https://t.me/<BOT_USERNAME>?start=<token>"}
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Сгенерировать одноразовую ссылку для привязки Telegram.
        Алгоритм:
        1) Удаляем старые неиспользованные токены текущего пользователя (опционально, но удобно).
        2) Создаём новый TelegramLinkToken на 30 минут.
        3) Строим deep-link ссылку на бота: https://t.me/<BOT_USERNAME>?start=<token>
        4) Возвращаем ссылку в сериализаторе TelegramLinkSerializer.
        :param request: DRF request
        :return: Response({"link": "<deep_link>"})
        """
        user = request.user

        # Удаляем предыдущие неиспользованные токены (чтобы у юзера была одна актуальная ссылка)
        TelegramLinkToken.objects.filter(user=user, is_used=False).delete()

        # Генерируем новый токен (по умолчанию 30 минут)
        link_token = TelegramLinkToken.create_for_user(user=user, lifetime_minutes=30)

        bot_username = settings.TELEGRAM_BOT_USERNAME
        deep_link = f"https://t.me/{bot_username}?start={link_token.token}"

        serializer = TelegramLinkSerializer({"link": deep_link})
        return Response(serializer.data)
