from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    
    @abstractmethod
    async def analyze_job(self, job_title: str, company: str, raw_description: str) -> Dict[str, Any]:
        """Extract structured details (required skills, preferred skills, min/max exp, min/max LPA salary, location)."""
        pass

    @abstractmethod
    async def match_candidate(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate transparent match score, strong matches, partial matches, missing skills."""
        pass

    @abstractmethod
    async def generate_tailored_resume(self, profile: Dict[str, Any], master_resume_text: str, job: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize job-specific ATS optimized resume JSON structure based strictly on verified profile facts."""
        pass

    @abstractmethod
    async def generate_answers(self, profile: Dict[str, Any], job: Dict[str, Any], questions: List[str]) -> Dict[str, str]:
        """Generate tailored application question answers."""
        pass

    @abstractmethod
    async def generate_cover_letter(self, profile: Dict[str, Any], job: Dict[str, Any]) -> str:
        """Generate a concise professional cover letter."""
        pass
