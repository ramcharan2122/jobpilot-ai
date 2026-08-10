import os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
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

        # Ensure 100% target job skills coverage in the resume skills matrix
        if "skills" in resume_content and isinstance(resume_content["skills"], dict):
            existing_skills_flat = set()
            for s_list in resume_content["skills"].values():
                if isinstance(s_list, list):
                    for s in s_list:
                        existing_skills_flat.add(str(s).lower())
            
            target_skills = (job.required_skills or []) + (job.preferred_skills or [])
            for sk in target_skills:
                if sk and sk.lower() not in existing_skills_flat:
                    cat_key = "Frameworks & Core Tools"
                    if cat_key not in resume_content["skills"]:
                        resume_content["skills"][cat_key] = []
                    resume_content["skills"][cat_key].append(sk)
                    existing_skills_flat.add(sk.lower())

        # Anti-Hallucination Validation
        is_valid, validation_notes = ResumeValidator.validate_resume_against_profile(resume_content, profile_dict)

        # Clean candidate full name for filename (e.g. "Shashi Kiran" -> "shashikiran")
        raw_name = f"{profile.first_name or ''} {profile.last_name or ''}".strip()
        clean_user = "".join([c for c in raw_name.lower() if c.isalnum()])
        if not clean_user:
            clean_user = "shashikiran"
            
        base_filename = f"{clean_user}.resume"
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
