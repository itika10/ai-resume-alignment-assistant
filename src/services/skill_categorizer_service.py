"""
Skill categorizer service.

Wraps the categorizer chain with a safe fallback so the assembler always
receives a usable SkillCategorizationResult, even when the LLM call fails or
returns an empty/invalid structure.
"""

from typing import List

from src.chains.skill_categorizer_chain import get_skill_categorizer_chain
from src.models.resume_models import SkillCategorizationResult, SkillCategory


def _build_experience_snapshot(parsed_resume) -> str:
    """
    Build a tiny role/company-only snapshot for domain context.
    Bullets are intentionally excluded to keep token usage low.
    """
    lines = []
    for exp in (parsed_resume.experience or [])[:6]:
        role = (exp.role or "").strip()
        company = (exp.company or "").strip()
        if role or company:
            lines.append(f"- {role} at {company}".strip())
    return "\n".join(lines) if lines else "(no experience provided)"


def _build_jd_signals(parsed_jd) -> str:
    """
    Compact JD signal block: title + required + preferred + keywords.
    """
    parts = []
    title = (parsed_jd.job_title or "").strip()
    if title:
        parts.append(f"Job title: {title}")

    if parsed_jd.required_skills:
        parts.append("Required skills: " + ", ".join(parsed_jd.required_skills))

    if parsed_jd.preferred_skills:
        parts.append("Preferred skills: " + ", ".join(parsed_jd.preferred_skills))

    if parsed_jd.keywords:
        parts.append("Keywords: " + ", ".join(parsed_jd.keywords))

    return "\n".join(parts) if parts else "(no JD signals)"


def _fallback_result(skills: List[str]) -> SkillCategorizationResult:
    """
    Safety net: if the LLM call fails for any reason, return a single
    'Technical Skills' category so exporters can still render the section.
    """
    if not skills:
        return SkillCategorizationResult(skill_categories=[])
    return SkillCategorizationResult(
        skill_categories=[SkillCategory(category="Technical Skills", items=list(skills))]
    )


def categorize_skills(
    skills: List[str],
    parsed_resume,
    parsed_jd,
    openai_api_key: str,
) -> SkillCategorizationResult:
    """
    Group the given (already deduped) skill list into resume-friendly categories.

    On any error or empty result, returns a single 'Technical Skills' category
    containing all input skills.
    """
    if not skills:
        return SkillCategorizationResult(skill_categories=[])

    try:
        chain = get_skill_categorizer_chain(openai_api_key=openai_api_key)
        result = chain.invoke(
            {
                "skills": ", ".join(skills),
                "summary": (parsed_resume.summary or "").strip() or "(no summary provided)",
                "experience_snapshot": _build_experience_snapshot(parsed_resume),
                "jd_signals": _build_jd_signals(parsed_jd),
            }
        )

        # Defensive: ensure we got something usable
        if not result or not result.skill_categories:
            return _fallback_result(skills)

        # Drop any empty categories the model may have returned
        cleaned = [
            SkillCategory(
                category=(c.category or "").strip(),
                items=[(item or "").strip() for item in (c.items or []) if (item or "").strip()],
            )
            for c in result.skill_categories
            if (c.category or "").strip()
        ]
        cleaned = [c for c in cleaned if c.items]

        if not cleaned:
            return _fallback_result(skills)

        return SkillCategorizationResult(skill_categories=cleaned)

    except Exception:
        return _fallback_result(skills)
