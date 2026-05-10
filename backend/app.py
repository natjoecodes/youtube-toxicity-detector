from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
from scripts.fetch_comments import get_comments, get_video_title

app = Flask(__name__)
CORS(app)

print("Loading toxicity model...")
classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    tokenizer="unitary/toxic-bert"
)
print("Model loaded.")


def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    return None


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL missing"}), 400

    video_id = extract_video_id(url)
    video_title = get_video_title(video_id)

    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    df = get_comments(video_id, max_results=50)

    if df.empty:
        return jsonify({"error": "No comments found"}), 404

    scores = []
    toxic_comments = []

    for comment in df["text"].astype(str).tolist():
        if comment.strip():
            pred = classifier(comment[:512])[0]
            score = pred["score"]

            scores.append(score)

            if score > 0.5:
                toxic_comments.append(comment)
        else:
            scores.append(0)

    df["toxicity_score"] = scores
    df["is_toxic"] = df["toxicity_score"].apply(lambda x: 1 if x > 0.5 else 0)

    toxic_count = int(df["is_toxic"].sum())
    non_toxic_count = int(len(df) - toxic_count)

    return jsonify({
        "title": video_title,
        "toxic": toxic_count,
        "non_toxic": non_toxic_count,
        "top_comments": toxic_comments[:5]
    })


@app.route("/")
def home():
    return jsonify({"status": "Backend running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)