from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
from .utils.webscraper import WebScraper
import logging

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:54807", "http://localhost:57018"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the scraper
scraper = WebScraper()

class WebsiteRequest(BaseModel):
    url: str
    description: Optional[str] = None

@app.post("/api/analyze-website")
async def analyze_website(request: WebsiteRequest):
    try:
        # Validate URL
        is_valid = await scraper.validate_url(request.url)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid or inaccessible URL")

        # Analyze website
        analysis = await scraper.analyze_website(request.url)
        
        return {
            "success": True,
            "data": analysis
        }

    except Exception as e:
        logging.error(f"Error analyzing website: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}