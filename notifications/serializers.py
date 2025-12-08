from rest_framework import serializers


class TelegramLinkSerializer(serializers.Serializer):
    link = serializers.CharField(read_only=True)