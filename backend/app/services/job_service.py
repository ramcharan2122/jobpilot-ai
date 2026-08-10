from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.job import Job
from app.models.profile import Profile
from app.models.settings import UserSettings
from app.job_sources.seed_demo_source import SeedDemoJobSource
from app.job_sources.real_sources import (
    GreenhouseJobSource,
    LeverJobSource,
    SmartRecruitersJobSource,
    AshbyJobSource,
    LinkedInJobSource,
    NaukriJobSource,
    IndeedJobSource,
    InstahyreJobSource,
    WellfoundJobSource,
    FounditJobSource,
    UnstopJobSource,
    GlassdoorJobSource
)
from app.services.matching_service import MatchingService

class JobService:
    
    @staticmethod
    async def seed_demo_jobs(db: AsyncSession) -> int:
        sources = [
            SeedDemoJobSource(),
            GreenhouseJobSource(),
            LeverJobSource(),
            SmartRecruitersJobSource(),
            AshbyJobSource(),
            LinkedInJobSource(),
            NaukriJobSource(),
            IndeedJobSource(),
            InstahyreJobSource(),
            WellfoundJobSource(),
            FounditJobSource(),
            UnstopJobSource(),
            GlassdoorJobSource()
        ]
        inserted_count = 0
        
        for source in sources:
            try:
                raw_jobs = await source.search_jobs([], [], 0, 100)
                for j_data in raw_jobs:
                    res = await db.execute(select(Job).filter(Job.duplicate_hash == j_data["duplicate_hash"]))
                    existing = res.scalars().first()
                    if not existing:
                        job = Job(**j_data)
                        db.add(job)
                        inserted_count += 1
            except Exception:
                continue

        await db.commit()
        return inserted_count

    @staticmethod
    async def list_jobs(db: AsyncSession, user_id: int, role_filter: Optional[str] = None, min_lpa: Optional[float] = None) -> List[dict]:
        res = await db.execute(select(Job))
        jobs = res.scalars().all()
        if not jobs or len(jobs) < 15:
            await JobService.seed_demo_jobs(db)
            res = await db.execute(select(Job))
            jobs = res.scalars().all()

        p_res = await db.execute(select(Profile).filter(Profile.user_id == user_id))
        profile = p_res.scalars().first()
        
        s_res = await db.execute(select(UserSettings).filter(UserSettings.user_id == user_id))
        settings = s_res.scalars().first()

        job_list = []
        for job in jobs:
            if role_filter and role_filter.lower() not in job.title.lower() and role_filter.lower() not in job.company.lower():
                continue
            if min_lpa is not None and job.salary_max_lpa and job.salary_max_lpa < min_lpa:
                continue

            match_info = None
            if profile and settings:
                match_rec = await MatchingService.evaluate_job_match(db, user_id, job, profile, settings)
                match_info = {
                    "match_score": match_rec.match_score,
                    "eligibility_status": match_rec.eligibility_status,
                    "strong_matches": match_rec.strong_matches,
                    "partial_matches": match_rec.partial_matches,
                    "missing_skills": match_rec.missing_skills
                }

            j_dict = {
                "id": job.id,
                "source": job.source,
                "company": job.company,
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
                "responsibilities": job.responsibilities,
                "required_skills": job.required_skills or [],
                "preferred_skills": job.preferred_skills or [],
                "salary_min_lpa": job.salary_min_lpa,
                "salary_max_lpa": job.salary_max_lpa,
                "salary_currency": job.salary_currency,
                "salary_confidence": job.salary_confidence,
                "location": job.location,
                "is_remote": job.is_remote,
                "employment_type": job.employment_type,
                "experience_min": job.experience_min,
                "experience_max": job.experience_max,
                "application_url": job.application_url,
                "posted_date": job.posted_date,
                "job_status": job.job_status,
                **(match_info or {})
            }
            job_list.append(j_dict)
            
        return job_list
