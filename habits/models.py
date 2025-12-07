import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Place(models.Model):
    """
    Справочник мест, где выполняются привычки.
    Например: "дом", "офис", "спортзал", "парк".
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
    Привычка по книге Джеймса Клира.

    Важные моменты:
    - Пользователь — создатель привычки.
    - Место — FK на справочник Place.
    - Признак приятной привычки (is_pleasant) — булево поле.
    - Связанная привычка — FK на саму себя, обычно приятная.
    - Вознаграждение и связанная привычка ВЗАИМОИСКЛЮЧАЮЩИЕ.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="пользователь",
        help_text="Пользователь, создавший привычку.",
    )

    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="habits",
        verbose_name="место",
        help_text="Место, где выполняется привычка. Можно оставить пустым — 'где бы то ни было'.",
    )

    time = models.TimeField(
        verbose_name="время",
        help_text="Время, когда необходимо выполнять привычку.",
    )

    action = models.CharField(
        max_length=255,
        verbose_name="действие",
        help_text="Что именно вы будете делать (например: пить воду, гулять и т.п.).",
    )

    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="приятная привычка",
        help_text=(
            "Если включено — привычка является приятной (используется как награда), "
            "а не полезной."
        ),
    )

    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reward_for",
        verbose_name="связанная привычка",
        help_text=(
            "Приятная привычка, которая является наградой за выполнение этой привычки. "
            "Используется для полезных привычек."
        ),
        limit_choices_to={"is_pleasant": True},
    )

    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="периодичность (дни)",
        help_text="Как часто выполнять привычку в днях (по умолчанию — каждый день).",
    )

    reward = models.CharField(
        max_length=255,
        verbose_name="вознаграждение",
        blank=True,
        help_text=(
            "Чем вы вознаградите себя после выполнения привычки "
            "(если не используете связанную приятную привычку)."
        ),
    )

    duration = models.DurationField(
        verbose_name="время на выполнение",
        default=datetime.timedelta(minutes=5),
        help_text="Примерное время, которое требуется для выполнения привычки.",
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name="публичная привычка",
        help_text=(
            "Если включено — привычка публикуется в общий доступ, "
            "чтобы другие пользователи могли брать её в пример."
        ),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="создана",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="обновлена",
    )

    class Meta:
        verbose_name = "привычка"
        verbose_name_plural = "привычки"
        ordering = ("-created_at",)

    # === Бизнес-логика ===

    def clean(self):
        """
        Валидация бизнес-правил:

        1. reward и related_habit взаимно исключаются.
        2. Если указана related_habit, она должна быть приятной.
        3. periodicity >= 1.
        """
        errors = {}

        # 1. Взаимоисключаемость reward и related_habit
        if self.reward and self.related_habit is not None:
            msg = "Нельзя одновременно указывать вознаграждение и связанную привычку."
            errors["reward"] = msg
            errors["related_habit"] = msg

        # 2. Связанная привычка должна быть приятной
        if self.related_habit and not self.related_habit.is_pleasant:
            errors["related_habit"] = "Связанная привычка должна быть отмечена как приятная."

        # 3. Ограничение периодичности
        if self.periodicity < 1:
            errors["periodicity"] = "Периодичность должна быть минимум 1 день."

        if errors:
            raise ValidationError(errors)

    @property
    def title(self) -> str:
        """
        Динамическое «название» привычки:

        «Я буду пить воду ежедневно в 12:00, где бы то ни было»
        или
        «Я буду гулять каждый день в 19:00 в парке».
        """
        # периодичность → текст
        if self.periodicity == 1:
            freq = "ежедневно"
        elif self.periodicity == 7:
            freq = "еженедельно"
        else:
            freq = f"каждые {self.periodicity} дней"

        time_str = self.time.strftime("%H:%M") if self.time else "в удобное время"

        if self.place:
            place_str = f"в {self.place.name}"
        else:
            place_str = "где бы то ни было"

        return f"Я буду {self.action.lower()} {freq} в {time_str} {place_str}"

    def __str__(self) -> str:
        return self.title
