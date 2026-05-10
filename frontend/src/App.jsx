import { useState } from "react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Pie } from "react-chartjs-2";
import "./App.css";

ChartJS.register(ArcElement, Tooltip, Legend);

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleAnalyze() {
    if (!url.trim() || loading) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (data.error) {
        alert(data.error);
      } else {
        setResult(data);
      }
    } catch (error) {
      console.error(error);
      alert("Backend connection failed");
    }

    setLoading(false);
  }

  const total = result ? result.toxic + result.non_toxic : 0;
  const toxicityRate = total
    ? ((result.toxic / total) * 100).toFixed(1)
    : 0;

  const severity =
    toxicityRate < 10
      ? "Low"
      : toxicityRate < 30
      ? "Moderate"
      : "High";

  const chartData = result
    ? {
        labels: ["Safe", "Toxic"],
        datasets: [
          {
            data: [result.non_toxic, result.toxic],
            backgroundColor: ["#22c55e", "#ff3b30"],
            borderWidth: 0,
            hoverOffset: 6,
          },
        ],
      }
    : null;

  return (
    <div className="app">
      <header className="hero">
        <div className="logo">
          <div className="play"></div>
        </div>
        <h1>YouTube Toxicity Detector</h1>
        <p>
          AI-powered analysis of comment toxicity in any YouTube video
        </p>

        <div className="search-box">
          <input
            type="text"
            placeholder="Paste YouTube URL..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleAnalyze();
            }}
          />
          <button onClick={handleAnalyze}>
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>
      </header>

      {result && (
        <>
        <h2 className="video-title">{result.title}</h2>
          <section className="stats-grid">
            <div className="stat-card">
              <span>Total Comments</span>
              <h2>{total}</h2>
            </div>

            <div className="stat-card toxic">
              <span>Toxic Comments</span>
              <h2>{result.toxic}</h2>
            </div>

            <div className="stat-card safe">
              <span>Safe Comments</span>
              <h2>{result.non_toxic}</h2>
            </div>

            <div className="stat-card">
              <span>Severity</span>
              <h2>{severity}</h2>
            </div>
          </section>

          <section className="main-grid">
            <div className="card chart-card">
              <h3>Comment Distribution</h3>
              <div className="chart-wrapper">
                <Pie data={chartData} />
              </div>
            </div>

            <div className="card score-card">
              <h3>Toxicity Score</h3>
              <div className="score">{toxicityRate}%</div>
              <div className={`badge ${severity.toLowerCase()}`}>
                {severity}
              </div>
            </div>
          </section>

          <section className="card comments-card">
            <h3>Top Toxic Comments</h3>

            {result.top_comments.length === 0 ? (
              <p className="empty">
                No toxic comments detected.
              </p>
            ) : (
              result.top_comments.map((comment, index) => (
                <div key={index} className="comment">
                  <span className="comment-icon">⚠</span>
                  <span>{comment}</span>
                </div>
              ))
            )}
          </section>
        </>
      )}
      <footer className="footer">
  <div className="footer-line"></div>

  <p>
    Built with React, Flask and Transformers · Crafted by{" "}
    <a
      className="footer-name"
      href="https://www.linkedin.com/in/natjoe/"
      target="_blank"
      rel="noreferrer"
    >
      Nathan Jose
    </a>
  </p>

  <a
    className="footer-link"
    href="https://github.com/natjoecodes/youtube-toxicity-detector"
    target="_blank"
    rel="noreferrer"
  >
    View on GitHub
  </a>
</footer>
    </div>
  );
}

export default App;