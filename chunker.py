# chunker.py - improved version
import re
import uuid

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """
    Improved chunker that tries to preserve paragraph structure
    """
    # Split by paragraphs first
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = []
    current_length = 0
    idx = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        para_length = len(para)
        
        # If adding this paragraph would exceed chunk size, save current chunk
        if current_length + para_length > chunk_size and current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({
                "id": f"chunk_{idx}_{uuid.uuid4().hex[:8]}",
                "text": chunk_text
            })
            idx += 1
            
            # Keep overlap for context preservation
            if overlap > 0:
                # Keep last few paragraphs for overlap
                overlap_text = []
                overlap_length = 0
                while current_chunk and overlap_length < overlap:
                    last_para = current_chunk.pop()
                    overlap_text.insert(0, last_para)
                    overlap_length += len(last_para)
                current_chunk = overlap_text
                current_length = overlap_length
            else:
                current_chunk = []
                current_length = 0
        
        current_chunk.append(para)
        current_length += para_length
    
    # Add the last chunk
    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunks.append({
            "id": f"chunk_{idx}_{uuid.uuid4().hex[:8]}",
            "text": chunk_text
        })
    
    return chunks