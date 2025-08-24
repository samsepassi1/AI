# YouTube Video Summarizer

A Flask web application that summarizes YouTube videos using OpenAI's Whisper and GPT models.

## Features

- Extracts audio from YouTube videos
- Transcribes audio using OpenAI Whisper
- Generates concise summaries using GPT-3.5-turbo
- Clean, responsive UI
- Rate limiting for API protection
- Environment-based configuration

## Prerequisites

- Python 3.8+
- OpenAI API key
- FFmpeg (for audio processing)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/youtube-video-summarizer.git
   cd youtube-video-summarizer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key.

## Usage

1. Start the development server:
   ```bash
   python VideoSummary.py
   ```

2. Open your browser to `http://localhost:5000`

3. Enter a YouTube URL and click "Summarize Video"

## Security Considerations

- API keys are stored in environment variables
- Rate limiting is enabled to prevent abuse
- Input validation is performed on YouTube URLs
- Security headers are set using Flask-Talisman
- Debug mode is disabled in production

## License

MIT

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
