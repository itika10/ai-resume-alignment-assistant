from io import BytesIO
from docx import Document


def add_heading(doc, text, level=1):
    if text:
        doc.add_heading(text, level=level)


def add_bullet_list(doc, items):
    for item in items:
        if item:
            doc.add_paragraph(item, style="List Bullet")


def generate_resume_docx(resume_data: dict) -> BytesIO:
    doc = Document()

    # Header
    if resume_data.get("name"):
        doc.add_heading(resume_data["name"], level=0)

    contact_parts = []
    if resume_data.get("email"):
        contact_parts.append(resume_data["email"])
    if resume_data.get("phone"):
        contact_parts.append(resume_data["phone"])

    if contact_parts:
        doc.add_paragraph(" | ".join(contact_parts))

    # Summary
    if resume_data.get("summary"):
        add_heading(doc, "Professional Summary", level=1)
        doc.add_paragraph(resume_data["summary"])

    # Skills
    skill_categories = resume_data.get("skill_categories") or []
    flat_skills = resume_data.get("skills") or []

    if skill_categories or flat_skills:
        add_heading(doc, "Skills", level=1)

        if skill_categories:
            for cat in skill_categories:
                category_name = (cat.get("category") or "").strip()
                items = [str(i).strip() for i in (cat.get("items") or []) if str(i).strip()]
                if not items:
                    continue

                paragraph = doc.add_paragraph()
                if category_name:
                    label_run = paragraph.add_run(f"{category_name}: ")
                    label_run.bold = True
                paragraph.add_run(", ".join(items))
        else:
            # Fallback: render the flat list as a single paragraph
            doc.add_paragraph(", ".join(flat_skills))

    # Experience
    if resume_data.get("experience"):
        add_heading(doc, "Experience", level=1)
        for exp in resume_data["experience"]:
            role = exp.get("role", "")
            company = exp.get("company", "")
            title_line = " | ".join(part for part in [role, company] if part)
            if title_line:
                doc.add_paragraph(title_line, style="Heading 2")
            add_bullet_list(doc, exp.get("bullets", []))

    # Projects
    if resume_data.get("projects"):
        add_heading(doc, "Projects", level=1)
        for proj in resume_data["projects"]:
            if proj.get("title"):
                doc.add_paragraph(proj["title"], style="Heading 2")
            add_bullet_list(doc, proj.get("bullets", []))

    # Certifications
    if resume_data.get("certifications"):
        add_heading(doc, "Certifications", level=1)
        add_bullet_list(doc, resume_data["certifications"])

    # Education
    if resume_data.get("education"):
        add_heading(doc, "Education", level=1)
        add_bullet_list(doc, resume_data["education"])

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output