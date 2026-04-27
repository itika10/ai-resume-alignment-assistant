from copy import deepcopy


def build_approved_tailored_resume(parsed_resume, rewrite_result, validation_result):
    """
    Build final approved tailored resume using:
    - parsed_resume as base
    - approved summary from validation
    - approved bullet replacements from validation
    - highlighted skills from rewrite_result
    """
    final_resume = deepcopy(parsed_resume.model_dump())

    # Apply approved summary
    if validation_result.approved_summary:
        final_resume["summary"] = validation_result.approved_summary

    # Merge skills with skills_to_highlight
    existing_skills = set(final_resume.get("skills", []))
    highlighted_skills = set(rewrite_result.skills_to_highlight or [])
    final_resume["skills"] = sorted(existing_skills | highlighted_skills)

    # Build section-aware replacement maps
    experience_replacements = {}
    project_replacements = {}

    # Replace bullets in experience and projects based on validation results
    for item in validation_result.approved_bullets:
        original = (item.original_bullet or "").strip()
        approved = (item.approved_bullet or "").strip()
        source_section = (item.source_section or "").strip().lower()

        if not original or not approved:
            continue

        if source_section == "experience":
            experience_replacements[original] = approved
        elif source_section == "projects":
            project_replacements[original] = approved
        else:
            # fallback: if section is missing or unexpected,
            # do not force replacement across all sections
            continue

    # Replace bullets in experience
    for exp in final_resume.get("experience", []):
        updated_bullets = []
        for bullet in exp.get("bullets", []):
            key = (bullet or "").strip()
            updated_bullets.append(experience_replacements.get(key, bullet))
        exp["bullets"] = updated_bullets

    # Replace bullets in projects
    for proj in final_resume.get("projects", []):
        updated_bullets = []
        for bullet in proj.get("bullets", []):
            key = (bullet or "").strip()
            updated_bullets.append(project_replacements.get(key, bullet))
        proj["bullets"] = updated_bullets

    return final_resume