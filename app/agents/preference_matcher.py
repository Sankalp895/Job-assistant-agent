import json
from typing import Dict, Any, Optional, List
from app.models import JobDescription

class PreferenceMatcher:
    """
    Analyzes job descriptions against user preferences to provide personalized insights
    and adjust match scores based on alignment with user values, field, location, and role level.
    """
    
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
    
    def calculate_preference_boost(self, job_description: JobDescription, preferences: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate preference-based boost to match score and generate personalized insights.
        
        Returns:
            {
                "preference_boost": int (0-20 points to add to base score),
                "preference_insights": List[str],
                "preference_warnings": List[str]
            }
        """
        if not preferences:
            return {
                "preference_boost": 0,
                "preference_insights": [],
                "preference_warnings": []
            }
        
        boost = 0
        insights = []
        warnings = []
        
        job_text = job_description.raw_text.lower()
        job_title = job_description.title.lower()
        job_location = job_description.location.lower() if job_description.location else ""
        
        # 1. Field & Subfield Matching (up to +8 points)
        field = preferences.get('field', '').lower()
        subfield = preferences.get('subfield', '').lower()
        specialization = preferences.get('specialization', '').lower()
        
        if field and field in job_text:
            boost += 3
            insights.append(f"✓ This role aligns with your {preferences.get('field')} field preference")
        
        if subfield and subfield in job_text:
            boost += 3
            insights.append(f"✓ Matches your {preferences.get('subfield')} expertise")
        
        if specialization and specialization in job_text:
            boost += 2
            insights.append(f"✓ Perfect fit for your {preferences.get('specialization')} specialization")
        
        # 2. Location Matching (up to +5 points)
        user_locations = [loc.lower() for loc in preferences.get('locations', [])]
        remote_preference = preferences.get('remote_preference', False)
        
        location_matched = False
        for loc in user_locations:
            if loc in job_location or loc in job_text:
                boost += 3
                insights.append(f"✓ Location match: {loc.title()}")
                location_matched = True
                break
        
        # Check for remote work
        remote_keywords = ['remote', 'work from home', 'wfh', 'distributed', 'anywhere']
        is_remote_job = any(keyword in job_text for keyword in remote_keywords)
        
        if remote_preference and is_remote_job:
            boost += 2
            insights.append("✓ Remote work available - matches your preference")
        elif remote_preference and not is_remote_job and not location_matched:
            warnings.append("⚠ This role appears to be on-site, but you prefer remote work")
        elif not remote_preference and is_remote_job:
            insights.append("ℹ This role offers remote work flexibility")
        
        # 3. Role Level Matching (up to +4 points)
        role_level = preferences.get('role_level', '').lower()
        level_keywords = {
            'entry level': ['entry', 'junior', 'associate', 'graduate'],
            'mid-level': ['mid', 'intermediate', 'engineer ii', 'engineer 2'],
            'senior': ['senior', 'sr.', 'lead engineer', 'staff'],
            'lead/principal': ['lead', 'principal', 'architect', 'staff engineer'],
            'executive/director': ['director', 'vp', 'vice president', 'executive', 'head of', 'chief']
        }
        
        if role_level in level_keywords:
            keywords = level_keywords[role_level]
            if any(keyword in job_title or keyword in job_text for keyword in keywords):
                boost += 4
                insights.append(f"✓ Role level matches your {preferences.get('role_level')} target")
            else:
                # Check if it's a mismatch
                for level, kws in level_keywords.items():
                    if level != role_level and any(kw in job_title for kw in kws):
                        warnings.append(f"⚠ This appears to be a {level.title()} role, but you're targeting {preferences.get('role_level')}")
                        break
        
        # 4. Values Alignment (up to +3 points) - Check if job description mentions user values
        user_values = [v.lower() for v in preferences.get('values', [])]
        value_keywords = {
            'competitive compensation': ['competitive salary', 'competitive compensation', 'competitive pay', 'equity', 'stock options'],
            'work-life balance': ['work-life balance', 'flexible hours', 'work life balance', 'flexible schedule'],
            'career growth': ['career growth', 'professional development', 'learning', 'advancement', 'promotion'],
            'company culture': ['culture', 'team environment', 'collaborative', 'inclusive', 'diversity'],
            'making impact': ['impact', 'mission', 'meaningful work', 'change lives', 'make a difference'],
            'flexibility': ['flexible', 'flexibility', 'hybrid', 'remote options', 'work from anywhere'],
            'benefits & perks': ['benefits', 'health insurance', 'dental', '401k', 'pto', 'vacation', 'perks'],
            'job security': ['stable', 'established', 'fortune 500', 'publicly traded', 'security']
        }
        
        values_matched = 0
        for value in user_values:
            if value in value_keywords:
                keywords = value_keywords[value]
                if any(keyword in job_text for keyword in keywords):
                    values_matched += 1
        
        if values_matched > 0:
            boost += min(3, values_matched)
            insights.append(f"✓ Job description mentions {values_matched} of your core values")
        
        # Cap the boost at 20 points
        boost = min(20, boost)
        
        return {
            "preference_boost": boost,
            "preference_insights": insights,
            "preference_warnings": warnings
        }
    
    async def generate_preference_summary(self, job_description: JobDescription, preferences: Optional[Dict[str, Any]]) -> str:
        """
        Use LLM to generate a personalized summary of how well the job matches user preferences.
        """
        if not preferences or not self.llm_provider:
            return ""
        
        prompt = f"""
You are a career advisor analyzing how well a job matches a candidate's preferences.

USER PREFERENCES:
- Values: {', '.join(preferences.get('values', []))}
- Field: {preferences.get('field')}
- Subfield: {preferences.get('subfield')}
- Specialization: {preferences.get('specialization')}
- Preferred Locations: {', '.join(preferences.get('locations', []))}
- Remote Preference: {'Yes' if preferences.get('remote_preference') else 'No'}
- Target Role Level: {preferences.get('role_level')}

JOB DETAILS:
- Title: {job_description.title}
- Company: {job_description.company}
- Location: {job_description.location}
- Description: {job_description.raw_text[:1500]}

Provide a brief 2-3 sentence personalized analysis of how this job aligns with the user's preferences. 
Focus on the most important matches or mismatches. Be honest but constructive.

Return ONLY the analysis text, no JSON or formatting.
"""
        
        try:
            response = await self.llm_provider.chat(prompt)
            return response.strip()
        except Exception as e:
            return ""
