from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.schemas.schemas import CampaignCreate, CampaignOut
from app.services.campaign_service import CampaignService
from app.models.campaign import Campaign
from app.models.user import User
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.post("", response_model=CampaignOut)
async def create_campaign(camp_in: CampaignCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await CampaignService.create_campaign(db, current_user.id, camp_in)

@router.get("", response_model=List[CampaignOut])
async def list_campaigns(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Campaign).filter(Campaign.user_id == current_user.id))
    return res.scalars().all()
