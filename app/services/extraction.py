import json
from groq import Groq

from app.config import settings
from app.models.job import JobRequirements
from app.models.candidate import CandidateProfile
from app.utils.exceptions import DocumentProcessingError

client = Groq(api_key=settings.groq_api_key)


def _call_llm_json(prompt: str) -> dict:
    """Calls the LLM and parses its response as JSON. Raises on failure."""
    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise information-extraction engine. "
                        "Respond with ONLY valid JSON, no markdown fences, no preamble."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise DocumentProcessingError(f"LLM returned invalid JSON: {e}")
    except Exception as e:
        raise DocumentProcessingError(f"LLM call failed: {e}")


def extract_job_requirements(title: str, raw_text: str) -> JobRequirements:
    prompt = f"""
Extract structured requirements from this Job Description.

Job Description:
\"\"\"{raw_text}\"\"\"

Return JSON with EXACTLY these keys:
{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1", "skill2"],
  "min_experience_years": 0,
  "education_requirements": ["requirement1"],
  "responsibilities": ["responsibility1"]
}}

Rules:
- required_skills: must-have technical skills only
- preferred_skills: nice-to-have skills
- min_experience_years: a number (use 0 if not specified)
- Keep lists concise, use short phrases
"""
    data = _call_llm_json(prompt)
    return JobRequirements(
        title=title,
        raw_text=raw_text,
        required_skills=data.get("required_skills", []),
        preferred_skills=data.get("preferred_skills", []),
        min_experience_years=data.get("min_experience_years", 0),
        education_requirements=data.get("education_requirements", []),
        responsibilities=data.get("responsibilities", []),
    )


def extract_candidate_profile(candidate_id: str, raw_text: str) -> CandidateProfile:
    prompt = f"""
Extract structured information from this resume.

Resume:
\"\"\"{raw_text}\"\"\"

Return JSON with EXACTLY these keys:
{{
  "name": "Candidate Name",
  "skills": ["skill1", "skill2"],
  "experience_years": 0,
  "education": "highest degree and field",
  "projects": ["project1"],
  "certifications": ["cert1"]
}}

Rules:
- experience_years: a number, estimate from work history if not stated explicitly
- If a field is not found, use an empty list/string/0 as appropriate
"""
    data = _call_llm_json(prompt)
    return CandidateProfile(
        candidate_id=candidate_id,
        raw_text=raw_text,
        name=data.get("name", "Unknown"),
        skills=data.get("skills", []),
        experience_years=data.get("experience_years", 0),
        education=data.get("education"),
        projects=data.get("projects", []),
        certifications=data.get("certifications", []),
    )