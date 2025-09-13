# retriever.py - simplified version without NLTK
import math
import re
from collections import Counter

def tokenize(s: str):
    s = s.lower()
    # Remove special characters but keep basic punctuation
    s = re.sub(r'[^a-z0-9\s\.\?\!]', ' ', s)
    # Split by spaces and common punctuation
    tokens = re.findall(r'\b[a-z0-9]{3,}\b', s)  # words with 3+ characters
    return tokens

def vectorize(tokens):
    return Counter(tokens)

def cosine_sim(a: Counter, b: Counter):
    intersection = set(a.keys()) & set(b.keys())
    num = sum(a[x] * b[x] for x in intersection)
    denom_a = math.sqrt(sum(v*v for v in a.values()))
    denom_b = math.sqrt(sum(v*v for v in b.values()))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return num / (denom_a * denom_b)

def rank_chunks(chunks: list, query: str, top_k: int = 5):
    qvec = vectorize(tokenize(query))
    scored = []
    for c in chunks:
        tvec = vectorize(tokenize(c.get("text","")))
        sc = cosine_sim(qvec, tvec)
        scored.append((sc, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [c for s,c in scored[:top_k] if s > 0.1]  # Minimum similarity threshold
    return top