import pdfplumber
import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configure the NEW Gemini API Client
client = genai.Client(api_key=os.getenv("LLM_API_KEY"))

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts raw text from a given PDF file."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def chunk_text(text: str, chunk_size: int = 1000) -> list:
    """Breaks raw text into manageable segments."""
    words = text.split()
    chunks = []
    current_chunk = []
    
    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

async def generate_questions_from_llm(chunk_text: str, chunk_id: str):
    """Uses Gemini to generate quiz questions from text."""
    
    prompt = f"""
    You are an expert educational AI. Based on the following text, generate 3 quiz questions.
    Include a mix of Multiple Choice Questions (MCQ), True / False, and Fill in the blank.
    
    Format the output EXACTLY as a JSON array of objects with the following keys:
    "question" (string), "type" (string: "MCQ", "True/False", or "Fill in the blank"), "options" (array of strings, or null if not MCQ), "answer" (string), "difficulty" (string: "easy", "medium", or "hard"), "source_chunk_id" (string: exactly "{chunk_id}").

    Text Context:
    {chunk_text}
    """

    try:
        # Requesting a JSON response directly from Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        
        # Parse the JSON string returned by the LLM
        content = json.loads(response.text)
        
        # FIX: Check if it's a list or a dict to prevent the 'get' error
        if isinstance(content, list):
            return content
        elif isinstance(content, dict):
            return content.get("questions", [])
        else:
            return []
            
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []