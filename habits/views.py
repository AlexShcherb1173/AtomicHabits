"""
API views для приложения habits.
Содержит:
- PlaceViewSet: CRUD по справочнику мест (требует авторизацию).
- HabitViewSet: CRUD по привычкам текущего пользователя (только свои привычки).
- PublicHabitListAPIView: публичный read-only список привычек (доступен без авторизации).
ТЗ по доступу:
- Каждый пользователь имеет CRUD доступ только к своим привычкам.
- Публичные привычки доступны всем только на просмотр через отдельный endpoint.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, permissions, viewsets

from habits.models import Habit, Place
from habits.pagination import HabitPagination
from habits.serializers import HabitSerializer, PlaceSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: редактировать/удалять объект может только владелец.
    Примечание:
    Для SAFE методов (GET/HEAD/OPTIONS) разрешаем доступ,
    но реальная видимость объектов контролируется queryset'ом.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "user_id", None) == getattr(request.user, "id", None)


@extend_schema_view(
    list=extend_schema(tags=["Habits"], summary="Список мест"),
    retrieve=extend_schema(tags=["Habits"], summary="Получить место"),
    create=extend_schema(tags=["Habits"], summary="Создать место"),
    update=extend_schema(tags=["Habits"], summary="Обновить место"),
    partial_update=extend_schema(tags=["Habits"], summary="Частично обновить место"),
    destroy=extend_schema(tags=["Habits"], summary="Удалить место"),
)
class PlaceViewSet(viewsets.ModelViewSet):
    """
    CRUD API для справочника мест (Place).
    Сейчас доступ ограничен авторизованными пользователями.
    Если нужно — можно ужесточить до admin/staff.
    """

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["Habits"], summary="Список моих привычек (с пагинацией)"),
    retrieve=extend_schema(tags=["Habits"], summary="Получить мою привычку"),
    create=extend_schema(tags=["Habits"], summary="Создать привычку"),
    update=extend_schema(tags=["Habits"], summary="Обновить привычку"),
    partial_update=extend_schema(tags=["Habits"], summary="Частично обновить привычку"),
    destroy=extend_schema(tags=["Habits"], summary="Удалить привычку"),
)
class HabitViewSet(viewsets.ModelViewSet):
    """
    CRUD API для привычек текущего пользователя.
    По ТЗ:
    - пользователь может создавать/читать/редактировать/удалять ТОЛЬКО свои привычки;
    - публичные привычки других пользователей доступны только через отдельный endpoint:
      GET /api/habits/public/ (read-only).
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = HabitPagination

    def get_queryset(self):
        """
        Возвращает queryset только с привычками текущего пользователя.
        Это обеспечивает:
        - список /api/habits/ содержит только мои привычки;
        - retrieve /api/habits/{id}/ не отдаст чужой объект (будет 404).
        """
        user = self.request.user
        return Habit.objects.filter(user=user).select_related(
            "user", "place", "related_habit"
        )

    def perform_create(self, serializer):
        """
        На всякий случай принудительно привязываем привычку к request.user,
        чтобы клиент не мог подложить чужого пользователя.
        """
        serializer.save(user=self.request.user)


@extend_schema(
    summary="Список публичных привычек",
    description="Публичные привычки доступны без авторизации (только чтение).",
    tags=["Habits"],
    auth=[],
)
class PublicHabitListAPIView(generics.ListAPIView):
    """
    Public read-only endpoint для публичных привычек.
    Endpoint:
    - GET /api/habits/public/
    Особенности:
    - доступен анонимно;
    - возвращает только Habit.is_public=True;
    - пагинация: 5 объектов на страницу.
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = HabitPagination

    def get_queryset(self):
        """
        Публичные привычки (без авторизации).
        """
        return Habit.objects.filter(is_public=True).select_related(
            "user", "place", "related_habit"
        )
