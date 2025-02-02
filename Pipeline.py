import logging
import whisper
import os
import time
from yt_dlp import YoutubeDL
from typing import List

from OllamaClient import OllamaClient

class Pipeline:
    def __init__(self, youtube_url: str, ollama_client: OllamaClient, output_audio_path: str = "audio.mp3"):
        """
        Initializes the Pipeline with necessary components.

        :param youtube_url: URL of the YouTube video to process.
        :param ollama_client: Instance of OllamaClient for interacting with Ollama server.
        :param output_audio_path: Path to save the downloaded audio file.
        """
        self.youtube_url = youtube_url
        self.ollama_client = ollama_client
        self.output_audio_path = output_audio_path
        self.logger = logging.getLogger(self.__class__.__name__)

    def download_audio(self) -> str:
        """
        Downloads the audio from the YouTube URL as an MP3 file.

        :return: Path to the downloaded audio file.
        """
        self.logger.info("Downloading audio from YouTube")
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
            'quiet': True,  # Suppress yt_dlp output
            'no_warnings': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.youtube_url])

        if not os.path.exists(self.output_audio_path):
            self.logger.error(f"Audio file not found after download at path: {self.output_audio_path}")
            raise FileNotFoundError("Audio file not found after download!")

        self.logger.info(f"Audio downloaded successfully: {self.output_audio_path}")
        return self.output_audio_path

    def transcribe_audio(self, audio_path: str, model_name: str = "base") -> str:
        """
        Transcribes the given MP3 audio file using Whisper.

        :param audio_path: Path to the audio file.
        :param model_name: Name of the Whisper model to use.
        :return: Transcribed text.
        """
        self.logger.info(f"Loading Whisper model: {model_name}")
        model = whisper.load_model(model_name, download_root=None, in_memory=True)

        model_size = sum(p.numel() for p in model.parameters() if p.requires_grad) * 4 / (1024 ** 2)
        self.logger.info(f"Model loaded into memory. Size: {model_size:.2f} MB")

        self.logger.info(f"Transcribing audio file: {audio_path} ...")
        result = model.transcribe(audio_path)
        self.logger.info("Transcription completed successfully")
        return result["text"]

    def chunk_text(self, text: str, chunk_size: int = 3000) -> List[str]:
        """
        Splits the text into chunks of approximately 3000 characters each.

        :param text: The text to be chunked.
        :param chunk_size: Maximum size of each chunk.
        :return: List of text chunks.
        """
        self.logger.info("Chunking transcript")
        sentences = text.split('. ')
        chunk = []
        current_length = 0
        chunks = []

        for sentence in sentences:
            sentence_length = len(sentence) + 2  # account for the period + space
            if current_length + sentence_length > chunk_size:
                chunked_text = '. '.join(chunk) + '.' if chunk else ''
                if chunked_text:
                    chunks.append(chunked_text)
                chunk = []
                current_length = 0
            chunk.append(sentence)
            current_length += sentence_length

        if chunk:
            chunked_text = '. '.join(chunk) + '.' if chunk else ''
            if chunked_text:
                chunks.append(chunked_text)

        self.logger.info(f"Total chunks created: {len(chunks)}")
        return chunks

    def extract_bullet_points(self, chunks: list[str], model_name: str = "mistral") -> list[str]:
        """
        Extracts bullet points from each text chunk using Ollama.

        :param chunks: List of text chunks.
        :param model_name: Ollama model to use.
        :return: List of extracted bullet points.
        """
        self.logger.info("Extracting bullet points using Ollama")
        bullet_points = []
        bullet_points_prompt_template = """[SYSTEM MESSAGE]
You are a helpful assistant that extracts key points from user-provided text. 
Extract concise bullet points representing the key ideas. 
You can have 3-7 bullet points , no more. In your answer, do not give numbers to bullet points.
No extra commentary. Just the 3-7 key points.

[USER MESSAGE]
{chunkText}
"""

        for idx, chunk_text in enumerate(chunks, start=1):
            self.logger.info(f"Processing chunk {idx}/{len(chunks)} for bullet point extraction, chunk text {chunk_text}")
            prompt = bullet_points_prompt_template.format(chunkText=chunk_text)
            try:
                result = self.ollama_client.get_completion(prompt, model=model_name)
                # Split the result into lines and clean
                extracted_points = [line.strip() for line in result.splitlines() if line.strip()]
                bullet_points.extend(extracted_points)
                self.logger.debug(f"Extracted bullet points for chunk {idx}: {extracted_points}")
            except Exception as e:
                self.logger.debug(f"Prompt used for chunk {idx}: {prompt}")
                self.logger.error(f"Failed to extract bullet points for chunk {idx}: {e}")
                continue

        self.logger.info(f"Total bullet points extracted: {len(bullet_points)}")
        return bullet_points

    def clean_bullet_points(self, bullet_points: List[str], model_name: str = "mistral") -> List[str]:
        """
        Cleans bullet points by removing leading numbers and indentation.

        :param bullet_points: List of bullet points to clean.
        :param model_name: Ollama model to use.
        :return: List of cleaned bullet points.
        """
        self.logger.info("Cleaning bullet points using Ollama")
        cleaned_bullet_points = []
        cleaning_prompt_template = """[SYSTEM MESSAGE]
You are a helpful assistant that processes text lines. 
You remove the beginning number (like '1.' '2.') and any indentation from the text. 
If there's no number, do nothing. Return only the cleaned text. No additional commentary.

[USER MESSAGE]
{line}
"""

        for idx, bp in enumerate(bullet_points, start=1):
            bp_str = bp.strip()
            if not bp_str:
                self.logger.debug(f"Skipping empty bullet point at index {idx}")
                continue

            prompt = cleaning_prompt_template.format(line=bp_str)
            try:
                cleaned_line = self.ollama_client.get_completion(prompt, model=model_name).strip()
                if cleaned_line:
                    cleaned_bullet_points.append(cleaned_line)
                    self.logger.debug(f"Cleaned bullet point {idx}: {cleaned_line}")
                else:
                    self.logger.debug(f"No content returned after cleaning bullet point {idx}")
            except Exception as e:
                self.logger.error(f"Failed to clean bullet point {idx}: {e}")
                continue

        self.logger.info(f"Total bullet points after cleaning: {len(cleaned_bullet_points)}")
        return cleaned_bullet_points

    def generate_final_summary(self, cleaned_bullet_points: List[str], model_name: str = "mistral") -> str:
        """
        Generates a final structured summary from the cleaned bullet points using Ollama.

        :param cleaned_bullet_points: List of cleaned bullet points.
        :param model_name: Ollama model to use.
        :return: Final summary string.
        """
        self.logger.info("Generating final summary layout using Ollama")
        layout_template = """[SYSTEM MESSAGE]
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

        cleaned_text_block = "\n".join(cleaned_bullet_points)
        prompt = layout_template.format(cleanedText=cleaned_text_block)
        try:
            final_result = self.ollama_client.get_completion(prompt, model=model_name)
            self.logger.debug(f"Final summary generated: {final_result}")
            return final_result
        except Exception as e:
            self.logger.error(f"Failed to generate final summary: {e}")
            raise

    def run(self) -> str:
        """
        Executes the entire pipeline: downloading audio, transcribing, chunking,
        extracting and cleaning bullet points, and generating the final summary.

        :return: Final summary string.
        """
        self.logger.info("Starting the video processing pipeline")
        time_dict = {}
        final_result = ""

        try:
            # Step 1: Downloading audio
            start_time = time.time()
            audio_path = self.download_audio()
            end_time = time.time()
            time_dict["Downloading audio"] = end_time - start_time
            self.logger.info(f"Time taken for Step 1 (Downloading audio): {time_dict['Downloading audio']:.1f} seconds")

            # Step 2: Transcribing audio
            start_time = time.time()
            transcription = self.transcribe_audio(audio_path)
            end_time = time.time()
            time_dict["Transcribing audio with Whisper"] = end_time - start_time
            self.logger.info(f"Time taken for Step 2 (Transcribing audio): {time_dict['Transcribing audio with Whisper']:.1f} seconds")

            # Step 3: Chunking transcript
            start_time = time.time()
            chunks = self.chunk_text(transcription)
            end_time = time.time()
            time_dict["Chunking transcript"] = end_time - start_time
            self.logger.info(f"Time taken for Step 3 (Chunking transcript): {time_dict['Chunking transcript']:.1f} seconds")

            # Step 4: Extracting bullet points
            start_time = time.time()
            bullet_points = self.extract_bullet_points(chunks)
            end_time = time.time()
            time_dict["Extracting Bullet Points"] = end_time - start_time
            self.logger.info(f"Time taken for Step 4 (Extracting Bullet Points): {time_dict['Extracting Bullet Points']:.1f} seconds")

            # Step 5: Cleaning bullet points
            start_time = time.time()
            cleaned_bullet_points = self.clean_bullet_points(bullet_points)
            end_time = time.time()
            time_dict["Cleaning Bullet Points"] = end_time - start_time
            self.logger.info(f"Time taken for Step 5 (Cleaning Bullet Points): {time_dict['Cleaning Bullet Points']:.1f} seconds")

            # Step 6: Generating final summary
            start_time = time.time()
            final_result = self.generate_final_summary(cleaned_bullet_points)
            end_time = time.time()
            time_dict["Generating Final Summary"] = end_time - start_time
            self.logger.info(f"Time taken for Step 6 (Generating Final Summary): {time_dict['Generating Final Summary']:.1f} seconds")

            self.logger.info("Pipeline completed successfully")

        except Exception as e:
            self.logger.error(f"An error occurred during the pipeline execution: {e}")
            raise

        finally:
            # Cleanup: Remove the temporary audio file
            if os.path.exists(self.output_audio_path):
                os.remove(self.output_audio_path)
                self.logger.info(f"Removed temporary audio file: {self.output_audio_path}")

            # Close OllamaClient session
            self.ollama_client.close()
            self.logger.info("Closed OllamaClient session")

        return final_result
