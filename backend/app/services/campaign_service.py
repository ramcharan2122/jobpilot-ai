from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.campaign import Campaign
from app.models.job import Job
from app.models.profile import Profile
from app.models.settings import UserSettings
from app.schemas.schemas import CampaignCreate
from app.services.matching_service import MatchingService
from app.services.application_service import ApplicationService

class CampaignService:
    
    @staticmethod
    async def create_campaign(db: AsyncSession, user_id: int, camp_in: CampaignCreate) -> Campaign:
        campaign = Campaign(
            user_id=user_id,
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

        # Trigger initial batch processing
        await CampaignService.run_campaign_batch(db, campaign.id)
        return campaign

    @staticmethod
    async def run_campaign_batch(db: AsyncSession, campaign_id: int) -> Campaign:
        res = await db.execute(select(Campaign).filter(Campaign.id == campaign_id))
        campaign = res.scalars().first()
        if not campaign:
            return None

        # Fetch jobs
        j_res = await db.execute(select(Job))
        jobs = j_res.scalars().all()
        
        p_res = await db.execute(select(Profile).filter(Profile.user_id == campaign.user_id))
        profile = p_res.scalars().first()

        s_res = await db.execute(select(UserSettings).filter(UserSettings.user_id == campaign.user_id))
        settings = s_res.scalars().first()

        total_disc = len(jobs)
        total_elig = 0
        applied_count = 0
        action_req = 0
        failed_count = 0

        for job in jobs:
            if applied_count >= campaign.daily_limit:
                break
                
            match_rec = await MatchingService.evaluate_job_match(db, campaign.user_id, job, profile, settings)
            
            # Filter checks
            if match_rec.eligibility_status != "ELIGIBLE":
                continue
            if match_rec.match_score < campaign.min_match_score:
                continue

            total_elig += 1
            
            # Apply
            mode = "AUTO" if campaign.auto_apply else "APPROVAL"
            app = await ApplicationService.create_application(db, campaign.user_id, job.id, mode=mode, campaign_id=campaign.id)
            
            if app.status == "SUBMITTED":
                applied_count += 1
            elif app.status == "ACTION_REQUIRED":
                action_req += 1
            elif app.status == "FAILED":
                failed_count += 1
            elif app.status in ["READY", "RESUME_READY", "APPROVAL"]:
                applied_count += 1 # Queued / Prepared

        campaign.total_discovered = total_disc
        campaign.total_eligible = total_elig
        campaign.total_applied = applied_count
        campaign.total_action_required = action_req
        campaign.total_failed = failed_count
        campaign.status = "COMPLETED"

        await db.commit()
        await db.refresh(campaign)
        return campaign
