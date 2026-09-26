import pytest

from app.models.job import JobRequirements
from app.models.candidate import CandidateProfile
from app.services.scoring import calculate_match_score


def make_job(**overrides):
    defaults = dict(
        title="Backend Developer",
        raw_text="...",
        required_skills=["Python", "Docker"],
        preferred_skills=["AWS"],
        min_experience_years=2,
        education_requirements=["Bachelor degree in Computer Science"],
        responsibilities=["Build and maintain REST APIs"],
    )
    defaults.update(overrides)
    return JobRequirements(**defaults)


def make_candidate(**overrides):
    defaults = dict(
        candidate_id="cand_test",
        name="Test Candidate",
        raw_text="...",
        skills=["Python", "Docker", "AWS"],
        experience_years=3,
        education="Bachelor's in Computer Science",
        projects=["Built a REST API service for internal tools"],
        certifications=[],
    )
    defaults.update(overrides)
    return CandidateProfile(**defaults)


def test_high_match_candidate_scores_high():
    job = make_job()
    candidate = make_candidate()
    score, matching, missing = calculate_match_score(candidate, job)

    assert score.total_score > 70
    assert "Python" in matching or "Docker" in matching
    assert missing == [] or len(missing) < len(job.required_skills)


def test_low_match_candidate_scores_low():
    job = make_job()
    candidate = make_candidate(
        skills=["Java", "Spring Boot"],
        experience_years=0,
        education=None,
        projects=[],
    )
    score, matching, missing = calculate_match_score(candidate, job)

    assert score.total_score < 40
    assert score.projects_score == 0.0


def test_no_required_skills_gives_full_required_score():
    job = make_job(required_skills=[])
    candidate = make_candidate()
    score, matching, missing = calculate_match_score(candidate, job)

    assert score.required_skills_score == 40
    assert missing == []


def test_experience_capped_at_full_weight():
    job = make_job(min_experience_years=2)
    candidate = make_candidate(experience_years=10)  # far exceeds requirement
    score, matching, missing = calculate_match_score(candidate, job)

    assert score.experience_score == 25  # capped, not over-awarded


def test_score_components_sum_to_total():
    job = make_job()
    candidate = make_candidate()
    score, matching, missing = calculate_match_score(candidate, job)

    expected_total = round(
        score.required_skills_score
        + score.experience_score
        + score.projects_score
        + score.education_score
        + score.additional_skills_score,
        2,
    )
    assert score.total_score == expected_total