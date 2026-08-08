from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.schemas import JobOut
from app.services.job_service import JobService
from app.models.user import User
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=List[JobOut])
async def list_jobs(
    role: Optional[str] = Query(None),
    min_lpa: Optional[float] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await JobService.list_jobs(db, current_user.id, role_filter=role, min_lpa=min_lpa)

@router.post("/seed-demo")
async def seed_demo_jobs(db: AsyncSession = Depends(get_db)):
    count = await JobService.seed_demo_jobs(db)
    return {"message": "Demo jobs seeded", "count": count}
