export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Education {
  id?: number;
  degree: string;
  specialization?: string;
  university: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  relevant_coursework?: string;
}

export interface Experience {
  id?: number;
  company: string;
  job_title: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  is_current?: boolean;
  responsibilities?: string;
  achievements?: string;
  technologies?: string;
  projects?: string;
}

export interface Skill {
  id?: number;
  category: string;
  name: string;
  proficiency?: string;
}

export interface Project {
  id?: number;
  name: string;
  description?: string;
  technologies?: string;
  responsibilities?: string;
  achievements?: string;
  github_url?: string;
  demo_url?: string;
  dates?: string;
}

export interface Certification {
  id?: number;
  name: string;
  issuing_organization: string;
  date?: string;
  credential_url?: string;
}

export interface Profile {
  id?: number;
  user_id?: number;
  first_name?: string;
  middle_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  current_city?: string;
  country?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  personal_website?: string;
  summary?: string;
  education: Education[];
  experiences: Experience[];
  skills: Skill[];
  projects: Project[];
  certifications: Certification[];
}

export interface UserSettings {
  id?: number;
  user_id?: number;
  min_lpa: number;
  max_lpa: number;
  currency: string;
  apply_undisclosed_salary: boolean;
  allow_estimated_salary: boolean;
  preferred_roles: string[];
  experience_min: number;
  experience_max: number;
  locations: string[];
  remote_preference: string;
  employment_types: string[];
  min_match_score: number;
  daily_application_limit: number;
  auto_apply_enabled: boolean;
  application_mode: 'MANUAL' | 'APPROVAL' | 'AUTO';
  cover_letter_enabled: boolean;
}

export interface Job {
  id: number;
  source: string;
  company: string;
  title: string;
  description: string;
  requirements?: string;
  responsibilities?: string;
  required_skills: string[];
  preferred_skills: string[];
  salary_min_lpa?: number;
  salary_max_lpa?: number;
  salary_currency: string;
  salary_confidence: string;
  location?: string;
  is_remote: boolean;
  employment_type: string;
  experience_min: number;
  experience_max: number;
  application_url: string;
  posted_date: string;
  job_status: string;
  
  match_score?: number;
  eligibility_status?: 'ELIGIBLE' | 'SALARY_MISMATCH' | 'EXP_MISMATCH' | 'LOW_MATCH';
  strong_matches?: string[];
  partial_matches?: string[];
  missing_skills?: string[];
}

export interface GeneratedResume {
  id: number;
  job_id: number;
  file_name: string;
  pdf_url: string;
  docx_url: string;
  validation_passed: boolean;
  validation_notes: string[];
  content_json: any;
  generated_at: string;
}

export interface Application {
  id: number;
  job_id: number;
  status: 'READY' | 'GENERATING_RESUME' | 'RESUME_READY' | 'APPLYING' | 'SUBMITTED' | 'ACTION_REQUIRED' | 'FAILED' | 'SKIPPED';
  application_mode: string;
  job?: Job;
  resume_id?: number;
  pdf_url?: string;
  answers_json: Record<string, string>;
  cover_letter?: string;
  error_type?: string;
  error_message?: string;
  screenshot_url?: string;
  submitted_at?: string;
  created_at: string;
}

export interface Campaign {
  id: number;
  name: string;
  min_lpa: number;
  max_lpa: number;
  target_roles: string[];
  locations: string[];
  min_match_score: number;
  daily_limit: number;
  auto_apply: boolean;
  status: string;
  total_discovered: number;
  total_eligible: number;
  total_applied: number;
  total_action_required: number;
  total_failed: number;
  created_at: string;
}

export interface DashboardStats {
  jobs_found: number;
  eligible_jobs: number;
  ai_matches: number;
  resumes_generated: number;
  applications_submitted: number;
  action_required: number;
  failed_applications: number;
  interviews: number;
  offers: number;
  applications_by_day: { date: string; submitted: number; failed: number }[];
  applications_by_role: { name: string; value: number }[];
  match_distribution: { range: string; count: number }[];
}
