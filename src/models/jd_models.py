from typing import List
from pydantic import BaseModel, Field

class JobDescriptionData(BaseModel):
    job_title: str = Field(default="", description="title of the job position.")
    required_skills: List[str] = Field(default_factory=list, description="Skills or tools explicitly required for the job.")
    preferred_skills: List[str] = Field(default_factory=list, description="Skills or tools listed as preferred, good to have, or nice to have.")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities or duties mentioned in the job description.")
    keywords: List[str] = Field(default_factory=list, description="Important ATS-relevant keywords and phrases from the JD.")