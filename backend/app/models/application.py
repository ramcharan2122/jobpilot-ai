from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("generated_resumes.id"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # States: READY, GENERATING_RESUME, RESUME_READY, APPLYING, SUBMITTED, FAILED, ACTION_REQUIRED, SKIPPED, DUPLICATE
    status = Column(String, default="READY", nullable=False)
    application_mode = Column(String, default="APPROVAL") # MANUAL, APPROVAL, AUTO
    
    answers_json = Column(JSON, default=dict)
    cover_letter = Column(Text, nullable=True)
    
    error_type = Column(String, nullable=True) # CAPTCHA_DETECTED, FORM_CHANGED, MISSING_FIELD, NETWORK_ERROR, etc.
    error_message = Column(Text, nullable=True)
    screenshot_path = Column(String, nullable=True)
    
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("GeneratedResume", back_populates="applications")
    campaign = relationship("Campaign", back_populates="applications")
    events = relationship("ApplicationEvent", back_populates="application", cascade="all, delete-orphan")

class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    event_type = Column(String, nullable=False) # STATUS_CHANGE, LOG, RESUME_ATTACHED, FORM_FILLED, ERROR
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="events")
