from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class ContentChunk(BaseModel):
    source_id: str
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    grade: int
    subject: str
    topic: str
    text: str

class QuizQuestion(BaseModel):
    question: str
    type: str = Field(..., description="MCQ, True/False, or Fill in the blank")
    options: Optional[List[str]] = None
    answer: str
    difficulty: str = Field(..., description="easy, medium, or hard")
    source_chunk_id: str

class StudentAnswer(BaseModel):
    student_id: str
    question_id: str
    selected_answer: str
    topic: str # Keeping track of topic helps with adaptive logic