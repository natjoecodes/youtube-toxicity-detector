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
    if (!url.trim()) return;

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

  const chartData = result
    ? {
        labels: ["Non-toxic", "Toxic"],
        datasets: [
          {
            data: [result.non_toxic, result.toxic],
            backgroundColor: ["#22c55e", "#ef4444"],
            borderWidth: 0,
          },
        ],
      }
    : null;

  return (
    <div className="app">
      <h1>YouTube Toxicity Detector</h1>
      <p>Analyze YouTube comments using AI</p>

      <div className="search-box">
        <input
          type="text"
          placeholder="Paste YouTube URL..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !loading) {
              handleAnalyze();
            }
          }}
        />
        <button onClick={handleAnalyze}>Analyze</button>
      </div>

      {loading && <h3>Analyzing comments...</h3>}

      {result && (
        <div className="results">
          <div className="card chart-card">
            <h2>Comment Distribution</h2>
            <Pie data={chartData} />
          </div>

          <div className="card stats-card">
            <h2>Summary</h2>
            <h3 style={{ color: "#ef4444" }}>Toxic: {result.toxic}</h3>
            <h3 style={{ color: "#22c55e" }}>
              Non-toxic: {result.non_toxic}
            </h3>

            <h3>
              Toxicity Rate:{" "}
              {(
                (result.toxic /
                  (result.toxic + result.non_toxic)) *
                100
              ).toFixed(1)}
              %
            </h3>
          </div>

          <div className="card comments-card">
            <h2>Top Toxic Comments</h2>

            {result.top_comments.length === 0 ? (
              <p>No toxic comments detected.</p>
            ) : (
              result.top_comments.map((comment, index) => (
                <div key={index} className="comment">
                  {comment}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;