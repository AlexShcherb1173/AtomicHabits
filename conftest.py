import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="alex", password="password123")


@pytest.fixture
def user2(db):
    return User.objects.create_user(username="bob", password="password123")


@pytest.fixture
def token(user):
    return Token.objects.get_or_create(user=user)[0]


@pytest.fixture
def auth_client(api_client, token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def auth_client_user2(api_client, user2):
    token2 = Token.objects.get_or_create(user=user2)[0]
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token2.key}")
    return api_client
