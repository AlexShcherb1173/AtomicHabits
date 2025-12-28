"""
Админ-конфигурация приложения habits.
Содержит настройки отображения моделей Place и Habit
в административной панели Django:
- списки полей
- фильтры
- поиск
- автодополнение связей
"""

from django.contrib import admin

from .models import Place, Habit


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    """
    Админ-настройки для модели Place (место выполнения привычки).
    Позволяет:
    - просматривать список мест
    - искать по названию места
    """

    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Админ-настройки для модели Habit (привычка).
    Обеспечивает удобное управление привычками:
    - отображение ключевых атрибутов в списке
    - фильтрацию по типу привычки и периодичности
    - поиск по действию, награде и пользователю
    - автодополнение связей (user, place, related_habit)
    """

    list_display = (
        "action",
        "user",
        "place",
        "time",
        "is_pleasant",
        "related_habit",
        "periodicity",
        "is_public",
        "created_at",
    )
    list_filter = ("is_pleasant", "is_public", "periodicity", "place")
    search_fields = ("action", "reward", "user__username")
    autocomplete_fields = ("user", "place", "related_habit")
