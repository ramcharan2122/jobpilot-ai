from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db, AsyncSessionLocal
from app.schemas.schemas import CampaignCreate, CampaignOut
from app.services.campaign_service import CampaignService
from app.models.campaign import Campaign
from app.models.user import User
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

async def run_bg_campaign_batch(campaign_id: int):
    try:
        async with AsyncSessionLocal() as db:
            await CampaignService.run_campaign_batch(db, campaign_id)
    except Exception as e:
        print(f"⚠️ Campaign background execution error: {e}")

@router.post("", response_model=CampaignOut)
async def create_campaign(camp_in: CampaignCreate, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    campaign = Campaign(
        user_id=current_user.id,
        name=camp_in.name,
        min_lpa=camp_in.min_lpa,
        max_lpa=camp_in.max_lpa,
        target_roles=camp_in.target_roles,
        locations=camp_in.locations,
        min_match_score=camp_in.min_match_score,
        daily_limit=camp_in.daily_limit,
        auto_apply=camp_in.auto_apply,
        status="RUNNING"
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    background_tasks.add_task(run_bg_campaign_batch, campaign.id)
    return campaign

@router.get("", response_model=List[CampaignOut])
async def list_campaigns(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Campaign).filter(Campaign.user_id == current_user.id).order_by(Campaign.created_at.desc()))
    return res.scalars().all()
