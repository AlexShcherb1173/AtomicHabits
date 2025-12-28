"""
Модели приложения notifications.
Отвечают за:
- привязку пользователя к Telegram (chat_id);
- хранение одноразовых токенов для deep-link авторизации через Telegram-бота.
"""

import datetime
import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


class TelegramProfile(models.Model):
    """
    Привязка пользователя к его Telegram-аккаунту.
    Используется для:
    - хранения chat_id Telegram;
    - отправки уведомлений о привычках;
    - включения/отключения уведомлений пользователем.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
        verbose_name="пользователь",
    )
    chat_id = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Telegram chat ID",
        help_text="Идентификатор чата, куда отправляются уведомления.",
    )
    username = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Telegram username",
        help_text="Имя пользователя в Telegram (@username), если доступно.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="уведомления включены",
        help_text="Если выключено — напоминания в Telegram не отправляются.",
    )

    class Meta:
        verbose_name = "Telegram-профиль"
        verbose_name_plural = "Telegram-профили"
        ordering = ("user",)

    def __str__(self) -> str:
        return f"{self.user} — {self.chat_id}"


class TelegramLinkToken(models.Model):
    """
    Одноразовый токен для привязки Telegram-аккаунта.
    Используется в deep-link:
    https://t.me/<BOT_USERNAME>?start=<token>
    После использования или истечения срока действия токен становится невалидным.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_link_tokens",
        verbose_name="пользователь",
    )
    token = models.CharField(
        max_length=128,
        unique=True,
        verbose_name="токен",
        help_text="Одноразовый токен для привязки Telegram.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="создан",
    )
    expires_at = models.DateTimeField(
        verbose_name="действителен до",
        help_text="Дата и время, после которых токен считается просроченным.",
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="использован",
        help_text="Отмечается True после успешной привязки Telegram.",
    )

    class Meta:
        verbose_name = "токен привязки Telegram"
        verbose_name_plural = "токены привязки Telegram"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        status = "used" if self.is_used else "active"
        return f"{self.user} — {self.token} ({status})"

    @classmethod
    def create_for_user(cls, user, lifetime_minutes: int = 30) -> "TelegramLinkToken":
        """
        Создаёт новый одноразовый токен для пользователя.
        :param user: пользователь, для которого создаётся токен
        :param lifetime_minutes: срок действия токена в минутах
        :return: созданный TelegramLinkToken
        """
        token = secrets.token_urlsafe(32)
        now = timezone.now()
        expires_at = now + datetime.timedelta(minutes=lifetime_minutes)

        return cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at,
        )

    def is_valid(self) -> bool:
        """
        Проверяет, валиден ли токен.
        Токен считается валидным, если:
        - он не был использован;
        - текущее время меньше expires_at.
        """
        return (not self.is_used) and (self.expires_at > timezone.now())
