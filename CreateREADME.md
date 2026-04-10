# 🚀 Code Quest

Code Quest is an AI-powered full-stack application that analyzes user-submitted code and generates personalized learning content, including conceptual questions, implementation tasks, and automated test cases.

---

## ✨ Features

- 🤖 AI-driven code analysis using Large Language Models (LLMs)
- 🧠 Generates conceptual and implementation-based questions
- 🧪 Automated test case generation and execution
- 🔒 Secure sandboxed code execution using Docker
- ⚡ Asynchronous task processing with Redis and RQ
- 🌐 Interactive frontend with real-time feedback

---

## 🏗️ Architecture

- **Backend:** FastAPI (Python)
- **Frontend:** Next.js (TypeScript)
- **Database:** PostgreSQL
- **Queue System:** Redis + RQ
- **Sandboxing:** Docker (secure execution environment)
- **AI Integration:** OpenAI API (LLM-based generation)

---

## 📁 Project Structure
backend/ # FastAPI backend
frontend/ # Next.js frontend
sandbox/ # Code execution environment
requirements.txt


---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/neilpais/Code-Quest-.git
cd Code-Quest-
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt

Create a .env file inside the backend/ directory:

OPENAI_API_KEY=your_api_key_here

Setup backend: uvicorn main:app --reload
Steup frontend:
cd frontend
npm install
npm run dev

Get the redis server up and running:
redis-server
rq worker sandbox

🚀 Future Improvements
Multi-language support (C/C++)
Enhanced test case generation
User authentication and dashboards
Adaptive learning paths based on performance

👨‍💻 Author

Neil Allister Pais

GitHub: https://github.com/neilpais
LinkedIn: https://linkedin.com/in/neil-allister-pais

📌 Notes

This project demonstrates:

Full-stack application development
Scalable backend system design
Secure execution environments
Integration of AI/LLMs into real-world applications

