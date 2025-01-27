from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from summaryPipeline import process_video  # Your pipeline function

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html
@app.get("/", response_class=HTMLResponse)
def serve_index():
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return html_content

class VideoRequest(BaseModel):
    url: str

# API endpoint
@app.post("/summarize")
def summarize_video(req: VideoRequest):
    youtube_url = req.url.strip()
    if not youtube_url:
        raise HTTPException(status_code=400, detail="YouTube URL is required")

    try:
        summary = process_video(youtube_url)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
