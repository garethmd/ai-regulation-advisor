import logging
import os
import pickle

import chromadb
import fitz  # PyMuPDF
from dotenv import load_dotenv

# from llama_index.agents import BaseAgent
from llama_index.core import (
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

# from llama_index.workflows import BaseWorkflow

load_dotenv()

# Access the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the .env file")

print(f"Your API Key: {OPENAI_API_KEY}")  # Just for debugging; remove in production


# Step 1: Extract text from the PDF
def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page in document:
        text += page.get_text()
    return text


def get_legislation_embeddings(
    pdf_path: str = "../../../data/Artificial Intelligence 2024 Legislation.pdf",
) -> VectorStoreIndex:
    # Path to your PDF file
    legislation_text = extract_text_from_pdf(pdf_path)
    splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=50)
    logging.info(f"{pdf_path} NOT FOUND chunking and embedding")
    text_chunks = splitter.split_text(legislation_text)

    if os.path.exists(f"{pdf_path}.pkl"):
        logging.info(f"{pdf_path} found loading")
        with open(f"{pdf_path}.pkl", "rb") as f:
            embeddings = pickle.load(f)
    else:
        # Code to generate embeddings with OpenAI
        # Split the text into chunks

        # Step 3: Generate embeddings for each chunk
        openai_model = OpenAIEmbedding(model="text-embedding-ada-002")
        embeddings = [openai_model.get_text_embedding(chunk) for chunk in text_chunks]
        logging.info(f"created {len(embeddings)} chunks")
        with open(f"{pdf_path}.pkl", "wb") as f:
            pickle.dump(embeddings, f)

    # Initialize Chroma client
    client = chromadb.PersistentClient(path="./chroma_db")
    chroma_collection = client.get_or_create_collection("my_collection")
    # Create a Chroma vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    # Create nodes with embeddings
    nodes = [
        TextNode(text=text, embedding=embedding)
        for text, embedding in zip(text_chunks, embeddings)
    ]
    # Add nodes to the Chroma vector store
    vector_store.add(nodes)
    # Create a VectorStoreIndex using the Chroma vector store
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    vector_store_index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)
    return vector_store_index


if __name__ == "__main__":
    index = get_legislation_embeddings()
    query_engine = index.as_query_engine()
    response = query_engine.query("Which pieces of legislation are enacted?")
    print(f"<b>{response}</b>")

# class ImpactAnalysisAgent(BaseAgent):

#     def analyze_impact(self, embeddings):
#         # Implement logic to analyze the impact
#         # For example, compare embeddings with company data
#         impact_results = ()
#         # Pseudo-code for analysis
#         # for legislation in document_embedding:
#         #     impact_results[legislation] = some_analysis_function(legislation, company_data)
#         return impact_results


# class ImpactAnalysisWorkflow(BaseWorkflow):
#     def run(self, document_embedding):
#         agent = ImpactAnalysisAgent()
#         impact_analysis = agent.analyze_impact(document_embedding)
#         return impact_analysis


# # Execute the workflow
# workflow = ImpactAnalysisWorkflow()
# impact_report = workflow.run(embeddings)


# def generate_report(impact_analysis):
#     report = "Legislation Impact Report\n\n"
#     for legislation, impact in impact_analysis.items():
#         report += f"Legislation: {legislation}\nImpact: {impact}\n\n"
#     return report


# # Generate and print the report
# report = generate_report(impact_report)
# print(report)
