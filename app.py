from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scraper import scrape_website
from storage import load_chunks, save_chunks, save_raw
from chunker import chunk_text
from retriever import rank_chunks  # Add this import
from gemini_client import ask_gemini  # Add this import
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str

class AskRequest(BaseModel):
    question: str

@app.post("/scrape")
def scrape(req: ScrapeRequest):
    result = scrape_website(req.url, max_depth=4, max_pages=67)
    return result

@app.post("/ask")
def ask(req: AskRequest):
    chunks = load_chunks()

    if not chunks:
        return {"answer": "I don't know. The provided context is empty.", "used_chunks": []}

    # Use retriever to find relevant chunks instead of random selection
    relevant_chunks = rank_chunks(chunks, req.question, top_k=5)
    
    if not relevant_chunks:
        return {"answer": "I couldn't find relevant information to answer your question.", "used_chunks": []}

    # Extract text from relevant chunks
    context_texts = [chunk["text"] for chunk in relevant_chunks]
    
    # Get answer from Gemini with proper context
    answer = ask_gemini(req.question, context_texts)
    
    return {
        "answer": answer, 
        "used_chunks": [chunk["id"] for chunk in relevant_chunks]
    }