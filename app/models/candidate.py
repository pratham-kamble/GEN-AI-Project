from pydantic import BaseModel, Field
from typing import List, Optional


class CandidateProfile(BaseModel):
    candidate_id: str
    name: str
    skills: List[str] = Field(default_factory=list)
    experience_years: float = 0
    education: Optional[str] = None
    projects: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    raw_text: str


class ScoreBreakdown(BaseModel):
    required_skills_score: float
    experience_score: float
    projects_score: float
    education_score: float
    additional_skills_score: float
    total_score: float


class MatchResult(BaseModel):
    candidate_id: str
    candidate_name: str
    score: ScoreBreakdown
    matching_skills: List[str]
    missing_skills: List[str]
    explanation: Optional[str] = None