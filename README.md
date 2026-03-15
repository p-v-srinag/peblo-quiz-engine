# Peblo AI - Content Ingestion & Adaptive Quiz Engine

This repository contains a prototype backend system designed to ingest educational PDFs, extract and chunk the content, and utilize Large Language Models (LLMs) to automatically generate structured, adaptive quiz questions. This project was built for the Peblo AI Backend Engineer Challenge.

##  System Architecture

The system is built with a modern, asynchronous Python stack designed for speed and clean data modeling:

* **Backend Framework:** **FastAPI**. Chosen for its high performance, native asynchronous support, and automatic generation of interactive API documentation (Swagger UI).
* **Database:** **MongoDB** (using the `motor` async driver). A NoSQL database is ideal here due to the flexible, document-based nature of text chunks and highly nested JSON quiz schemas.
* **AI Integration:** **Google Gemini 2.5 Flash**. Utilized for fast, highly structured JSON data generation, ensuring the AI outputs perfectly map to our Pydantic database models.
* **PDF Processing:** **pdfplumber** is used for robust text extraction before the text is chunked into manageable segments.

##  Setup Instructions

### 1. Prerequisites
Ensure you have the following installed on your system:
* Python 3.9+
* A MongoDB cluster (MongoDB Atlas or a local instance)
* A Google Gemini API Key

### 2. Installation
Clone the repository and navigate into the project directory:

```bash
git clone [https://github.com/p-v-srinag/peblo-quiz-engine.git](https://github.com/p-v-srinag/peblo-quiz-engine.git)
cd peblo-quiz-engine
```

Set up and activate a Python virtual environment to isolate dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory. You can use the provided `.env.example` as a template. Do not commit your actual `.env` file to version control.

```env
DATABASE_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
LLM_API_KEY=your_actual_gemini_api_key_here
```

### 4. Running the Backend
Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```
The server will start on `http://127.0.0.1:8000`.

##  Testing the Endpoints

FastAPI automatically generates an interactive testing UI. Once the server is running, open your browser and navigate to:
**http://127.0.0.1:8000/docs**

From this interface, you can test the entire pipeline in order:

1. **`POST /ingest`**: Upload a PDF file, assign it a grade, subject, and topic. The system will extract the text, chunk it, and save the chunks to MongoDB.
2. **`POST /generate-quiz`**: Provide a topic (e.g., "Machine Learning"). The system queries the database for relevant chunks and prompts the LLM to generate MCQ, True/False, and Fill-in-the-blank questions.
3. **`GET /quiz`**: Retrieve a list of generated questions filtered by topic and difficulty level.
4. **`POST /submit-answer`**: Accepts student answers, validates them, and adjusts the student's difficulty profile.

##  Adaptive Difficulty Logic

The system implements a simple adaptive learning path to tailor the experience to the student's performance. 

When a student submits an answer via the `/submit-answer` endpoint, the system fetches the correct answer from the database and evaluates the response. 
* **If Correct:** The student's profile is upgraded to the next difficulty tier (e.g., from `easy` to `medium`).
* **If Incorrect:** The difficulty tier is downgraded (e.g., from `medium` to `easy`).

Subsequent calls to the `/quiz` endpoint will then dynamically fetch questions matching the student's newly adjusted cognitive level.
