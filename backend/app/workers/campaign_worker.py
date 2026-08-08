import asyncio
import random
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.campaign import Campaign
from app.models.job import Job
from app.models.profile import Profile
from app.models.settings import UserSettings
from app.services.matching_service import MatchingService
from app.services.application_service import ApplicationService

class HighVolumeCampaignWorker:
    """
    Asynchronous high-volume campaign runner capable of processing 200-300 job applications per day.
    Uses concurrency semaphores, anti-bot backoff jitter, and robust queue error handling.
    """

    def __init__(self, max_concurrency: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def run_high_volume_batch(self, db: AsyncSession, campaign_id: int, target_daily_limit: int = 300) -> dict:
        camp_res = await db.execute(
            db.select(Campaign).filter(Campaign.id == campaign_id)
        )
        campaign = camp_res.scalars().first()
        if not campaign:
            return {"status": "ERROR", "message": "Campaign not found"}

        campaign.daily_limit = min(target_daily_limit, 300)
        campaign.status = "RUNNING"
        await db.commit()

        # Fetch jobs
        j_res = await db.execute(db.select(Job))
        jobs = j_res.scalars().all()

        p_res = await db.execute(db.select(Profile).filter(Profile.user_id == campaign.user_id))
        profile = p_res.scalars().first()

        s_res = await db.execute(db.select(UserSettings).filter(UserSettings.user_id == campaign.user_id))
        settings = s_res.scalars().first()

        total_discovered = len(jobs)
        eligible_jobs = []

        # 1. Screen & Evaluate Matches
        for job in jobs:
            match_rec = await MatchingService.evaluate_job_match(db, campaign.user_id, job, profile, settings)
            if match_rec.eligibility_status == "ELIGIBLE" and match_rec.match_score >= campaign.min_match_score:
                eligible_jobs.append(job)

        # Truncate to target daily limit (up to 300)
        eligible_jobs = eligible_jobs[:campaign.daily_limit]

        # 2. Process High-Volume Queue concurrently with Semaphores & Jitter Delays
        async def process_single_job(job: Job):
            async with self.semaphore:
                # Anti-bot delay jitter (1.5s to 4.0s)
                await asyncio.sleep(random.uniform(1.5, 4.0))
                mode = "AUTO" if campaign.auto_apply else "APPROVAL"
                app = await ApplicationService.create_application(db, campaign.user_id, job.id, mode=mode, campaign_id=campaign.id)
                return app.status

        results = await asyncio.gather(*[process_single_job(job) for job in eligible_jobs], return_exceptions=True)

        submitted_cnt = len([r for r in results if r == "SUBMITTED" or r == "APPROVAL" or r == "READY"])
        action_req_cnt = len([r for r in results if r == "ACTION_REQUIRED"])
        failed_cnt = len([r for r in results if r == "FAILED"])

        campaign.total_discovered = total_discovered
        campaign.total_eligible = len(eligible_jobs)
        campaign.total_applied = submitted_cnt
        campaign.total_action_required = action_req_cnt
        campaign.total_failed = failed_cnt
        campaign.status = "COMPLETED"

        await db.commit()

        return {
            "status": "COMPLETED",
            "campaign_id": campaign.id,
            "total_discovered": total_discovered,
            "total_eligible": len(eligible_jobs),
            "total_applied": submitted_cnt,
            "action_required": action_req_cnt,
            "failed": failed_cnt
        }
