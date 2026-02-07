from app.models import User, JobDescription, ScoringResponse, PersonalInfo, WorkExperience, JobPreferences
import pytest
from pydantic import ValidationError

def test_user_model_valid():
    user_data = {
        "personal_info": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "123-456-7890",
            "linkedin_url": "https://linkedin.com/in/janedoe"
        },
        "work_history": [
            {
                "company": "Tech Corp",
                "role": "Software Engineer",
                "duration": "2 years",
                "description": "Built cool stuff"
            }
        ],
        "preferences": {
            "company_size": "Enterprise",
            "industry_excitement": "AI",
            "minimum_salary": 150000
        },
        "skills": ["Python", "AI"],
        "education": ["BS CS"]
    }
    user = User(**user_data)
    assert user.personal_info.name == "Jane Doe"
    assert user.work_history[0].company == "Tech Corp"
    assert user.preferences.minimum_salary == 150000

def test_job_description_valid():
    job_data = {
        "title": "AI Engineer",
        "company": "DeepMind",
        "location": "London",
        "raw_text": "We need an AI expert.",
        "url": "https://deepmind.com/careers"
    }
    job = JobDescription(**job_data)
    assert job.title == "AI Engineer"
    assert str(job.url) == "https://deepmind.com/careers/" or str(job.url) == "https://deepmind.com/careers"

def test_scoring_response_valid():
    resp_data = {
        "match_score": 85,
        "strengths": ["Strong Python"],
        "gaps": ["No K8s"],
        "reasoning_steps": ["Step 1", "Step 2"]
    }
    resp = ScoringResponse(**resp_data)
    assert resp.match_score == 85
    assert len(resp.reasoning_steps) == 2

def test_scoring_response_invalid_score():
    resp_data = {
        "match_score": 105, # Invalid > 100
        "strengths": ["Strong Python"],
        "gaps": ["No K8s"],
        "reasoning_steps": ["Step 1"]
    }
    with pytest.raises(ValidationError):
        ScoringResponse(**resp_data)
