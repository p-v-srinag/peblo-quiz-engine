import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("DATABASE_URL")
if not MONGO_URL:
    raise ValueError("No DATABASE_URL found in .env file")

client = AsyncIOMotorClient(MONGO_URL)
db = client.peblo_db

# Collections
chunks_collection = db.chunks
questions_collection = db.questions
answers_collection = db.student_answers
student_profiles = db.student_profiles # To track difficulty levels