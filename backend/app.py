import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline
from scripts.fetch_comments import get_comments  # your existing function

# Streamlit App Title
st.title("YouTube Comment Toxicity Detector")
st.write("Paste a YouTube video link to see the toxicity breakdown of its comments.")

# Input: YouTube URL
url = st.text_input("YouTube Video URL")

if url:
    if "v=" in url:
        video_id = url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
    else:
        st.error("Invalid YouTube URL format.")
        st.stop()

    st.write(f"Fetching comments for video ID: `{video_id}` ...")
    
    # Fetch comments
    try:
        df = get_comments(video_id, max_results=50)  # limit to 50 for speed
    except Exception as e:
        st.error(f"Error fetching comments: {e}")
        st.stop()

    if df.empty:
        st.warning("No comments found for this video.")
        st.stop()

    st.success(f"Fetched {len(df)} comments.")

    # Analyze toxicity
    st.write("Analyzing toxicity...")
    classifier = pipeline("text-classification", model="unitary/toxic-bert")

    toxicity_scores = []
    for comment in df["text"].astype(str).tolist():
        if comment.strip():
            result = classifier(comment[:512])[0]  # truncate long comments
            toxicity_scores.append(result["score"])
        else:
            toxicity_scores.append(None)

    df["toxicity_score"] = toxicity_scores
    df["is_toxic"] = df["toxicity_score"].apply(lambda x: 1 if x and x > 0.5 else 0)


    # Pie Chart
    counts = df["is_toxic"].value_counts().reindex([0,1], fill_value=0)
    fig, ax = plt.subplots()
    ax.pie(counts, labels=["Non-Toxic", "Toxic"], autopct="%1.1f%%", colors=["#4CAF50", "#F44336"])
    st.pyplot(fig)

    # Show top toxic comments
    st.subheader("Top Toxic Comments")
    top_toxic = df[df["is_toxic"]==1]["text"].head(5)
    if not top_toxic.empty:
        for i, comment in enumerate(top_toxic, 1):
            st.write(f"{i}. {comment}")
    else:
        st.write("No toxic comments detected.")
        