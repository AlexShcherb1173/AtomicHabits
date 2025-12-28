"""
Модели приложения habits.
Содержит:
- Place: справочник мест выполнения привычек.
- Habit: привычка пользователя по ТЗ проекта AtomicHabits.
Важные бизнес-правила (по ТЗ) реализованы в Habit.clean():
1) Нельзя одновременно указывать reward и related_habit.
2) Время выполнения должно быть > 0 и <= 120 секунд (если задано).
3) Связанная привычка (related_habit) может быть только pleasant (is_pleasant=True).
4) У pleasant-привычки не может быть reward или related_habit.
5) Periodicity (периодичность) — от 1 до 7 дней включительно.
"""

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
    Примеры:
    - дом
    - офис
    - спортзал
    - парк
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

    def __str__(self) -> str:
        return self.name


class Habit(models.Model):
    """
    Привычка по книге Джеймса Клира (AtomicHabits).
    Полезная привычка:
    - is_pleasant=False
    - может иметь reward ИЛИ related_habit (pleasant-награду)

    Приятная привычка (награда):
    - is_pleasant=True
    - не может иметь reward
    - не может иметь related_habit
    См. метод clean() — там реализованы все правила ТЗ.
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
        null=True,
        blank=True,
        help_text="Сколько времени требуется на выполнение привычки (максимум 120 секунд).",
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

    def clean(self) -> None:
        """
        Валидирует бизнес-правила (по ТЗ).
        Ошибки возвращаются как словарь по полям, чтобы DRF/админка
        показывали их корректно.
        """
        errors: dict[str, str] = {}

        # 1) reward и related_habit взаимоисключающие
        if self.reward and self.related_habit is not None:
            msg = "Нельзя одновременно указывать вознаграждение и связанную привычку."
            errors["reward"] = msg
            errors["related_habit"] = msg

        # 4) pleasant-привычка не может иметь reward или related_habit
        if self.is_pleasant:
            if self.reward:
                errors["reward"] = "У приятной привычки не может быть вознаграждения."
            if self.related_habit is not None:
                errors["related_habit"] = (
                    "У приятной привычки не может быть связанной привычки."
                )

        # 3) related_habit может быть только pleasant
        if self.related_habit and not self.related_habit.is_pleasant:
            errors["related_habit"] = (
                "Связанная привычка должна быть отмечена как приятная."
            )

        # 5) periodicity: 1..7
        if self.periodicity < 1:
            errors["periodicity"] = "Периодичность должна быть минимум 1 день."
        elif self.periodicity > 7:
            errors["periodicity"] = (
                "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."
            )

        # 2) duration: > 0 и <= 120 секунд (если задано)
        if self.duration is not None:
            if self.duration <= datetime.timedelta(0):
                errors["duration"] = "Время на выполнение должно быть больше нуля."
            elif self.duration > datetime.timedelta(seconds=120):
                errors["duration"] = (
                    "Время на выполнение не должно превышать 120 секунд."
                )

        if errors:
            raise ValidationError(errors)

        super().clean()

    @property
    def title(self) -> str:
        """
        Динамическое «название» привычки.
        Пример:
        «Я буду пить воду ежедневно в 12:00 в офисе»
        """
        if self.periodicity == 1:
            freq = "ежедневно"
        elif self.periodicity == 7:
            freq = "еженедельно"
        else:
            freq = f"каждые {self.periodicity} дней"

        time_str = self.time.strftime("%H:%M")

        place_str = f"в {self.place.name}" if self.place else "где бы то ни было"

        return f"Я буду {self.action.lower()} {freq} в {time_str} {place_str}"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        """
        Сохраняет модель с обязательной проверкой бизнес-правил.
        full_clean() гарантирует вызов:
        - field validators (validators=...)
        - clean()
        """
        self.full_clean()
        return super().save(*args, **kwargs)
