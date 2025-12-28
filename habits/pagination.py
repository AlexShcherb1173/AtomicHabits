"""
Пагинация для API привычек.
Используется в HabitViewSet для ограничения количества привычек,
возвращаемых за один запрос.
По ТЗ:
- выводить по 5 привычек на страницу;
- фронтенд не должен иметь возможности менять размер страницы.
"""

from rest_framework.pagination import PageNumberPagination


class HabitPagination(PageNumberPagination):
    """
    Пагинация привычек (PageNumberPagination).
    Особенности:
    - фиксированный размер страницы: 5 элементов;
    - параметр page_size_query_param отключён,
      чтобы клиент не мог менять лимит через query-параметры;
    - max_page_size = 5 для дополнительной защиты.
    """

    page_size = 5
    page_size_query_param = None  # запрещаем изменение лимита со стороны клиента
    max_page_size = 5