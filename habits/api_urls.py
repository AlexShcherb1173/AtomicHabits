
from django.urls import path
from rest_framework.routers import DefaultRouter

from habits.views import PlaceViewSet, HabitViewSet, PublicHabitListAPIView

router = DefaultRouter()
router.register(r"places", PlaceViewSet, basename="place")
router.register(r"habits", HabitViewSet, basename="habit")

uurlpatterns = router.urls + [
    path("habits/public/", PublicHabitListAPIView.as_view(), name="public-habits"),
]