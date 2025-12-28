"""
Валидаторы бизнес-правил для модели Habit.
Содержит независимые функции-валидаторы, которые используются
на уровне модели (models.py) и обеспечивают соблюдение требований ТЗ.
"""

import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_duration_max_120_seconds(value: datetime.timedelta | None) -> None:
    """
    Проверяет длительность выполнения привычки.
    Правила:
    - значение может быть None (длительность не указана);
    - длительность должна быть больше 0 секунд;
    - длительность не должна превышать 120 секунд.

    Используется в поле Habit.duration.
    """
    if value is None:
        return

    if value <= datetime.timedelta(0):
        raise ValidationError(
            _("Время на выполнение должно быть больше нуля.")
        )

    if value > datetime.timedelta(seconds=120):
        raise ValidationError(
            _("Время на выполнение не должно превышать 120 секунд.")
        )


def validate_periodicity_1_to_7_days(value: int) -> None:
    """
    Проверяет периодичность выполнения привычки.
    Правила:
    - привычка должна выполняться не реже, чем 1 раз в 7 дней;
    - допустимые значения: от 1 до 7 включительно.

    Используется в поле Habit.periodicity.
    """
    if value < 1:
        raise ValidationError(
            _("Периодичность должна быть минимум 1 день.")
        )

    if value > 7:
        raise ValidationError(
            _("Нельзя выполнять привычку реже, чем 1 раз в 7 дней.")
        )