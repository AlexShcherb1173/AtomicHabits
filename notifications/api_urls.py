from django.urls import path

from .views import TelegramLinkAPIView

urlpatterns = [
    path("telegram/link/", TelegramLinkAPIView.as_view(), name="telegram-link"),
]