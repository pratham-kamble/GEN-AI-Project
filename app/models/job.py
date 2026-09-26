from pydantic import BaseModel, Field
from typing import List


class JobDescriptionInput(BaseModel):
    title: str
    raw_text: str


class JobRequirements(BaseModel):
    title: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    min_experience_years: float = 0
    education_requirements: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    raw_text: str