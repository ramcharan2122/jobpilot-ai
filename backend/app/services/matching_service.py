from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.job import Job, JobMatch
from app.models.profile import Profile
from app.models.settings import UserSettings
from app.ai.factory import get_ai_provider

class MatchingService:
    
    @staticmethod
    async def evaluate_job_match(db: AsyncSession, user_id: int, job: Job, profile: Profile, settings: UserSettings) -> JobMatch:
        result = await db.execute(
            select(JobMatch).filter(JobMatch.job_id == job.id, JobMatch.user_id == user_id)
        )
        existing_match = result.scalars().first()
        if existing_match:
            return existing_match

        # Ensure profile relationships are loaded
        p_res = await db.execute(
            select(Profile)
            .options(
                selectinload(Profile.skills),
                selectinload(Profile.experiences),
                selectinload(Profile.projects),
                selectinload(Profile.education)
            )
            .filter(Profile.user_id == user_id)
        )
        loaded_profile = p_res.scalars().first() or profile

        eligibility = "ELIGIBLE"
        salary_max = job.salary_max_lpa or 0.0
        
        if job.salary_confidence == "UNDISCLOSED":
            if not settings.apply_undisclosed_salary:
                eligibility = "SALARY_MISMATCH"
        else:
            if salary_max > 0 and salary_max < settings.min_lpa:
                eligibility = "SALARY_MISMATCH"

        profile_dict = {
            "first_name": loaded_profile.first_name,
            "last_name": loaded_profile.last_name,
            "email": loaded_profile.email,
            "skills": [{"name": s.name, "category": s.category} for s in (loaded_profile.skills or [])],
            "experiences": [
                {
                    "company": exp.company,
                    "job_title": exp.job_title,
                    "technologies": exp.technologies
                } for exp in (loaded_profile.experiences or [])
            ],
            "projects": [
                {
                    "name": pr.name,
                    "technologies": pr.technologies
                } for pr in (loaded_profile.projects or [])
            ],
            "education": [{"degree": ed.degree, "university": ed.university} for ed in (loaded_profile.education or [])]
        }

        job_dict = {
            "title": job.title,
            "company": job.company,
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or [],
            "experience_min": job.experience_min,
            "experience_max": job.experience_max,
            "salary_min_lpa": job.salary_min_lpa,
            "salary_max_lpa": job.salary_max_lpa,
            "location": job.location,
            "is_remote": job.is_remote
        }

        ai_provider = get_ai_provider()
        match_res = await ai_provider.match_candidate(profile_dict, job_dict)

        match_score = match_res.get("match_score", 75)
        if eligibility == "ELIGIBLE" and match_score < settings.min_match_score:
            eligibility = "LOW_MATCH"

        job_match = JobMatch(
            job_id=job.id,
            user_id=user_id,
            match_score=match_score,
            eligibility_status=eligibility,
            strong_matches=match_res.get("strong_matches", []),
            partial_matches=match_res.get("partial_matches", []),
            missing_skills=match_res.get("missing_skills", []),
            score_breakdown=match_res.get("score_breakdown", {})
        )

        db.add(job_match)
        await db.commit()
        await db.refresh(job_match)
        return job_match
