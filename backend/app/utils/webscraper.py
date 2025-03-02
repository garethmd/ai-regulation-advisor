import asyncio
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AIRegulationAnalyzer/1.0; +http://example.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.ai_keywords = [
            "artificial intelligence",
            "ai",
            "machine learning",
            "ml",
            "deep learning",
            "neural network",
            "automation",
            "data science",
            "algorithm",
            "predictive analytics",
            "computer vision",
            "natural language processing",
            "nlp",
            "robotics",
        ]

    async def validate_url(self, url: str) -> bool:
        """Validate if a URL is accessible."""
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(
                    url, headers=self.headers, timeout=10, ssl=False
                ) as response:
                    return response.status == 200
        except Exception as e:
            logging.error(f"Error validating URL {url}: {str(e)}")
            return False

    def _extract_text_from_element(self, element) -> str:
        """Extract clean text from a BeautifulSoup element."""
        if element is None:
            return ""
        return " ".join(element.get_text(separator=" ", strip=True).split())

    def _is_ai_related(self, text: str) -> bool:
        """Check if text contains AI-related keywords."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.ai_keywords)

    # Extract and clean text

    def clean_text(self, text):
        return re.sub(
            r"\s+", " ", text
        ).strip()  # Replace multiple spaces/newlines with a single space

    async def scrape_website(self, url: str) -> Dict:
        """Scrape website content with focus on AI-related information."""
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, headers=self.headers, timeout=30, ssl=False
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Failed to fetch URL: Status code {response.status}"
                        )

                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Initialize content dictionary
                    content = {
                        "title": "",
                        "raw": "",
                    }

                    # Extract title
                    content["title"] = self._extract_text_from_element(soup.title)
                    content["raw"] = self.clean_text(
                        soup.get_text(separator=" ")
                    )  # Avoids multiple line breaks

                    return content

        except Exception as e:
            logging.error(f"Error scraping URL {url}: {str(e)}")
            raise

    async def analyze_website(self, url: str) -> Dict:
        """Analyze website content for AI-related information."""
        try:
            content = await self.scrape_website(url)

            return content

        except Exception as e:
            logging.error(f"Error analyzing website {url}: {str(e)}")
            raise
