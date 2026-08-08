import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.user import User
from app.models.profile import Profile
from app.models.settings import UserSettings
from app.models.otp import EmailOTP
from app.schemas.schemas import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token

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
        settings = UserSettings(user_id=new_user.id)
        
        db.add(profile)
        db.add(settings)
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
        
        # Log code to console/file
        print(f"[AUTH_EMAIL_OTP] 6-digit OTP code for {email}: {otp_code}")
        
        return {
            "message": f"6-Digit OTP sent successfully to {email}",
            "expires_in_minutes": 10,
            "demo_otp_code": otp_code # Included for instant demonstration testing
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
        
        # Find or register user
        u_res = await db.execute(select(User).filter(User.email == email))
        user = u_res.scalars().first()
        
        if not user:
            # Auto-register user from verified OTP email
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
