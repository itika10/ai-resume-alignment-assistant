"""
Shared date utilities.

normalize_date_to_rendercv:
    Convert common resume date formats into RenderCV-compatible output:
    YYYY-MM-DD, YYYY-MM, YYYY, or "present". Returns None when input cannot
    be parsed.

compute_duration_months:
    Compute whole months between a start and end date string. Both inputs
    are normalized first. "present"/"current"/"now" map to today. Returns
    None when either side cannot be parsed (caller should treat that as
    "long duration / no constraint").
"""

from __future__ import annotations

import re
from datetime import datetime, date
from typing import Optional


def normalize_date_to_rendercv(date_str: Optional[str]) -> Optional[str]:
    """
    Convert common resume date formats into RenderCV-compatible formats:
    - YYYY-MM-DD
    - YYYY-MM
    - YYYY
    - present
    """
    if not date_str:
        return None

    raw = date_str.strip()
    if not raw:
        return None

    lowered = raw.lower()

    if lowered in {"present", "current", "now", "ongoing", "working"}:
        return "present"

    # Normalize uncommon month abbreviations to ones strptime accepts.
    # Examples: "Sept 2018" -> "Sep 2018"
    raw = re.sub(r"\bSept\b\.?", "Sep", raw, flags=re.IGNORECASE)

    # 1) Already valid full ISO date: YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        return raw

    # 2) Already valid year-month: YYYY-MM
    if re.fullmatch(r"\d{4}-\d{2}", raw):
        return raw

    # 3) Year only: YYYY
    if re.fullmatch(r"\d{4}", raw):
        return raw

    # 4) MM/YYYY or M/YYYY
    match = re.fullmatch(r"(\d{1,2})[/-](\d{4})", raw)
    if match:
        month, year = match.groups()
        month = int(month)
        if 1 <= month <= 12:
            return f"{year}-{month:02d}"

    # 5) YYYY/MM or YYYY/M
    match = re.fullmatch(r"(\d{4})[/-](\d{1,2})", raw)
    if match:
        year, month = match.groups()
        month = int(month)
        if 1 <= month <= 12:
            return f"{year}-{month:02d}"

    # 6) MM/DD/YYYY or M/D/YYYY
    match = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", raw)
    if match:
        month, day, year = match.groups()
        month = int(month)
        day = int(day)
        try:
            dt = datetime(int(year), month, day)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # 7) YYYY/M/D or YYYY/MM/DD
    match = re.fullmatch(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", raw)
    if match:
        year, month, day = match.groups()
        month = int(month)
        day = int(day)
        try:
            dt = datetime(int(year), month, day)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # 8) Month name formats like "Apr 2021" or "April 2021"
    for fmt in ("%b %Y", "%B %Y"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m")
        except ValueError:
            pass

    # 9) Month name + day + year formats
    for fmt in ("%b %d %Y", "%B %d %Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None


def _to_date(normalized: str) -> Optional[date]:
    """
    Convert a normalized RenderCV-style date string into a python date.
    Day defaults to 1 when missing; month defaults to 1 when missing.
    """
    if normalized == "present":
        return date.today()

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized):
        return datetime.strptime(normalized, "%Y-%m-%d").date()

    if re.fullmatch(r"\d{4}-\d{2}", normalized):
        return datetime.strptime(normalized + "-01", "%Y-%m-%d").date()

    if re.fullmatch(r"\d{4}", normalized):
        return datetime.strptime(normalized + "-01-01", "%Y-%m-%d").date()

    return None


def compute_duration_months(
    start_date: Optional[str],
    end_date: Optional[str],
) -> Optional[int]:
    """
    Compute whole months between start_date and end_date.

    - Both inputs are normalized using normalize_date_to_rendercv.
    - "present"/"current"/"now" on the end resolves to today.
    - Returns None if either date cannot be parsed. Callers should treat None
      as "no constraint" (i.e., do not enforce the short-duration rule).
    - Returns 0 for negative or zero spans (defensive).
    """
    norm_start = normalize_date_to_rendercv(start_date)
    norm_end = normalize_date_to_rendercv(end_date)

    if not norm_start or not norm_end:
        return None

    start = _to_date(norm_start)
    end = _to_date(norm_end)

    if start is None or end is None:
        return None

    months = (end.year - start.year) * 12 + (end.month - start.month)
    return max(months, 0)
