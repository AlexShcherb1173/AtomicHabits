from django.urls import path, include
from rest_framework.routers import DefaultRouter

from habits.views import PlaceViewSet, HabitViewSet, PublicHabitListAPIView

router = DefaultRouter()
router.register(r"places", PlaceViewSet, basename="place")
router.register(r"habits", HabitViewSet, basename="habit")

urlpatterns = [
    # все стандартные CRUD-эндпоинты от ViewSet’ов:
    path("", include(router.urls)),
    # отдельный публичный список привычек:
    path("habits/public/", PublicHabitListAPIView.as_view(), name="public-habits"),
]