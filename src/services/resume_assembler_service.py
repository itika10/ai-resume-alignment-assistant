from copy import deepcopy
from typing import Any, Dict, List

from src.services.skill_categorizer_service import categorize_skills
from src.services.bullet_condenser_service import condense_bullets
from src.utils.skill_normalizer import dedupe_skills


def _key_experience(role: str, company: str) -> str:
    return f"{(role or '').strip().lower()}|{(company or '').strip().lower()}"


def _key_project(title: str) -> str:
    return (title or "").strip().lower()


def _apply_condensed_experiences(experiences: List[Dict[str, Any]], condensed) -> None:
    """
    Override experience bullets with condensed bullets.
    Match by role+company (case-insensitive); fall back to positional match
    if no exact key match is found.
    """
    if not condensed:
        return

    by_key = {
        _key_experience(c.role, c.company): list(c.bullets or [])
        for c in condensed
        if (c.role or c.company)
    }

    for idx, exp in enumerate(experiences):
        key = _key_experience(exp.get("role", ""), exp.get("company", ""))
        if key in by_key:
            exp["bullets"] = by_key[key]
        elif idx < len(condensed):
            exp["bullets"] = list(condensed[idx].bullets or [])


def _apply_condensed_projects(projects: List[Dict[str, Any]], condensed) -> None:
    """
    Override project bullets and descriptions with condensed output.
    Match by title (case-insensitive); fall back to positional match.
    """
    if not condensed:
        return

    by_key = {
        _key_project(c.title): c
        for c in condensed
        if (c.title or "").strip()
    }

    for idx, proj in enumerate(projects):
        key = _key_project(proj.get("title", ""))
        match = by_key.get(key)
        if match is None and idx < len(condensed):
            match = condensed[idx]

        if match is None:
            continue

        proj["bullets"] = list(match.bullets or [])
        if match.description:
            proj["description"] = match.description


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
    - approved bullet replacements from validation (in-place substitution)
    - bullet condenser to enforce bullet limits and generate project descriptions
    - skill deduplication and LLM-based categorization
    """
    final_resume = deepcopy(parsed_resume.model_dump())

    # 1) Apply approved summary
    if validation_result.approved_summary:
        final_resume["summary"] = validation_result.approved_summary

    # 2) Apply approved bullet substitutions in-place
    experience_replacements = {}
    project_replacements = {}

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
            continue

    for exp in final_resume.get("experience", []):
        updated_bullets = []
        for bullet in exp.get("bullets", []):
            key = (bullet or "").strip()
            updated_bullets.append(experience_replacements.get(key, bullet))
        exp["bullets"] = updated_bullets

    for proj in final_resume.get("projects", []):
        updated_bullets = []
        for bullet in proj.get("bullets", []):
            key = (bullet or "").strip()
            updated_bullets.append(project_replacements.get(key, bullet))
        proj["bullets"] = updated_bullets

    # 3) Condense bullets and generate project descriptions
    condensation = condense_bullets(
        experiences=final_resume.get("experience", []) or [],
        projects=final_resume.get("projects", []) or [],
        parsed_jd=parsed_jd,
        openai_api_key=openai_api_key,
    )
    _apply_condensed_experiences(final_resume.get("experience", []) or [], condensation.experiences)
    _apply_condensed_projects(final_resume.get("projects", []) or [], condensation.projects)

    # 4) Skills: dedupe + categorize
    merged_skills = list(final_resume.get("skills", []) or []) + list(
        rewrite_result.skills_to_highlight or []
    )
    deduped = dedupe_skills(merged_skills)
    final_resume["skills"] = deduped

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

    return final_resume
