from copy import deepcopy

from src.services.skill_categorizer_service import categorize_skills
from src.utils.skill_normalizer import dedupe_skills


def build_approved_tailored_resume(
    parsed_resume,
    parsed_jd,
    rewrite_result,
    validation_result,
    openai_api_key: str,
):
    """
    Build final approved tailored resume using:
    - parsed_resume as base
    - approved summary from validation
    - approved bullet replacements from validation
    - highlighted skills from rewrite_result, deduplicated and case-normalized
    - LLM-generated skill categories grouped by domain/JD relevance
    """
    final_resume = deepcopy(parsed_resume.model_dump())

    # Apply approved summary
    if validation_result.approved_summary:
        final_resume["summary"] = validation_result.approved_summary

    # Merge skills (existing + highlighted) and normalize
    merged_skills = list(final_resume.get("skills", []) or []) + list(
        rewrite_result.skills_to_highlight or []
    )
    deduped = dedupe_skills(merged_skills)
    final_resume["skills"] = deduped

    # Categorize skills via LLM (with safe fallback inside the service)
    categorization = categorize_skills(
        skills=deduped,
        parsed_resume=parsed_resume,
        parsed_jd=parsed_jd,
        openai_api_key=openai_api_key,
    )
    final_resume["skill_categories"] = [
        {"category": c.category, "items": list(c.items)}
        for c in categorization.skill_categories
    ]

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
