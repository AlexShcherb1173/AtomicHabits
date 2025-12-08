from django.conf import settings
from django.db import models


class TelegramProfile(models.Model):
    """
    Привязка пользователя к его Telegram-аккаунту (chat_id).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
        verbose_name="пользователь",
    )
    chat_id = models.CharField(
        max_length=64,
        verbose_name="Telegram chat ID",
        help_text="Идентификатор чата, куда слать уведомления.",
        unique=True,
    )
    username = models.CharField(
        max_length=255,
        verbose_name="Telegram username",
        blank=True,
        help_text="@username в Telegram (по желанию).",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="получать уведомления",
    )

    class Meta:
        verbose_name = "Telegram-профиль"
        verbose_name_plural = "Telegram-профили"

    def __str__(self):
        return f"{self.user} — {self.chat_id}"
