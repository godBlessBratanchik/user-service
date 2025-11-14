import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models import Profile

def test_profile_creation():
    """Тест создания профиля с валидными данными"""
    profile = Profile(
        user_id="user_123",
        full_name="John Doe",
        email="john@example.com",
        avatar_url="https://example.com/avatar.jpg",
        bio="Test bio"
    )
    
    assert profile.user_id == "user_123"
    assert profile.full_name == "John Doe"
    assert profile.email == "john@example.com"
    assert profile.avatar_url == "https://example.com/avatar.jpg"
    assert profile.bio == "Test bio"

def test_profile_user_id_required():
    """Тест что user_id обязателен"""
    with pytest.raises(Exception):  # SQLAlchemy / Pydantic ошибка
        Profile(
            full_name="John Doe",
            email="john@example.com"
        )

def test_profile_full_name_required():
    """Тест что full_name обязателен"""
    with pytest.raises(Exception):
        Profile(
            user_id="user_123",
            email="john@example.com"
        )

def test_profile_email_required():
    """Тест что email обязателен"""
    with pytest.raises(Exception):
        Profile(
            user_id="user_123",
            full_name="John Doe"
        )

def test_profile_optional_fields():
    """Тест что avatar_url и bio опциональны"""
    profile = Profile(
        user_id="user_123",
        full_name="John Doe",
        email="john@example.com"
    )
    
    assert profile.avatar_url is None
    assert profile.bio is None
    assert profile.created_at is not None
    assert profile.updated_at is not None

def test_profile_timestamps():
    """Тест что timestamps устанавливаются"""
    before_creation = datetime.utcnow()
    profile = Profile(
        user_id="user_123",
        full_name="John Doe",
        email="john@example.com"
    )
    after_creation = datetime.utcnow()
    
    assert before_creation <= profile.created_at <= after_creation
    assert profile.updated_at == profile.created_at
