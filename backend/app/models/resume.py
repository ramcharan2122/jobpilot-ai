from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class GeneratedResume(Base):
    __tablename__ = "generated_resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    file_name = Column(String, nullable=False)
    pdf_path = Column(String, nullable=False)
    docx_path = Column(String, nullable=False)
    
    # Validation results
    validation_passed = Column(Boolean, default=True)
    validation_notes = Column(JSON, default=list)
    
    # Tailored content structure
    content_json = Column(JSON, nullable=False)
    
    generated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="generated_resumes")
    job = relationship("Job", back_populates="generated_resumes")
    applications = relationship("Application", back_populates="resume")
