"""
Bullet condenser service.

Computes per-section bullet counts using duration_months, then calls the
condenser chain to select/combine bullets and produce project descriptions.

Falls back to verbatim truncation when the LLM call fails or returns
mismatched data.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.chains.bullet_condenser_chain import get_bullet_condenser_chain
from src.models.resume_models import (
    BulletCondensationResult,
    CondensedExperience,
    CondensedProject,
)
from src.utils.date_utils import compute_duration_months


SHORT_DURATION_BULLET_COUNT = 1
LONG_DURATION_BULLET_COUNT = 3
SHORT_DURATION_THRESHOLD_MONTHS = 12


def _bullet_count_for_duration(duration_months: Optional[int]) -> int:
    """
    Apply the bullet-count rule:
      - duration < 12 months         -> 1 bullet
      - duration >= 12 months        -> 3 bullets
      - duration unknown (None)      -> 3 bullets (no constraint)
    """
    if duration_months is None:
        return LONG_DURATION_BULLET_COUNT
    if duration_months < SHORT_DURATION_THRESHOLD_MONTHS:
        return SHORT_DURATION_BULLET_COUNT
    return LONG_DURATION_BULLET_COUNT


def _build_jd_signals(parsed_jd) -> str:
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


def _build_experience_payloads(experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    payloads = []
    for exp in experiences:
        duration = compute_duration_months(exp.get("start_date"), exp.get("end_date"))
        payloads.append(
            {
                "role": (exp.get("role") or "").strip(),
                "company": (exp.get("company") or "").strip(),
                "duration_months": duration,
                "bullet_count": _bullet_count_for_duration(duration),
                "input_bullets": [
                    str(b).strip() for b in (exp.get("bullets") or []) if str(b).strip()
                ],
            }
        )
    return payloads


def _build_project_payloads(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    payloads = []
    for proj in projects:
        duration = compute_duration_months(proj.get("start_date"), proj.get("end_date"))
        payloads.append(
            {
                "title": (proj.get("title") or "").strip(),
                "duration_months": duration,
                "bullet_count": _bullet_count_for_duration(duration),
                "existing_description": (proj.get("description") or "").strip(),
                "tech_stack": [
                    str(t).strip() for t in (proj.get("tech_stack") or []) if str(t).strip()
                ],
                "input_bullets": [
                    str(b).strip() for b in (proj.get("bullets") or []) if str(b).strip()
                ],
            }
        )
    return payloads


def _truncate_bullets(bullets: List[str], count: int) -> List[str]:
    cleaned = [str(b).strip() for b in (bullets or []) if str(b).strip()]
    return cleaned[: max(count, 0)]


def _fallback_result(
    experience_payloads: List[Dict[str, Any]],
    project_payloads: List[Dict[str, Any]],
) -> BulletCondensationResult:
    """
    Safe fallback when the chain fails: take the first N bullets verbatim.
    Use any existing description for projects, or leave empty.
    """
    experiences = [
        CondensedExperience(
            role=p["role"],
            company=p["company"],
            bullets=_truncate_bullets(p["input_bullets"], p["bullet_count"]),
        )
        for p in experience_payloads
    ]
    projects = [
        CondensedProject(
            title=p["title"],
            description=p.get("existing_description") or "",
            bullets=_truncate_bullets(p["input_bullets"], p["bullet_count"]),
        )
        for p in project_payloads
    ]
    return BulletCondensationResult(experiences=experiences, projects=projects)


def _enforce_counts(
    result: BulletCondensationResult,
    experience_payloads: List[Dict[str, Any]],
    project_payloads: List[Dict[str, Any]],
) -> BulletCondensationResult:
    """
    Defensive: if the model ignored the bullet_count instruction, trim the
    output to the requested count without padding.
    """
    fixed_experiences: List[CondensedExperience] = []
    for idx, condensed in enumerate(result.experiences or []):
        target = experience_payloads[idx]["bullet_count"] if idx < len(experience_payloads) else LONG_DURATION_BULLET_COUNT
        bullets = _truncate_bullets(condensed.bullets, target)
        fixed_experiences.append(
            CondensedExperience(
                role=condensed.role,
                company=condensed.company,
                bullets=bullets,
            )
        )

    fixed_projects: List[CondensedProject] = []
    for idx, condensed in enumerate(result.projects or []):
        target = project_payloads[idx]["bullet_count"] if idx < len(project_payloads) else LONG_DURATION_BULLET_COUNT
        bullets = _truncate_bullets(condensed.bullets, target)
        # Light defensive trim on description length: keep it readable but not enormous.
        description = (condensed.description or "").strip()
        if len(description.split()) > 35:
            description = " ".join(description.split()[:35]).rstrip(",;:") + "..."
        fixed_projects.append(
            CondensedProject(
                title=condensed.title,
                description=description,
                bullets=bullets,
            )
        )

    return BulletCondensationResult(experiences=fixed_experiences, projects=fixed_projects)


def condense_bullets(
    experiences: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    parsed_jd,
    openai_api_key: str,
) -> BulletCondensationResult:
    """
    Condense bullets and generate project descriptions.

    Inputs are already-validated experience and project dicts (the post-
    substitution form produced by the assembler). Returns a structured
    BulletCondensationResult; on failure, returns a verbatim-truncated
    fallback so the resume always renders.
    """
    experience_payloads = _build_experience_payloads(experiences)
    project_payloads = _build_project_payloads(projects)

    if not experience_payloads and not project_payloads:
        return BulletCondensationResult()

    try:
        chain = get_bullet_condenser_chain(openai_api_key=openai_api_key)
        result = chain.invoke(
            {
                "jd_signals": _build_jd_signals(parsed_jd),
                "experiences": json.dumps(experience_payloads, indent=2),
                "projects": json.dumps(project_payloads, indent=2),
            }
        )
        if not result:
            return _fallback_result(experience_payloads, project_payloads)
        return _enforce_counts(result, experience_payloads, project_payloads)
    except Exception:
        return _fallback_result(experience_payloads, project_payloads)
