"use client"

import { useState } from "react"
import axios from "axios"

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function Page() {
  const [codeFile, setCodeFile] = useState<File | null>(null)
  const [questions, setQuestions] = useState<any[]>([])
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [submissionId, setSubmissionId] = useState<number | null>(null)
  const [darkMode, setDarkMode] = useState(true)
  const [loading, setLoading] = useState(false)

  const [questionResults, setQuestionResults] = useState<Record<number, boolean>>({})
  const [mcqFeedback, setMcqFeedback] = useState<Record<number, any>>({})

  const score = Object.values(questionResults).filter(Boolean).length

  const updateQuestionScore = (questionIndex: number, isCorrect: boolean) => {
    setQuestionResults((prev) => ({
      ...prev,
      [questionIndex]: isCorrect,
    }))
  }

  const handleAnalyze = async () => {
    if (!codeFile) {
      alert("Upload a file first")
      return
    }

    setLoading(true)

    const formData = new FormData()
    formData.append("file", codeFile)

    try {
      const res = await axios.post(`${API_BASE}/analyze`, formData)
      setQuestions(res.data.questions)
      setSubmissionId(res.data.submission_id)

      // reset state
      setQuestionResults({})
      setMcqFeedback({})
      setAnswers({})
    } catch (err) {
      alert("Error generating quest")
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitMCQ = async (index: number) => {
    if (submissionId === null) return

    const selectedOption = answers[index]
    if (!selectedOption) {
      alert("Please select an option first")
      return
    }

    try {
      const res = await axios.post(`${API_BASE}/submit-mcq`, {
        submission_id: submissionId,
        question_index: index,
        selected_option: selectedOption,
      })

      setMcqFeedback((prev) => ({
        ...prev,
        [index]: res.data,
      }))

      updateQuestionScore(index, !!res.data.correct)
    } catch (err) {
      alert("Error submitting MCQ answer")
    }
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
      }}
    >
      <h1
        style={{
          textAlign: "center",
          fontSize: "32px",
          textShadow: "0 2px 10px rgba(34,197,94,0.5)",
        }}
      >
        🎮 Code Quest
      </h1>

      {questions.length > 0 && (
        <div
          style={{
            textAlign: "center",
            margin: "16px 0",
            fontSize: "22px",
            fontWeight: "bold",
            color: "#facc15",
          }}
        >
          Score: {score} / {questions.length}
        </div>
      )}

      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <button
          onClick={() => setDarkMode(!darkMode)}
          style={{
            padding: "10px 18px",
            borderRadius: "10px",
            border: "none",
            background: "#22c55e",
            color: "white",
            cursor: "pointer",
          }}
        >
          Toggle {darkMode ? "Light" : "Dark"}
        </button>
      </div>

      {/* Upload */}
      <div style={{ textAlign: "center" }}>
        <input
          type="file"
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
            }}
          >
            📂 Upload File
          </div>
        </label>

        {codeFile && (
          <div style={{ marginTop: "10px", color: "#22c55e" }}>
            {codeFile.name}
          </div>
        )}

        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            marginTop: "20px",
            padding: "12px 24px",
            borderRadius: "12px",
            border: "none",
            background: loading ? "#64748b" : "#22c55e",
            color: "white",
            cursor: "pointer",
            fontWeight: "bold",
          }}
        >
          {loading ? "Generating..." : "Generate Quest 🎯"}
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: "center", marginTop: "20px" }}>
          Generating questions...
        </div>
      )}

      {/* Questions */}
      <div style={{ marginTop: "30px" }}>
        {questions.map((q, index) => (
          <div
            key={index}
            style={{
              border: "1px solid #22c55e",
              padding: "16px",
              marginBottom: "16px",
              borderRadius: "10px",
            }}
          >
            <p style={{ fontWeight: "bold" }}>{q.question}</p>

            {q.options?.map((opt: string, i: number) => {
              const value = opt[0]

              return (
                <div key={i}>
                  <input
                    type="radio"
                    name={`q${index}`}
                    value={value}
                    checked={answers[index] === value}
                    onChange={(e) =>
                      setAnswers((prev) => ({
                        ...prev,
                        [index]: e.target.value,
                      }))
                    }
                  />
                  <span style={{ marginLeft: "6px" }}>{opt}</span>
                </div>
              )
            })}

            <button
              onClick={() => handleSubmitMCQ(index)}
              style={{
                marginTop: "10px",
                padding: "8px 16px",
                borderRadius: "8px",
                border: "none",
                background: "#22c55e",
                color: "white",
                cursor: "pointer",
              }}
            >
              Submit
            </button>

            {mcqFeedback[index] && (
              <div style={{ marginTop: "10px" }}>
                {mcqFeedback[index].correct ? (
                  <p style={{ color: "green" }}>Correct</p>
                ) : (
                  <>
                    <p style={{ color: "red" }}>Incorrect</p>
                    <p>
                      Correct answer:{" "}
                      {mcqFeedback[index].correct_option}
                    </p>
                  </>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
