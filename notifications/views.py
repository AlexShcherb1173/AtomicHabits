from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TelegramLinkToken
from .serializers import TelegramLinkSerializer


class TelegramLinkAPIView(APIView):
    """
    GET /api/telegram/link/

    Возвращает ссылку вида:
    https://t.me/<BOT_USERNAME>?start=<token>
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # можно удалить/деактивировать старые токены, если нужно
        TelegramLinkToken.objects.filter(user=user, is_used=False).delete()

        link_token = TelegramLinkToken.create_for_user(user=user, lifetime_minutes=30)

        bot_username = settings.TELEGRAM_BOT_USERNAME
        deep_link = f"https://t.me/{bot_username}?start={link_token.token}"

        serializer = TelegramLinkSerializer({"link": deep_link})
        return Response(serializer.data)
