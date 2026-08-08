from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.schemas import ProfileOut, ProfileCreateOrUpdate
from app.services.profile_service import ProfileService
from app.models.user import User
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=ProfileOut)
async def get_user_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await ProfileService.get_profile(db, current_user.id)

@router.put("", response_model=ProfileOut)
async def update_user_profile(profile_in: ProfileCreateOrUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await ProfileService.update_profile(db, current_user.id, profile_in)

@router.post("/upload-resume")
async def upload_master_resume(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await ProfileService.upload_master_resume(db, current_user.id, file)
