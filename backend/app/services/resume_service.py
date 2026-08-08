import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.resume import GeneratedResume
from app.models.job import Job
from app.models.profile import Profile, MasterResume
from app.ai.factory import get_ai_provider
from app.resume_generator.validator import ResumeValidator
from app.resume_generator.pdf_formatter import generate_pdf_resume
from app.resume_generator.docx_formatter import generate_docx_resume
from app.core.config import settings

class ResumeService:
    
    @staticmethod
    async def generate_job_resume(db: AsyncSession, user_id: int, job_id: int) -> GeneratedResume:
        # Check existing resume
        res = await db.execute(
            select(GeneratedResume).filter(GeneratedResume.user_id == user_id, GeneratedResume.job_id == job_id)
        )
        existing = res.scalars().first()
        if existing:
            return existing

        j_res = await db.execute(select(Job).filter(Job.id == job_id))
        job = j_res.scalars().first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        p_res = await db.execute(select(Profile).filter(Profile.user_id == user_id))
        profile = p_res.scalars().first()
        if not profile:
            from app.models.user import User
            u_res = await db.execute(select(User).filter(User.id == user_id))
            user = u_res.scalars().first()
            full_name = user.full_name if user else "Applicant"
            name_parts = full_name.split(" ")
            profile = Profile(
                user_id=user_id,
                first_name=name_parts[0] if len(name_parts) > 0 else "Applicant",
                last_name=" ".join(name_parts[1:]) if len(name_parts) > 1 else "",
                email=user.email if user else ""
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        # Master resume text if available
        mr_res = await db.execute(select(MasterResume).filter(MasterResume.profile_id == profile.id))
        master_resumes = mr_res.scalars().all()
        master_text = master_resumes[-1].parsed_content if master_resumes else ""

        # Profile dict for AI
        profile_dict = {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "email": profile.email,
            "phone": profile.phone,
            "current_city": profile.current_city,
            "country": profile.country,
            "linkedin_url": profile.linkedin_url,
            "github_url": profile.github_url,
            "portfolio_url": profile.portfolio_url,
            "summary": profile.summary,
            "skills": [{"name": s.name, "category": s.category} for s in profile.skills],
            "experiences": [
                {
                    "company": exp.company,
                    "job_title": exp.job_title,
                    "location": exp.location,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "is_current": exp.is_current,
                    "technologies": exp.technologies
                } for exp in profile.experiences
            ],
            "projects": [
                {
                    "name": pr.name,
                    "description": pr.description,
                    "technologies": pr.technologies
                } for pr in profile.projects
            ],
            "education": [
                {
                    "degree": ed.degree,
                    "specialization": ed.specialization,
                    "university": ed.university,
                    "start_date": ed.start_date,
                    "end_date": ed.end_date
                } for ed in profile.education
            ]
        }

        job_dict = {
            "title": job.title,
            "company": job.company,
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or []
        }

        ai_provider = get_ai_provider()
        resume_content = await ai_provider.generate_tailored_resume(profile_dict, master_text, job_dict)

        # Anti-Hallucination Validation
        is_valid, validation_notes = ResumeValidator.validate_resume_against_profile(resume_content, profile_dict)

        # File paths
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_company = "".join([c for c in job.company if c.isalnum()])
        safe_title = "".join([c for c in job.title if c.isalnum()])
        base_filename = f"{safe_title}_{safe_company}_{user_id}_{date_str}"
        
        pdf_path = os.path.join(settings.STORAGE_DIR, "resumes", f"{base_filename}.pdf")
        docx_path = os.path.join(settings.STORAGE_DIR, "resumes", f"{base_filename}.docx")

        generate_pdf_resume(resume_content, pdf_path)
        generate_docx_resume(resume_content, docx_path)

        gen_resume = GeneratedResume(
            user_id=user_id,
            job_id=job_id,
            file_name=f"{base_filename}.pdf",
            pdf_path=pdf_path,
            docx_path=docx_path,
            validation_passed=is_valid,
            validation_notes=validation_notes,
            content_json=resume_content
        )

        db.add(gen_resume)
        await db.commit()
        await db.refresh(gen_resume)
        return gen_resume
