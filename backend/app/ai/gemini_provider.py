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

    async def generate_tailored_resume(self, profile: Dict[str, Any], master_resume_text: str, job: Dict[str, Any]) -> Dict[str, Any]:
        from app.ai.smart_mock import SmartMockAIProvider
        return await SmartMockAIProvider().generate_tailored_resume(profile, master_resume_text, job)

    async def generate_answers(self, profile: Dict[str, Any], job: Dict[str, Any], questions: List[str]) -> Dict[str, str]:
        from app.ai.smart_mock import SmartMockAIProvider
        return await SmartMockAIProvider().generate_answers(profile, job, questions)

    async def generate_cover_letter(self, profile: Dict[str, Any], job: Dict[str, Any]) -> str:
        from app.ai.smart_mock import SmartMockAIProvider
        return await SmartMockAIProvider().generate_cover_letter(profile, job)
