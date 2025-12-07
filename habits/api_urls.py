from rest_framework.routers import DefaultRouter

from habits.api.views import PlaceViewSet, HabitViewSet

router = DefaultRouter()
router.register(r"places", PlaceViewSet, basename="place")
router.register(r"habits", HabitViewSet, basename="habit")

urlpatterns = router.urls