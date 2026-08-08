from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.schemas.schemas import UserCreate, UserLogin, Token, UserOut
from app.services.auth_service import AuthService
from app.models.user import User
from app.api.v1.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

class SendOTPRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str

class GoogleOAuthRequest(BaseModel):
    email: EmailStr
    full_name: str
    credential_token: str

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await AuthService.register_user(db, user_in)

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    return await AuthService.authenticate_user(db, user_in)

@router.post("/send-otp")
async def send_otp(req: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.send_email_otp(db, req.email)

@router.post("/verify-otp", response_model=Token)
async def verify_otp(req: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.verify_email_otp(db, req.email, req.otp_code)

@router.post("/google", response_model=Token)
async def google_auth(req: GoogleOAuthRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.google_oauth_auth(db, req.email, req.full_name)

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
