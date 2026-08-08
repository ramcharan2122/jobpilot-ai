import json
from typing import Dict, Any, List
from google import genai
from app.ai.base import AIProvider
from app.core.config import settings

class GeminiProvider(AIProvider):
    
    def __init__(self):
        if settings.AI_API_KEY:
            self.client = genai.Client(api_key=settings.AI_API_KEY)
        else:
            self.client = None

    async def analyze_job(self, job_title: str, company: str, raw_description: str) -> Dict[str, Any]:
        if not self.client:
            from app.ai.smart_mock import SmartMockAIProvider
            return await SmartMockAIProvider().analyze_job(job_title, company, raw_description)
            
        prompt = f"""
        Extract structured JSON details for this job posting:
        Title: {job_title}
        Company: {company}
        Description: {raw_description}

        Return strictly a JSON object with fields:
        "required_skills": list of strings,
        "preferred_skills": list of strings,
        "experience_min": integer,
        "experience_max": integer,
        "salary_min_lpa": float in INR LPA,
        "salary_max_lpa": float in INR LPA,
        "location": string,
        "is_remote": boolean
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception:
            from app.ai.smart_mock import SmartMockAIProvider
            return await SmartMockAIProvider().analyze_job(job_title, company, raw_description)

    async def match_candidate(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        from app.ai.smart_mock import SmartMockAIProvider
        return await SmartMockAIProvider().match_candidate(profile, job)

    async def parse_resume_text(self, raw_resume_text: str) -> Dict[str, Any]:
        if not self.client or not raw_resume_text.strip():
            from app.ai.smart_mock import SmartMockAIProvider
            return await SmartMockAIProvider().parse_resume_text(raw_resume_text)

        prompt = f"""
        Act as an Expert ATS Resume Parser. Extract all structured information from the following raw resume text.

        RAW RESUME TEXT:
        \"\"\"
        {raw_resume_text[:6000]}
        \"\"\"

        Return strictly valid JSON with this exact schema:
        {{
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email Address",
            "phone": "Phone Number",
            "current_city": "City",
            "country": "Country",
            "linkedin_url": "LinkedIn URL",
            "github_url": "GitHub URL",
            "portfolio_url": "Portfolio URL",
            "summary": "Professional Summary",
            "skills": [
                {{"name": "Skill Name", "category": "Programming/Frameworks/Databases/AI-ML/Cloud/Tools"}}
            ],
            "experiences": [
                {{
                    "company": "Company Name",
                    "job_title": "Title",
                    "location": "Location",
                    "start_date": "Start Date",
                    "end_date": "End Date",
                    "is_current": false,
                    "technologies": "Comma separated technologies",
                    "description": "Key achievements and responsibilities"
                }}
            ],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Description and achievements",
                    "technologies": "Comma separated technologies"
                }}
            ],
            "education": [
                {{
                    "degree": "Degree",
                    "specialization": "Specialization",
                    "university": "University/College Name",
                    "location": "Location",
                    "start_date": "Start Date",
                    "end_date": "End Date",
                    "gpa": "GPA/Percentage"
                }}
            ]
        }}
        Do not include markdown tags outside JSON. Return raw valid JSON.
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"[GEMINI_PARSE_ERROR] {e}")
            from app.ai.smart_mock import SmartMockAIProvider
            return await SmartMockAIProvider().parse_resume_text(raw_resume_text)

    async def generate_tailored_resume(self, profile: Dict[str, Any], master_resume_text: str, job: Dict[str, Any]) -> Dict[str, Any]:
        if not self.client:
            from app.ai.smart_mock import SmartMockAIProvider
            return await SmartMockAIProvider().generate_tailored_resume(profile, master_resume_text, job)

        first_name = profile.get("first_name", "")
        last_name = profile.get("last_name", "")
        cand_name = f"{first_name} {last_name}".strip() or "Candidate"

        prompt = f"""
        Act as a Senior Executive Tech Resume Writer and Staff Recruiter.
        Your goal is to transform the candidate's master resume into a top-tier, highly professional, ATS-optimized resume tailored specifically for the target job description.

        TARGET JOB DETAILS:
        - Job Title: {job.get('title', 'Software Engineer')}
        - Company: {job.get('company', 'Tech Company')}
        - Required Skills: {', '.join(job.get('required_skills', []))}
        - Preferred Skills: {', '.join(job.get('preferred_skills', []))}

        CANDIDATE MASTER RESUME TEXT:
        \"\"\"
        {master_resume_text if master_resume_text else "No raw text provided."}
        \"\"\"

        CANDIDATE PROFILE STRUCTURED DATA:
        {json.dumps(profile, indent=2)}

        INSTRUCTIONS:
        1. STRICT FACTUAL PRESERVATION OF EXPERIENCE & EDUCATION: You MUST KEEP ALL Company Names, Job Titles, Employment Dates, University Names, Degree Titles, and Graduation Dates 100% IDENTICAL to the candidate's real Master Resume Text and Profile Data. DO NOT invent, change, or substitute fake company names, job titles, or fake university names under ANY circumstances.
        2. ATS KEYWORD ENHANCEMENT: Include ALL Required Skills ({', '.join(job.get('required_skills', []))}) and Preferred Skills ({', '.join(job.get('preferred_skills', []))}) into the candidate's Technical Skills Matrix and Professional Experience/Projects bullet points.
        3. Format 3-4 bullet points for each REAL work experience and project using strong Action Verbs (Architected, Engineered, Optimized, Scaled, Developed) with quantified impact (% speedup, latency reduction, scale, efficiency) demonstrating practical use of the target job technologies.
        4. Organize skills cleanly into categories (e.g. "Languages & Core", "Frameworks & Web", "Databases, Cloud & AI/ML", "Tools & Platforms").
        5. Write a compelling 3-4 sentence Professional Summary tailored specifically to the target role at {job.get('company', 'the company')}, explicitly referencing key required technologies.

        Return strictly valid JSON with this exact schema:
        {{
            "personal_info": {{
                "name": "{cand_name}",
                "email": "{profile.get('email', '')}",
                "phone": "{profile.get('phone', '')}",
                "location": "{profile.get('current_city', '')}",
                "linkedin": "{profile.get('linkedin_url', '')}",
                "github": "{profile.get('github_url', '')}",
                "portfolio": "{profile.get('portfolio_url', '')}"
            }},
            "target_role": "{job.get('title', 'Software Engineer')}",
            "target_company": "{job.get('company', 'Tech Company')}",
            "summary": "Tailored 3-4 sentence professional summary",
            "skills": {{
                "Languages & Core": ["Python", "JavaScript", "..."],
                "Frameworks & Web": ["FastAPI", "React", "..."],
                "Cloud, Databases & AI/ML": ["PostgreSQL", "GenAI", "..."]
            }},
            "experiences": [
                {{
                    "company": "Company Name",
                    "job_title": "Role Title",
                    "location": "City or Remote",
                    "dates": "Start - End Date",
                    "bullets": [
                        "Action-oriented bullet point 1 with technical detail and metrics",
                        "Bullet point 2",
                        "Bullet point 3"
                    ]
                }}
            ],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Short description",
                    "technologies": "Tech stack",
                    "bullets": [
                        "Project achievement bullet point 1",
                        "Project achievement bullet point 2"
                    ]
                }}
            ],
            "education": [
                {{
                    "degree": "Degree Name",
                    "specialization": "Field of Study",
                    "university": "University Name",
                    "location": "City",
                    "dates": "Start - End Date"
                }}
            ]
        }}
        Do not include markdown tags outside JSON. Return raw valid JSON.
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            print(f"[GEMINI_RESUME_GEN_ERROR] {e}")
            from app.ai.smart_mock import SmartMockAIProvider
            return await SmartMockAIProvider().generate_tailored_resume(profile, master_resume_text, job)

    async def generate_answers(self, profile: Dict[str, Any], job: Dict[str, Any], questions: List[str]) -> Dict[str, str]:
        from app.ai.smart_mock import SmartMockAIProvider
        return await SmartMockAIProvider().generate_answers(profile, job, questions)

    async def generate_cover_letter(self, profile: Dict[str, Any], job: Dict[str, Any]) -> str:
        from app.ai.smart_mock import SmartMockAIProvider
        return await SmartMockAIProvider().generate_cover_letter(profile, job)
