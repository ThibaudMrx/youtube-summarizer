# main.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl
import logging
import requests

from Pipeline import Pipeline
from OllamaClient import OllamaClient

app = FastAPI()

# Configure logging for FastAPI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger("API")

# Serve static files from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the index.html file at the root URL
@app.get("/", response_class=HTMLResponse)
def serve_index():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        logger.error("index.html not found in the static directory.")
        raise HTTPException(status_code=404, detail="Index page not found.")

# Pydantic model for request validation
class VideoRequest(BaseModel):
    url: HttpUrl  # Ensures the URL is a valid HTTP/HTTPS URL



# API endpoint to summarize a YouTube video
@app.post("/summarize")
def summarize_video(req: VideoRequest):
    logger.info(f"Received request to summarize video: {req.url}")
    youtube_url = str(req.url).strip()
    if not youtube_url:
        logger.warning("Empty YouTube URL received.")
        raise HTTPException(status_code=400, detail="YouTube URL is required.")

    # Initialize OllamaClient with desired configuration
    ollama_client = OllamaClient()

    # Initialize Pipeline with the YouTube URL and OllamaClient instance
    pipeline = Pipeline(
        youtube_url=youtube_url,
        ollama_client=ollama_client,
        output_audio_path="audio.mp3"  # You can customize the path as needed
    )
    result = OllamaClient().get_completion("This is a test prompt")

    try:
        # Run the pipeline to process the video and generate a summary
        summary = pipeline.run()
        logger.info(f"Summary generated successfully for URL: {youtube_url}")
        return {"summary": summary}
    except FileNotFoundError as fnf_error:
        logger.error(fnf_error)
        raise HTTPException(status_code=400, detail=str(fnf_error))
    except requests.exceptions.RequestException as req_error:
        logger.error(f"Network error: {req_error}")
        raise HTTPException(status_code=502, detail="Failed to communicate with Ollama server.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during processing.")
    finally:
        # Ensure that the OllamaClient session is closed even if an error occurs
        ollama_client.close()
        logger.info("OllamaClient session closed.")
