# College Chatbot Demo (Hackathon starter)

This is a minimal, hackathon-friendly demo that shows how to:
1. Scrape a single site page and extract text.
2. Chunk the scraped text and store it locally.
3. Run a lightweight retrieval (bag-of-words + cosine similarity) to pick relevant chunks.
4. Send those top chunks + user question to Gemini (or any LLM) to get a final answer.
5. Simple frontend to trigger scraping and ask questions.

### Quick start (local)
1. Create a Python virtualenv and install requirements:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Set your Gemini/OpenAI API key in the environment if you integrate the real client:
   ```
   export GEMINI_API_KEY="your_key_here"
   ```
3. Run the backend:
   ```
   uvicorn backend.app:app --reload --port 8000
   ```
4. Open `frontend/index.html` in your browser (or serve it with a static server).

### Notes
- This project intentionally avoids using a vector DB. It uses a simple local chunk store (JSON).
- The `ask_gemini` function is a stub that returns a mock answer. Replace it with your real Gemini/OpenAI client calls.
- For multi-page scraping, extend `scraper.scrape_site` to crawl links and aggregate pages.
