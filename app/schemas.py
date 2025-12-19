from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ProfileCreate(BaseModel):
    user_id: str = Field(..., min_length=1)
    full_name: str = Field(..., min_length=1, max_length=120)
    email: str = Field(..., min_length=1)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[str] = Field(None, min_length=1)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class ProfileRead(BaseModel):
    user_id: str
    full_name: str
    email: str
    avatar_url: Optional[str]
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProfileEvent(BaseModel):
    event_type: str
    user_id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)