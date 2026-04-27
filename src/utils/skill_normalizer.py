"""
Skill list utilities.

dedupe_skills:
    Case-insensitive deduplication that preserves the original casing of the
    first occurrence of each skill and trims whitespace.

    Example:
        ["AWS", "aws", "  Python ", "python", "SQL"]
        -> ["AWS", "Python", "SQL"]
"""

from typing import Iterable, List


def dedupe_skills(skills: Iterable[str]) -> List[str]:
    seen_lower = set()
    deduped: List[str] = []

    for raw in skills or []:
        if raw is None:
            continue

        cleaned = str(raw).strip()
        if not cleaned:
            continue

        key = cleaned.lower()
        if key in seen_lower:
            continue

        seen_lower.add(key)
        deduped.append(cleaned)

    return deduped
