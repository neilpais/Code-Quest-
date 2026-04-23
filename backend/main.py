from fastapi import UploadFile, File, Depends, FastAPI
from models import Submission, Base
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from code_analysis import analyze_code
import json
import os

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# ✅ CORS (required for Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change later to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB setup
Base.metadata.create_all(bind=engine)


# ✅ Request model for MCQ
class MCQSubmission(BaseModel):
    submission_id: int
    question_index: int
    selected_option: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Health check
@app.get("/")
def home():
    return {"message": "MCQ API running 🚀"}


# ✅ Generate MCQs
@app.post("/analyze")
def analyze(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".c"):
        return {"error": "Only .c files allowed"}

    code = file.file.read().decode("utf-8")

    result = analyze_code(code, assignment="A1")

    # IMPORTANT: make sure result["questions"] ONLY contains MCQs
    new_submission = Submission(
        code=code,
        concept=json.dumps(result.get("concept_analysis", {})),
        questions=json.dumps(result["questions"])
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return {
        "questions": result["questions"],
        "submission_id": new_submission.id
    }


# ✅ Submit MCQ answer
@app.post("/submit-mcq")
def submit_mcq(answer: MCQSubmission, db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(
        Submission.id == answer.submission_id
    ).first()

    if not submission:
        return {"error": "Submission not found"}

    questions = json.loads(submission.questions)

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
