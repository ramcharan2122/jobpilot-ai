from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    name = Column(String, nullable=False)
    min_lpa = Column(Float, default=8.0)
    max_lpa = Column(Float, default=15.0)
    target_roles = Column(JSON, default=list)
    locations = Column(JSON, default=list)
    min_match_score = Column(Integer, default=75)
    daily_limit = Column(Integer, default=50)
    auto_apply = Column(Boolean, default=True)
    
    # Status: DRAFT, RUNNING, PAUSED, COMPLETED
    status = Column(String, default="RUNNING")
    
    total_discovered = Column(Integer, default=0)
    total_eligible = Column(Integer, default=0)
    total_applied = Column(Integer, default=0)
    total_action_required = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="campaigns")
    applications = relationship("Application", back_populates="campaign")
