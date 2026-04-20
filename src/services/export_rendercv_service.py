from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any
import sys
import os

import phonenumbers
from phonenumbers import NumberParseException

import yaml


def _build_rendercv_yaml(resume_data: dict[str, Any]) -> dict[str, Any]:
    """
    Convert approved tailored resume dict into a minimal RenderCV YAML structure.
    """
    name = resume_data.get("name") or "Candidate Name"
    email = resume_data.get("email") or None
    phone = (resume_data.get("phone") or "").strip()

    # Validate and format phone number
    digits_only = "".join(ch for ch in phone if ch.isdigit())

    try:
        if not digits_only or len(digits_only) < 10:
            phone = None

        elif len(digits_only) == 10:
            # local number without country code, with work on it later if needed
            phone = None

        else:
            # phone number with country code
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

    summary = resume_data.get("summary") or ""
    skills = resume_data.get("skills") or []
    experience = resume_data.get("experience") or []
    projects = resume_data.get("projects") or []
    certifications = resume_data.get("certifications") or []
    education = resume_data.get("education") or []

    sections: dict[str, list[dict[str, Any] | str]] = {}

    if summary:
        sections["Professional Summary"] = [summary]

    if skills:
        sections["Skills"] = [
            {
                "label": "Technical Skills",
                "details": ", ".join(skills),
            }
        ]

    if experience:
        exp_entries = []
        for exp in experience:
            company = (exp.get("company") or "").strip()
            role = (exp.get("role") or "").strip()
            bullets = exp.get("bullets", []) or []

            # ExperienceEntry requires company and position
            if not company and not role:
                continue

            exp_entries.append(
                {
                    "company": company or "Company",
                    "position": role or "Role",
                    "highlights": bullets,
                }
            )
         
        if exp_entries:
            sections["Experience"] = exp_entries

    if projects:
        project_entries = []
        for proj in projects:
            title = (proj.get("title") or "").strip()
            bullets = proj.get("bullets", []) or []

            if not title and not bullets:
                continue

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

    if education:
        sections["Education"] = [{"bullet": edu} for edu in education if edu]

    cv_block: dict[str, Any] = {
        "name": name,
        "sections": sections,
    }

    if email:
        cv_block["email"] = email

    if phone:
        cv_block["phone"] = phone

    return {
        "cv": cv_block,
        "design": {
            "theme": "classic",
            "page": {
                "size": "us-letter",
                "top_margin": "1.5cm",
                "bottom_margin": "1.5cm",
                "left_margin": "1.8cm",
                "right_margin": "1.8cm",
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

        yaml_path.write_text(yaml_text, encoding="utf-8")

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