import React, { useState } from "react";
import styles from "../styles/AskQuestion.module.css";

interface AskQuestionProps {
  bookId: string;
}

const AskQuestion = ({ bookId }: AskQuestionProps) => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleAskQuestion = async () => {
    if (!question) return;

    const token = localStorage.getItem("token");
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/books/books/${bookId}/ask?question=${question}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );
      if (!response.ok) throw new Error("Failed to get an answer");
      const data = await response.json();
      setAnswer(data.answer);
    } catch (error) {
      console.error("Error:", error);
      setAnswer("An error occurred while fetching the answer.");
    }
  };

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Ask a Question About This Book</h3>
      <input
        type="text"
        placeholder="Enter your question"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        className={styles.input}
      />
      <button onClick={handleAskQuestion} className={styles.button}>
        Ask
      </button>
      {answer && (
        <div className={styles.answer}>
          <h4>Answer:</h4>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
};

export default AskQuestion;
