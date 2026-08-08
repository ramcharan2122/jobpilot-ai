from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    min_lpa = Column(Float, default=8.0)  # e.g., 8 LPA (₹800,000)
    max_lpa = Column(Float, default=15.0) # e.g., 15 LPA (₹1,500,000)
    currency = Column(String, default="INR")
    apply_undisclosed_salary = Column(Boolean, default=False)
    allow_estimated_salary = Column(Boolean, default=True)

    preferred_roles = Column(JSON, default=lambda: [
        "Software Engineer",
        "Software Developer",
        "Python Developer",
        "Backend Developer",
        "GenAI Engineer",
        "AI Engineer"
    ])
    
    experience_min = Column(Integer, default=0)
    experience_max = Column(Integer, default=2)
    locations = Column(JSON, default=lambda: ["India", "Bangalore", "Remote", "Hyderabad", "Pune"])
    remote_preference = Column(String, default="Any") # Remote, Hybrid, On-site, Any
    employment_types = Column(JSON, default=lambda: ["Full-time"])

    min_match_score = Column(Integer, default=75)
    daily_application_limit = Column(Integer, default=50)
    auto_apply_enabled = Column(Boolean, default=False)
    application_mode = Column(String, default="APPROVAL")  # MANUAL, APPROVAL, AUTO
    
    cover_letter_enabled = Column(Boolean, default=True)

    user = relationship("User", back_populates="settings")
