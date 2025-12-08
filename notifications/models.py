import secrets
import datetime
from django.utils import timezone


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

class TelegramLinkToken(models.Model):
    """
    Одноразовый токен для привязки Telegram через /start <token>.
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
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        verbose_name="действителен до",
    )
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "токен привязки Telegram"
        verbose_name_plural = "токены привязки Telegram"

    def __str__(self):
        return f"{self.user} – {self.token} (used={self.is_used})"

    @classmethod
    def create_for_user(cls, user, lifetime_minutes: int = 30):
        """
        Создаёт новый токен для пользователя, можно вызывать при каждом запросе.
        Старые можно помечать использованными/просроченными.
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
        return (not self.is_used) and (self.expires_at > timezone.now())
