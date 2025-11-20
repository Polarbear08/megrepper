import { useState } from 'react';
import axios from 'axios';
import './App.css';

interface Question {
  question_key: string;
  correct_answer: unknown;
  options: unknown[];
  data_format: string;
  data_display: string;
}

const API_BASE_URL = '/api';

export default function App() {
  const [question, setQuestion] = useState<Question | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<unknown | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [score, setScore] = useState(0);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchQuestion = async () => {
    setLoading(true);
    setSelectedAnswer(null);
    setIsAnswered(false);
    setIsCorrect(null);

    try {
      const response = await axios.post<Question>(`${API_BASE_URL}/question`);
      setQuestion(response.data);
      setTotalQuestions(totalQuestions + 1);
    } catch (error) {
      console.error('Failed to fetch question:', error);
      alert('問題の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const checkAnswer = async () => {
    if (!question || selectedAnswer === null) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/check-answer`, {
        correct_answer: question.correct_answer,
        user_answer: selectedAnswer,
      });

      const correct = response.data.is_correct;
      setIsCorrect(correct);
      setIsAnswered(true);

      if (correct) {
        setScore(score + 1);
      }
    } catch (error) {
      console.error('Failed to check answer:', error);
      alert('回答チェックに失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuestion = () => {
    fetchQuestion();
  };

  return (
    <div className="app-container">
      <div className="game-card">
        <h1>🎮 Megrepper</h1>
        <p className="subtitle">JSON/YAML データから値を推測しよう!</p>

        <div className="score-board">
          <div className="score-item">
            <span className="score-label">正解数</span>
            <span className="score-value">{score}</span>
          </div>
          <div className="score-item">
            <span className="score-label">問題数</span>
            <span className="score-value">{totalQuestions}</span>
          </div>
          <div className="score-item">
            <span className="score-label">正解率</span>
            <span className="score-value">
              {totalQuestions > 0
                ? Math.round((score / totalQuestions) * 100)
                : 0}
              %
            </span>
          </div>
        </div>

        {!question ? (
          <div className="start-section">
            <p className="instruction">ゲームを開始して、データから値を推測しましょう!</p>
            <button
              className="btn btn-primary"
              onClick={fetchQuestion}
              disabled={loading}
            >
              {loading ? '読込中...' : '問題を出題'}
            </button>
          </div>
        ) : (
          <div className="game-section">
            <div className="data-display">
              <div className="format-badge">{question.data_format.toUpperCase()}</div>
              <pre className="data-content">{question.data_display}</pre>
            </div>

            <div className="question-section">
              <h2 className="question-text">
                <span className="key-name">「{question.question_key}」</span>
                の値は？
              </h2>

              <div className="options-grid">
                {question.options.map((option, index) => (
                  <button
                    key={index}
                    className={`option-btn ${
                      selectedAnswer === option ? 'selected' : ''
                    } ${isAnswered && option === question.correct_answer ? 'correct' : ''} ${
                      isAnswered &&
                      selectedAnswer === option &&
                      !isCorrect
                        ? 'incorrect'
                        : ''
                    }`}
                    onClick={() => !isAnswered && setSelectedAnswer(option)}
                    disabled={isAnswered}
                  >
                    {typeof option === 'object'
                      ? JSON.stringify(option)
                      : String(option)}
                  </button>
                ))}
              </div>

              {!isAnswered ? (
                <button
                  className="btn btn-submit"
                  onClick={checkAnswer}
                  disabled={selectedAnswer === null || loading}
                >
                  {loading ? '確認中...' : '回答を送信'}
                </button>
              ) : (
                <div className="result-section">
                  {isCorrect ? (
                    <div className="result-correct">
                      <span className="result-icon">✨</span>
                      <p className="result-text">正解です!</p>
                    </div>
                  ) : (
                    <div className="result-incorrect">
                      <span className="result-icon">❌</span>
                      <p className="result-text">不正解です</p>
                      <p className="correct-answer">
                        正解: {JSON.stringify(question.correct_answer)}
                      </p>
                    </div>
                  )}

                  <button
                    className="btn btn-next"
                    onClick={handleNextQuestion}
                    disabled={loading}
                  >
                    {loading ? '読込中...' : '次の問題へ'}
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
