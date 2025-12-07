from django.contrib import admin

from .models import Place, Habit


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
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
