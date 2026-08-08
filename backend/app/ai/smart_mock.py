import re
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

        total_req = max(len(req_job_skills), 1)
        skill_score = min(100, (len(strong) / total_req) * 100)
        
        user_exp_years = len(profile.get("experiences", [])) * 1.5
        job_exp_min = job.get("experience_min", 0)
        exp_score = 100 if user_exp_years >= job_exp_min else 60

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

    async def parse_resume_text(self, raw_resume_text: str) -> Dict[str, Any]:
        text_lower = raw_resume_text.lower()
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_resume_text)
        email = email_match.group(0) if email_match else ""

        # Extract phone
        phone_match = re.search(r'\(?\+?\d{1,3}\)?[-.\s]?\d{3,5}[-.\s]?\d{4,6}', raw_resume_text)
        phone = phone_match.group(0) if phone_match else ""

        # Extract name from first non-empty line
        lines = [l.strip() for l in raw_resume_text.split('\n') if l.strip()]
        first_line = lines[0] if lines else "Candidate"
        name_parts = first_line.split(" ")
        first_name = name_parts[0] if len(name_parts) > 0 else "Candidate"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Extract skills
        tech_keywords = [
            "Python", "FastAPI", "Django", "Flask", "React", "TypeScript", "JavaScript", "Node.js",
            "Next.js", "HTML", "CSS", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
            "AWS", "GCP", "Git", "REST APIs", "GenAI", "LLMs", "LangChain", "PyTorch", "TensorFlow",
            "C++", "Java", "Spring Boot", "System Design", "Microservices", "CI/CD", "Linux"
        ]
        
        extracted_skills = []
        for tech in tech_keywords:
            if tech.lower() in text_lower:
                category = "Languages & Core" if tech in ["Python", "JavaScript", "TypeScript", "C++", "Java"] else \
                           ("Frameworks & Web" if tech in ["React", "FastAPI", "Django", "Node.js", "Next.js"] else \
                           ("Cloud, Databases & AI" if tech in ["PostgreSQL", "MongoDB", "Redis", "Docker", "AWS", "GenAI", "LLMs"] else "Tools"))
                extracted_skills.append({"name": tech, "category": category})

        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "current_city": "Hyderabad" if "hyderabad" in text_lower else ("Bangalore" if "bangalore" in text_lower else ""),
            "country": "India",
            "summary": f"Experienced software engineer with expertise in {', '.join([s['name'] for s in extracted_skills[:4]])}." if extracted_skills else "",
            "skills": extracted_skills,
            "experiences": [],
            "projects": [],
            "education": []
        }

    async def generate_tailored_resume(self, profile: Dict[str, Any], master_resume_text: str, job: Dict[str, Any]) -> Dict[str, Any]:
        first_name = profile.get("first_name", "")
        last_name = profile.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip() or "Candidate"
        
        job_title = job.get("title", "Software Engineer")
        company = job.get("company", "Tech Company")
        
        summary = (
            f"Dynamic {job_title} with strong technical expertise in building high-throughput systems, scalable APIs, and modern web applications. "
            f"Proven track record in {', '.join(job.get('required_skills', ['Software Development'])[:3])}. "
            f"Eager to drive technological innovation and deliver measurable value at {company}."
        )

        experiences = []
        raw_experiences = profile.get("experiences", [])
        if raw_experiences:
            for exp in raw_experiences:
                c_name = exp.get("company")
                if c_name:
                    techs = exp.get('technologies') or 'Python, REST APIs, SQL'
                    experiences.append({
                        "company": c_name,
                        "job_title": exp.get("job_title", job_title),
                        "location": exp.get("location", ""),
                        "dates": f"{exp.get('start_date', '')} - {'Present' if exp.get('is_current') else exp.get('end_date', '')}".strip(" -"),
                        "bullets": [
                            f"Architected and deployed production services using {techs}, improving system throughput and operational efficiency.",
                            f"Designed and optimized database schemas, reducing query latency by 35% across core API endpoints.",
                            f"Collaborated across engineering teams to build and ship production features for target scale."
                        ]
                    })

        projects = []
        raw_projects = profile.get("projects", [])
        if raw_projects:
            for proj in raw_projects:
                p_name = proj.get("name")
                if p_name:
                    techs = proj.get('technologies') or 'Python, React, PostgreSQL'
                    projects.append({
                        "name": p_name,
                        "description": proj.get("description", ""),
                        "technologies": techs,
                        "bullets": [
                            f"Built full-stack application using {techs}.",
                            "Implemented secure authentication, responsive UI components, and automated data processing."
                        ]
                    })

        education = []
        raw_education = profile.get("education", [])
        if raw_education:
            for edu in raw_education:
                u_name = edu.get("university") or edu.get("degree")
                if u_name:
                    education.append({
                        "degree": edu.get("degree", ""),
                        "specialization": edu.get("specialization", ""),
                        "university": edu.get("university", ""),
                        "location": edu.get("location", ""),
                        "dates": f"{edu.get('start_date', '')} - {edu.get('end_date', '')}".strip(" -")
                    })

        # Categorize skills
        skills_by_cat = {}
        user_skills = profile.get("skills", [])
        if user_skills:
            for s in user_skills:
                cat = (s.get("category") if isinstance(s, dict) else "Languages & Core") or "Languages & Core"
                cat_clean = cat.title()
                if cat_clean not in skills_by_cat:
                    skills_by_cat[cat_clean] = []
                s_name = s.get("name") if isinstance(s, dict) else str(s)
                if s_name and s_name not in skills_by_cat[cat_clean]:
                    skills_by_cat[cat_clean].append(s_name)

        # Merge job required skills into skills matrix
        if "Languages & Core" not in skills_by_cat:
            skills_by_cat["Languages & Core"] = []
        if "Frameworks & Tools" not in skills_by_cat:
            skills_by_cat["Frameworks & Tools"] = []

        for req in job.get("required_skills", []):
            if not any(req in slist for slist in skills_by_cat.values()):
                skills_by_cat["Languages & Core"].append(req)

        # Format city location cleanly without "None"
        city = profile.get('current_city', '') or ''
        country = profile.get('country', '') or ''
        loc_parts = [p for p in [city, country] if p and p.lower() != 'none']
        loc_str = ", ".join(loc_parts)

        return {
            "personal_info": {
                "name": full_name,
                "email": profile.get("email") or "",
                "phone": profile.get("phone") or "",
                "location": loc_str or "Hyderabad, India",
                "linkedin": profile.get("linkedin_url") or "",
                "github": profile.get("github_url") or "",
                "portfolio": profile.get("portfolio_url") or ""
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
        title = job.get("title", "this position")
        company = job.get("company", "your organization")
        
        for q in questions:
            q_lower = q.lower()
            if "why" in q_lower or "interest" in q_lower:
                answers[q] = f"I am very excited about the {title} position at {company}. My technical background in software engineering and scalable systems aligns strongly with your team's goals."
            elif "python" in q_lower or "experience" in q_lower:
                answers[q] = "I have extensive practical experience designing RESTful microservices, optimizing database queries, and building production backend services."
            elif "authorized" in q_lower or "sponsorship" in q_lower:
                answers[q] = "Yes, I am fully authorized to work without requiring visa sponsorship."
            elif "notice" in q_lower or "start" in q_lower:
                answers[q] = "I am available to join within 15 to 30 days."
            elif "salary" in q_lower or "expectation" in q_lower:
                answers[q] = "My salary expectations are aligned with competitive market standards for this role."
            else:
                answers[q] = f"My technical experience makes me a strong fit for {company}'s engineering standards."
        return answers

    async def generate_cover_letter(self, profile: Dict[str, Any], job: Dict[str, Any]) -> str:
        name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip() or "Applicant"
        company = job.get("company", "Hiring Team")
        title = job.get("title", "Software Engineer")
        
        return (
            f"Dear Hiring Team at {company},\n\n"
            f"I am writing to express my enthusiastic interest in the {title} role. "
            f"With a strong background in software development, high-performance API design, and system architecture, "
            f"I am confident in my ability to make an immediate, positive impact on your engineering projects.\n\n"
            f"Throughout my experience, I have consistently demonstrated a commitment to writing clean, maintainable code "
            f"and delivering scalable technical solutions. The engineering challenges your team is solving at {company} align perfectly with my technical focus.\n\n"
            f"Thank you for your time and consideration. I welcome the opportunity to discuss how my skill set aligns with your team's vision.\n\n"
            f"Sincerely,\n{name}"
        )
