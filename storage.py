import os, json
BASE = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(BASE, exist_ok=True)
RAW_PATH = os.path.join(BASE, "raw.txt")
CHUNKS_PATH = os.path.join(BASE, "chunks.json")

def save_raw(text: str):
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        f.write(text)

def load_raw() -> str:
    if not os.path.exists(RAW_PATH):
        return ""
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        return f.read()

def save_chunks(chunks: list):
    # chunks is list of dicts with id and text
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def load_chunks() -> list:
    if not os.path.exists(CHUNKS_PATH):
        return []
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
# Alias to match app.py import
save_text = save_raw
