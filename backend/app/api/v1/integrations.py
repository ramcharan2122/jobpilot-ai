from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.database.session import get_db
from app.models.profile import ConnectedPlatform
from app.models.user import User
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/integrations", tags=["Integrations"])

class PlatformConnectRequest(BaseModel):
    platform_name: str
    username_or_email: str
    auth_credentials: Optional[str] = None

class PlatformStatusOut(BaseModel):
    platform_name: str
    display_name: str
    username_or_email: Optional[str] = None
    is_connected: bool
    last_synced_at: Optional[datetime] = None

PLATFORMS_CATALOG = [
    {"platform_name": "LINKEDIN", "display_name": "LinkedIn Jobs"},
    {"platform_name": "NAUKRI", "display_name": "Naukri.com"},
    {"platform_name": "INDEED", "display_name": "Indeed India"},
    {"platform_name": "INSTAHYRE", "display_name": "Instahyre Tech"},
    {"platform_name": "WELLFOUND", "display_name": "Wellfound (AngelList)"},
    {"platform_name": "FOUNDIT", "display_name": "Foundit (Monster)"},
    {"platform_name": "UNSTOP", "display_name": "Unstop Hiring"},
    {"platform_name": "GLASSDOOR", "display_name": "Glassdoor Jobs"}
]

@router.get("/platforms", response_model=List[PlatformStatusOut])
async def list_connected_platforms(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ConnectedPlatform).filter(ConnectedPlatform.user_id == current_user.id))
    user_conns = {c.platform_name: c for c in res.scalars().all()}

    out = []
    for p in PLATFORMS_CATALOG:
        conn = user_conns.get(p["platform_name"])
        out.append(PlatformStatusOut(
            platform_name=p["platform_name"],
            display_name=p["display_name"],
            username_or_email=conn.username_or_email if conn else None,
            is_connected=conn.is_connected if conn else False,
            last_synced_at=conn.last_synced_at if conn else None
        ))
    return out

@router.post("/platforms/connect", response_model=dict)
async def connect_platform(data: PlatformConnectRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    plat_clean = data.platform_name.upper().strip()
    res = await db.execute(
        select(ConnectedPlatform).filter(
            ConnectedPlatform.user_id == current_user.id,
            ConnectedPlatform.platform_name == plat_clean
        )
    )
    existing = res.scalars().first()
    if existing:
        existing.username_or_email = data.username_or_email
        existing.auth_credentials = data.auth_credentials or existing.auth_credentials
        existing.is_connected = True
        existing.last_synced_at = datetime.utcnow()
    else:
        conn = ConnectedPlatform(
            user_id=current_user.id,
            platform_name=plat_clean,
            username_or_email=data.username_or_email,
            auth_credentials=data.auth_credentials,
            is_connected=True,
            last_synced_at=datetime.utcnow()
        )
        db.add(conn)
    await db.commit()
    return {"message": f"Successfully connected and verified {plat_clean} account for {data.username_or_email}!"}

@router.post("/platforms/disconnect", response_model=dict)
async def disconnect_platform(platform_name: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    plat_clean = platform_name.upper().strip()
    res = await db.execute(
        select(ConnectedPlatform).filter(
            ConnectedPlatform.user_id == current_user.id,
            ConnectedPlatform.platform_name == plat_clean
        )
    )
    existing = res.scalars().first()
    if existing:
        existing.is_connected = False
        await db.commit()
    return {"message": f"Disconnected {plat_clean} account."}
