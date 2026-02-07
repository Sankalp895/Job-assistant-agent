import pytest
from app.agents.scoring_agent import ScoringAgent
from app.models import JobDescription

@pytest.mark.asyncio
async def test_scoring_agent_error_handling():
    """
    Test that the ScoringAgent gracefully handles a JobDescription 
    that represents a scraper error, instead of trying to analyze it with the LLM.
    """
    
    # Create an "Error" JobDescription
    error_jd = JobDescription(
        title="Error: Initialization Failed",
        company="System",
        location="Unknown",
        raw_text="Failed to launch browser which uses Async IO and Playwright.",
        url="http://example.com"
    )
    
    # Initialize agent without an LLM provider (shouldn't need it if the check works)
    agent = ScoringAgent(llm_provider=None)
    
    # Run generation
    result = await agent.generate_score(
        resume_text="Some resume text",
        job_description=error_jd
    )
    
    # Assertions
    assert result["match_score"] == 0
    assert "Job scraping failed" in result["tailoring_tips"][0]
    assert result["fit_summary"] == "Analysis failed due to invalid job description."
    assert "Playwright" not in str(result) # Ensure no hallucination from the raw text

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scoring_agent_error_handling())
