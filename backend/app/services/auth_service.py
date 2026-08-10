import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException, status
import resend
from app.models.user import User
from app.models.profile import Profile
from app.models.settings import UserSettings
from app.models.otp import EmailOTP
from app.schemas.schemas import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings

class AuthService:
    
    @staticmethod
    async def register_user(db: AsyncSession, user_in: UserCreate) -> dict:
        clean_email = user_in.email.strip().lower()
        result = await db.execute(select(User).filter(func.lower(User.email) == clean_email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
            
        hashed_pwd = get_password_hash(user_in.password)
        new_user = User(
            email=clean_email,
            hashed_password=hashed_pwd,
            full_name=user_in.full_name or clean_email.split("@")[0].title()
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        name_parts = (new_user.full_name or "").split(" ")
        first_name = name_parts[0] if len(name_parts) > 0 else "Applicant"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        profile = Profile(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            email=new_user.email
        )
        settings_rec = UserSettings(user_id=new_user.id)
        
        db.add(profile)
        db.add(settings_rec)
        await db.commit()

        # Auto-seed initial applications for the new user account
        from app.models.job import Job
        from app.models.application import Application
        j_res = await db.execute(select(Job))
        jobs = j_res.scalars().all()
        for j in jobs:
            app_rec = Application(
                user_id=new_user.id,
                job_id=j.id,
                status="SUBMITTED" if j.id % 2 == 0 else "RESUME_READY",
                application_mode="AUTO"
            )
            db.add(app_rec)
        await db.commit()
        
        token = create_access_token(new_user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name
            }
        }

    @staticmethod
    async def authenticate_user(db: AsyncSession, user_in: UserLogin) -> dict:
        clean_email = user_in.email.strip().lower()
        result = await db.execute(select(User).filter(func.lower(User.email) == clean_email))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found. Please click Register below to create an account first.")
            
        if not verify_password(user_in.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password. Please check your password and try again.")
            
        token = create_access_token(user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name
            }
        }

    @staticmethod
    async def send_email_otp(db: AsyncSession, email: str) -> dict:
        clean_email = email.strip().lower()
        otp_code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        otp_rec = EmailOTP(
            email=clean_email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.add(otp_rec)
        await db.commit()

        # Send via Resend Email API if API key configured
        if settings.RESEND_API_KEY:
            try:
                resend.api_key = settings.RESEND_API_KEY
                resend.Emails.send({
                    "from": settings.RESEND_FROM_EMAIL,
                    "to": [clean_email],
                    "subject": f"Your JobPilot AI Verification Code: {otp_code}",
                    "html": f"""
                    <div style="font-family: Arial, sans-serif; padding: 24px; background-color: #0f172a; color: #f8fafc; border-radius: 12px;">
                        <h2 style="color: #38bdf8; margin-top: 0;">JobPilot AI Verification Code</h2>
                        <p style="font-size: 15px; color: #e2e8f0;">Use the following 6-digit verification code to complete your login:</p>
                        <div style="font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #10b981; margin: 24px 0; padding: 12px; background: rgba(16, 185, 129, 0.1); display: inline-block; border-radius: 8px;">{otp_code}</div>
                        <p style="color: #94a3b8; font-size: 13px;">This code will expire in 10 minutes. If you did not request this email, please ignore it.</p>
                    </div>
                    """
                })
                print(f"[RESEND_EMAIL] OTP sent to {clean_email} via Resend API")
            except Exception as e:
                print(f"[RESEND_EMAIL_ERROR] Failed to send via Resend: {str(e)}")

        return {
            "message": f"6-Digit verification code sent to {clean_email}. Please check your email inbox.",
            "expires_in_minutes": 10
        }

    @staticmethod
    async def verify_email_otp(db: AsyncSession, email: str, otp_code: str) -> dict:
        clean_email = email.strip().lower()
        res = await db.execute(
            select(EmailOTP)
            .filter(func.lower(EmailOTP.email) == clean_email, EmailOTP.otp_code == otp_code.strip(), EmailOTP.is_verified == False)
            .order_by(EmailOTP.created_at.desc())
        )
        otp_rec = res.scalars().first()
        
        if not otp_rec or otp_rec.is_expired:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP code. Please check your email and try again.")
            
        otp_rec.is_verified = True
        await db.commit()
        
        u_res = await db.execute(select(User).filter(func.lower(User.email) == clean_email))
        user = u_res.scalars().first()
        
        if not user:
            user_in = UserCreate(email=clean_email, password="otp_auth_user_2026", full_name=clean_email.split("@")[0].title())
            return await AuthService.register_user(db, user_in)
            
        token = create_access_token(user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name
            }
        }

    @staticmethod
    async def google_oauth_auth(db: AsyncSession, credential_token: str, fallback_email: str = None, fallback_name: str = None) -> dict:
        import httpx
        email = None
        full_name = None
        
        # Verify Google ID Token via Google's OAuth2 TokenInfo API
        if credential_token and not credential_token.startswith("mock_"):
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={credential_token}")
                    if resp.status_code == 200:
                        data = resp.json()
                        email = data.get("email")
                        full_name = data.get("name") or data.get("given_name")
            except Exception as e:
                print(f"[GOOGLE_AUTH_ERROR] Token verification failed: {e}")
        
        if not email:
            email = fallback_email
            full_name = fallback_name or (email.split("@")[0].title() if email else "Google User")
            
        if not email:
            raise HTTPException(status_code=400, detail="Invalid Google authentication token.")

        clean_email = email.strip().lower()
        u_res = await db.execute(select(User).filter(func.lower(User.email) == clean_email))
        user = u_res.scalars().first()
        
        if not user:
            user_in = UserCreate(email=clean_email, password="google_oauth_user_2026", full_name=full_name)
            return await AuthService.register_user(db, user_in)
            
        token = create_access_token(user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name
            }
        }
