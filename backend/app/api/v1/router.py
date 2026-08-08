from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.profile import router as profile_router
from app.api.v1.settings import router as settings_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.applications import router as applications_router
from app.api.v1.campaigns import router as campaigns_router
from app.api.v1.mock_portal import router as mock_portal_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(settings_router)
api_router.include_router(jobs_router)
api_router.include_router(resumes_router)
api_router.include_router(applications_router)
api_router.include_router(campaigns_router)
api_router.include_router(mock_portal_router)
