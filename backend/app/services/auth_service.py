import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
        result = await db.execute(select(User).filter(User.email == user_in.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
            
        hashed_pwd = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email,
            hashed_password=hashed_pwd,
            full_name=user_in.full_name or user_in.email.split("@")[0].title()
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
        result = await db.execute(select(User).filter(User.email == user_in.email))
        user = result.scalars().first()
        if not user or not verify_password(user_in.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
            
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
        otp_code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        otp_rec = EmailOTP(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.add(otp_rec)
        await db.commit()

        # Send via Resend Email API if API key configured
        resend_sent = False
        if settings.RESEND_API_KEY:
            try:
                resend.api_key = settings.RESEND_API_KEY
                resend.Emails.send({
                    "from": settings.RESEND_FROM_EMAIL,
                    "to": [email],
                    "subject": f"Your JobPilot AI Verification Code: {otp_code}",
                    "html": f"""
                    <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #0f172a; color: #f8fafc; border-radius: 8px;">
                        <h2 style="color: #38bdf8;">JobPilot AI Verification Code</h2>
                        <p>Use the following 6-digit verification code to complete your login:</p>
                        <div style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #10b981; margin: 20px 0;">{otp_code}</div>
                        <p style="color: #94a3b8; font-size: 12px;">This code will expire in 10 minutes. If you did not request this email, please ignore it.</p>
                    </div>
                    """
                })
                resend_sent = True
                print(f"[RESEND_EMAIL] OTP sent to {email} via Resend API")
            except Exception as e:
                print(f"[RESEND_EMAIL_ERROR] Failed to send via Resend: {str(e)}")

        print(f"[AUTH_EMAIL_OTP] 6-digit OTP code for {email}: {otp_code}")

        return {
            "message": f"6-Digit OTP code sent to {email} via {'Resend Email Service' if resend_sent else 'JobPilot Auth Service'}",
            "expires_in_minutes": 10,
            "resend_delivered": resend_sent,
            "demo_otp_code": otp_code # Provided for instant demonstration testing
        }

    @staticmethod
    async def verify_email_otp(db: AsyncSession, email: str, otp_code: str) -> dict:
        res = await db.execute(
            select(EmailOTP)
            .filter(EmailOTP.email == email, EmailOTP.otp_code == otp_code, EmailOTP.is_verified == False)
            .order_by(EmailOTP.created_at.desc())
        )
        otp_rec = res.scalars().first()
        
        if not otp_rec or otp_rec.is_expired:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP code.")
            
        otp_rec.is_verified = True
        await db.commit()
        
        u_res = await db.execute(select(User).filter(User.email == email))
        user = u_res.scalars().first()
        
        if not user:
            user_in = UserCreate(email=email, password="otp_auth_user_2026", full_name=email.split("@")[0].title())
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
    async def google_oauth_auth(db: AsyncSession, email: str, full_name: str) -> dict:
        u_res = await db.execute(select(User).filter(User.email == email))
        user = u_res.scalars().first()
        
        if not user:
            user_in = UserCreate(email=email, password="google_oauth_user_2026", full_name=full_name)
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
