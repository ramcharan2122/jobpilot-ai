import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_resume(resume_data: dict, output_path: str) -> str:
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=4
    )
    
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569'),
        alignment=1, # Center
        spaceAfter=10
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=14,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    story = []
    
    # Personal Info
    p_info = resume_data.get("personal_info", {})
    name = p_info.get("name", "Candidate")
    story.append(Paragraph(name.upper(), name_style))
    
    contact_bits = []
    if p_info.get("email"): contact_bits.append(p_info["email"])
    if p_info.get("phone"): contact_bits.append(p_info["phone"])
    
    loc_raw = p_info.get("location") or ""
    loc_clean = loc_raw.replace(", None", "").replace("None", "").strip(", ")
    if loc_clean: contact_bits.append(loc_clean)
    
    if p_info.get("linkedin"): contact_bits.append(f"LinkedIn: {p_info['linkedin']}")
    if p_info.get("github"): contact_bits.append(f"GitHub: {p_info['github']}")
    if p_info.get("portfolio"): contact_bits.append(f"Portfolio: {p_info['portfolio']}")
    
    story.append(Paragraph(" | ".join(contact_bits), contact_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=8))

    # Summary
    if resume_data.get("summary"):
        story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
        story.append(Paragraph(resume_data["summary"], body_style))
        story.append(Spacer(1, 4))

    # Skills
    if resume_data.get("skills"):
        story.append(Paragraph("TECHNICAL SKILLS", section_heading))
        skills_dict = resume_data["skills"]
        if isinstance(skills_dict, dict):
            for cat, s_list in skills_dict.items():
                if s_list and isinstance(s_list, list):
                    skills_str = f"<b>{cat}:</b> {', '.join(s_list)}"
                    story.append(Paragraph(skills_str, body_style))
        elif isinstance(skills_dict, list):
            story.append(Paragraph(f"<b>Core Skills:</b> {', '.join(skills_dict)}", body_style))
        story.append(Spacer(1, 4))

    # Experience
    if resume_data.get("experiences"):
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_heading))
        for exp in resume_data["experiences"]:
            title = exp.get('job_title', 'Software Engineer')
            company = exp.get('company', 'Company')
            dates = exp.get('dates', '')
            loc = exp.get('location', '')
            
            loc_str = f" ({loc})" if loc else ""
            head_str = f"<b>{title}</b> — <i>{company}</i>{loc_str} <font color='#64748B'>[{dates}]</font>"
            story.append(Paragraph(head_str, body_style))
            
            bullets = exp.get("bullets", [])
            if not bullets and exp.get("description"):
                bullets = [exp["description"]]
            for bullet in bullets:
                story.append(Paragraph(f"• {bullet}", bullet_style))
            story.append(Spacer(1, 4))

    # Projects
    if resume_data.get("projects"):
        story.append(Paragraph("KEY TECHNICAL PROJECTS", section_heading))
        for proj in resume_data["projects"]:
            name = proj.get('name', 'Project')
            techs = proj.get('technologies', '')
            tech_str = f" | <i>{techs}</i>" if techs else ""
            phead = f"<b>{name}</b>{tech_str}"
            story.append(Paragraph(phead, body_style))
            
            bullets = proj.get("bullets", [])
            if not bullets and proj.get("description"):
                bullets = [proj["description"]]
            for bullet in bullets:
                story.append(Paragraph(f"• {bullet}", bullet_style))
            story.append(Spacer(1, 4))

    # Education
    if resume_data.get("education"):
        story.append(Paragraph("EDUCATION", section_heading))
        for edu in resume_data["education"]:
            degree = edu.get('degree', 'Degree')
            spec = edu.get('specialization', '')
            spec_str = f" in {spec}" if spec else ""
            uni = edu.get('university', 'University')
            dates = edu.get('dates', '')
            
            ehead = f"<b>{degree}{spec_str}</b> — {uni} <font color='#64748B'>[{dates}]</font>"
            story.append(Paragraph(ehead, body_style))

    doc.build(story)
    return output_path
