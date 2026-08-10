from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    first_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    current_city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    personal_website = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="profile")
    education = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="profile", cascade="all, delete-orphan")
    master_resumes = relationship("MasterResume", back_populates="profile", cascade="all, delete-orphan")

class Education(Base):
    __tablename__ = "education"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    degree = Column(String, nullable=False)
    specialization = Column(String, nullable=True)
    university = Column(String, nullable=False)
    location = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    gpa = Column(String, nullable=True)
    relevant_coursework = Column(Text, nullable=True)

    profile = relationship("Profile", back_populates="education")

class Experience(Base):
    __tablename__ = "experience"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    company = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    location = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    is_current = Column(Boolean, default=False)
    responsibilities = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)
    technologies = Column(String, nullable=True)
    projects = Column(Text, nullable=True)

    profile = relationship("Profile", back_populates="experiences")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    category = Column(String, nullable=False)  # programming, frameworks, databases, cloud, devops, ai_ml, frontend, backend, tools, soft
    name = Column(String, nullable=False)
    proficiency = Column(String, nullable=True)  # Beginner, Intermediate, Expert

    profile = relationship("Profile", back_populates="skills")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(String, nullable=True)
    responsibilities = Column(Text, nullable=True)
    achievements = Column(Text, nullable=True)
    github_url = Column(String, nullable=True)
    demo_url = Column(String, nullable=True)
    dates = Column(String, nullable=True)

    profile = relationship("Profile", back_populates="projects")

class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    name = Column(String, nullable=False)
    issuing_organization = Column(String, nullable=False)
    date = Column(String, nullable=True)
    credential_url = Column(String, nullable=True)

    profile = relationship("Profile", back_populates="certifications")

class MasterResume(Base):
    __tablename__ = "master_resumes"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # PDF, DOCX
    parsed_content = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="master_resumes")

class ConnectedPlatform(Base):
    __tablename__ = "connected_platforms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform_name = Column(String, nullable=False)  # LINKEDIN, NAUKRI, INDEED, INSTAHYRE, WELLFOUND, FOUNDIT, UNSTOP, GLASSDOOR
    username_or_email = Column(String, nullable=True)
    auth_credentials = Column(String, nullable=True)
    is_connected = Column(Boolean, default=True)
    last_synced_at = Column(DateTime, default=datetime.utcnow)
