import logging
import os
from typing import Dict

from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.readers.web import SimpleWebPageReader

# Load environment variables from .env
load_dotenv()

# Access the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the .env file")

print(f"Your API Key: {OPENAI_API_KEY}")  # Just for debugging; remove in production


async def analyze_website(url: str) -> Dict:
    # Load data from a list of URLs
    reader = SimpleWebPageReader()
    documents = reader.load_data([url])
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    response = query_engine.query(
        "Find companies that are working on web agent, list their names, locations and link"
    )
    logging.info(response)
    return response
