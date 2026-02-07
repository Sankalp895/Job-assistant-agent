from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

# --- User Profile Models (For Autofill Agent) ---

class WorkExperience(BaseModel):
    company: str
    role: str
    duration: Optional[str] = None
    description: Optional[str] = None

class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None # Changed to str for easier DB storage
    portfolio_url: Optional[str] = None

class UserProfile(BaseModel):
    personal_info: PersonalInfo
    work_history: List[WorkExperience] = []
    skills: List[str] = []
    education: List[str] = []

# --- Job & Analysis Models (For Scraper & Scoring Agent) ---

class JobDescription(BaseModel):
    title: str
    company: str
    location: Optional[str] = "Unknown"
    raw_text: str
    url: Optional[str] = None

class ResumeMatch(BaseModel):
    """The output from the Scoring Agent"""
    match_score: int = Field(..., ge=0, le=100)
    matched_skills: List[str]
    missing_skills: List[str]
    tailoring_tips: List[str] = Field(..., description="Actionable advice to improve resume")
    fit_summary: str

# --- Dashboard Model (To track progress) ---

class JobApplication(BaseModel):
    """Stores the history of a user's applications"""
    id: Optional[int] = None
    job_title: str
    company: str
    status: str = "Not Submitted" # e.g., Submitted, Interview Requested, Rejected
    match_score: int
    date_applied: Optional[str] = None

# --- User Preferences Model (For Onboarding) ---

class UserPreferences(BaseModel):
    """Stores user preferences from onboarding"""
    user_id: str
    values: List[str]
    field: str
    subfield: str
    specialization: str
    locations: List[str]
    remote_preference: bool
    role_level: str
