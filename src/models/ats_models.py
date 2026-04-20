from typing import List
from pydantic import BaseModel, Field


class ATSResult(BaseModel):
    alignment_score: int = Field(
        default=0,
        description="Overall alignment score from 0 to 100."
    )
    matched_keywords: List[str] = Field(
        default_factory=list,
        description="Important JD keywords that are already reflected in the resume or validated rewrite."
    )
    missing_keywords: List[str] = Field(
        default_factory=list,
        description="Important JD keywords that are still missing or weakly represented."
    )
    section_warnings: List[str] = Field(
        default_factory=list,
        description="Warnings about missing or weak resume sections relevant to ATS compatibility."
    )
    content_warnings: List[str] = Field(
        default_factory=list,
        description="Warnings about content quality, such as vague bullets or unsupported emphasis."
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Specific suggestions to improve ATS compatibility and resume alignment."
    )