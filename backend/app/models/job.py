from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False, default="DEMO_SEED") # DEMO_SEED, LINKEDIN, GREENHOUSE, LEVER, CAREERS
    external_id = Column(String, nullable=True)
    company = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    
    salary_min_lpa = Column(Float, nullable=True) # in LPA e.g. 8.0
    salary_max_lpa = Column(Float, nullable=True) # in LPA e.g. 12.0
    salary_currency = Column(String, default="INR")
    salary_confidence = Column(String, default="HIGH") # CONFIRMED, ESTIMATED, UNDISCLOSED
    
    location = Column(String, nullable=True)
    is_remote = Column(Boolean, default=False)
    employment_type = Column(String, default="Full-time")
    experience_min = Column(Integer, default=0)
    experience_max = Column(Integer, default=2)
    
    application_url = Column(String, nullable=False)
    posted_date = Column(DateTime, default=datetime.utcnow)
    collected_date = Column(DateTime, default=datetime.utcnow)
    job_status = Column(String, default="OPEN") # OPEN, CLOSED, EXPIRED
    duplicate_hash = Column(String, index=True, nullable=False)

    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    generated_resumes = relationship("GeneratedResume", back_populates="job", cascade="all, delete-orphan")

class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    match_score = Column(Integer, nullable=False) # 0 to 100
    eligibility_status = Column(String, nullable=False) # ELIGIBLE, SALARY_MISMATCH, EXP_MISMATCH, LOW_MATCH
    
    # Store transparent matching evaluation
    strong_matches = Column(JSON, default=list)
    partial_matches = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    score_breakdown = Column(JSON, default=dict) # {"skills": 35, "experience": 20, ...}
    
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="matches")
    user = relationship("User", back_populates="job_matches")
