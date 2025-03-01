import asyncio
import logging
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
                        "description": "",
                        "company_info": [],
                        "ai_related_content": [],
                        "main_content": "",
                        "technologies_used": [],
                        "privacy_policy_url": None,
                    }

                    # Extract title
                    content["title"] = self._extract_text_from_element(soup.title)

                    # Extract meta description
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc:
                        content["description"] = meta_desc.get("content", "")

                    # Find privacy policy link
                    privacy_links = soup.find_all(
                        "a", href=True, text=lambda t: t and "privacy" in t.lower()
                    )
                    if privacy_links:
                        content["privacy_policy_url"] = urljoin(
                            url, privacy_links[0]["href"]
                        )

                    # Extract company information
                    about_sections = soup.find_all(
                        ["div", "section"],
                        class_=lambda x: x
                        and any(
                            term in str(x).lower()
                            for term in ["about", "company", "who-we-are"]
                        ),
                    )
                    for section in about_sections:
                        text = self._extract_text_from_element(section)
                        if text:
                            content["company_info"].append(text)

                    # Extract main content and AI-related information
                    main_content_tags = ["p", "article", "section", "div"]
                    for tag in soup.find_all(main_content_tags):
                        text = self._extract_text_from_element(tag)
                        if text:
                            if len(text) > 50:  # Filter out very short sections
                                content["main_content"] += text + "\n\n"
                            if self._is_ai_related(text):
                                content["ai_related_content"].append(text)

                    # Look for technology mentions
                    tech_sections = soup.find_all(
                        ["div", "section"],
                        class_=lambda x: x
                        and any(
                            term in str(x).lower()
                            for term in ["tech", "technology", "stack", "solution"]
                        ),
                    )
                    for section in tech_sections:
                        text = self._extract_text_from_element(section)
                        if text:
                            content["technologies_used"].append(text)
                    return content

        except Exception as e:
            logging.error(f"Error scraping URL {url}: {str(e)}")
            raise

    async def analyze_website(self, url: str) -> Dict:
        """Analyze website content for AI-related information."""
        try:
            content = await self.scrape_website(url)

            # Analyze the content
            analysis = {
                "url": url,
                "company_name": (
                    content["title"].split("|")[0].strip()
                    if "|" in content["title"]
                    else content["title"]
                ),
                "uses_ai": len(content["ai_related_content"]) > 0,
                "ai_applications": [],
                "privacy_concerns": bool(content["privacy_policy_url"]),
                "summary": (
                    content["description"] or content["company_info"][0]
                    if content["company_info"]
                    else ""
                ),
            }

            # Categorize AI applications
            if analysis["uses_ai"]:
                ai_categories = {
                    "automation": ["automation", "workflow", "process"],
                    "analytics": ["analytics", "prediction", "forecasting"],
                    "nlp": ["language", "text", "nlp", "chatbot"],
                    "computer_vision": ["vision", "image", "recognition"],
                    "decision_making": ["decision", "recommendation", "optimization"],
                }

                for text in content["ai_related_content"]:
                    for category, keywords in ai_categories.items():
                        if any(keyword in text.lower() for keyword in keywords):
                            if category not in analysis["ai_applications"]:
                                analysis["ai_applications"].append(category)

            return analysis

        except Exception as e:
            logging.error(f"Error analyzing website {url}: {str(e)}")
            raise
