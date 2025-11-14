from typing import Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Profile
from .schemas import ProfileCreate, ProfileUpdate

class ProfileRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: str) -> Optional[Profile]:
        result = await self.session.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, data: Union[ProfileCreate, ProfileUpdate], user_id: str) -> Profile:
        obj = await self.get(user_id)
    
        if obj is None:
        # Новый профиль
            create_data = data.model_dump(exclude={"user_id"})
            create_data["user_id"] = user_id
            obj = Profile(**create_data)
            self.session.add(obj)
        else:
        # Обновление существующего
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key != "user_id":
                    setattr(obj, key, value)

        await self.session.commit()
        await self.session.refresh(obj)
        return obj
