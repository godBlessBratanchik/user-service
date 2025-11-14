from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_session
from .repository import ProfileRepo
from .schemas import ProfileCreate, ProfileUpdate, ProfileRead, ProfileEvent
from .kafka import get_kafka_producer, KafkaProducerManager, TOPIC_PROFILE_EVENTS

router = APIRouter(prefix="/profiles", tags=["profiles"])

async def get_user_id(
    x_user_id: Optional[str] = Header(default=None),
    user_id_q: Optional[str] = Query(None, alias="user_id")
) -> str:
    uid = x_user_id or user_id_q
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_id required (X-User-Id header or user_id query param)"
        )
    return uid

@router.get("/{user_id}", response_model=ProfileRead)
async def get_profile(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    repo = ProfileRepo(session)
    profile = await repo.get(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile {user_id} not found"
        )
    return profile

@router.post("", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    data: ProfileCreate,
    session: AsyncSession = Depends(get_session),
    kafka: KafkaProducerManager = Depends(get_kafka_producer)
):
    repo = ProfileRepo(session)
    profile = await repo.upsert(data, data.user_id)
    event = ProfileEvent(
        event_type="ProfileCreated",
        user_id=profile.user_id,
        full_name=profile.full_name,
        email=profile.email
    )
    await kafka.send_event(TOPIC_PROFILE_EVENTS, event.model_dump(mode='json'))
    return profile

@router.patch("", response_model=ProfileRead)
async def update_profile(
    data: ProfileUpdate,
    user_id: str = Depends(get_user_id),
    session: AsyncSession = Depends(get_session),
    kafka: KafkaProducerManager = Depends(get_kafka_producer)
):
    repo = ProfileRepo(session)
    profile = await repo.upsert(data, user_id)
    event = ProfileEvent(
        event_type="ProfileUpdated",
        user_id=profile.user_id,
        full_name=profile.full_name,
        email=profile.email
    )
    await kafka.send_event(TOPIC_PROFILE_EVENTS, event.model_dump(mode='json'))
    return profile
