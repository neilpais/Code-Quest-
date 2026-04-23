from fastapi import UploadFile, File, FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from code_analysis import analyze_code
import os

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# ✅ CORS (required for Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Simple in-memory storage (temporary)
submissions_store = {}

# ✅ Request model for MCQ
class MCQSubmission(BaseModel):
    submission_id: int
    question_index: int
    selected_option: str


# ✅ Health check
@app.get("/")
def home():
    return {"message": "MCQ API running 🚀"}


# ✅ Generate MCQs (NO DB)
@app.post("/analyze")
def analyze(file: UploadFile = File(...)):
    if not file.filename.endswith(".c"):
        return {"error": "Only .c files allowed"}

    code = file.file.read().decode("utf-8")

    result = analyze_code(code, assignment="A1")

    # store questions in memory
    submission_id = len(submissions_store) + 1
    submissions_store[submission_id] = result["questions"]

    return {
        "questions": result["questions"],
        "submission_id": submission_id
    }


# ✅ Submit MCQ answer (NO DB)
@app.post("/submit-mcq")
def submit_mcq(answer: MCQSubmission):
    questions = submissions_store.get(answer.submission_id)

    if not questions:
        return {"error": "Submission not found"}

    if answer.question_index < 0 or answer.question_index >= len(questions):
        return {"error": "Invalid question index"}

    question = questions[answer.question_index]

    correct_option = question.get("correct_answer", "")
    is_correct = answer.selected_option == correct_option

    return {
        "correct": is_correct,
        "selected_option": answer.selected_option,
        "correct_option": correct_option
    }
