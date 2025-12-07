from datetime import timedelta

from rest_framework import serializers

from habits.models import Place, Habit


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ("id", "name", "description")


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор привычки.

    - user берём из текущего запроса (HiddenField + CurrentUserDefault).
    - title — только для чтения (динамическое название привычки).
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

    def validate(self, attrs):
        """
        Дублируем бизнес-валидацию на уровне DRF,
        чтобы получать ошибки уже на уровне API.
        """
        # Объект при update, при create — None
        instance = getattr(self, "instance", None)

        reward = attrs.get("reward", getattr(instance, "reward", ""))
        related_habit = attrs.get("related_habit", getattr(instance, "related_habit", None))
        is_pleasant = attrs.get("is_pleasant", getattr(instance, "is_pleasant", False))
        periodicity = attrs.get("periodicity", getattr(instance, "periodicity", 1))

        errors = {}

        # 1. reward и related_habit взаимоисключающие
        if reward and related_habit is not None:
            msg = "Нельзя одновременно указывать вознаграждение и связанную привычку."
            errors["reward"] = msg
            errors["related_habit"] = msg

        # 2. Связанная привычка должна быть приятной
        if related_habit and not related_habit.is_pleasant:
            errors["related_habit"] = "Связанная привычка должна быть отмечена как приятная."

        # 3. Приятная привычка: можно не ограничивать, но при желании:
        #    например, pleasant нельзя привязать к другой привычке и т.п.
        if is_pleasant and related_habit is not None:
            errors["related_habit"] = (
                "Приятная привычка не может иметь связанную привычку."
            )

        # 4. periodicity >= 1
        if periodicity < 1:
            errors["periodicity"] = "Периодичность должна быть минимум 1 день."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def validate_duration(self, value: timedelta):
        # Пример: ограничить действие до 2 часов
        max_duration = timedelta(hours=2)
        if value <= timedelta(0):
            raise serializers.ValidationError("Время на выполнение должно быть больше нуля.")
        if value > max_duration:
            raise serializers.ValidationError("Время на выполнение не должно превышать 2 часов.")
        return value