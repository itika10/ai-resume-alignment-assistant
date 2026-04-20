from typing import List
from pydantic import BaseModel, Field

class RewrittenBulletItem(BaseModel):
    original_bullet: str = Field(default="", description="Original bullet point from the resume.")
    rewritten_bullet: str = Field(default="", description="Tailored rewritten bullet point that better aligns with the job description.")
    source_section: str = Field(default="", description ="Section of the resume where the original bullet was found (e.g., Experience, Projects).")
    reason: str = Field(default="", description="Brief explanation of why the bullet was rewritten and how it better matches the job description.")

class RewrittenResult(BaseModel):
    tailored_summary: str = Field(default="", description="Tailored professional summary aligned to JD.")
    rewritten_bullets: List[RewrittenBulletItem] = Field(default_factory=list, description="List of rewritten bullet points with explanations.")
    skills_to_highlight: List[str] = Field(default_factory=list, description="List of key skills that should be emphasized in the tailored resume based on the JD.")
