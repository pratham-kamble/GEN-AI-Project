from groq import Groq

from app.config import settings
from app.models.candidate import ScoreBreakdown
from app.utils.exceptions import DocumentProcessingError

client = Groq(api_key=settings.groq_api_key)


def generate_explanation(
    candidate_name: str,
    job_title: str,
    score: ScoreBreakdown,
    matching_skills: list[str],
    missing_skills: list[str],
) -> str:
    prompt = f"""
Write a concise, recruiter-facing explanation (3-5 sentences) of this candidate's fit
for the role. Be specific and objective — no generic filler.

Candidate: {candidate_name}
Job: {job_title}
Overall match score: {score.total_score}/100

Score breakdown:
- Required skills: {score.required_skills_score}/40
- Experience: {score.experience_score}/25
- Projects: {score.projects_score}/20
- Education: {score.education_score}/10
- Additional skills: {score.additional_skills_score}/5

Matching skills: {", ".join(matching_skills) if matching_skills else "none"}
Missing skills: {", ".join(missing_skills) if missing_skills else "none"}

Explain the candidate's main strengths and weaknesses relative to this role.
"""
    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": "You are an assistant helping recruiters evaluate candidates."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise