from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def generate_resume_pdf(resume_data: dict) -> BytesIO:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading1"]
    subheading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=styles["BodyText"],
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=4,
    )

    story = []

    # Header
    if resume_data.get("name"):
        story.append(Paragraph(resume_data["name"], title_style))
        story.append(Spacer(1, 8))

    contact_parts = []
    if resume_data.get("email"):
        contact_parts.append(resume_data["email"])
    if resume_data.get("phone"):
        contact_parts.append(resume_data["phone"])

    if contact_parts:
        story.append(Paragraph(" | ".join(contact_parts), body_style))
        story.append(Spacer(1, 12))

    # Summary
    if resume_data.get("summary"):
        story.append(Paragraph("Professional Summary", heading_style))
        story.append(Paragraph(resume_data["summary"], body_style))
        story.append(Spacer(1, 10))

    # Skills
    if resume_data.get("skills"):
        story.append(Paragraph("Skills", heading_style))
        story.append(Paragraph(", ".join(resume_data["skills"]), body_style))
        story.append(Spacer(1, 10))

    # Experience
    if resume_data.get("experience"):
        story.append(Paragraph("Experience", heading_style))
        for exp in resume_data["experience"]:
            role = exp.get("role", "")
            company = exp.get("company", "")
            title_line = " | ".join(part for part in [role, company] if part)
            if title_line:
                story.append(Paragraph(title_line, subheading_style))
            for bullet in exp.get("bullets", []):
                story.append(Paragraph(bullet, bullet_style, bulletText="•"))
            story.append(Spacer(1, 8))

    # Projects
    if resume_data.get("projects"):
        story.append(Paragraph("Projects", heading_style))
        for proj in resume_data["projects"]:
            if proj.get("title"):
                story.append(Paragraph(proj["title"], subheading_style))
            for bullet in proj.get("bullets", []):
                story.append(Paragraph(bullet, bullet_style, bulletText="•"))
            story.append(Spacer(1, 8))

    # Certifications
    if resume_data.get("certifications"):
        story.append(Paragraph("Certifications", heading_style))
        for cert in resume_data["certifications"]:
            story.append(Paragraph(cert, bullet_style, bulletText="•"))
        story.append(Spacer(1, 8))

    # Education
    if resume_data.get("education"):
        story.append(Paragraph("Education", heading_style))
        for edu in resume_data["education"]:
            story.append(Paragraph(edu, bullet_style, bulletText="•"))
        story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer