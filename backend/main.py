import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.database.session import engine, Base, AsyncSessionLocal
from app.api.v1.router import api_router
from app.services.job_service import JobService

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file storage for PDF/DOCX downloads and screenshots
os.makedirs(os.path.join(settings.STORAGE_DIR, "resumes"), exist_ok=True)
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        await JobService.seed_demo_jobs(session)
        
        # Pre-seed demo candidate account
        from app.schemas.schemas import UserCreate
        from app.services.auth_service import AuthService
        try:
            demo_user = UserCreate(
                email="candidate@example.com",
                password="password123",
                full_name="Shashi Kiran"
            )
            await AuthService.register_user(session, demo_user)
        except Exception:
            pass # User already exists

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mode": "DEMO MODE" if settings.DEMO_MODE else "PRODUCTION MODE",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
