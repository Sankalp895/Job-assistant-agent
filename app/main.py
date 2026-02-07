from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi import UploadFile, File, Form
import PyPDF2
import io
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_client import AIClient

from app.tools.scraper import JobScraper
from app.agents.scoring_agent import ScoringAgent
from app.agents.answer_agent import AnswerAgent
from app.agents.autofill_agent import AutofillAgent
from app.database import add_application, get_all_applications, save_user_profile, save_user_preferences, get_user_preferences
from app.models import ResumeMatch, UserProfile, JobApplication, JobDescription, UserPreferences


app = FastAPI(title="AI Job Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# setup stuf
ai_client = AIClient()
scraper = JobScraper()
scoring_agent = ScoringAgent(llm_provider=ai_client)
answer_agent = AnswerAgent(llm_provider=ai_client)
autofill_agent = AutofillAgent()


class AnalyzeRequest(BaseModel):
    url: str
    resume_text: str
    user_id: Optional[str] = None

class ManualJobAnalyzeRequest(BaseModel):
    job_title: str
    company: str
    location: str = "Not Specified"
    job_description: str
    resume_text: str
    user_id: Optional[str] = None

class AnswerRequest(BaseModel):
    question: str
    job_url: str
    user_profile: UserProfile

class SearchJobRequest(BaseModel):
    query: str
    location: str = ""
    limit: int = 10


async def extract_text_from_pdf(file: UploadFile) -> str:
    """Extract text from uploaded PDF file"""
    pdf_content = await file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
    
    resume_text = ""
    for page in pdf_reader.pages:
        resume_text += page.extract_text()

    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
    
    return resume_text

async def analyze_and_save(resume_text: str, job_data: JobDescription, url_for_db: str, user_id: str = None) -> ResumeMatch:
    """Common logic for analyzing resume against job and saving to database"""
    
    # if user exists get prefs
    user_preferences = None
    if user_id:
        user_preferences = get_user_preferences(user_id)
    
    # run analysis w/ prefs
    analysis = await scoring_agent.generate_score(resume_text, job_data, user_preferences)
    
    add_application(
        job_title=job_data.title,
        company=job_data.company,
        score=analysis.get("match_score", 0),
        url=url_for_db
    )
    
    return analysis



@app.post("/api/analyze", response_model=ResumeMatch)
async def analyze_job(request: AnalyzeRequest):
    """Analyze job from URL with text resume"""
    job_data = scraper.scrape(request.url)
    if job_data.title.startswith("Error"):
        raise HTTPException(status_code=400, detail="Scraping failed.")
    
    return await analyze_and_save(request.resume_text, job_data, request.url, request.user_id)

@app.post("/api/analyze-manual", response_model=ResumeMatch)
async def analyze_job_manual(request: ManualJobAnalyzeRequest):
    """Analyze job with manually entered job description and text resume"""
    job_data = JobDescription(
        title=request.job_title,
        company=request.company,
        location=request.location,
        raw_text=request.job_description,
        url=None
    )
    
    return await analyze_and_save(request.resume_text, job_data, "Manual Entry", request.user_id)

@app.post("/api/analyze-pdf", response_model=ResumeMatch)
async def analyze_job_pdf(
    url: str = Form(...), 
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """Analyze job from URL with PDF resume"""
    try:
        resume_text = await extract_text_from_pdf(file)
        job_data = scraper.scrape(url)
        
        if job_data.title.startswith("Error"):
            raise HTTPException(status_code=400, detail="Scraping failed.")
        
        return await analyze_and_save(resume_text, job_data, url, user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Processing failed: {str(e)}")

@app.post("/api/analyze-manual-pdf", response_model=ResumeMatch)
async def analyze_job_manual_pdf(
    job_title: str = Form(...),
    company: str = Form(...),
    location: str = Form("Not Specified"),
    job_description: str = Form(...),
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """Analyze job with manually entered job description and PDF resume"""
    try:
        resume_text = await extract_text_from_pdf(file)
        
        job_data = JobDescription(
            title=job_title,
            company=company,
            location=location,
            raw_text=job_description,
            url=None
        )
        
        return await analyze_and_save(resume_text, job_data, "Manual Entry", user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Processing failed: {str(e)}")

@app.post("/api/generate-answer")
async def get_tailored_answer(request: AnswerRequest):
    """Generate tailored answer for job application question"""
    job_data = scraper.scrape(request.job_url)
    answer = await answer_agent.generate_answer(request.question, job_data, request.user_profile)
    return {"answer": answer}

@app.post("/api/search-jobs")
async def search_jobs(request: SearchJobRequest):
    """Search for jobs using JobSpy"""
    results = scraper.search_jobs(request.query, request.location, request.limit)
    # fix pandas NaNs, json hates them
    cleaned_results = []
    for job in results:
        cleaned_job = {k: (v if pd.notna(v) else None) for k, v in job.items()}
        cleaned_results.append(cleaned_job)
    return {"results": cleaned_results}

@app.get("/api/dashboard", response_model=List[JobApplication])
async def get_dashboard():
    """Get all job applications from database"""
    return get_all_applications()



@app.post("/api/preferences")
async def save_preferences(preferences: UserPreferences):
    """Save user preferences from onboarding"""
    success = save_user_preferences(preferences.dict())
    if success:
        return {"status": "success", "message": "Preferences saved successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save preferences")

@app.get("/api/preferences/{user_id}")
async def get_preferences(user_id: str):
    """Get user preferences by user_id"""
    prefs = get_user_preferences(user_id)
    if prefs:
        return prefs
    else:
        raise HTTPException(status_code=404, detail="Preferences not found")

@app.put("/api/preferences/{user_id}")
async def update_preferences(user_id: str, preferences: UserPreferences):
    """Update user preferences"""
    if user_id != preferences.user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    
    success = save_user_preferences(preferences.dict())
    if success:
        return {"status": "success", "message": "Preferences updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update preferences")
