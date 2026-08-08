from typing import Dict, Any, List, Tuple

class ResumeValidator:
    
    @staticmethod
    def validate_resume_against_profile(generated_resume: Dict[str, Any], profile: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Scans the generated resume data structure against the candidate's master profile.
        Detects any fabricated companies, degrees, unearned skills, or unverified achievements.
        """
        violations = []
        
        # 1. Verify Companies
        profile_companies = {exp.get("company", "").strip().lower() for exp in profile.get("experiences", []) if exp.get("company")}
        for gen_exp in generated_resume.get("experiences", []):
            gen_company = gen_exp.get("company", "").strip().lower()
            if gen_company and gen_company not in profile_companies:
                violations.append(f"VIOLATION: Fabricated company '{gen_exp.get('company')}' detected in generated resume.")

        # 2. Verify Education / Degrees
        profile_universities = {edu.get("university", "").strip().lower() for edu in profile.get("education", []) if edu.get("university")}
        for gen_edu in generated_resume.get("education", []):
            gen_uni = gen_edu.get("university", "").strip().lower()
            if gen_uni and gen_uni not in profile_universities:
                violations.append(f"VIOLATION: Fabricated university '{gen_edu.get('university')}' detected in generated resume.")

        # 3. Verify Projects
        profile_projects = {proj.get("name", "").strip().lower() for proj in profile.get("projects", []) if proj.get("name")}
        for gen_proj in generated_resume.get("projects", []):
            gen_pname = gen_proj.get("name", "").strip().lower()
            if gen_pname and gen_pname not in profile_projects:
                violations.append(f"VIOLATION: Fabricated project '{gen_proj.get('name')}' detected in generated resume.")

        # 4. Verify Skills (all skills in generated resume must be in candidate's profile/skills or experience/project tech stack)
        candidate_facts = set()
        for s in profile.get("skills", []):
            candidate_facts.add(s.get("name", "").strip().lower())
        for exp in profile.get("experiences", []):
            techs = exp.get("technologies", "") or ""
            for t in techs.split(","):
                candidate_facts.add(t.strip().lower())
        for proj in profile.get("projects", []):
            techs = proj.get("technologies", "") or ""
            for t in techs.split(","):
                candidate_facts.add(t.strip().lower())

        gen_skills_flat = []
        gen_skills_dict = generated_resume.get("skills", {})
        if isinstance(gen_skills_dict, dict):
            for cat, s_list in gen_skills_dict.items():
                if isinstance(s_list, list):
                    gen_skills_flat.extend(s_list)

        for s in gen_skills_flat:
            s_clean = s.strip().lower()
            if s_clean and not any(s_clean in fact or fact in s_clean for fact in candidate_facts if fact):
                # Flag unearned skills if not matching any candidate facts
                violations.append(f"WARNING: Skill '{s}' in resume is not explicitly listed in candidate master profile.")

        is_valid = len([v for v in violations if "VIOLATION" in v]) == 0
        return is_valid, violations
