import pytest
from app.repository import ProfileRepo
from app.schemas import ProfileCreate, ProfileUpdate

@pytest.mark.asyncio
async def test_get_nonexistent_profile(test_session, any_profile_data):
    """Тест получения несуществующего профиля"""
    repo = ProfileRepo(test_session)
    
    profile = await repo.get("nonexistent_user")
    assert profile is None

@pytest.mark.asyncio
async def test_create_profile(test_session, any_profile_data):
    """Тест создания профиля"""
    repo = ProfileRepo(test_session)
    
    create_data = ProfileCreate(**any_profile_data)
    profile = await repo.upsert(create_data, any_profile_data["user_id"])
    
    assert profile.user_id == any_profile_data["user_id"]
    assert profile.full_name == any_profile_data["full_name"]
    assert profile.email == any_profile_data["email"]

@pytest.mark.asyncio
async def test_get_created_profile(test_session, any_profile_data):
    """Тест получения созданного профиля"""
    repo = ProfileRepo(test_session)
    
    create_data = ProfileCreate(**any_profile_data)
    await repo.upsert(create_data, any_profile_data["user_id"])
    
    profile = await repo.get(any_profile_data["user_id"])
    assert profile is not None
    assert profile.user_id == any_profile_data["user_id"]
    assert profile.full_name == any_profile_data["full_name"]

@pytest.mark.asyncio
async def test_update_profile(test_session, any_profile_data):
    """Тест обновления профиля"""
    repo = ProfileRepo(test_session)
    
    # Создание
    create_data = ProfileCreate(**any_profile_data)
    await repo.upsert(create_data, any_profile_data["user_id"])
    
    # Обновление
    update_data = ProfileUpdate(full_name="Updated Name", email="newemail@example.com")
    updated_profile = await repo.upsert(update_data, any_profile_data["user_id"])
    
    assert updated_profile.full_name == "Updated Name"
    assert updated_profile.email == "newemail@example.com"
    assert updated_profile.avatar_url == any_profile_data["avatar_url"]  # Не изменилось

@pytest.mark.asyncio
async def test_multiple_profiles(test_session, any_profile_data, another_profile_data):
    """Тест работы с несколькими профилями"""
    repo = ProfileRepo(test_session)
    
    # Создание первого
    create_data1 = ProfileCreate(**any_profile_data)
    await repo.upsert(create_data1, any_profile_data["user_id"])
    
    # Создание второго
    create_data2 = ProfileCreate(**another_profile_data)
    await repo.upsert(create_data2, another_profile_data["user_id"])
    
    # Получение обоих
    profile1 = await repo.get(any_profile_data["user_id"])
    profile2 = await repo.get(another_profile_data["user_id"])
    
    assert profile1.full_name == any_profile_data["full_name"]
    assert profile2.full_name == another_profile_data["full_name"]
    assert profile1.user_id != profile2.user_id
