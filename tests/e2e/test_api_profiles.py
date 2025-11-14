import pytest
import httpx
import asyncio
from datetime import datetime
import time

base_url = "http://localhost:8001"
timeout = httpx.Timeout(30.0)  # 30 секунд timeout

@pytest.fixture
async def http_client():
    """HTTP клиент для тестирования API"""
    # Пытаемся подключиться несколько раз, т.к. сервис может не сразу стартовать
    for attempt in range(5):
        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as client:
                await client.get("/health")
                break
        except (httpx.ConnectError, httpx.ReadTimeout):
            if attempt < 4:
                await asyncio.sleep(2)
            else:
                raise
    
    async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as client:
        yield client

@pytest.fixture
def profile_data():
    return {
        "user_id": "test_user_e2e",
        "full_name": "E2E Test User",
        "email": "e2e@example.com",
        "avatar_url": "https://example.com/avatar.jpg",
        "bio": "E2E test bio"
    }

@pytest.mark.asyncio
async def test_health_check(http_client):
    """Тест health check"""
    response = await http_client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data

@pytest.mark.asyncio
async def test_root_endpoint(http_client):
    """Тест root endpoint"""
    response = await http_client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "profile-service"

@pytest.mark.asyncio
async def test_create_profile(http_client, profile_data):
    """Тест создания профиля через API"""
    response = await http_client.post(
        "/profiles",
        json=profile_data
    )
    
    assert response.status_code == 201, f"Error: {response.text}"
    data = response.json()
    assert data["user_id"] == profile_data["user_id"]
    assert data["full_name"] == profile_data["full_name"]

@pytest.mark.asyncio
async def test_get_profile(http_client, profile_data):
    """Тест получения профиля через API"""
    # Сначала создаём
    create_resp = await http_client.post("/profiles", json=profile_data)
    assert create_resp.status_code == 201
    
    # Затем получаем
    response = await http_client.get(f"/profiles/{profile_data['user_id']}")
    
    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()
    assert data["user_id"] == profile_data["user_id"]

@pytest.mark.asyncio
async def test_get_nonexistent_profile(http_client):
    """Тест получения несуществующего профиля"""
    response = await http_client.get("/profiles/nonexistent_user_xyz")
    
    assert response.status_code == 404, f"Error: {response.text}"

@pytest.mark.asyncio
async def test_update_profile(http_client, profile_data):
    """Тест обновления профиля через API"""
    # Создание
    create_resp = await http_client.post("/profiles", json=profile_data)
    assert create_resp.status_code == 201
    
    # Обновление
    update_data = {
        "full_name": "Updated Name",
        "email": "updated@example.com"
    }
    response = await http_client.patch(
        f"/profiles?user_id={profile_data['user_id']}",
        json=update_data
    )
    
    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "updated@example.com"

@pytest.mark.asyncio
async def test_update_without_user_id(http_client):
    """Тест обновления без user_id"""
    update_data = {"full_name": "Test"}
    response = await http_client.patch(
        "/profiles",
        json=update_data
    )
    
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_with_minimal_data(http_client):
    """Тест создания профиля с минимальными данными"""
    minimal_data = {
        "user_id": "minimal_user",
        "full_name": "Minimal",
        "email": "minimal@example.com"
    }
    response = await http_client.post(
        "/profiles",
        json=minimal_data
    )
    
    assert response.status_code == 201, f"Error: {response.text}"
    data = response.json()
    assert data["user_id"] == "minimal_user"
    assert data["avatar_url"] is None

@pytest.mark.asyncio
async def test_create_without_required_field(http_client):
    """Тест создания без обязательного поля email"""
    invalid_data = {
        "user_id": "invalid_user",
        "full_name": "Invalid"
    }
    response = await http_client.post(
        "/profiles",
        json=invalid_data
    )
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_partial_fields(http_client, profile_data):
    """Тест обновления только некоторых полей"""
    # Создание
    create_resp = await http_client.post("/profiles", json=profile_data)
    assert create_resp.status_code == 201
    
    # Обновление только имени
    update_data = {"full_name": "Only Name Updated"}
    response = await http_client.patch(
        f"/profiles?user_id={profile_data['user_id']}",
        json=update_data
    )
    
    assert response.status_code == 200, f"Error: {response.text}"
    data = response.json()
    assert data["full_name"] == "Only Name Updated"
    assert data["email"] == profile_data["email"]
