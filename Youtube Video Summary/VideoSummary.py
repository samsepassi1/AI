import os
import re
import logging
from functools import wraps
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template_string, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import openai
import yt_dlp

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Determine environment
FLASK_ENV = os.getenv('FLASK_ENV', 'development').lower()
is_dev = FLASK_ENV != 'production'
logger.info(f"Environment detected: {FLASK_ENV} (is_dev={is_dev})")

# Security headers: only force HTTPS in production
Talisman(
    app,
    force_https=not is_dev,
    strict_transport_security=not is_dev,
    session_cookie_secure=not is_dev,
    content_security_policy={
        'default-src': "'self'",
        'img-src': ["'self'", 'data:', 'https:', 'http:'],
        'media-src': ["'self'", 'data:', 'https:', 'http:', 'blob:'],
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'connect-src': ["'self'", 'https://api.openai.com'],
        'frame-src': ["'self'", 'https://www.youtube.com'],
        'object-src': "'none'"
    },
    content_security_policy_nonce_in=['script-src']
)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[os.getenv('RATELIMIT_DEFAULT', '5 per minute')]
)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    logger.warning('OpenAI API key not found in environment variables')

# Constants
ALLOWED_EXTENSIONS = {'m4a', 'mp3', 'wav', 'mp4', 'webm'}
MAX_VIDEO_LENGTH = 3600  # 1 hour in seconds

# HTML template with tech-themed styling
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video Summarizer</title>
    <style>
        body {
            background-color: #0a0a0a;
            color: #ffffff;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #1f1c2c, #928dab);
        }
        h1 {
            font-size: 2em;
            margin-bottom: 20px;
        }
        .container {
            text-align: center;
            width: 60%;
        }
        input[type="text"] {
            width: 80%;
            padding: 10px;
            font-size: 1.1em;
            margin: 20px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        input[type="submit"] {
            padding: 10px 20px;
            font-size: 1em;
            color: #ffffff;
            background-color: #333;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #555;
        }
        .result {
            margin-top: 20px;
            font-size: 1.1em;
            color: #ddd;
            background-color: #222;
            padding: 20px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <h1>YouTube Video Summarizer</h1>
    <div class="container">
        <form action="/summarize" method="post">
            <input type="text" name="video_url" placeholder="Enter YouTube Video URL" required>
            <br>
            <input type="submit" value="Summarize Video">
        </form>
        {% if summary %}
            <div class="result">
                <h2>Summary:</h2>
                <p>{{ summary }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.errorhandler(400)
def bad_request_error(error):
    return render_template_string(html_template, summary=f"Error: {str(error)}"), 400

@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template_string(html_template, 
        summary="Too many requests. Please try again later."), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return render_template_string(html_template, 
        summary="An unexpected error occurred. Please try again later."), 500

@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(html_template, summary=None)

@app.route('/summarize', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limiting
def summarize():
    """Handle video summarization requests."""
    video_url = request.form.get('video_url', '').strip()
    
    if not video_url:
        return render_template_string(html_template, 
            summary="Error: Please provide a YouTube URL"), 400
    
    audio_file = None
    try:
        # Download audio from YouTube
        audio_file = download_audio(video_url)
        
        # Transcribe audio
        transcript = transcribe_audio(audio_file)
        
        # Summarize transcription
        summary = summarize_text(transcript)
        
        return render_template_string(html_template, summary=summary)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return render_template_string(html_template, 
            summary=f"Error: {str(e)}"), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return render_template_string(html_template, 
            summary="An error occurred while processing your request. Please try again."), 500
    finally:
        # Clean up downloaded file
        if audio_file and os.path.exists(audio_file):
            cleanup_files(audio_file)

def validate_youtube_url(url):
    """Validate YouTube URL format."""
    youtube_regex = re.compile(
        r'(?:https?://)?(?:www\.)?'
        r'(?:youtube|youtu|youtube-nocookie)\.(?:com|be)/'
        r'(?:watch\?v=|embed/|v/|.+/|\w+\?v=)?([^&=%?\s/]{11})',
        re.IGNORECASE
    )
    return youtube_regex.match(url) is not None

def cleanup_files(*files):
    """Safely remove files."""
    for file_path in files:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Error removing file {file_path}: {e}")

def download_audio(video_url):
    """Download audio from YouTube and return the file path."""
    if not validate_youtube_url(video_url):
        raise ValueError("Invalid YouTube URL")

    temp_dir = Path('temp')
    temp_dir.mkdir(exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
        'outtmpl': str(temp_dir / 'audio.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extract_flat': False,
        'max_duration': MAX_VIDEO_LENGTH,
        'logger': logger
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Verify the file exists and has content
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                raise ValueError("Failed to download audio content")
                
            return file_path
    except yt_dlp.DownloadError as e:
        logger.error(f"YouTube download error: {e}")
        raise ValueError("Error downloading video. Please check the URL and try again.")
    except Exception as e:
        logger.error(f"Unexpected error in download_audio: {e}")
        raise

def transcribe_audio(file_path):
    """Transcribe audio using OpenAI Whisper API."""
    if not os.path.exists(file_path):
        raise FileNotFoundError("Audio file not found")

    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            
        if not transcript or 'text' not in transcript:
            raise ValueError("Invalid response from transcription service")
            
        return transcript["text"]
    except openai.error.AuthenticationError:
        logger.error("OpenAI authentication failed. Check your API key.")
        raise ValueError("Authentication error with the transcription service.")
    except openai.error.RateLimitError:
        logger.error("OpenAI API rate limit exceeded")
        raise ValueError("Rate limit exceeded. Please try again later.")
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {e}")
        raise ValueError("Error processing audio. Please try again.")

def summarize_text(text):
    """Generate a summary of the given text using OpenAI's GPT model."""
    if not text or not text.strip():
        return "No content to summarize."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that summarizes text. "
                        "Provide a clear, concise summary with key points. "
                        "Focus on main ideas and important details."
                    )
                },
                {
                    "role": "user",
                    "content": f"Summarize the following text concisely:\n\n{text}"
                }
            ],
            temperature=0.5,
            max_tokens=300,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )

        if not response.choices or not response.choices[0].message.content:
            raise ValueError("Empty response from summarization service")

        return response.choices[0].message.content.strip()

    except openai.error.AuthenticationError:
        logger.error("OpenAI authentication failed during summarization")
        raise
    except openai.error.RateLimitError:
        logger.error("OpenAI rate limit exceeded during summarization")
        raise ValueError("Rate limit exceeded. Please try again later.")
    except Exception as e:
        logger.error(f"Error in summarize_text: {e}")
        raise ValueError("Error generating summary. Please try again.")

if __name__ == '__main__':
    import argparse
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Run the YouTube Video Summarizer')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind the server to')
    args = parser.parse_args()
    
    # Only use debug mode in development
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting server on http://{args.host}:{args.port}")
    app.run(debug=debug, host=args.host, port=args.port)
