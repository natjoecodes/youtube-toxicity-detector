from flask import Flask, request, jsonify
from flask_cors import CORS
from scripts.fetch_comments import get_comments, get_video_title
from dotenv import load_dotenv
import requests
import os

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/unitary/toxic-bert"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

app = Flask(__name__)
CORS(app)


def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None

def analyze_comment(comment):

    payload = {
        "inputs": comment[:512]
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    print("HF STATUS:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return 0

    try:
        result = response.json()

        print("HF RESULT:", result)

        if isinstance(result, list) and len(result) > 0:

            prediction = result[0]

            label = prediction.get("label", "").lower()
            score = prediction.get("score", 0)

            if label == "toxic":
                return score

            return 0

        return 0

    except Exception as e:
        print("JSON ERROR:", e)
        print(response.text)
        return 0


@app.route("/")
def home():
    return jsonify({"status": "Backend running"})


@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        data = request.json
        url = data.get("url")

        if not url:
            return jsonify({"error": "URL missing"}), 400

        video_id = extract_video_id(url)

        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400

        video_title = get_video_title(video_id)

        df = get_comments(video_id, max_results=50)

        if df.empty:
            return jsonify({"error": "No comments found"}), 404

        scores = []
        toxic_comments = []

        for comment in df["text"].astype(str).tolist():

            if not comment.strip():
                scores.append(0)
                continue

            score = analyze_comment(comment)

            scores.append(score)

            if score > 0.5:
                toxic_comments.append(comment)

        df["toxicity_score"] = scores

        df["is_toxic"] = df["toxicity_score"].apply(
            lambda x: 1 if x > 0.5 else 0
        )

        toxic_count = int(df["is_toxic"].sum())
        non_toxic_count = int(len(df) - toxic_count)

        return jsonify({
            "title": video_title,
            "toxic": toxic_count,
            "non_toxic": non_toxic_count,
            "top_comments": toxic_comments[:5]
        })

    except Exception as e:

        print("BACKEND ERROR:", str(e))

        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)