from typing import List, Optional
from pydantic import BaseModel, Field

class ExperienceItem(BaseModel):
    role: str = Field(default="", description="job title or role.")
    company: str = Field(default="", description="name of the company or organization.")
    bullets: List[str] = Field(default_factory=list, description="list of bullet points describing the responsibilities and achievements in this role.")

class ProjectItem(BaseModel):
    title: str = Field(default="", description="title of the project.")
    bullets: List[str] = Field(default_factory=list, description="list of bullet points describing the project and the contributions.")

class ResumeData(BaseModel):
    name: str = Field(default="", description="full name")
    email: Optional[str] = Field(default=None, description="email address")
    phone: Optional[str] = Field(default=None, description="phone number")
    summary: Optional[str] = Field(default="", description="brief summary or objective statement")
    skills: List[str] = Field(default_factory=list, description="list of skills")
    experience: List[ExperienceItem] = Field(default_factory=list, description="list of work experience items, each containing role, company, and bullet points.")
    projects: List[ProjectItem] = Field(default_factory=list, description="list of project items, each containing a title and bullet points describing the project.")
    certifications: List[str] = Field(default_factory=list, description="list of certifications obtained")
    education: List[str] = Field(default_factory=list, description="Educational background.")
