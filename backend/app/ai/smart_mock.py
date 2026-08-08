from typing import Dict, Any, List
from app.ai.base import AIProvider

class SmartMockAIProvider(AIProvider):
    
    async def analyze_job(self, job_title: str, company: str, raw_description: str) -> Dict[str, Any]:
        desc_lower = raw_description.lower()
        title_lower = job_title.lower()
        
        req_skills = []
        pref_skills = []
        
        keywords_map = {
            "python": ("Python", "required"),
            "fastapi": ("FastAPI", "required"),
            "django": ("Django", "preferred"),
            "rest": ("REST APIs", "required"),
            "postgresql": ("PostgreSQL", "required"),
            "sql": ("SQL", "required"),
            "docker": ("Docker", "preferred"),
            "aws": ("AWS", "preferred"),
            "react": ("React", "required"),
            "typescript": ("TypeScript", "required"),
            "javascript": ("JavaScript", "required"),
            "genai": ("GenAI", "required"),
            "llm": ("LLMs", "required"),
            "langchain": ("LangChain", "preferred"),
            "pytorch": ("PyTorch", "preferred"),
            "redis": ("Redis", "preferred"),
            "kubernetes": ("Kubernetes", "preferred"),
            "node": ("Node.js", "required"),
            "git": ("Git", "required")
        }
        
        for k, (name, category) in keywords_map.items():
            if k in desc_lower or k in title_lower:
                if category == "required":
                    req_skills.append(name)
                else:
                    pref_skills.append(name)
                    
        if not req_skills:
            req_skills = ["Software Engineering", "Problem Solving", "Git"]
        if not pref_skills:
            pref_skills = ["Docker", "CI/CD"]

        return {
            "required_skills": req_skills,
            "preferred_skills": pref_skills,
            "experience_min": 0 if "0-" in desc_lower or "fresher" in desc_lower else 1,
            "experience_max": 2 if "2" in desc_lower or "junior" in title_lower else 3,
            "salary_min_lpa": 8.0,
            "salary_max_lpa": 14.0,
            "location": "Bangalore" if "bangalore" in desc_lower else ("Remote" if "remote" in desc_lower else "India"),
            "is_remote": "remote" in desc_lower or "remote" in title_lower
        }

    async def match_candidate(self, profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        user_skills = set()
        for s in profile.get("skills", []):
            if isinstance(s, dict) and "name" in s:
                user_skills.add(s["name"].lower())
            elif isinstance(s, str):
                user_skills.add(s.lower())
                
        for proj in profile.get("projects", []):
            techs = proj.get("technologies", "") or ""
            for t in techs.split(","):
                if t.strip():
                    user_skills.add(t.strip().lower())
                    
        for exp in profile.get("experiences", []):
            techs = exp.get("technologies", "") or ""
            for t in techs.split(","):
                if t.strip():
                    user_skills.add(t.strip().lower())

        req_job_skills = [s.lower() for s in job.get("required_skills", [])]
        pref_job_skills = [s.lower() for s in job.get("preferred_skills", [])]
        
        strong = []
        partial = []
        missing = []
        
        for req in job.get("required_skills", []):
            r_lower = req.lower()
            if any(u in r_lower or r_lower in u for u in user_skills):
                strong.append(req)
            else:
                missing.append(req)
                
        for pref in job.get("preferred_skills", []):
            p_lower = pref.lower()
            if any(u in p_lower or p_lower in u for u in user_skills):
                partial.append(pref)
            elif pref not in missing:
                missing.append(pref)

        # Weighted calculation:
        total_req = max(len(req_job_skills), 1)
        skill_score = min(100, (len(strong) / total_req) * 100)
        
        # Experience match
        user_exp_years = len(profile.get("experiences", [])) * 1.5
        job_exp_min = job.get("experience_min", 0)
        exp_score = 100 if user_exp_years >= job_exp_min else 60

        # Title match
        target_roles = [t.lower() for t in job.get("title", "").split()]
        title_score = 85

        final_score = int(
            (skill_score * 0.45) +
            (exp_score * 0.25) +
            (title_score * 0.30)
        )
        final_score = min(98, max(50, final_score))

        return {
            "match_score": final_score,
            "strong_matches": strong,
            "partial_matches": partial,
            "missing_skills": missing,
            "score_breakdown": {
                "skills_weight": 45,
                "skills_score": int(skill_score),
                "experience_weight": 25,
                "experience_score": int(exp_score),
                "title_weight": 30,
                "title_score": title_score
            }
        }

    async def generate_tailored_resume(self, profile: Dict[str, Any], master_resume_text: str, job: Dict[str, Any]) -> Dict[str, Any]:
        full_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Candidate"
        job_title = job.get("title", "Software Engineer")
        company = job.get("company", "Tech Company")
        
        summary = (
            f"Results-driven {job_title} with proven expertise in building scalable web applications and high-performance backend systems. "
            f"Strong background in {', '.join(job.get('required_skills', ['Software Engineering'])[:3])}. "
            f"Passionate about delivering high quality solutions for {company}."
        )

        experiences = []
        for exp in profile.get("experiences", []):
            experiences.append({
                "company": exp.get("company"),
                "job_title": exp.get("job_title"),
                "location": exp.get("location"),
                "dates": f"{exp.get('start_date', '')} - {'Present' if exp.get('is_current') else exp.get('end_date', '')}",
                "bullets": [
                    f"Architected and deployed scalable backend services using {exp.get('technologies', 'Python, REST APIs')}.",
                    f"Optimized database query performance and API latency by 35% through caching and asynchronous processing.",
                    f"Collaborated across cross-functional engineering teams to implement production features."
                ]
            })

        projects = []
        for proj in profile.get("projects", []):
            projects.append({
                "name": proj.get("name"),
                "description": proj.get("description"),
                "technologies": proj.get("technologies"),
                "bullets": [
                    f"Built full-stack application using {proj.get('technologies', 'React, Python, PostgreSQL')}.",
                    "Implemented responsive UI design, secure authentication, and robust data persistence."
                ]
            })

        education = []
        for edu in profile.get("education", []):
            education.append({
                "degree": edu.get("degree"),
                "specialization": edu.get("specialization"),
                "university": edu.get("university"),
                "location": edu.get("location"),
                "dates": f"{edu.get('start_date', '')} - {edu.get('end_date', '')}",
                "gpa": edu.get("gpa")
            })

        skills_by_cat = {}
        for s in profile.get("skills", []):
            cat = s.get("category", "General").title()
            if cat not in skills_by_cat:
                skills_by_cat[cat] = []
            skills_by_cat[cat].append(s.get("name"))

        return {
            "personal_info": {
                "name": full_name,
                "email": profile.get("email"),
                "phone": profile.get("phone"),
                "location": f"{profile.get('current_city', '')}, {profile.get('country', '')}".strip(", "),
                "linkedin": profile.get("linkedin_url"),
                "github": profile.get("github_url"),
                "portfolio": profile.get("portfolio_url")
            },
            "target_role": job_title,
            "target_company": company,
            "summary": summary,
            "skills": skills_by_cat,
            "experiences": experiences,
            "projects": projects,
            "education": education
        }

    async def generate_answers(self, profile: Dict[str, Any], job: Dict[str, Any], questions: List[str]) -> Dict[str, str]:
        answers = {}
        first_name = profile.get("first_name", "Applicant")
        company = job.get("company", "your organization")
        title = job.get("title", "this position")
        
        for q in questions:
            q_lower = q.lower()
            if "why" in q_lower or "interest" in q_lower:
                answers[q] = f"I am very excited about the {title} position at {company}. My technical background in software development and problem solving aligns strongly with your engineering goals."
            elif "python" in q_lower or "experience" in q_lower:
                answers[q] = "I have extensive practical experience designing RESTful microservices, optimizing database queries, and building production backend pipelines."
            elif "authorized" in q_lower or "sponsorship" in q_lower:
                answers[q] = "Yes, I am fully authorized to work without requiring visa sponsorship."
            elif "notice" in q_lower or "start" in q_lower:
                answers[q] = "I am available to join within 15 to 30 days."
            elif "salary" in q_lower or "expectation" in q_lower:
                answers[q] = "My salary expectations are aligned with industry standards for this role (INR 8 - 15 LPA)."
            else:
                answers[q] = f"My experience as a Software Developer makes me a strong fit for {company}'s technical standards and collaborative culture."
        return answers

    async def generate_cover_letter(self, profile: Dict[str, Any], job: Dict[str, Any]) -> str:
        name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Applicant"
        company = job.get("company", "Hiring Manager")
        title = job.get("title", "Software Engineer")
        
        return (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my enthusiastic interest in the {title} opportunity. "
            f"With a strong foundation in modern software development, API design, and system architecture, "
            f"I am confident in my ability to make an immediate impact on your engineering projects.\n\n"
            f"Throughout my projects and technical background, I have consistently demonstrated a commitment to clean code, "
            f"high performance, and thorough testing. The challenges your team is addressing at {company} resonate deeply with my career goals.\n\n"
            f"Thank you for your time and consideration. I welcome the opportunity to discuss how my skill set aligns with your team's vision.\n\n"
            f"Sincerely,\n{name}"
        )
