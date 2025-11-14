import pytest
from pydantic import ValidationError
from app.schemas import ProfileCreate, ProfileUpdate, ProfileRead

def test_profile_create_schema_valid(any_profile_data):
    """Тест валидного ProfileCreate"""
    schema = ProfileCreate(**any_profile_data)
    
    assert schema.user_id == any_profile_data["user_id"]
    assert schema.full_name == any_profile_data["full_name"]
    assert schema.email == any_profile_data["email"]

def test_profile_create_schema_user_id_required():
    """Тест что user_id обязателен в ProfileCreate"""
    with pytest.raises(ValidationError):
        ProfileCreate(
            full_name="John",
            email="john@example.com"
        )

def test_profile_create_schema_empty_user_id():
    """Тест что user_id не может быть пустым"""
    with pytest.raises(ValidationError):
        ProfileCreate(
            user_id="",
            full_name="John",
            email="john@example.com"
        )

def test_profile_update_schema_partial():
    """Тест что ProfileUpdate позволяет обновлять только часть полей"""
    schema = ProfileUpdate(full_name="Jane")
    
    assert schema.full_name == "Jane"
    assert schema.email is None
    assert schema.avatar_url is None

def test_profile_update_schema_empty():
    """Тест что ProfileUpdate может быть пустым"""
    schema = ProfileUpdate()
    
    assert schema.full_name is None
    assert schema.email is None

def test_profile_read_schema(any_profile_data):
    """Тест ProfileRead схемы"""
    data = {
        **any_profile_data,
        "created_at": "2025-11-14T12:00:00",
        "updated_at": "2025-11-14T12:00:00"
    }
    
    schema = ProfileRead(**data)
    assert schema.user_id == any_profile_data["user_id"]
    assert schema.full_name == any_profile_data["full_name"]
