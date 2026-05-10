# YouTube Toxicity Detector ▶️

A full-stack web app that analyzes the toxicity of comments on any public YouTube video using NLP and visualizes the results in a modern dashboard.

## Features

- Fetch YouTube comments using YouTube Data API
- Toxicity detection using Hugging Face (`unitary/toxic-bert`)
- Interactive pie chart visualization
- Toxicity score and severity classification
- Top toxic comments display
- Responsive UI for desktop and mobile

## Tech Stack

**Frontend**
- React
- Vite
- Chart.js

**Backend**
- Flask
- Python

**ML / APIs**
- Hugging Face Transformers
- YouTube Data API v3

## Run Locally

Clone repo:

```bash
git clone https://github.com/natjoecodes/youtube-toxicity-detector.git
cd youtube-toxicity-detector
```

Backend:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Create `backend/.env`:

```env
YOUTUBE_API_KEY=your_api_key_here
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Limitations

- Currently analyzes first 50 comments
- Replies are not included
- Primarily optimized for English comments

## Author

**Nathan Jose**  
LinkedIn: https://www.linkedin.com/in/natjoe/  
GitHub: https://github.com/natjoecodes
