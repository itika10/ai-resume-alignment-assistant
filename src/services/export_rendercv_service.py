from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any
import sys
import os
import yaml
from datetime import datetime
from urllib.parse import urlparse

import phonenumbers
from phonenumbers import NumberParseException

def _format_phone_for_rendercv(phone:str | None) -> str | None:
    phone = (phone or "").strip()
    digits_only = "".join(ch for ch in phone if ch.isdigit())

    try:
        if not digits_only or len(digits_only) < 10:
            return None

        elif len(digits_only) == 10:
            # RenderCV requires country code, so skip local-only numbers for now
            return None

       
        parsed = phonenumbers.parse("+" + digits_only, None)

        if phonenumbers.is_valid_number(parsed):
            phone = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
        else:
            phone = None

    except NumberParseException:
        phone = None

    return phone

def _format_experience_company(exp: dict[str, Any]) -> str:
    company = (exp.get("company") or "").strip()
    client = (exp.get("client") or "").strip()

    if company and client:
        return f"{company} (Client: {client})"
    
    return company or "Company"

def _format_education_entries(education: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries = []

    for edu in education:
        degree = (edu.get("degree") or "").strip()
        institution = (edu.get("institution") or "").strip()
        location = (edu.get("location") or "").strip()
        graduation_date = (edu.get("graduation_date") or "").strip()

        if not degree and not institution:
            continue

        entry: dict[str, Any] = {
            "institution": institution or "Institution",
            "area": degree or "Degree",
        }

        if location:
            entry["location"] = location

        if graduation_date:
            entry["end_date"] = graduation_date

        entries.append(entry)

    return entries

def _extract_username_from_url(url: str) -> str:
    if not url:
        return ""

    parsed = urlparse(url)
    path = (parsed.path or "").strip("/")

    if not path:
        return ""

    # take first path segment
    return path.split("/")[0].strip()

def _format_socials(socials: list[dict[str, Any]]) -> list[dict[str, Any]]:
    formatted = []

    for item in socials:
        label = (item.get("label") or "").strip()
        url = (item.get("url") or "").strip()

        if not label:
            continue
        else:
            if label.lower() in {"linkedin", "linkedin.com"}:
                label = "LinkedIn"
            if label.lower() in {"github", "github.com"}:
                label = "GitHub"
            if label.lower() in {"twitter", "twitter.com"}:
                label = "Twitter"
            if label.lower() in {"portfolio", "website", "personal website"}:
                label = "Portfolio"
            if label.lower() in {"facebook", "facebook.com"}:
                label = "Facebook"
            if label.lower() in {"instagram", "instagram.com"}:
                label = "Instagram"

            username = _extract_username_from_url(url)
            if not username:
                continue

            formatted.append(
                {
                    "network": label,
                    "username": username
                }
            )

    return formatted

import re
from datetime import datetime


def _normalize_rendercv_date(date_str: str | None) -> str | None:
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

    if lowered in {"present", "current", "now"}:
        return "present"

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

    # 5) YYYY/MM or YYYY/M or YYYY-MM with single-digit month
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

    # 8) Month name formats like Apr 2021, April 2021
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
    
def _build_rendercv_yaml(resume_data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert approved tailored resume dict into a minimal RenderCV YAML structure.
    """

    # Header info
    name = resume_data.get("name") or "Candidate Name"
    email = resume_data.get("email") or None
    phone = _format_phone_for_rendercv(resume_data.get("phone"))
    location = (resume_data.get("location") or "").strip()
    socials = resume_data.get("socials") or []

    # Body sections
    summary = resume_data.get("summary") or ""
    skills = resume_data.get("skills") or []
    skill_categories = resume_data.get("skill_categories") or []
    experience = resume_data.get("experience") or []
    projects = resume_data.get("projects") or []
    certifications = resume_data.get("certifications") or []
    education = resume_data.get("education") or []

    sections: dict[str, list[dict[str, Any] | str]] = {}

    if summary:
        sections["Professional Summary"] = [summary]

    # Prefer categorized skills; fall back to a single 'Technical Skills' entry.
    if skill_categories:
        category_entries: list[dict[str, Any]] = []
        for cat in skill_categories:
            label = (cat.get("category") or "").strip()
            items = [str(i).strip() for i in (cat.get("items") or []) if str(i).strip()]
            if not label or not items:
                continue
            category_entries.append(
                {
                    "label": label,
                    "details": ", ".join(items),
                }
            )

        if category_entries:
            sections["Skills"] = category_entries
        elif skills:
            clean_skills = [str(skill).strip() for skill in skills if str(skill).strip()]
            if clean_skills:
                sections["Skills"] = [
                    {
                        "label": "Technical Skills",
                        "details": ", ".join(clean_skills),
                    }
                ]
    elif skills:
        clean_skills = [str(skill).strip() for skill in skills if str(skill).strip()]
        if clean_skills:
            sections["Skills"] = [
                {
                    "label": "Technical Skills",
                    "details": ", ".join(clean_skills),
                }
            ]

    if experience:
        exp_entries = []

        for exp in experience:
            company = _format_experience_company(exp)
            role = (exp.get("role") or "").strip()
            bullets = [str(b).strip() for b in (exp.get("bullets") or []) if str(b).strip()]
            exp_location = (exp.get("location") or "").strip()
            start_date = _normalize_rendercv_date(exp.get("start_date"))
            end_date = _normalize_rendercv_date(exp.get("end_date"))

            # ExperienceEntry requires company and position
            if not company and not role:
                continue

            entry: dict[str, Any] = {
                "company": company,
                "position": role or "Role",
                "highlights": bullets,
            }

            if exp_location:
                entry["location"] = exp_location

            if start_date:
                entry["start_date"] = start_date

            if end_date:
                entry["end_date"] = end_date

            exp_entries.append(entry)
         
        if exp_entries:
            sections["Experience"] = exp_entries

    if projects:
        project_entries = []

        for proj in projects:
            title = (proj.get("title") or "").strip()
            bullets = [str(b).strip() for b in (proj.get("bullets") or []) if str(b).strip()]
            tech_stack = [str(t).strip() for t in (proj.get("tech_stack") or []) if str(t).strip()]

            if not title and not bullets and not tech_stack:
                continue

            if tech_stack:
                bullets = bullets + [f"Tech Stack: {', '.join(tech_stack)}"]

            project_entries.append(
                {
                    "name": title or "Project",
                    "highlights": bullets,
                }
            )

        if project_entries:
            sections["Projects"] = project_entries

    if certifications:
        sections["Certifications"] = [{"bullet": cert} for cert in certifications if cert]

    education_entries = _format_education_entries(education)
    if education:
        sections["Education"] = education_entries

    # Construct the final RenderCV YAML structure with header and sections
    cv_block: dict[str, Any] = {
        "name": name,
        "sections": sections,
    }

    if location:
        cv_block["location"] = location

    if email:
        cv_block["email"] = email
        
    if phone:
        cv_block["phone"] = phone

    formatted_socials = _format_socials(socials)
    if formatted_socials:
        cv_block["social_networks"] = formatted_socials

    return {
        "cv": cv_block,
        "design": {
            "theme": "classic",
            "page": {
                "size": "us-letter",
                "top_margin": "1.5cm",
                "bottom_margin": "1.5cm",
                "left_margin": "1.6cm",
                "right_margin": "1.6cm",
            },
        },
    }

   
def generate_resume_pdf_rendercv(resume_data: dict[str, Any]) -> bytes:
    """
    Generate a polished PDF using RenderCV CLI.
    Returns PDF bytes.
    """
    if shutil.which("python") is None:
        raise RuntimeError("Python executable not found in PATH.")

    rendercv_yaml = _build_rendercv_yaml(resume_data)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        yaml_path = tmp_path / "tailored_resume.yaml"

        yaml_text = yaml.safe_dump(
            rendercv_yaml,
            sort_keys=False,
            allow_unicode=True,
        )

        with yaml_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(rendercv_yaml, f, sort_keys=False, allow_unicode=True)

        cmd = [
            sys.executable,
            "-m",
            "rendercv",
            "render",
            str(yaml_path),
            # "--quiet",
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=tmp_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",   # important for Windows / Unicode safety
                check=False,
                env={
                    **os.environ,
                    "PYTHONIOENCODING": "utf-8",
                    "PYTHONUTF8": "1",
                }
            )
        except FileNotFoundError as e:
            raise RuntimeError(
                f"Subprocess launch failed.\n"
                f"Python executable: {sys.executable}\n"
                f"Command: {cmd}\n"
                f"Original error: {e}"
            )
        

        if result.returncode != 0:
            raise RuntimeError(
                "RenderCV PDF generation failed.\n"
                f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            )

        output_dir = tmp_path / "rendercv_output"
        pdf_files = list(output_dir.glob("*.pdf"))

        if not pdf_files:
            raise RuntimeError(
                "RenderCV ran successfully but no PDF file was found in rendercv_output."
            )

        pdf_path = pdf_files[0]
        return pdf_path.read_bytes()