# gemini_client.py - improved prompt
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(user_query: str, context_chunks: list[str]) -> str:
    """
    Improved prompt for better college-specific answers
    """
    context_text = "\n\n---\n\n".join(context_chunks)

    prompt = f"""
    ROLE: You are a helpful college assistant chatbot specifically trained on the college's website content.

    CONTEXT FROM COLLEGE WEBSITE:
    {context_text}

    USER QUESTION: {user_query}

    INSTRUCTIONS:
    1. Answer ONLY using the information provided in the context above
    2. Be specific, accurate, and concise
    3. If the information is not in the context, say "I don't have that information in my knowledge base. Please check the college website or contact the administration directly."
    4. Format your answer clearly with proper structure
    5. If referring to specific departments, programs, or contacts, be precise

    ANSWER:
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error while processing your request: {str(e)}"