from typing import List
from pydantic import BaseModel, Field

class SkillMappingItem(BaseModel):
    jd_skill: str = Field(default="", description="Skill or keyword extracted from the job description")
    resume_evidence: str = Field(default="", description="Matching skill, project, experience, or phrase from the resume.")
    relation: str = Field(default="", description="Relationship type. Use one of: exact_match, category_match, adjacent_framework, concept_match, partial_match, no_match.")
    safe_to_add: bool = Field(default=False, description="Whether the JD term can be safely reflected in the tailored resume without misrepresenting experience.")
    suggested_resume_phrases: str = Field(default="", description="A safe phrase that can be used later in resume rewriting.")
    reason: str = Field(default="", description="A safe phrase that can be used later in resume rewriting.")

class SkillMappingResult(BaseModel):
    mappings: List[SkillMappingItem] = Field(default_factory=list, description="List of skill mappings between the job description and the resume.")
    matched_skills: List[str] = Field(default_factory=list, description="List of skills that were matched between the job description and the resume.")
    missing_skills: List[str] = Field(default_factory=list, description="List of skills that were present in the job description but not found in the resume.")
