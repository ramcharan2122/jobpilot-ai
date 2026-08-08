from abc import ABC, abstractmethod
from typing import List, Dict, Any

class JobSource(ABC):
    
    @abstractmethod
    async def search_jobs(self, roles: List[str], locations: List[str], min_lpa: float, max_lpa: float) -> List[Dict[str, Any]]:
        """Search and discover jobs matching filters."""
        pass

    @abstractmethod
    async def get_job_details(self, external_id: str) -> Dict[str, Any]:
        """Fetch complete job posting details."""
        pass

    @abstractmethod
    async def normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw job payload into standardized schema."""
        pass
