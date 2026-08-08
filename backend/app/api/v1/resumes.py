import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.schemas.schemas import GeneratedResumeOut
from app.services.resume_service import ResumeService
from app.models.resume import GeneratedResume
from app.models.user import User
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/generate/{job_id}")
async def generate_resume_for_job(job_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rec = await ResumeService.generate_job_resume(db, current_user.id, job_id)
    return {
        "id": rec.id,
        "job_id": rec.job_id,
        "file_name": rec.file_name,
        "validation_passed": rec.validation_passed,
        "validation_notes": rec.validation_notes,
        "content_json": rec.content_json,
        "pdf_url": f"/api/v1/resumes/download/{rec.id}?format=pdf",
        "docx_url": f"/api/v1/resumes/download/{rec.id}?format=docx"
    }

@router.get("", response_model=List[dict])
async def list_user_resumes(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(GeneratedResume).filter(GeneratedResume.user_id == current_user.id))
    resumes = res.scalars().all()
    out = []
    for r in resumes:
        out.append({
            "id": r.id,
            "job_id": r.job_id,
            "file_name": r.file_name,
            "validation_passed": r.validation_passed,
            "validation_notes": r.validation_notes,
            "content_json": r.content_json,
            "generated_at": r.generated_at,
            "pdf_url": f"/api/v1/resumes/download/{r.id}?format=pdf",
            "docx_url": f"/api/v1/resumes/download/{r.id}?format=docx"
        })
    return out

@router.get("/download/{resume_id}")
async def download_resume(resume_id: int, format: str = "pdf", db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(GeneratedResume).filter(GeneratedResume.id == resume_id))
    rec = res.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Resume file not found.")

    file_path = rec.pdf_path if format.lower() == "pdf" else rec.docx_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File path does not exist on disk.")

    media_type = "application/pdf" if format.lower() == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(file_path, media_type=media_type, filename=os.path.basename(file_path))
