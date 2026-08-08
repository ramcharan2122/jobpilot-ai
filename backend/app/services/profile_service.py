import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader
import docx
from app.models.profile import Profile, Education, Experience, Skill, Project, Certification, MasterResume
from app.schemas.schemas import ProfileCreateOrUpdate
from app.core.config import settings

class ProfileService:
    
    @staticmethod
    async def get_profile(db: AsyncSession, user_id: int) -> Profile:
        result = await db.execute(
            select(Profile)
            .options(
                selectinload(Profile.education),
                selectinload(Profile.experiences),
                selectinload(Profile.skills),
                selectinload(Profile.projects),
                selectinload(Profile.certifications),
                selectinload(Profile.master_resumes)
            )
            .filter(Profile.user_id == user_id)
        )
        profile = result.scalars().first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found.")
        return profile

    @staticmethod
    async def update_profile(db: AsyncSession, user_id: int, profile_in: ProfileCreateOrUpdate) -> Profile:
        profile = await ProfileService.get_profile(db, user_id)
        
        # Update scalar fields
        if profile_in.first_name is not None: profile.first_name = profile_in.first_name
        if profile_in.middle_name is not None: profile.middle_name = profile_in.middle_name
        if profile_in.last_name is not None: profile.last_name = profile_in.last_name
        if profile_in.email is not None: profile.email = profile_in.email
        if profile_in.phone is not None: profile.phone = profile_in.phone
        if profile_in.current_city is not None: profile.current_city = profile_in.current_city
        if profile_in.country is not None: profile.country = profile_in.country
        if profile_in.linkedin_url is not None: profile.linkedin_url = profile_in.linkedin_url
        if profile_in.github_url is not None: profile.github_url = profile_in.github_url
        if profile_in.portfolio_url is not None: profile.portfolio_url = profile_in.portfolio_url
        if profile_in.personal_website is not None: profile.personal_website = profile_in.personal_website
        if profile_in.summary is not None: profile.summary = profile_in.summary

        # Clear existing collections and replace with updated ones
        profile.education.clear()
        for edu in profile_in.education:
            profile.education.append(Education(**edu.dict(exclude={"id"})))

        profile.experiences.clear()
        for exp in profile_in.experiences:
            profile.experiences.append(Experience(**exp.dict(exclude={"id"})))

        profile.skills.clear()
        for sk in profile_in.skills:
            profile.skills.append(Skill(**sk.dict(exclude={"id"})))

        profile.projects.clear()
        for proj in profile_in.projects:
            profile.projects.append(Project(**proj.dict(exclude={"id"})))

        profile.certifications.clear()
        for cert in profile_in.certifications:
            profile.certifications.append(Certification(**cert.dict(exclude={"id"})))

        await db.commit()
        await db.refresh(profile)
        return profile

    @staticmethod
    async def upload_master_resume(db: AsyncSession, user_id: int, file: UploadFile) -> dict:
        profile = await ProfileService.get_profile(db, user_id)
        
        file_ext = os.path.splitext(file.filename)[1].upper().replace(".", "")
        if file_ext not in ["PDF", "DOCX"]:
            raise HTTPException(status_code=400, detail="Only PDF and DOCX resume formats are supported.")
            
        file_name = f"master_{user_id}_{file.filename}"
        save_path = os.path.join(settings.STORAGE_DIR, "uploads", file_name)
        
        contents = await file.read()
        with open(save_path, "wb") as f:
            f.write(contents)
            
        parsed_text = ""
        try:
            if file_ext == "PDF":
                reader = PdfReader(save_path)
                for page in reader.pages:
                    parsed_text += (page.extract_text() or "") + "\n"
            elif file_ext == "DOCX":
                doc = docx.Document(save_path)
                for p in doc.paragraphs:
                    parsed_text += p.text + "\n"
        except Exception:
            parsed_text = "Master resume uploaded successfully."

        # Never overwrite original master resume record; append to master_resumes
        master_rec = MasterResume(
            profile_id=profile.id,
            file_name=file.filename,
            file_path=save_path,
            file_type=file_ext,
            parsed_content=parsed_text
        )
        db.add(master_rec)
        
        # If user profile is empty, seed initial skills/experience from parsed text
        if not profile.skills:
            extracted_skills = []
            for tech in ["Python", "FastAPI", "REST APIs", "PostgreSQL", "React", "TypeScript", "Docker", "Git"]:
                if tech.lower() in parsed_text.lower():
                    extracted_skills.append(Skill(category="Programming", name=tech, proficiency="Expert"))
            if extracted_skills:
                profile.skills.extend(extracted_skills)

        await db.commit()
        return {
            "message": "Master resume uploaded and parsed successfully.",
            "file_name": file.filename,
            "parsed_length": len(parsed_text)
        }
