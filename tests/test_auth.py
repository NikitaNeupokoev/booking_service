import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_user_success(client: AsyncClient):
    """Тест успешной регистрации нового пользователя"""
    response = await client.post(
        '/api/auth/register',
        json={
            'username': 'tester_junior',
            'email': 'test_junior@example.com',
            'password': 'password123',
            'full_name': 'Тестовый Джун'
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data['username'] == 'tester_junior'
    assert data['email'] == 'test_junior@example.com'
    assert 'id' in data


async def test_login_user_success(client: AsyncClient):
    """Тест успешной авторизации и получения JWT-токена"""
    response = await client.post(
        '/api/auth/login',
        data={
            'username': 'tester_junior',
            'password': 'password123'
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


async def test_login_user_wrong_password(client: AsyncClient):
    """Тест ошибки авторизации при неверном пароле"""
    response = await client.post(
        '/api/auth/login',
        data={
            'username': 'tester_junior',
            'password': 'wrong_password_here'
        }
    )

    assert response.status_code == 401
    assert response.json()['detail'] == 'Неверный логин или пароль'
