import json
from unittest.mock import patch, MagicMock

import pytest

from app.services.extraction import extract_job_requirements, extract_candidate_profile
from app.utils.exceptions import DocumentProcessingError


def make_mock_response(content: str):
    mock_choice = MagicMock()
    mock_choice.message.content = content
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


@patch("app.services.extraction.client.chat.completions.create")
def test_extract_job_requirements_valid_json(mock_create):
    mock_create.return_value = make_mock_response(json.dumps({
        "required_skills": ["Python", "Docker"],
        "preferred_skills": ["AWS"],
        "min_experience_years": 2,
        "education_requirements": ["Bachelor's in CS"],
        "responsibilities": ["Build APIs"],
    }))

    result = extract_job_requirements("Backend Developer", "some raw JD text")

    assert result.title == "Backend Developer"
    assert result.required_skills == ["Python", "Docker"]
    assert result.min_experience_years == 2


@patch("app.services.extraction.client.chat.completions.create")
def test_extract_job_requirements_strips_markdown_fences(mock_create):
    mock_create.return_value = make_mock_response(
        "```json\n" + json.dumps({"required_skills": ["Python"]}) + "\n```"
    )

    result = extract_job_requirements("Backend Developer", "some raw JD text")

    assert result.required_skills == ["Python"]


@patch("app.services.extraction.client.chat.completions.create")
def test_extract_job_requirements_invalid_json_raises(mock_create):
    mock_create.return_value = make_mock_response("this is not json at all")

    with pytest.raises(DocumentProcessingError):
        extract_job_requirements("Backend Developer", "some raw JD text")


@patch("app.services.extraction.client.chat.completions.create")
def test_extract_job_requirements_missing_fields_use_defaults(mock_create):
    mock_create.return_value = make_mock_response(json.dumps({}))  # empty object

    result = extract_job_requirements("Backend Developer", "some raw JD text")

    assert result.required_skills == []
    assert result.min_experience_years == 0


@patch("app.services.extraction.client.chat.completions.create")
def test_extract_candidate_profile_valid_json(mock_create):
    mock_create.return_value = make_mock_response(json.dumps({
        "name": "Jane Smith",
        "skills": ["Python", "AWS"],
        "experience_years": 4,
        "education": "B.Tech CS",
        "projects": ["Built a chatbot"],
        "certifications": [],
    }))

    result = extract_candidate_profile("cand_001", "some raw resume text")

    assert result.name == "Jane Smith"
    assert result.experience_years == 4
    assert result.candidate_id == "cand_001"


@patch("app.services.extraction.client.chat.completions.create")
def test_extract_candidate_profile_api_failure_raises(mock_create):
    mock_create.side_effect = Exception("connection timeout")

    with pytest.raises(DocumentProcessingError):
        extract_candidate_profile("cand_001", "some raw resume text")