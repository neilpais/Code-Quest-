"use client"

import { useState } from "react"
import axios from "axios"

export default function Page() {
  const [codeFile, setCodeFile] = useState<File | null>(null)
  const [questions, setQuestions] = useState<any[]>([])
  const [answers, setAnswers] = useState<any>({})
  const [codeAnswers, setCodeAnswers] = useState<any>({})
  const [results, setResults] = useState<any>({})
  const [submissionId, setSubmissionId] = useState<number | null>(null)
  const [darkMode, setDarkMode] = useState(true)
  const [loading, setLoading] = useState(false)

  const handleAnalyze = async () => {
    if (!codeFile) {
      alert("Upload a .c file first")
      return
    }

    setLoading(true)

    const formData = new FormData()
    formData.append("file", codeFile)

    try {
      const res = await axios.post("http://127.0.0.1:8000/analyze", formData)
      setQuestions(res.data.questions)
      setSubmissionId(res.data.submission_id)
    } catch (err) {
      alert("Error generating quest")
    } finally {
      setLoading(false)
    }
  }

  const runTests = async (index: number) => {
    const formData = new FormData()
    formData.append("file", codeFile!)
    formData.append("submission_id", String(submissionId))
    formData.append("question_index", String(index))

    const res = await axios.post("http://127.0.0.1:8000/submit", formData)

    const jobId = res.data.job_id

    const interval = setInterval(async () => {
      const r = await axios.get(`http://127.0.0.1:8000/job/${jobId}`)

      if (r.data.status === "finished") {
        setResults((prev: any) => ({
          ...prev,
          [index]: r.data.result,
        }))
        clearInterval(interval)
      }
    }, 1500)
  }

  const calculateScore = () => {
    let score = 0

    questions.forEach((q, i) => {
      if (q.type === "general_programming") {
        if (answers[i] === q.correct_answer) score++
      }
    })

    alert(`Score: ${score}/${questions.length}`)
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "20px",
        background: darkMode
          ? "linear-gradient(135deg, #020617, #0f172a)"
          : "linear-gradient(135deg, #e2e8f0, #f8fafc)",
        color: darkMode ? "#e2e8f0" : "#0f172a",
        fontFamily: "inherit",
      }}
    >
      {/* HEADER */}
      <h1
        style={{
          textAlign: "center",
          fontSize: "32px",
          letterSpacing: "1px",
          textShadow: "0 2px 10px rgba(34,197,94,0.5)",
        }}
      >
        🎮 Code Quest
      </h1>

      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <button
          onClick={() => setDarkMode(!darkMode)}
          style={{
            padding: "10px 18px",
            borderRadius: "10px",
            border: "none",
            cursor: "pointer",
            background: "#22c55e",
            color: "white",
            fontWeight: "bold",
            boxShadow: "0 0 12px rgba(34,197,94,0.6)",
          }}
        >
          Toggle {darkMode ? "Light" : "Dark"}
        </button>
      </div>

      {/* FILE UPLOAD */}
      <div style={{ textAlign: "center", marginTop: "20px" }}>
        <input
          type="file"
          accept=".c"
          id="fileUpload"
          style={{ display: "none" }}
          onChange={(e) => setCodeFile(e.target.files?.[0] || null)}
        />

        <label htmlFor="fileUpload">
          <div
            style={{
              border: "2px dashed #22c55e",
              padding: "25px",
              cursor: "pointer",
              borderRadius: "14px",
              background: darkMode ? "#020617" : "#e2e8f0",
              boxShadow: "0 0 20px rgba(34,197,94,0.2)",
              transition: "0.25s",
            }}
          >
            <div style={{ fontSize: "28px" }}>📂</div>
            <div style={{ fontSize: "16px", marginTop: "6px" }}>
              Click to Upload C File
            </div>
          </div>
        </label>

        {codeFile && (
          <div
            style={{
              marginTop: "12px",
              color: "#22c55e",
              fontWeight: "bold",
            }}
          >
            ✅ Current File: {codeFile.name}
          </div>
        )}

        {/* BUTTON */}
        <div style={{ marginTop: "20px" }}>
          <button
            onClick={handleAnalyze}
            disabled={loading}
            style={{
              padding: "14px 28px",
              borderRadius: "14px",
              border: "none",
              cursor: "pointer",
              background: loading
                ? "#64748b"
                : "linear-gradient(135deg,#22c55e,#4ade80)",
              color: "white",
              fontSize: "17px",
              fontWeight: "bold",
              boxShadow: "0 6px 20px rgba(34,197,94,0.4)",
              transform: "scale(1)",
              transition: "0.2s",
            }}
            onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.96)")}
            onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
          >
            {loading ? "Generating Quest... ⏳" : "Generate Quest 🎯"}
          </button>
        </div>
      </div>

      {/* LOADING */}
      {loading && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            background: "rgba(0,0,0,0.85)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            flexDirection: "column",
            zIndex: 1000,
            color: "white",
            fontSize: "24px",
          }}
        >
          <div className="spinner" style={{ marginBottom: "20px" }} />
          Generating Quest...
        </div>
      )}

      {/* QUESTIONS */}
      <div style={{ marginTop: "30px" }}>
        {questions.map((q, index) => (
          <div
            key={index}
            style={{
              border: "1px solid rgba(34,197,94,0.4)",
              padding: "18px",
              marginBottom: "20px",
              borderRadius: "12px",
              backdropFilter: "blur(8px)",
              background: "rgba(2,6,23,0.6)",
              boxShadow: "0 4px 15px rgba(0,0,0,0.4)",
            }}
          >
            <p style={{ fontWeight: "bold", marginBottom: "10px" }}>
              {q.question}
            </p>

            {q.type === "general_programming" &&
              q.options?.map((opt: string, i: number) => (
                <div key={i} style={{ marginBottom: "6px" }}>
                  <input
                    type="radio"
                    name={`q${index}`}
                    value={opt[0]}
                    onChange={(e) =>
                      setAnswers({ ...answers, [index]: e.target.value })
                    }
                  />
                  <span style={{ marginLeft: "6px" }}>{opt}</span>
                </div>
              ))}

            {q.type === "code_specific" && (
              <div>
                <textarea
                  placeholder="Write your code here..."
                  style={{
                    width: "100%",
                    height: "120px",
                    borderRadius: "8px",
                    padding: "8px",
                    marginTop: "10px",
                  }}
                  onChange={(e) =>
                    setCodeAnswers({
                      ...codeAnswers,
                      [index]: e.target.value,
                    })
                  }
                />

                <button
                  onClick={() => runTests(index)}
                  style={{
                    marginTop: "10px",
                    padding: "10px 18px",
                    borderRadius: "10px",
                    border: "none",
                    background: "#38bdf8",
                    color: "white",
                    cursor: "pointer",
                    boxShadow: "0 4px 12px rgba(56,189,248,0.5)",
                  }}
                >
                  Run Tests 🧪
                </button>

                {results[index] && (
                  <pre style={{ marginTop: "10px" }}>
                    {JSON.stringify(results[index], null, 2)}
                  </pre>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {questions.length > 0 && (
        <div style={{ textAlign: "center" }}>
          <button
            onClick={calculateScore}
            style={{
              padding: "12px 24px",
              borderRadius: "12px",
              border: "none",
              background: "#facc15",
              color: "black",
              fontWeight: "bold",
              cursor: "pointer",
              boxShadow: "0 4px 12px rgba(250,204,21,0.5)",
            }}
          >
            Show Score 🏆
          </button>
        </div>
      )}

      <style>{`
        .spinner {
          border: 6px solid #f3f3f3;
          border-top: 6px solid #22c55e;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
