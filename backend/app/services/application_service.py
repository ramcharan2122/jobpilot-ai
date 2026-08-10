from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.application import Application, ApplicationEvent
from app.models.job import Job
from app.models.profile import Profile
from app.models.settings import UserSettings
from app.models.resume import GeneratedResume
from app.services.resume_service import ResumeService
from app.ai.factory import get_ai_provider
from app.applications.adapters.local_mock_adapter import LocalMockApplicationAdapter

class ApplicationService:
    
    @staticmethod
    async def create_application(db: AsyncSession, user_id: int, job_id: int, mode: Optional[str] = None, campaign_id: Optional[int] = None) -> Application:
        res = await db.execute(
            select(Application).filter(Application.user_id == user_id, Application.job_id == job_id)
        )
        existing = res.scalars().first()
        if existing:
            return existing

        s_res = await db.execute(select(UserSettings).filter(UserSettings.user_id == user_id))
        settings = s_res.scalars().first()
        app_mode = mode or (settings.application_mode if settings else "APPROVAL")

        app = Application(
            user_id=user_id,
            job_id=job_id,
            campaign_id=campaign_id,
            status="READY",
            application_mode=app_mode
        )
        db.add(app)
        await db.commit()
        await db.refresh(app)

        # Log event
        evt = ApplicationEvent(
            application_id=app.id,
            event_type="STATUS_CHANGE",
            message=f"Application created in mode {app_mode}"
        )
        db.add(evt)
        await db.commit()

        # Trigger application workflow execution
        await ApplicationService.process_application(db, app.id)
        return app

    @staticmethod
    async def process_application(db: AsyncSession, application_id: int) -> Application:
        res = await db.execute(
            select(Application)
            .options(
                selectinload(Application.job),
                selectinload(Application.events)
            )
            .filter(Application.id == application_id)
        )
        app = res.scalars().first()
        if not app:
            raise HTTPException(status_code=404, detail="Application not found.")

        try:
            # 1. State transition: GENERATING_RESUME
            app.status = "GENERATING_RESUME"
            db.add(ApplicationEvent(application_id=app.id, event_type="LOG", message="Generating tailored job-specific resume..."))
            await db.commit()

            # 2. Generate Custom Resume
            gen_resume = await ResumeService.generate_job_resume(db, app.user_id, app.job_id)
            app.resume_id = gen_resume.id
            app.status = "RESUME_READY"
            db.add(ApplicationEvent(application_id=app.id, event_type="LOG", message="Resume generated & verified. File ready."))
            await db.commit()

            # 3. Generate Custom Application Question Answers & Cover Letter
            p_res = await db.execute(
                select(Profile)
                .options(
                    selectinload(Profile.skills),
                    selectinload(Profile.experiences),
                    selectinload(Profile.projects),
                    selectinload(Profile.education)
                )
                .filter(Profile.user_id == app.user_id)
            )
            profile = p_res.scalars().first()
            profile_dict = {
                "first_name": profile.first_name if profile else "Applicant",
                "last_name": profile.last_name if profile else "",
                "email": profile.email if profile else "",
                "phone": profile.phone if profile else "",
                "skills": [s.name for s in (profile.skills if profile else [])],
                "experiences": [{"company": e.company, "job_title": e.job_title} for e in (profile.experiences if profile else [])]
            }
            job_dict = {
                "title": app.job.title if app.job else "Software Engineer",
                "company": app.job.company if app.job else "Tech Company"
            }

            ai_provider = get_ai_provider()
            sample_questions = [
                f"Why do you want to work as a {job_dict['title']} at {job_dict['company']}?",
                "What is your expected salary and notice period?"
            ]
            answers = await ai_provider.generate_answers(profile_dict, job_dict, sample_questions)
            cover_letter = await ai_provider.generate_cover_letter(profile_dict, job_dict)

            app.answers_json = answers
            app.cover_letter = cover_letter
            await db.commit()

            # If Mode is APPROVAL, stop here and await user approval before submitting!
            if app.application_mode == "APPROVAL":
                db.add(ApplicationEvent(application_id=app.id, event_type="LOG", message="Application ready for user review/approval."))
                await db.commit()
                return app

            # 4. If Mode is AUTO or user triggered Submit: Proceed to APPLYING via Playwright
            app.status = "APPLYING"
            db.add(ApplicationEvent(application_id=app.id, event_type="LOG", message="Launching browser automation engine..."))
            await db.commit()

            app_url = app.job.application_url if app.job else ""
            if app_url and "mock-portal" not in app_url:
                from app.applications.adapters.real_ats_adapters import ProductionApplicationAdapter
                prod_adapter = ProductionApplicationAdapter()
                auto_res = await prod_adapter.apply_to_real_job(
                    application_id=app.id,
                    application_url=app_url,
                    user_profile=profile_dict,
                    resume_path=gen_resume.pdf_path,
                    answers=answers
                )
            else:
                adapter = LocalMockApplicationAdapter()
                auto_res = await adapter.apply_to_job(
                    application_id=app.id,
                    application_url=app_url,
                    user_profile=profile_dict,
                    resume_path=gen_resume.pdf_path,
                    answers=answers
                )

            app.status = auto_res.get("status", "SUBMITTED")
            app.error_type = auto_res.get("error_type")
            app.error_message = auto_res.get("error_message")
            app.screenshot_path = auto_res.get("screenshot_path")
            if app.status == "SUBMITTED":
                app.submitted_at = datetime.utcnow()

            db.add(ApplicationEvent(application_id=app.id, event_type="STATUS_CHANGE", message=f"Application status changed to {app.status}"))
            await db.commit()
            return app

        except Exception as e:
            print(f"⚠️ Application processing error: {e}")
            app.status = "ACTION_REQUIRED"
            app.error_message = str(e)
            db.add(ApplicationEvent(application_id=app.id, event_type="ERROR", message=f"Processing failed: {str(e)}"))
            await db.commit()
            return app
