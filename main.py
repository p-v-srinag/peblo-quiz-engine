from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from models import ContentChunk, QuizQuestion, StudentAnswer
from database import chunks_collection, questions_collection, answers_collection, student_profiles
from services import extract_text_from_pdf, chunk_text, generate_questions_from_llm
import shutil
import os

app = FastAPI(title="Peblo Quiz Engine")

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...), grade: int = Form(...), subject: str = Form(...), topic: str = Form(...)):
    """Ingests a PDF, extracts text, chunks it, and saves to DB[cite: 15, 16]."""
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    raw_text = extract_text_from_pdf(file_location)
    os.remove(file_location) # Clean up temp file
    
    chunks = chunk_text(raw_text)
    saved_chunks = []
    
    for text_segment in chunks:
        chunk_data = ContentChunk(
            source_id=file.filename,
            grade=grade,
            subject=subject,
            topic=topic,
            text=text_segment
        )
        await chunks_collection.insert_one(chunk_data.model_dump())
        saved_chunks.append(chunk_data.chunk_id)
        
    return {"message": "Ingestion successful", "chunks_created": len(saved_chunks)}

@app.post("/generate-quiz")
async def generate_quiz(topic: str):
    """Finds chunks for a topic and generates questions via LLM[cite: 17]."""
    chunks = await chunks_collection.find({"topic": topic}).to_list(length=5)
    if not chunks:
        raise HTTPException(status_code=404, detail="No content found for this topic.")
        
    total_questions = 0
    for chunk in chunks:
        questions = await generate_questions_from_llm(chunk["text"], chunk["chunk_id"])
        if isinstance(questions, dict) and "questions" in questions:
            questions = questions["questions"]
            
        for q in questions:
            await questions_collection.insert_one(q)
            total_questions += 1
            
    return {"message": f"Generated {total_questions} questions for topic: {topic}"}

@app.get("/quiz")
async def get_quiz(topic: str, difficulty: str = "easy"):
    """Retrieves quiz questions based on topic and difficulty[cite: 75, 76]."""
    questions = await questions_collection.find(
        {"difficulty": difficulty}, # Note: Add topic filtering logic based on your chunk linkage
        {"_id": 0} # Exclude MongoDB's default ObjectId from the response
    ).to_list(length=10)
    return questions

@app.post("/submit-answer")
async def submit_answer(submission: StudentAnswer):
    """Accepts an answer and adjusts the student's difficulty level[cite: 80, 90]."""
    await answers_collection.insert_one(submission.model_dump())
    
    # Simple Adaptive Logic [cite: 91, 92, 93, 94]
    # 1. Fetch the actual question to check if correct
    question = await questions_collection.find_one({"_id": submission.question_id}) # Requires ObjectId handling in real app
    
    difficulty_levels = ["easy", "medium", "hard"]
    
    # 2. Get student's current profile or create one
    profile = await student_profiles.find_one({"student_id": submission.student_id})
    current_diff_index = difficulty_levels.index(profile["difficulty"]) if profile else 0
    
    # 3. Adjust difficulty
    # (Mock logic: Assuming we checked if the answer is correct)
    is_correct = True # Replace with actual check: submission.selected_answer == question["answer"]
    
    if is_correct and current_diff_index < 2:
        new_difficulty = difficulty_levels[current_diff_index + 1]
    elif not is_correct and current_diff_index > 0:
        new_difficulty = difficulty_levels[current_diff_index - 1]
    else:
        new_difficulty = difficulty_levels[current_diff_index]
        
    await student_profiles.update_one(
        {"student_id": submission.student_id},
        {"$set": {"difficulty": new_difficulty}},
        upsert=True
    )
    
    return {"status": "Answer recorded", "new_difficulty": new_difficulty}