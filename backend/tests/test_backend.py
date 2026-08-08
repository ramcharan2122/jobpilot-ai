import pytest
from app.resume_generator.validator import ResumeValidator
from app.job_sources.seed_demo_source import SeedDemoJobSource

def test_resume_validator_no_hallucinations():
    profile = {
        "experiences": [{"company": "Swiggy"}],
        "education": [{"university": "IIT Bombay"}],
        "projects": [{"name": "AI Search Engine"}],
        "skills": [{"name": "Python"}, {"name": "FastAPI"}]
    }

    valid_resume = {
        "experiences": [{"company": "Swiggy"}],
        "education": [{"university": "IIT Bombay"}],
        "projects": [{"name": "AI Search Engine"}],
        "skills": {"Programming": ["Python", "FastAPI"]}
    }

    is_valid, notes = ResumeValidator.validate_resume_against_profile(valid_resume, profile)
    assert is_valid is True

def test_resume_validator_detects_fake_company():
    profile = {
        "experiences": [{"company": "Swiggy"}],
        "education": [{"university": "IIT Bombay"}],
        "projects": [],
        "skills": []
    }

    fake_resume = {
        "experiences": [{"company": "Google (Fabricated)"}],
        "education": [{"university": "IIT Bombay"}],
        "projects": [],
        "skills": {}
    }

    is_valid, notes = ResumeValidator.validate_resume_against_profile(fake_resume, profile)
    assert is_valid is False
    assert any("Fabricated company" in n for n in notes)

@pytest.mark.asyncio
async def test_seed_demo_job_source():
    source = SeedDemoJobSource()
    jobs = await source.search_jobs([], [], 0, 100)
    assert len(jobs) >= 5
    assert jobs[0]["company"] == "Swiggy Engineering"
