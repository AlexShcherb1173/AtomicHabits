"""
URL-конфигурация API для приложения habits.
Содержит:
- публичный эндпоинт для просмотра публичных привычек
- стандартные CRUD-эндпоинты для привычек и мест,
  автоматически сгенерированные DRF Router'ом
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from habits.views import PlaceViewSet, HabitViewSet, PublicHabitListAPIView


# Router для стандартных CRUD-эндпоинтов ViewSet'ов
router = DefaultRouter()
router.register(r"places", PlaceViewSet, basename="place")
router.register(r"habits", HabitViewSet, basename="habit")


urlpatterns = [
    # Публичный список привычек (доступен без авторизации, только чтение)
    path(
        "habits/public/",
        PublicHabitListAPIView.as_view(),
        name="public-habits",
    ),
    # Все стандартные CRUD-эндпоинты от ViewSet’ов:
    # - /places/
    # - /habits/
    # - /habits/<id>/
    path("", include(router.urls)),
]
