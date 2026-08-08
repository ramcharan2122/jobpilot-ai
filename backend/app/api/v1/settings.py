from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.schemas.schemas import UserSettingsOut, UserSettingsUpdate
from app.models.settings import UserSettings
from app.models.user import User
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=UserSettingsOut)
async def get_settings(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(UserSettings).filter(UserSettings.user_id == current_user.id))
    settings = res.scalars().first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings

@router.put("", response_model=UserSettingsOut)
async def update_settings(settings_in: UserSettingsUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(UserSettings).filter(UserSettings.user_id == current_user.id))
    settings = res.scalars().first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        
    for field, val in settings_in.dict(exclude_unset=True).items():
        setattr(settings, field, val)
        
    await db.commit()
    await db.refresh(settings)
    return settings
