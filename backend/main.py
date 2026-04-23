from fastapi import UploadFile, File, Form, Request, Depends, FastAPI
from rq.job import Job
import redis
from queue_worker import enqueue_job
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from models import Submission, Base
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from code_analysis import analyze_code
from code_runner import run_code
import json
import os

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_conn = redis.Redis()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

Base.metadata.create_all(bind=engine)


class AnalyzeRequest(BaseModel):
    code: str


class SubmitRequest(BaseModel):
    code: str
    question_index: int
    submission_id: int


class AnswerSubmission(BaseModel):
    code: str
    input: str


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


@app.get("/")
def home():
    return {"message": "Assignment Coach API running"}


@app.post("/analyze")
def analyze(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".c"):
        return {"error": "Only .c files allowed"}

    code = file.file.read().decode("utf-8")
    result = analyze_code(code, assignment="A1")

    new_submission = Submission(
        code=code,
        concept=json.dumps(result["concept_analysis"]),
        questions=json.dumps(result["questions"])
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return {
        "questions": result["questions"],
        "submission_id": new_submission.id
    }


@app.post("/submit")
@limiter.limit("5/minute")
def submit(
    request: Request,
    file: UploadFile = File(...),
    submission_id: int = Form(...),
    question_index: int = Form(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".c"):
        return {"error": "Only .c files allowed"}

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()

    if not submission:
        return {"error": "Submission not found"}

    questions = json.loads(submission.questions)

    if question_index < 0 or question_index >= len(questions):
        return {"error": "Invalid question index"}

    question = questions[question_index]
    tests = question.get("tests", [])

    job_id = enqueue_job(file_path, tests)
    return {"job_id": job_id}


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


@app.post("/run")
def run(answer: AnswerSubmission):
    result = run_code(answer.code, answer.input)
    return result


@app.get("/job/{job_id}")
def get_job(job_id: str):
    job = Job.fetch(job_id, connection=redis_conn)

    if job.is_finished:
        return {"status": "finished", "result": job.result}

    if job.is_failed:
        return {
            "status": "failed",
            "error": job.exc_info
        }

    return {"status": "running"}
