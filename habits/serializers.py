"""
DRF-сериализаторы для приложения habits.
Содержит:
- PlaceSerializer: справочник мест.
- HabitSerializer: привычки с бизнес-валидацией по ТЗ.
"""

from datetime import timedelta

from rest_framework import serializers

from habits.models import Habit, Place


class PlaceSerializer(serializers.ModelSerializer):
    """
    Сериализатор справочника мест (Place).
    Используется для CRUD по местам.
    """

    class Meta:
        model = Place
        fields = ("id", "name", "description")


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор привычки (Habit).
    Особенности:
    - user задаётся автоматически из request.user (HiddenField).
    - title — read-only поле (динамическое название привычки из модели).
    Бизнес-правила (по ТЗ) валидируются на уровне API:
    - reward и related_habit взаимно исключаются;
    - duration: > 0 и <= 120 секунд;
    - periodicity: 1..7;
    - related_habit может быть только pleasant;
    - pleasant-привычка не может иметь reward или related_habit.
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    title = serializers.ReadOnlyField()

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "periodicity",
            "reward",
            "duration",
            "is_public",
            "created_at",
            "updated_at",
            "title",
        )
        read_only_fields = ("id", "created_at", "updated_at", "title")

    def validate_duration(self, value: timedelta) -> timedelta:
        """
        Проверяет длительность выполнения привычки.
        По ТЗ:
        - время выполнения должно быть > 0 секунд;
        - время выполнения должно быть <= 120 секунд.
        """
        if value is None:
            # По текущей модели duration не nullable, и по ТЗ это обязательное поле.
            raise serializers.ValidationError("Время на выполнение обязательно.")

        if value <= timedelta(0):
            raise serializers.ValidationError(
                "Время на выполнение должно быть больше нуля."
            )
        if value > timedelta(seconds=120):
            raise serializers.ValidationError(
                "Время на выполнение не должно превышать 120 секунд."
            )
        return value

    def validate_periodicity(self, value: int) -> int:
        """
        Проверяет периодичность выполнения привычки.
        По ТЗ:
        - нельзя выполнять привычку реже, чем 1 раз в 7 дней;
        - периодичность допустима от 1 до 7 включительно.
        """
        if value < 1:
            raise serializers.ValidationError(
                "Периодичность должна быть минимум 1 день."
            )
        if value > 7:
            raise serializers.ValidationError(
                "Нельзя выполнять привычку реже, чем 1 раз в 7 дней."
            )
        return value

    def validate(self, attrs: dict) -> dict:
        """
        Общая бизнес-валидация для нескольких полей.
        Важно: при update учитываем значения instance, если поле не пришло в attrs.
        """
        instance: Habit | None = getattr(self, "instance", None)

        reward = attrs.get("reward", getattr(instance, "reward", ""))
        related_habit = attrs.get(
            "related_habit", getattr(instance, "related_habit", None)
        )
        is_pleasant = attrs.get("is_pleasant", getattr(instance, "is_pleasant", False))

        errors: dict[str, str] = {}

        # 1) reward и related_habit взаимно исключаются
        if reward and related_habit is not None:
            msg = "Нельзя одновременно указывать вознаграждение и связанную привычку."
            errors["reward"] = msg
            errors["related_habit"] = msg

        # 2) related_habit должен быть pleasant
        if related_habit is not None and not related_habit.is_pleasant:
            errors["related_habit"] = (
                "Связанная привычка должна быть отмечена как приятная."
            )

        # 3) pleasant-привычка не может иметь reward или related_habit
        if is_pleasant:
            if reward:
                errors["reward"] = "У приятной привычки не может быть вознаграждения."
            if related_habit is not None:
                errors["related_habit"] = (
                    "У приятной привычки не может быть связанной привычки."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
