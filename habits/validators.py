import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_duration_max_120_seconds(value: datetime.timedelta) -> None:
    """
    Время выполнения должно быть не больше 120 секунд и больше 0.
    """
    max_duration = datetime.timedelta(seconds=120)

    if value <= datetime.timedelta(0):
        raise ValidationError(_("Время на выполнение должно быть больше 0 секунд."))

    if value > max_duration:
        raise ValidationError(
            _("Время на выполнение не должно превышать 120 секунд (2 минуты).")
        )


def validate_periodicity_1_to_7_days(value: int) -> None:
    """
    Нельзя выполнять привычку реже, чем 1 раз в 7 дней.
    Допустимые значения: от 1 до 7 (1 раз в день ... 1 раз в неделю).
    """
    if value < 1 or value > 7:
        raise ValidationError(
            _("Периодичность должна быть от 1 до 7 дней (не реже, чем раз в неделю).")
        )