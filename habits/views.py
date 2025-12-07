from django.db.models import Q
from rest_framework import viewsets, permissions, generics
from rest_framework.pagination import PageNumberPagination

from habits.models import Place, Habit
from .serializers import PlaceSerializer, HabitSerializer


class HabitPagination(PageNumberPagination):
    """
    Пагинация для списка привычек: по 5 штук на страницу.
    GET /api/habits/?page=2
    """
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Права доступа к отдельной привычке (object-level permission):
    - Для безопасных методов (GET/HEAD/OPTIONS) доступ разрешён всем
      аутентифицированным пользователям, если объект попал в queryset.
    - Для небезопасных (PUT/PATCH/DELETE) — только если obj.user == request.user.

    Таким образом:
    - редактировать/удалять можно ТОЛЬКО свои привычки;
    - чужие публичные привычки доступны только для чтения.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class PlaceViewSet(viewsets.ModelViewSet):
    """
    CRUD API для справочника мест.
    Пока доступен только аутентифицированным пользователям.
    """

    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]


class HabitViewSet(viewsets.ModelViewSet):
    """
    CRUD API для привычек.

    Правила доступа:
    - Любой аутентифицированный пользователь:
        * видит ВСЕ свои привычки (публичные и непубличные),
        * видит публичные привычки других пользователей,
        * НЕ может редактировать или удалять чужие привычки.
    - CRUD (create, update, delete) фактически только над собственными привычками.
    """

    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = HabitPagination

    def get_queryset(self):
        user = self.request.user

        # list / retrieve:
        #   - свои привычки (любые)
        #   - чужие только с is_public=True
        if self.action in ("list", "retrieve"):
            return (
                Habit.objects.filter(Q(user=user) | Q(is_public=True))
                .select_related("user", "place", "related_habit")
            )

        # create / update / partial_update / destroy:
        #   - работаем только со своими привычками
        return Habit.objects.filter(user=user).select_related(
            "user", "place", "related_habit"
        )

    def perform_create(self, serializer):
        # user приезжает из request, другие пользователи не могут подложить чужой id
        serializer.save(user=self.request.user)

class PublicHabitListAPIView(generics.ListAPIView):
    """
    Список публичных привычек.
    GET /api/habits/public/
    """

    queryset = Habit.objects.filter(is_public=True).select_related(
        "user", "place", "related_habit"
    )
    serializer_class = HabitSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = HabitPagination
