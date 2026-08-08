import hashlib
from typing import List, Dict, Any
from app.job_sources.base import JobSource

class SeedDemoJobSource(JobSource):
    
    RAW_SEED_JOBS = [
        {
            "external_id": "demo-001",
            "company": "Swiggy Engineering",
            "title": "Python Developer",
            "description": "Swiggy is seeking a Python Developer to build high-scale microservices, order dispatching backend, and API integrations using FastAPI, PostgreSQL, and Redis.",
            "requirements": "0-2 years experience in Python, REST APIs, FastAPI/Django, SQL, unit testing.",
            "responsibilities": "Develop scalable APIs, write clean code, work with cross-functional product teams.",
            "required_skills": ["Python", "FastAPI", "REST APIs", "PostgreSQL"],
            "preferred_skills": ["Docker", "Redis", "AWS"],
            "salary_min_lpa": 10.0,
            "salary_max_lpa": 14.0,
            "salary_currency": "INR",
            "salary_confidence": "HIGH",
            "location": "Bangalore",
            "is_remote": False,
            "experience_min": 0,
            "experience_max": 2,
            "application_url": "http://localhost:8000/api/v1/mock-portal/apply?job=demo-001"
        },
        {
            "external_id": "demo-002",
            "company": "PhonePe Tech",
            "title": "Backend Developer",
            "description": "Join PhonePe Payments platform team. Responsible for high-throughput payment transaction pipelines, distributed caching, and microservices.",
            "requirements": "1-3 years experience in Python, SQL, RESTful microservices, Docker.",
            "responsibilities": "Maintain 99.99% system uptime, optimize database query latency, implement automated test coverage.",
            "required_skills": ["Python", "REST APIs", "SQL", "Docker"],
            "preferred_skills": ["Redis", "Kafka", "Kubernetes"],
            "salary_min_lpa": 12.0,
            "salary_max_lpa": 18.0,
            "salary_currency": "INR",
            "salary_confidence": "HIGH",
            "location": "Bangalore",
            "is_remote": True,
            "experience_min": 1,
            "experience_max": 3,
            "application_url": "http://localhost:8000/api/v1/mock-portal/apply?job=demo-002"
        },
        {
            "external_id": "demo-003",
            "company": "Zepto AI Labs",
            "title": "GenAI Engineer",
            "description": "Build cutting-edge LLM agents, RAG document search pipelines, and automated customer intent models using LangChain, OpenAI/Gemini APIs, and FastAPI.",
            "requirements": "0-2 years hands-on experience with GenAI models, Python, Vector DBs, LangChain.",
            "responsibilities": "Design agentic workflows, fine-tune prompts, deploy containerized AI APIs.",
            "required_skills": ["Python", "GenAI", "LLMs", "FastAPI"],
            "preferred_skills": ["LangChain", "Vector DBs", "Docker"],
            "salary_min_lpa": 14.0,
            "salary_max_lpa": 22.0,
            "salary_currency": "INR",
            "salary_confidence": "HIGH",
            "location": "Hyderabad",
            "is_remote": True,
            "experience_min": 0,
            "experience_max": 2,
            "application_url": "http://localhost:8000/api/v1/mock-portal/apply?job=demo-003"
        },
        {
            "external_id": "demo-004",
            "company": "Razorpay Labs",
            "title": "Software Engineer",
            "description": "Razorpay is hiring Junior Software Engineers to craft robust backend payment APIs, merchant dashboard tools, and devops integrations.",
            "requirements": "0-2 years experience, strong computer science fundamentals, Python or TypeScript.",
            "responsibilities": "Implement new merchant features, collaborate with design and product, write clean modular code.",
            "required_skills": ["Python", "TypeScript", "SQL", "Git"],
            "preferred_skills": ["React", "AWS", "PostgreSQL"],
            "salary_min_lpa": 9.0,
            "salary_max_lpa": 15.0,
            "salary_currency": "INR",
            "salary_confidence": "HIGH",
            "location": "Bangalore",
            "is_remote": False,
            "experience_min": 0,
            "experience_max": 2,
            "application_url": "http://localhost:8000/api/v1/mock-portal/apply?job=demo-004"
        },
        {
            "external_id": "demo-005",
            "company": "Postman Engineering",
            "title": "AI Developer",
            "description": "Develop AI assistant extensions and automated API documentation generators using Python, TypeScript, and modern LLM APIs.",
            "requirements": "1-2 years experience, experience building web applications and AI agent workflows.",
            "responsibilities": "Develop developer tools, integrate LLM prompt engines, optimize client-server data flow.",
            "required_skills": ["Python", "TypeScript", "REST APIs", "LLMs"],
            "preferred_skills": ["React", "FastAPI", "Docker"],
            "salary_min_lpa": 11.0,
            "salary_max_lpa": 17.0,
            "salary_currency": "INR",
            "salary_confidence": "HIGH",
            "location": "Remote",
            "is_remote": True,
            "experience_min": 1,
            "experience_max": 2,
            "application_url": "http://localhost:8000/api/v1/mock-portal/apply?job=demo-005"
        },
        {
            "external_id": "demo-006",
            "company": "Figma India",
            "title": "Frontend Developer",
            "description": "Build high performance vector canvas rendering tools and collaborative SaaS web components using React, TypeScript, and WebAssembly.",
            "requirements": "0-2 years experience in React, TypeScript, CSS, State management.",
            "responsibilities": "Develop silky smooth 60fps UI components, collaborate with product designers.",
            "required_skills": ["React", "TypeScript", "JavaScript", "Git"],
            "preferred_skills": ["CSS3", "WebGL", "Redux"],
            "salary_min_lpa": 10.0,
            "salary_max_lpa": 16.0,
            "salary_currency": "INR",
            "salary_confidence": "HIGH",
            "location": "Pune",
            "is_remote": True,
            "experience_min": 0,
            "experience_max": 2,
            "application_url": "http://localhost:8000/api/v1/mock-portal/apply?job=demo-006"
        },
        {
            "external_id": "demo-007",
            "company": "Startup Alpha",
            "title": "Junior Python Developer",
            "description": "Early stage stealth startup looking for a passionate Junior Python developer to build web scrapers, data processing pipelines, and FastAPI endpoints.",
            "requirements": "0-1 year experience or strong personal projects in Python and REST APIs.",
            "responsibilities": "Scrape public datasets, build async web endpoints, write unit tests.",
            "required_skills": ["Python", "REST APIs", "Git"],
            "preferred_skills": ["FastAPI", "PostgreSQL"],
            "salary_min_lpa": 6.0,  # Below ₹8 LPA threshold for salary filter demonstration!
            "salary_max_lpa": 7.5,
            "salary_currency": "INR",
            "salary_confidence": "HIGH",
            "location": "Delhi NCR",
            "is_remote": False,
            "experience_min": 0,
            "experience_max": 1,
            "application_url": "http://localhost:8000/api/v1/mock-portal/apply?job=demo-007"
        }
    ]

    async def search_jobs(self, roles: List[str], locations: List[str], min_lpa: float, max_lpa: float) -> List[Dict[str, Any]]:
        results = []
        for raw in self.RAW_SEED_JOBS:
            norm = await self.normalize_job(raw)
            results.append(norm)
        return results

    async def get_job_details(self, external_id: str) -> Dict[str, Any]:
        for raw in self.RAW_SEED_JOBS:
            if raw["external_id"] == external_id:
                return await self.normalize_job(raw)
        return await self.normalize_job(self.RAW_SEED_JOBS[0])

    async def normalize_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        dup_str = f"{raw_job.get('company')}:{raw_job.get('title')}:{raw_job.get('location')}"
        dup_hash = hashlib.md5(dup_str.lower().encode('utf-8')).hexdigest()
        
        return {
            "source": "DEMO_SEED",
            "external_id": raw_job.get("external_id"),
            "company": raw_job.get("company"),
            "title": raw_job.get("title"),
            "description": raw_job.get("description"),
            "requirements": raw_job.get("requirements"),
            "responsibilities": raw_job.get("responsibilities"),
            "required_skills": raw_job.get("required_skills", []),
            "preferred_skills": raw_job.get("preferred_skills", []),
            "salary_min_lpa": raw_job.get("salary_min_lpa"),
            "salary_max_lpa": raw_job.get("salary_max_lpa"),
            "salary_currency": raw_job.get("salary_currency", "INR"),
            "salary_confidence": raw_job.get("salary_confidence", "HIGH"),
            "location": raw_job.get("location"),
            "is_remote": raw_job.get("is_remote", False),
            "employment_type": "Full-time",
            "experience_min": raw_job.get("experience_min", 0),
            "experience_max": raw_job.get("experience_max", 2),
            "application_url": raw_job.get("application_url"),
            "duplicate_hash": dup_hash
        }
