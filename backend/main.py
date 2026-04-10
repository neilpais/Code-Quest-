from fastapi import UploadFile, File, Form, Request
from rq.job import Job
import redis
from queue_worker import enqueue_job
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from models import Submission
from database import SessionLocal
from fastapi import Depends
from sqlalchemy.orm import Session
from database import engine
from models import Base
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from code_analysis import analyze_code
import json


from agent import process_code
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
    concept=json.dumps(result["concept_analysis"]),   # ✅ convert dict → string
    questions=json.dumps(result["questions"])         # ✅ convert list → string
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
    # ✅ Validate file type
    if not file.filename.endswith(".c"):
        return {"error": "Only .c files allowed"}

    # ✅ Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # ✅ Fetch tests from DB
    submission = db.query(Submission).filter(
        Submission.id == submission_id
    ).first()

    if not submission:
        return {"error": "Submission not found"}

    questions = json.loads(submission.questions)   # ✅ convert back

    question = questions[question_index]
    tests = question.get("tests", [])

    # ✅ Pass FILE PATH (not code)
    job_id = enqueue_job(file_path, tests)

    return {"job_id": job_id}


@app.post("/run")
def run(answer: AnswerSubmission):

    output = run_code(answer.code, answer.input)

    return {"output": output}


@app.get("/job/{job_id}")
def get_job(job_id: str):

    job = Job.fetch(job_id, connection=redis_conn)

    print("JOB STATUS:", job.get_status())  # 👈 ADD THIS

    if job.is_finished:
        return {"status": "finished", "result": job.result}

    if job.is_failed:
        print("JOB FAILED:", job.exc_info)  # 👈 ADD THIS
        return {
            "status": "failed",
            "error": job.exc_info
        }

    return {"status": "running"}
