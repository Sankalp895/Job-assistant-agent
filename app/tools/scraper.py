import json
import re
from bs4 import BeautifulSoup
import httpx
from jobspy import scrape_jobs
import pandas as pd
from typing import List, Dict, Optional
from app.models import JobDescription

class JobScraper:
    def __init__(self):
        # Using a reliable, modern user agent
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape(self, url: str) -> JobDescription:
        """
        Scrapes a job URL using httpx (Standard HTTP Request) instead of Playwright.
        This is faster and more lightweight but essentially does the same parsing.
        """
        try:
            with httpx.Client(headers=self.headers, follow_redirects=True, timeout=15.0) as client:
                response = client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # 1. Attempt to extract structured JSON-LD data (most reliable)
                json_data = self._extract_json_ld(soup)
                
                # 2. Extract Title
                title = json_data.get("title") or (soup.title.string if soup.title else None)
                if not title or title.strip() == "":
                    h1 = soup.find("h1")
                    title = h1.get_text(strip=True) if h1 else "Unknown Job Title"
                
                # 3. Extract Company
                company = json_data.get("hiringOrganization", {}).get("name")
                if not company:
                    meta_company = soup.find("meta", property="og:site_name")
                    company = meta_company["content"] if meta_company else "Unknown Company"

                # 4. Extract Location
                loc = json_data.get("jobLocation", {}).get("address", {})
                if loc:
                     # Combine locality and region if available
                     location = f"{loc.get('addressLocality', '')}, {loc.get('addressRegion', '')}".strip(", ")
                else:
                    location = "See Description"

                # 5. Extract and Clean Text Description
                # Remove non-content tags
                for junk in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "svg", "button", "input", "form"]):
                    junk.decompose()
                    
                # Find the main content area - heuristics
                content_area = soup.find("main") or soup.find("article") or soup.find("div", {"id": re.compile(r"content|job|desc", re.I)}) or soup.body
                raw_text = content_area.get_text(separator="\n", strip=True) if content_area else ""
                
                # Normalize whitespace
                raw_text = re.sub(r'\n+', '\n', raw_text).strip()

                return JobDescription(
                    title=title.strip(),
                    company=company.strip(),
                    location=location,
                    raw_text=raw_text,
                    url=url
                )

        except httpx.RequestError as e:
            return JobDescription(
                title="Error: Connection Failed",
                company="System",
                raw_text=f"Could not connect to the URL: {str(e)}",
                url=url
            )
        except Exception as e:
            return JobDescription(
                title="Error: Scraping Failed",
                company="System",
                raw_text=f"An error occurred while scraping: {str(e)}",
                url=url
            )

    def search_jobs(self, query: str, location: str = "", limit: int = 10) -> List[Dict]:
        """
        Uses JobSpy to search for jobs across multiple boards.
        """
        try:
            # JobSpy supports: linkedin, indeed, glassdoor, ziprecruiter
            site_names = ["linkedin", "indeed", "glassdoor", "ziprecruiter"]
            
            jobs: pd.DataFrame = scrape_jobs(
                site_name=site_names,
                search_term=query,
                location=location,
                results_wanted=limit,
                country_indeed='USA'  # Default to USA, can be parameterized if needed
            )
            
            # Convert DataFrame to list of dicts
            return jobs.to_dict(orient="records")
            
        except Exception as e:
            print(f"JobSpy Search Error: {e}")
            return []

    def _extract_json_ld(self, soup: BeautifulSoup) -> dict:
        """
        Helper method to look for structured 'JobPosting' data in the page's HTML.
        """
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                if not script.string: continue
                data = json.loads(script.string)
                
                if isinstance(data, list): 
                    data = data[0]
                
                obj_type = data.get("@type", "")
                if obj_type == "JobPosting" or (isinstance(obj_type, list) and "JobPosting" in obj_type):
                    return data
            except:
                continue
        return {}