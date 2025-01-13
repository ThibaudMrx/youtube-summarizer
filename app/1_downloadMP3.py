import os
import whisper
from yt_dlp import YoutubeDL
from pydub import AudioSegment



def download_audio_ytdlp(youtube_url, output_path="audio.mp3"):
    # Define download options
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
        'outtmpl': 'audio.%(ext)s',  # Save as 'audio.ext'
    }
    
    # Download the audio
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    # Ensure the output file exists
    if not os.path.exists("audio.mp3"):
        raise FileNotFoundError("Audio file not found!")
    
    return output_path

youtubeVideotestURL = 'http://www.youtube.com/watch?v=4FTIVJEBkNY'
download_audio_ytdlp(youtubeVideotestURL)