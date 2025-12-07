import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .validators import (
    validate_duration_max_120_seconds,
    validate_periodicity_1_to_7_days,
)


class Place(models.Model):
    """
    Справочник мест, где выполняются привычки.
    Например: дом, офис, спортзал, парк.
    """

    name = models.CharField(
        max_length=100,
        verbose_name="название места",
        help_text="Короткое название места (дом, офис, парк и т.п.).",
        unique=True,
    )
    description = models.TextField(
        verbose_name="описание",
        blank=True,
        help_text="Дополнительное описание места (по желанию).",
    )

    class Meta:
        verbose_name = "место"
        verbose_name_plural = "список мест"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Habit(models.Model):
    """
    Привычка по книге Джеймса Клира.

    Правила:
    - Нельзя одновременно указать reward и related_habit.
    - В связанные привычки могут попадать только приятные (is_pleasant=True).
    - У приятной привычки (is_pleasant=True) не может быть reward и related_habit.
    - Периодичность: от 1 до 7 дней.
    - Время выполнения: > 0 и ≤ 120 секунд.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="пользователь",
    )

    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="habits",
        verbose_name="место",
        help_text="Место, где выполняется привычка. Можно оставить пустым.",
    )

    time = models.TimeField(
        verbose_name="время",
        help_text="Время, когда необходимо выполнять привычку.",
    )

    action = models.CharField(
        max_length=255,
        verbose_name="действие",
        help_text="Что именно нужно делать: пить воду, гулять, медитировать и т.д.",
    )

    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="приятная привычка",
        help_text="Отметьте, если эта привычка является приятной (используется как награда).",
    )

    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reward_for",
        verbose_name="связанная привычка",
        help_text="Приятная привычка, являющаяся наградой.",
        limit_choices_to={"is_pleasant": True},
    )

    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="периодичность (дни)",
        help_text=(
            "Как часто выполнять привычку (в днях). "
            "Допустимо от 1 до 7 (не реже, чем раз в неделю)."
        ),
        validators=[validate_periodicity_1_to_7_days],
    )

    reward = models.CharField(
        max_length=255,
        verbose_name="вознаграждение",
        blank=True,
        help_text="Вознаграждение, если НЕ используется приятная привычка.",
    )

    duration = models.DurationField(
        verbose_name="время на выполнение",
        default=datetime.timedelta(seconds=60),
        help_text="Сколько времени требуется на выполнение привычки.",
        validators=[validate_duration_max_120_seconds],
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name="публичная привычка",
        help_text="Показывать ли привычку другим пользователям.",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="обновлена")

    class Meta:
        verbose_name = "привычка"
        verbose_name_plural = "привычки"
        ordering = ("-created_at",)

    # -------------------------
    #  БИЗНЕС-ВАЛИДАЦИЯ
    # -------------------------

    def clean(self):
        errors = {}

        # 1) Исключить одновременный выбор связанной привычки и вознаграждения
        if self.reward and self.related_habit:
            msg = "Нельзя одновременно указывать вознаграждение и связанную привычку."
            errors["reward"] = msg
            errors["related_habit"] = msg

        # 2) В связанные привычки могут попадать только приятные привычки
        if self.related_habit and not self.related_habit.is_pleasant:
            errors["related_habit"] = (
                "В связанные привычки могут попадать только привычки "
                "с признаком приятной привычки."
            )

        # 3) У приятной привычки не может быть вознаграждения или связанной привычки
        if self.is_pleasant:
            if self.reward:
                errors["reward"] = (
                    "У приятной привычки не может быть вознаграждения."
                )
            if self.related_habit:
                errors["related_habit"] = (
                    "У приятной привычки не может быть связанной привычки."
                )

        # validators уже проверяют duration и periodicity,
        # но можно подстраховаться/дополнить логику при необходимости.

        if errors:
            raise ValidationError(errors)

    # -------------------------
    #  ДИНАМИЧЕСКОЕ НАЗВАНИЕ
    # -------------------------

    @property
    def title(self) -> str:
        """Генерирует текст вида:
        «Я буду пить воду ежедневно в 12:00 в офисе»
        """
        if self.periodicity == 1:
            freq = "ежедневно"
        elif self.periodicity == 7:
            freq = "еженедельно"
        else:
            freq = f"каждые {self.periodicity} дней"

        time_str = self.time.strftime("%H:%M")

        if self.place:
            place_str = f"в {self.place.name}"
        else:
            place_str = "где бы то ни было"

        return f"Я буду {self.action.lower()} {freq} в {time_str} {place_str}"

    def __str__(self):
        return self.title
