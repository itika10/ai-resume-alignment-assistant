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

    # Build replacement map
    replacement_map = {}
    for item in validation_result.approved_bullets:
        replacement_map[item.original_bullet.strip()] = {
            "approved_bullet": item.approved_bullet,
            "source_section": item.source_section,
        }

    # Replace bullets in experience
    for exp in final_resume.get("experience", []):
        updated_bullets = []
        for bullet in exp.get("bullets", []):
            key = bullet.strip()
            if key in replacement_map:
                updated_bullets.append(replacement_map[key]["approved_bullet"])
            else:
                updated_bullets.append(bullet)
        exp["bullets"] = updated_bullets

    # Replace bullets in projects
    for proj in final_resume.get("projects", []):
        updated_bullets = []
        for bullet in proj.get("bullets", []):
            key = bullet.strip()
            if key in replacement_map:
                updated_bullets.append(replacement_map[key]["approved_bullet"])
            else:
                updated_bullets.append(bullet)
        proj["bullets"] = updated_bullets

    return final_resume