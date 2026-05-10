# scripts/fetch_comments.py

import os
from datetime import datetime
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

# SETUP FOLDERS
project_root = os.path.dirname(os.path.dirname(__file__))  # youtube-toxicity-detector
data_folder = os.path.join(project_root, "data")
os.makedirs(data_folder, exist_ok=True)

def get_comments(video_id, max_results=50, save_csv=False):
    """
    Fetch top-level comments from a YouTube video.
    
    Parameters:
        video_id (str): YouTube video ID
        max_results (int): Maximum comments to fetch (1-100)
        save_csv (bool): If True, save comments to CSV in data/ folder
    
    Returns:
        pd.DataFrame: DataFrame with author, text, likes, published_at
    """
    youtube = build("youtube", "v3", developerKey=API_KEY)
    comments = []

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        )
        response = request.execute()

        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "author": comment["authorDisplayName"],
                "text": comment["textDisplay"],
                "likes": comment["likeCount"],
                "published_at": comment["publishedAt"]
            })

        if not comments:
            print("No comments found for this video.")
            return pd.DataFrame()

        df = pd.DataFrame(comments)

        if save_csv:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(data_folder, f"{video_id}_comments_{timestamp}.csv")
            df.to_csv(csv_path, index=False)
            print(f"Saved comments to {csv_path}")

        return df

    except HttpError as e:
        if e.resp.status == 404:
            print(f"Error: Video ID '{video_id}' not found or is private/deleted.")
        else:
            print(f"HTTP Error: {e}")
        return pd.DataFrame()  # return empty DataFrame on error
    
def get_video_title(video_id):
    """
    Fetch title of a YouTube video.
    Returns string title.
    """
    youtube = build("youtube", "v3", developerKey=API_KEY)

    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )

        response = request.execute()
        items = response.get("items", [])

        if not items:
            return "Unknown Video"

        return items[0]["snippet"]["title"]

    except HttpError as e:
        print(f"Error fetching title: {e}")
        return "Unknown Video"