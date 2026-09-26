from app.models.job import JobRequirements
from app.models.candidate import CandidateProfile, ScoreBreakdown
from app.services.embeddings import skill_semantic_match, semantic_similarity

# Weights per the assignment spec (must sum to 100)
WEIGHT_REQUIRED_SKILLS = 40
WEIGHT_EXPERIENCE = 25
WEIGHT_PROJECTS = 20
WEIGHT_EDUCATION = 10
WEIGHT_ADDITIONAL_SKILLS = 5


def score_required_skills(candidate: CandidateProfile, job: JobRequirements):
    matching, missing = skill_semantic_match(candidate.skills, job.required_skills)
    if not job.required_skills:
        return WEIGHT_REQUIRED_SKILLS, matching, missing
    ratio = len(matching) / len(job.required_skills)
    return round(ratio * WEIGHT_REQUIRED_SKILLS, 2), matching, missing


def score_experience(candidate: CandidateProfile, job: JobRequirements) -> float:
    if job.min_experience_years <= 0:
        return WEIGHT_EXPERIENCE
    ratio = min(candidate.experience_years / job.min_experience_years, 1.0)
    return round(ratio * WEIGHT_EXPERIENCE, 2)


def score_projects(candidate: CandidateProfile, job: JobRequirements) -> float:
    """
    Scores relevance of candidate projects to job responsibilities via semantic
    similarity, falling back to a simple count-based score if no projects exist.
    """
    if not candidate.projects:
        return 0.0
    if not job.responsibilities:
        # No responsibilities to compare against — reward having projects at all
        ratio = min(len(candidate.projects) / 3, 1.0)
        return round(ratio * WEIGHT_PROJECTS, 2)

    job_context = " ".join(job.responsibilities)
    sims = [semantic_similarity(project, job_context) for project in candidate.projects]
    avg_relevance = sum(sims) / len(sims)
    return round(avg_relevance * WEIGHT_PROJECTS, 2)


def score_education(candidate: CandidateProfile, job: JobRequirements) -> float:
    if not job.education_requirements:
        return WEIGHT_EDUCATION
    if not candidate.education:
        return 0.0
    best_sim = max(
        semantic_similarity(candidate.education, req) for req in job.education_requirements
    )
    return round(min(best_sim / 0.6, 1.0) * WEIGHT_EDUCATION, 2)


def score_additional_skills(candidate: CandidateProfile, job: JobRequirements):
    if not job.preferred_skills:
        return WEIGHT_ADDITIONAL_SKILLS, []
    matching, _ = skill_semantic_match(candidate.skills, job.preferred_skills)
    if not matching:
        return 0.0, []
    ratio = len(matching) / len(job.preferred_skills)
    return round(ratio * WEIGHT_ADDITIONAL_SKILLS, 2), matching


def calculate_match_score(candidate: CandidateProfile, job: JobRequirements) -> ScoreBreakdown:
    required_score, matching_required, missing_required = score_required_skills(candidate, job)
    experience_score = score_experience(candidate, job)
    projects_score = score_projects(candidate, job)
    education_score = score_education(candidate, job)
    additional_score, matching_preferred = score_additional_skills(candidate, job)

    total = round(
        required_score + experience_score + projects_score + education_score + additional_score, 2
    )

    return ScoreBreakdown(
        required_skills_score=required_score,
        experience_score=experience_score,
        projects_score=projects_score,
        education_score=education_score,
        additional_skills_score=additional_score,
        total_score=total,
    ), matching_required + matching_preferred, missing_required