from typing import List, Optional
from pydantic import BaseModel, Field

class SocialLink(BaseModel):
    label: str = Field(default="", description="platform name such as LinkedIn or GitHub.")
    url: str = Field(default="", description="full public URL for the profile.")

class SkillCategory(BaseModel):
    category: str = Field(default="", description="skill group name such as Programming, AI / Generative AI, Backend, Tools, or Cloud.")
    items: List[str] = Field(default_factory=list, description="list of skills belonging to this category.")

class SkillCategorizationResult(BaseModel):
    skill_categories: List[SkillCategory] = Field(
        default_factory=list,
        description="ordered list of skill categories with their items, produced by the skill categorizer chain.",
    )

class ExperienceItem(BaseModel):
    role: str = Field(default="", description="job title or role.")
    company: str = Field(default="", description="name of the company or organization.")
    client: Optional[str] = Field(default=None, description="client name if this role was performed for a client through a consulting company.")
    location: Optional[str] = Field(default=None, description="job location such as city, province/state, and country, or country only.")
    start_date: Optional[str] = Field(default=None, description="start date in a readable format such as 04/2021.")
    end_date: Optional[str] = Field(default=None, description="end date in a readable format such as 03/2021 or Present.")
    bullets: List[str] = Field(default_factory=list, description="list of bullet points describing responsibilities and achievements in this role.")

class ProjectItem(BaseModel):
    title: str = Field(default="", description="title of the project.")
    description: Optional[str] = Field(
        default=None,
        description="short header sentence summarizing what the project does, shown above the bullets.",
    )
    bullets: List[str] = Field(default_factory=list, description="list of bullet points describing the project and the contributions.")
    tech_stack: List[str] = Field(default_factory=list, description="optional list of technologies used in the project.")
    start_date: Optional[str] = Field(default=None, description="start date if shown in the resume, e.g. 01/2023.")
    end_date: Optional[str] = Field(default=None, description="end date if shown in the resume, e.g. 03/2024 or Present.")

class EducationItem(BaseModel):
    degree: str = Field(
        default="",
        description="short degree label such as B.Tech, PhD, M.Sc, BA. Avoid the full long form when an abbreviation is present.",
    )
    area: Optional[str] = Field(
        default=None,
        description="field of study such as Computer Science, Mathematics, Mechanical Engineering.",
    )
    institution: str = Field(default="", description="name of the institution.")
    location: Optional[str] = Field(default=None, description="location of the institution if available.")
    start_date: Optional[str] = Field(default=None, description="start date if shown, e.g. 09/2018.")
    end_date: Optional[str] = Field(default=None, description="end or graduation date if shown, e.g. 05/2023 or 2023.")

class CondensedExperience(BaseModel):
    role: str = Field(default="", description="role for the experience being condensed; used to match back to the source experience.")
    company: str = Field(default="", description="company for the experience being condensed; used to match back to the source experience.")
    bullets: List[str] = Field(default_factory=list, description="condensed bullets for this experience.")

class CondensedProject(BaseModel):
    title: str = Field(default="", description="project title; used to match back to the source project.")
    description: str = Field(default="", description="single-sentence project summary, max 25 words.")
    bullets: List[str] = Field(default_factory=list, description="condensed bullets for this project.")

class BulletCondensationResult(BaseModel):
    experiences: List[CondensedExperience] = Field(default_factory=list, description="condensed experiences in the same order as the input.")
    projects: List[CondensedProject] = Field(default_factory=list, description="condensed projects in the same order as the input.")

class ResumeData(BaseModel):
    name: str = Field(default="", description="full name")
    email: Optional[str] = Field(default=None, description="email address")
    phone: Optional[str] = Field(default=None, description="phone number")
    location: Optional[str] = Field(default=None, description="primary contact location shown in the resume header")
    socials: List[SocialLink] = Field(default_factory=list, description="list of social or portfolio links such as LinkedIn and GitHub")
    summary: Optional[str] = Field(default="", description="brief summary or objective statement")
    skills: List[str] = Field(default_factory=list, description="list of skills")
    skill_categories: List[SkillCategory] = Field(default_factory=list, description="structured skill groups for improved formatting and future LLM-based categorization")
    experience: List[ExperienceItem] = Field(default_factory=list, description="list of work experience items, each containing role, company, and bullet points.")
    projects: List[ProjectItem] = Field(default_factory=list, description="list of project items, each containing a title and bullet points describing the project.")
    certifications: List[str] = Field(default_factory=list, description="list of certifications obtained")
    education: List[EducationItem] = Field(default_factory=list, description="educational background")
