import json
import re
from typing import Dict, Any
from app.models import JobDescription

class ScoringAgent:
    def __init__(self, llm_provider=None):
        """
        llm_provider: The AIClient instance from your root directory.
        """
        self.llm_provider = llm_provider

    async def generate_score(self, resume_text: str, job_description: JobDescription, user_preferences: dict = None) -> Dict[str, Any]:
        """
        Performs deep analysis and keyword extraction to provide actionable insights.
        Now includes preference-based matching for personalized results.
        """
        # check if err so we dont crash
        if job_description.title.startswith("Error"):
            return {
                "match_score": 0,
                "matched_skills": [],
                "missing_skills": [],
                "tailoring_tips": ["Job scraping failed. Please check the URL."],
                "fit_summary": "Analysis failed due to invalid job description."
            }

        prompt = f"""
Role: Expert ATS (Applicant Tracking System) Optimization Engineer.
Task: Provide a high-fidelity match analysis between the Resume and Job Description.

[CONTEXT]
JOB TITLE: {job_description.title}
JD CONTENT (Truncated): {job_description.raw_text[:2000]}
USER RESUME: {resume_text[:2000]}

[ANALYSIS REQUIREMENTS]
1. IDENTIFY: Top 5 matched technical skills/keywords.
2. IDENTIFY: Top 5 missing technical skills/keywords required by the JD.
3. ADVISE: 3 specific, actionable tailoring tips using the format: "Update [Section] to include [Skill/Action] because [Reason]."
4. SCORE: 0-100 based on core technical alignment.

[REQUIRED OUTPUT FORMAT - JSON ONLY]
{{
    "match_score": (int),
    "matched_skills": ["skill1", "skill2"],
    "missing_skills": ["keyword1", "keyword2"],
    "tailoring_tips": [
        "Tip 1...",
        "Tip 2...",
        "Tip 3..."
    ],
    "fit_summary": "One sentence data-driven explanation of the match."
}}

Constraint: Return ONLY valid JSON. No conversational text.
"""
        if not self.llm_provider:
            base_result = self._get_mock_analysis()
        else:
            # call teh ai
            response = await self.llm_provider.chat(prompt)
            base_result = self._parse_json_response(response)
        
        # apply prefs boost
        if user_preferences:
            from app.agents.preference_matcher import PreferenceMatcher
            matcher = PreferenceMatcher(self.llm_provider)
            pref_result = matcher.calculate_preference_boost(job_description, user_preferences)
            
            # boost score (max 100)
            base_score = base_result.get("match_score", 0)
            boosted_score = min(100, base_score + pref_result["preference_boost"])
            base_result["match_score"] = boosted_score
            
            # add insights to tips
            if pref_result["preference_insights"]:
                base_result["preference_insights"] = pref_result["preference_insights"]
            if pref_result["preference_warnings"]:
                base_result["preference_warnings"] = pref_result["preference_warnings"]
            
            # add context to summary
            if pref_result["preference_boost"] > 0:
                base_result["fit_summary"] += f" (+{pref_result['preference_boost']} preference boost)"
        
        return base_result


    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Robust JSON extractor that handles markdown trash.
        """
        try:
            # 1. try finding json in backticks
            code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if code_block:
                return json.loads(code_block.group(1))
            
            # 2. try finding curly braces
            brace_match = re.search(r'\{.*\}', response, re.DOTALL)
            if brace_match:
                return json.loads(brace_match.group())
            
            # 3. just load it
            return json.loads(response.strip())
        except Exception as e:
            return {
                "error": "Data Science Logic Failed: Invalid LLM Output Format",
                "match_score": 0,
                "fit_summary": f"Parsing Error: {str(e)}"
            }

    def _get_mock_analysis(self) -> Dict[str, Any]:
        """mock data so we dont use credits"""
        return {
            "match_score": 75,
            "matched_skills": ["Python", "SQL", "API Design"],
            "missing_skills": ["Docker", "Kubernetes", "AWS Lambda"],
            "tailoring_tips": [
                "Update Skills section to include Docker to match infrastructure requirements.",
                "Quantify your API impact in your current role.",
                "Add a project involving Cloud services."
            ],
            "fit_summary": "Strong backend candidate lacking specific DevOps and Cloud keywords."
        }