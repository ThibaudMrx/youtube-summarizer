import logging
import whisper
import os
import time
from yt_dlp import YoutubeDL
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate


def download_audio_ytdlp(youtube_url, output_path="audio.mp3"):
    """
    Downloads the audio from the provided YouTube URL as an MP3 file.
    Returns the local audio_path (default "audio.mp3").
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }
        ],
        'ffmpeg-location': '/usr/bin/ffmpeg',
        'outtmpl': 'audio.%(ext)s',
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    if not os.path.exists(output_path):
        raise FileNotFoundError("Audio file not found!")

    return output_path


def transcribe_audio(audio_path, model_name="base"):
    """
    Loads a Whisper model in memory and transcribes the given MP3 audio file,
    returning the transcript as a string.
    """
    logging.info(f"Loading Whisper model: {model_name}")
    model = whisper.load_model(model_name, download_root=None, in_memory=True)

    model_size = sum(p.numel() for p in model.parameters() if p.requires_grad) * 4 / (1024 ** 2)
    logging.info(f"Model loaded into memory. Size: {model_size:.2f} MB")

    logging.info(f"Transcribing audio file: {audio_path} ...")
    result = model.transcribe(audio_path)
    logging.info("Transcription completed successfully")
    return result["text"]


def chunk_text(text, chunk_size=3000):
    """
    Splits the text into chunks of ~3000 characters each,
    trying to break on sentence boundaries.
    Yields each chunk as a string.
    """
    sentences = text.split('. ')
    chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence) + 2  # account for the period + space
        if current_length + sentence_length > chunk_size:
            yield '. '.join(chunk) + '.'
            chunk = []
            current_length = 0
        chunk.append(sentence)
        current_length += sentence_length

    if chunk:
        yield '. '.join(chunk) + '.'


def process_video(youtube_url: str) -> str:
    """
    Downloads and transcribes the audio, extracts bullet points in memory,
    cleans them, arranges them into a final summary layout,
    and removes the temporary audio file. Returns the final summary string.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    time_dict = {}

    # Step 1: Downloading audio
    start_time = time.time()
    audio_path = download_audio_ytdlp(youtube_url)
    end_time = time.time()
    time_dict["Downloading audio"] = end_time - start_time
    logger.info(f"Time taken for step 1: {time_dict['Downloading audio']:.1f} seconds")

    # Step 2: Transcribing from audio to text
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found after download: {audio_path}")

    start_time = time.time()
    transcription = transcribe_audio(audio_path)
    end_time = time.time()
    time_dict["Transcribing audio with Whisper"] = end_time - start_time
    logger.info(f"Time taken for step 2: {time_dict['Transcribing audio with Whisper']:.1f} seconds")

    # Step 3: Creeating text chunks for better bullet point extraction consistency
    start_time = time.time()
    chunks = list(chunk_text(transcription))
    end_time = time.time()
    time_dict["Chunking transcript"] = end_time - start_time
    logger.info(f"Time taken for step 3: {time_dict['Chunking transcript']:.1f} seconds")

    # Step 4: Extract bullet points (Mistral) for each chunk
    model = OllamaLLM(model="mistral")
    bullet_points = []  

    template_bullets = """
[SYSTEM MESSAGE]
You are a helpful assistant that extracts key points from user-provided text. 
Extract concise bullet points representing the key ideas. 
You can have 3-7 bullet points per chunk, no more. In your answer, do not give numbers to bullet points.
No extra commentary. Just the 3-7 key points.

[USER MESSAGE]
{chunkText}
"""
    prompt_bullets = ChatPromptTemplate.from_template(template_bullets)
    chain_bullets = prompt_bullets | model

    logger.info(f"Starting to extract bullet points from {len(chunks)} chunks ...")
    start_time = time.time()
    for chunk_text_data in chunks:
        result = chain_bullets.invoke({"chunkText": chunk_text_data})
        # Each chunk of bullet points might contain newlines, we store as lines
        bullet_points.extend(result.splitlines())
        logger.info(f"Processed chunk => bullet points:\n{result}\n")
    end_time = time.time()
    time_dict["Extracting Bullet Points"] = end_time - start_time
    logger.info(f"Time taken for step 4: {time_dict['Extracting Bullet Points']:.1f} seconds")

    # Step 5: Clean bullet points with Mistral (temporary fix)
    cleaning_template = """
[SYSTEM MESSAGE]
You are a helpful assistant that processes text lines. 
You remove the beginning number (like '1.' '2.') and any indentation from the text. 
If there's no number, do nothing. Return only the cleaned text. No additional commentary.

[USER MESSAGE]
{line}
"""
    cleaning_prompt = ChatPromptTemplate.from_template(cleaning_template)
    cleaning_chain = cleaning_prompt | model

    start_time = time.time()
    cleaned_bullet_points = []
    for bp in bullet_points:
        bp_str = bp.strip()
        if bp_str:
            cleaned_line = cleaning_chain.invoke({"line": bp_str}).strip()
            cleaned_bullet_points.append(cleaned_line)
    end_time = time.time()
    time_dict["Cleaning Bullet Points"] = end_time - start_time
    logger.info(f"Time taken for step 5 (cleaning): {time_dict['Cleaning Bullet Points']:.1f} seconds")

    # Step 6: Layout / final summary
    layout_template = """
[SYSTEM MESSAGE]
You are a helpful assistant that extracts 3-5 key ideas and their sub-ideas (maximum 3-4 per general idea) 
from user-provided text. Return them in a clearly structured layout like:

[Quick introduction]
Part 1: [Title]
    1.a: [Idea]
        Explanation of 1.a
    1.b: [Another Smaller Idea]
    1.c: ...
    [Line break]

Part 2: [Same layout as Part 1]

Part 3: etc.

[Quick conclusion]
No extra commentary.

[USER MESSAGE]
{cleanedText}
"""
    layout_prompt = ChatPromptTemplate.from_template(layout_template)
    layout_chain = layout_prompt | model

    # Join all cleaned bullet points into one text block
    cleaned_text_block = "\n".join(cleaned_bullet_points)

    start_time = time.time()
    final_result = layout_chain.invoke({"cleanedText": cleaned_text_block})
    end_time = time.time()
    time_dict["Calculating summary"] = end_time - start_time
    logger.info(f"Time taken for step 6 (layout): {time_dict['Calculating summary']:.1f} seconds")

    logger.info("Final Summary:\n")
    logger.info(final_result)

    # Remove the temporary audio file
    if os.path.exists(audio_path):
        os.remove(audio_path)
        logger.info(f"Removed audio file: {audio_path}")

    return final_result
