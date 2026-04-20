from typing import List
from pydantic import BaseModel, Field

class ValidationIssue(BaseModel):
    issue_type: str = Field(
        default="",
        description="Type of issue. Use one of: unsupported_claim, overstatement, unsafe_tool_inference, ai_irrelevance, temporal_mismatch, meaning_drift."
    )
    severity: str = Field(
        default="",
        description="Severity level. Use one of: low, medium, high."
    )
    original_text: str = Field(
        default="",
        description="Original resume text related to the issue, if applicable."
    )
    rewritten_text: str = Field(
        default="",
        description="Rewritten text that triggered the issue."
    )
    reason: str = Field(
        default="",
        description="Short explanation of why this is a problem."
    )
    suggested_fix: str = Field(
        default="",
        description="A safer corrected version or recommendation."
    )

class ApprovedBulletItem(BaseModel):
    source_section: str = Field(default="", description="Section the bullet belongs to.")
    original_bullet: str = Field(default="", description="Original bullet from the resume.")
    approved_bullet: str = Field(default="", description="Safe approved rewritten bullet.")


class ValidationResult(BaseModel):
    is_valid: bool = Field(
        default=True,
        description="Whether the tailored rewrite is acceptable overall."
    )
    issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="List of detected validation issues."
    )
    approved_summary: str = Field(
        default="",
        description="Validated version of the tailored summary, possibly corrected."
    )
    approved_bullets: List[ApprovedBulletItem] = Field(
        default_factory=list,
        description="Validated rewritten bullets that are safe to use."
    )