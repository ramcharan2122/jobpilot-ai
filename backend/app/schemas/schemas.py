from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Profile Schemas ---
class EducationSchema(BaseModel):
    id: Optional[int] = None
    degree: str
    specialization: Optional[str] = None
    university: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    relevant_coursework: Optional[str] = None

class ExperienceSchema(BaseModel):
    id: Optional[int] = None
    company: str
    job_title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    responsibilities: Optional[str] = None
    achievements: Optional[str] = None
    technologies: Optional[str] = None
    projects: Optional[str] = None

class SkillSchema(BaseModel):
    id: Optional[int] = None
    category: str
    name: str
    proficiency: Optional[str] = "Intermediate"

class ProjectSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    technologies: Optional[str] = None
    responsibilities: Optional[str] = None
    achievements: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    dates: Optional[str] = None

class CertificationSchema(BaseModel):
    id: Optional[int] = None
    name: str
    issuing_organization: str
    date: Optional[str] = None
    credential_url: Optional[str] = None

class ProfileCreateOrUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    current_city: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    personal_website: Optional[str] = None
    summary: Optional[str] = None
    
    education: List[EducationSchema] = []
    experiences: List[ExperienceSchema] = []
    skills: List[SkillSchema] = []
    projects: List[ProjectSchema] = []
    certifications: List[CertificationSchema] = []

class ProfileOut(ProfileCreateOrUpdate):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- Settings Schemas ---
class UserSettingsUpdate(BaseModel):
    min_lpa: Optional[float] = 8.0
    max_lpa: Optional[float] = 15.0
    currency: Optional[str] = "INR"
    apply_undisclosed_salary: Optional[bool] = False
    allow_estimated_salary: Optional[bool] = True
    preferred_roles: Optional[List[str]] = None
    experience_min: Optional[int] = 0
    experience_max: Optional[int] = 2
    locations: Optional[List[str]] = None
    remote_preference: Optional[str] = "Any"
    employment_types: Optional[List[str]] = None
    min_match_score: Optional[int] = 75
    daily_application_limit: Optional[int] = 50
    auto_apply_enabled: Optional[bool] = False
    application_mode: Optional[str] = "APPROVAL"
    cover_letter_enabled: Optional[bool] = True

class UserSettingsOut(UserSettingsUpdate):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- Job Schemas ---
class JobOut(BaseModel):
    id: int
    source: str
    company: str
    title: str
    description: str
    requirements: Optional[str]
    responsibilities: Optional[str]
    required_skills: List[str]
    preferred_skills: List[str]
    salary_min_lpa: Optional[float]
    salary_max_lpa: Optional[float]
    salary_currency: str
    salary_confidence: str
    location: Optional[str]
    is_remote: bool
    employment_type: str
    experience_min: int
    experience_max: int
    application_url: str
    posted_date: datetime
    job_status: str
    
    # Match info if calculated
    match_score: Optional[int] = None
    eligibility_status: Optional[str] = None
    strong_matches: Optional[List[str]] = None
    partial_matches: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None

    class Config:
        from_attributes = True

# --- Resume Schemas ---
class GeneratedResumeOut(BaseModel):
    id: int
    job_id: int
    file_name: str
    pdf_url: str
    docx_url: str
    validation_passed: bool
    validation_notes: List[str]
    content_json: Dict[str, Any]
    generated_at: datetime

# --- Application Schemas ---
class ApplicationCreate(BaseModel):
    job_id: int
    application_mode: Optional[str] = "APPROVAL"

class ApplicationOut(BaseModel):
    id: int
    job_id: int
    status: str
    application_mode: str
    job: Optional[JobOut] = None
    resume_id: Optional[int] = None
    pdf_url: Optional[str] = None
    answers_json: Dict[str, Any] = {}
    cover_letter: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    screenshot_url: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Campaign Schemas ---
class CampaignCreate(BaseModel):
    name: str
    min_lpa: float = 8.0
    max_lpa: float = 15.0
    target_roles: List[str] = []
    locations: List[str] = []
    min_match_score: int = 75
    daily_limit: int = 50
    auto_apply: bool = True

class CampaignOut(CampaignCreate):
    id: int
    status: str
    total_discovered: int
    total_eligible: int
    total_applied: int
    total_action_required: int
    total_failed: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Dashboard Stats Schema ---
class DashboardStats(BaseModel):
    jobs_found: int
    eligible_jobs: int
    ai_matches: int
    resumes_generated: int
    applications_submitted: int
    action_required: int
    failed_applications: int
    interviews: int
    offers: int
    applications_by_day: List[Dict[str, Any]]
    applications_by_role: List[Dict[str, Any]]
    match_distribution: List[Dict[str, Any]]
