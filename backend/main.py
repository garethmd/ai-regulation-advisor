import logging

import requests
import uvicorn
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WebsiteRequest(BaseModel):
    url: str


class WebsiteResponse(BaseModel):
    success: bool
    content: str
    title: str | None = None
    description: str | None = None


def scrape_website(url: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Get title
        title = soup.title.string if soup.title else None

        # Get meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc.get("content") if meta_desc else None

        # Remove script and style elements
        for script in soup(["script", "style", "iframe", "nav", "footer"]):
            script.decompose()

        # Get main content
        main_content = soup.get_text(separator="\n", strip=True)

        # Clean up the text
        lines = [line.strip() for line in main_content.splitlines() if line.strip()]
        cleaned_content = "\n".join(lines)

        return {
            "success": True,
            "content": cleaned_content,
            "title": title,
            "description": description,
        }
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        return {
            "success": False,
            "content": f"Error scraping website: {str(e)}",
            "title": None,
            "description": None,
        }


@app.post("/api/analyze-website")
async def analyze_website(request: WebsiteRequest) -> WebsiteResponse:
    try:
        logger.info(f"Received request to analyze website: {request.url}")
        result = scrape_website(request.url)
        logger.info(f"Scraping result: {result}")
        return WebsiteResponse(**result)
    except Exception as e:
        logger.error(f"Error analyzing websites: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=54807)
