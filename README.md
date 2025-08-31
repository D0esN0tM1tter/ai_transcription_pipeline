# AI Transcription Pipeline

A FastAPI-based application that provides automated speech-to-text transcription and subtitle generation for audio and video files using OpenAI's Whisper models.

## Features

- **Multi-language Transcription**: Transcribe audio/video files in multiple languages
- **Subtitle Generation**: Create VTT subtitle files with embedded subtitles in videos
- **Multiple Model Sizes**: Choose from different Whisper model sizes (tiny to large)
- **Video Processing**: Extract audio from video files and embed subtitles back into videos
- **REST API**: Complete API for file upload, processing, and downloads
- **Summary Generation**: AI-powered text summarization of transcribed content
- **Async Processing**: Non-blocking job processing for better performance

## Supported Formats

- **Audio**: WAV, MP3, FLAC, OGG, M4A
- **Video**: MP4, AVI, MOV, MKV

## Prerequisites

Before running the application, ensure you have:

- **Python 3.10 or higher**
- **FFmpeg** (for audio/video processing)
- **Git**

### Installing FFmpeg

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
# Using Homebrew
brew install ffmpeg
```

**Windows:**
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

## Installation and Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai_transcription_pipeline
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Note: The first time you run transcription, Whisper models will be automatically downloaded (this may take some time).

### 4. Create Environment File

Create a `.env` file in the project root directory:

```bash
# Create the .env file
touch .env
```

Add the following environment variables to the `.env` file:

```env
DB_PATH=./database/app.json
AUDIOS_DIR=./data/audios
PROCESSED_VID_DIR=./data/videos/processed
TRANSCRIPTIONS_DIR=./data/transcriptions
UPLOAD_DIR=./data/videos/upload
```

The application will automatically load these variables when it starts.

## Running the Application

### Start the Server

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The application will be available at:
- **API**: http://127.0.0.1:8000
- **Interactive API Documentation**: http://127.0.0.1:8000/docs
- **Alternative API Documentation**: http://127.0.0.1:8000/redoc

### Using Docker (Alternative)

```bash
# Build the image
docker build -t ai-transcription-pipeline .

# Run the container
docker run -p 8000:8000 -v $(pwd)/data:/app/data -v $(pwd)/database:/app/database ai-transcription-pipeline
```

## Usage

### 1. Web Interface

Visit http://127.0.0.1:8000/docs to use the interactive API documentation:

1. Navigate to `/api/pipeline/process` endpoint
2. Click "Try it out"
3. Upload your audio/video file
4. Select input language (e.g., "english")
5. Choose target languages for transcription/translation
6. Select Whisper model size (tiny, base, small, medium, large)
7. Click "Execute"

### 2. Command Line Examples

**Upload and Process a File:**
```bash
curl -X POST "http://127.0.0.1:8000/api/pipeline/process" \
  -F "video=@your_file.mp4" \
  -F "input_language=english" \
  -F "target_languages=english" \
  -F "target_languages=spanish" \
  -F "asr_model_size=small"
```

**Download Processed Video:**
```bash
curl -X GET "http://127.0.0.1:8000/api/downloads/download_video/{job_id}" \
  -o processed_video.mkv
```

**Download Subtitles:**
```bash
curl -X GET "http://127.0.0.1:8000/api/downloads/download_subtitles/{job_id}/english" \
  -o subtitles.vtt
```

**Get Summaries:**
```bash
curl -X GET "http://127.0.0.1:8000/api/downloads/summaries/{job_id}"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/pipeline/process` | POST | Upload and process audio/video file |
| `/api/downloads/download_video/{job_id}` | GET | Download processed video with subtitles |
| `/api/downloads/download_subtitles/{job_id}/{language}` | GET | Download subtitle file for specific language |
| `/api/downloads/summaries/{job_id}` | GET | Get AI-generated summaries |

## Model Sizes

Choose the appropriate Whisper model size based on your needs:

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | ~39 MB | Fastest | Basic | Quick testing |
| base | ~74 MB | Fast | Good | General use |
| small | ~244 MB | Medium | Better | Recommended |
| medium | ~769 MB | Slow | High | High accuracy needed |
| large | ~1550 MB | Slowest | Highest | Best quality |

## Supported Languages

The application supports multiple languages including:
- English
- Spanish
- French
- Arabic
- And many more (depends on Whisper model capabilities)

## Project Structure

```
ai_transcription_pipeline/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── routers/           # API route handlers
│   │   └── schemas/           # Pydantic models
│   ├── config/                # Application configuration
│   ├── containers/            # Dependency injection containers
│   ├── models/                # Data models
│   ├── repositories/          # Data access layer
│   ├── services/              # Business logic
│   └── utils/                 # Utility functions
├── data/                      # File storage
│   ├── audios/               # Extracted audio files
│   ├── transcriptions/       # Generated subtitle files
│   └── videos/               # Uploaded and processed videos
├── database/                 # JSON database
├── requirements.txt          # Python dependencies
└── Dockerfile               # Docker configuration
```

## Troubleshooting

### Common Issues

**FFmpeg not found:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```
Solution: Install FFmpeg and ensure it's in your system PATH.

**Module import errors:**
```
ModuleNotFoundError: No module named 'app'
```
Solution: Ensure you're running the command from the project root directory and the virtual environment is activated.

**Out of memory errors:**
Solution: Use a smaller Whisper model size (e.g., "tiny" or "base").

**Permission errors (Windows):**
```
PowerShell execution policy error
```
Solution: Run PowerShell as administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### System Requirements

- **RAM**: Minimum 8GB (16GB recommended for larger models)
- **Storage**: At least 2GB free space for models and temporary files
- **GPU**: Optional but recommended for faster processing

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest app/tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Open an issue on the project repository

---

Built with FastAPI, OpenAI Whisper, and FFmpeg.
