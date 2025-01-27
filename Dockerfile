FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

# Copy requirements first (to leverage Docker caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of your project files
COPY . /app

# Expose port 8000 (FastAPI default if you run uvicorn on 8000)
EXPOSE 8000

# Ollama support
#COPY usr/local/bin/ollama /usr/local/bin/ollama
#RUN chmod +x /usr/local/bin/ollama

# Expose the Ollama port (optional, if you want external access)
EXPOSE 11411

# Then run Ollama in the background + your main app.
CMD ollama serve & uvicorn main:app --host 0.0.0.0 --port 8000

