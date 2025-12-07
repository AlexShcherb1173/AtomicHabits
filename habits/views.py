from django.db.models import Q
from rest_framework import viewsets, permissions

from habits.models import Place, Habit
from .serializers import PlaceSerializer, HabitSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Доступ:
    - Читать (GET) могут все анонимно только публичные привычки,
      а автор — свои.
    - Изменять/удалять (PUT/PATCH/DELETE) может только владелец.
    """

    def has_object_permission(self, request, view, obj):
        # Чтение — всегда разрешено (будем фильтровать queryset'ом)
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class PlaceViewSet(viewsets.ModelViewSet):
    """
    CRUD API для справочника мест.
    Можно при желании ограничить права (например, только staff).
    """

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]


class HabitViewSet(viewsets.ModelViewSet):
    """
    CRUD API для привычек.

    - list/retrieve: возвращает публичные привычки + привычки текущего пользователя.
    - create/update/delete: только для авторизованных и только своих привычек.
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        # Для чтения: свои + публичные
        if self.action in ("list", "retrieve"):
            return Habit.objects.filter(
                Q(user=user) | Q(is_public=True)
            ).select_related("user", "place", "related_habit")
        # Для изменения: только свои
        return Habit.objects.filter(user=user).select_related(
            "user", "place", "related_habit"
        )

    def perform_create(self, serializer):
        # user уже берётся из HiddenField, но на всякий случай:
        serializer.save(user=self.request.user)
