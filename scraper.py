import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from storage import save_raw, save_chunks
from chunker import chunk_text
import pdfplumber
import io
import re

visited = set()

def get_file_type(url, resp):
    """Determine file type from URL and response headers"""
    content_type = resp.headers.get("Content-Type", "").lower()
    path = urlparse(url).path.lower()
    
    # PDF detection
    if 'application/pdf' in content_type or path.endswith('.pdf'):
        return 'pdf'
    
    # Word documents
    if ('application/msword' in content_type or 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type or
        path.endswith(('.doc', '.docx'))):
        return 'doc'
    
    # Excel files
    if ('application/vnd.ms-excel' in content_type or
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type or
        path.endswith(('.xls', '.xlsx'))):
        return 'excel'
    
    # Powerpoint
    if ('application/vnd.ms-powerpoint' in content_type or
        'application/vnd.openxmlformats-officedocument.presentationml.presentation' in content_type or
        path.endswith(('.ppt', '.pptx'))):
        return 'ppt'
    
    # Text files
    if 'text/plain' in content_type or path.endswith('.txt'):
        return 'text'
    
    # JSON
    if 'application/json' in content_type or path.endswith('.json'):
        return 'json'
    
    # HTML/PHP/ASP - treat all as HTML
    if ('text/html' in content_type or 
        path.endswith(('.html', '.htm', '.php', '.asp', '.aspx', '.jsp'))):
        return 'html'
    
    return 'unknown'

def is_json_response(resp):
    try:
        resp.json()
        return True
    except Exception:
        return False

def extract_text_from_pdf(pdf_content):
    """Extract text from PDF bytes"""
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
    return text

def extract_text_from_docx(doc_content):
    """Placeholder for Word document extraction"""
    # For now, return empty string - you can add docx support later
    print("⚠️  Word document detected but not processed (add python-docx library)")
    return ""

def extract_text_from_text_file(content):
    """Extract text from plain text files"""
    try:
        return content.decode('utf-8')
    except:
        try:
            return content.decode('latin-1')
        except:
            return ""

def scrape_page(url, base_domain, all_chunks, depth, max_depth, max_pages):
    """
    Enhanced to handle multiple file types
    """
    if depth > max_depth:
        return
    if len(visited) >= max_pages:
        return

    print(f"Scraping: {url}")
    try:
        resp = requests.get(url, timeout=15)
    except Exception as e:
        print(f"❌ Failed: {url} -> {e}")
        return

    text_data = ""
    file_type = get_file_type(url, resp)

    # Handle different file types
    if file_type == 'pdf':
        print(f"✅ PDF found: {url}")
        text_data = extract_text_from_pdf(resp.content)
    
    elif file_type == 'doc':
        print(f"✅ Word document found: {url}")
        text_data = extract_text_from_docx(resp.content)
    
    elif file_type == 'text':
        print(f"✅ Text file found: {url}")
        text_data = extract_text_from_text_file(resp.content)
    
    elif file_type == 'json':
        print(f"✅ JSON found: {url}")
        try:
            text_data = str(resp.json())
        except:
            text_data = resp.text
    
    elif file_type == 'html':
        print(f"✅ HTML/PHP page found: {url}")
        soup = BeautifulSoup(resp.text, "html.parser")
        text_data = soup.get_text(" ", strip=True)
        
        # Also extract text from meta description and title
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            text_data = meta_desc['content'] + " " + text_data
        
        title = soup.find('title')
        if title:
            text_data = title.get_text() + " " + text_data
    
    else:
        print(f"⚠️  Unsupported file type: {url} ({file_type})")
        return

    # Save chunks if text is found
    if text_data and text_data.strip():
        chunks = chunk_text(text_data)
        all_chunks.extend(chunks)
        print(f"   Extracted {len(chunks)} chunks from {file_type.upper()}")

    # Only follow links for HTML pages (not documents/files)
    if file_type == 'html' and depth < max_depth:
        soup = BeautifulSoup(resp.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Skip javascript links and anchors
            if href.startswith(('javascript:', '#', 'mailto:', 'tel:')):
                continue
                
            full_url = urljoin(url, href)

            # stay in same domain
            if urlparse(full_url).netloc != base_domain:
                continue

            if full_url not in visited and len(visited) < max_pages:
                visited.add(full_url)
                scrape_page(full_url, base_domain, all_chunks, depth + 1, max_depth, max_pages)

def scrape_website(start_url: str, max_depth: int = 3, max_pages: int = 50):
    """
    Enhanced scraper for college websites - handles HTML, PHP, PDFs, and more!
    """
    domain = urlparse(start_url).netloc
    all_chunks = []
    visited.clear()
    visited.add(start_url)

    scrape_page(start_url, domain, all_chunks, depth=0, max_depth=max_depth, max_pages=max_pages)

    # Save everything
    full_text = "\n\n".join([c["text"] for c in all_chunks])
    save_raw(full_text)
    save_chunks(all_chunks)

    return {
        "status": "ok", 
        "scraped_pages": len(visited), 
        "chunks": len(all_chunks),
        "message": f"Scraped {len(visited)} URLs and extracted {len(all_chunks)} chunks"
    }