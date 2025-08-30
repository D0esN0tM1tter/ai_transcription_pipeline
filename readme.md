# AI Transcription Pipeline

## Overview
This project provides an AI-powered transcription and subtitle generation system for audio and video files. Built with FastAPI and modern AI models, it offers a robust REST API for automated speech-to-text conversion with multi-language support.

## Features
- **Automatic Audio Transcription**: Convert speech to text using state-of-the-art AI models
- **AI-Powered Summarization**: Generate concise summaries of transcribed content in multiple languages
- **Multi-language Support**: Process audio in multiple languages
- **Video Processing**: Extract audio from video files for transcription
- **Subtitle Generation**: Generate VTT subtitle files
- **RESTful API**: Complete API endpoints for job management and file processing
- **Modular Architecture**: Clean, extensible codebase with dependency injection
- **Async Processing**: Non-blocking transcription jobs for better performance

## Project Structure
```
ai_transcription_pipeline/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── api/                       # API routers and schemas
│   │   ├── routers/              # REST API endpoints
│   │   └── schemas/              # Pydantic data models
│   ├── config/                    # Application configuration
│   │   └── app_config.py         # Main configuration file
│   ├── containers/                # Dependency injection containers
│   │   ├── app_container.py      # Main DI container
│   │   ├── model_services_container.py
│   │   ├── pipeline_services_container.py
│   │   └── repositories_container.py
│   ├── models/                    # Domain models
│   │   ├── audio.py              # Audio file models
│   │   ├── transcription.py      # Transcription models
│   │   ├── transcription_job.py  # Job management models
│   │   └── summary.py            # Summary models
│   ├── repositories/              # Data access layer
│   ├── services/                  # Business logic
│   │   ├── model_services/       # AI model services
│   │   └── pipeline_services/    # Processing pipelines
│   ├── utils/                     # Utility functions
│   └── tests/                     # Test suite
├── data/                          # Data storage
│   ├── audios/                   # Processed audio files
│   ├── transcriptions/           # Generated transcription files
│   └── videos/                   # Video files (upload/processed)
├── database/                      # Database files
│   └── app.json                  # JSON database
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## Getting Started

### Prerequisites

#### System Requirements
- **Python**: 3.10 or higher
- **FFmpeg**: Required for audio/video processing
- **RAM**: Minimum 8GB (16GB recommended for large files)
- **Storage**: At least 2GB free space for models and data

#### Platform-Specific Prerequisites

##### Linux (Ubuntu/Debian)
```bash
# Update package manager
sudo apt update

# Install Python 3.10+ (if not already installed)
sudo apt install python3.10 python3.10-venv python3-pip

# Install FFmpeg
sudo apt install ffmpeg

# Install system dependencies for audio processing
sudo apt install libsndfile1 libasound2-dev
```

##### Linux (CentOS/RHEL/Fedora)
```bash
# For CentOS/RHEL
sudo yum install python3 python3-pip ffmpeg

# For Fedora
sudo dnf install python3 python3-pip ffmpeg

# Install audio libraries
sudo yum install libsndfile-devel alsa-lib-devel  # CentOS/RHEL
sudo dnf install libsndfile-devel alsa-lib-devel  # Fedora
```

##### Windows
1. **Install Python 3.10+**:
   - Download from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH" during installation
   - ✅ Check "Install pip"

2. **Install FFmpeg**:
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
   - Extract to `C:\ffmpeg`
   - Add `C:\ffmpeg\bin` to your PATH environment variable
   
3. **Verify installations**:
   ```cmd
   python --version
   pip --version
   ffmpeg -version
   ```

### Installation

#### 1. Clone the Repository
```bash
# Linux/macOS
git clone <your-repository-url>
cd ai_transcription_pipeline

# Windows (Command Prompt or PowerShell)
git clone <your-repository-url>
cd ai_transcription_pipeline
```

#### 2. Create Virtual Environment

##### Linux/macOS
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify activation (should show (.venv) in prompt)
which python
```

##### Windows

**Command Prompt:**
```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate.bat

# Verify activation
where python
```

**PowerShell:**
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify activation
Get-Command python
```

#### 3. Install Dependencies
```bash
# Upgrade pip (recommended)
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

#### 4. Environment Configuration
Create environment file:

##### Linux/macOS
```bash
# Create environment file
cp app/.env.example app/.env  # If example exists, or create manually:
touch app/.env
```

##### Windows
```cmd
# Create environment file
copy app\.env.example app\.env
# Or create manually if no example exists
```

Edit `app/.env` with your configuration:
```env
# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true

# File Storage
DATA_DIR=./data
UPLOAD_MAX_SIZE=100MB

# AI Model Configuration
MODEL_NAME=whisper-base
DEVICE=cpu  # or 'cuda' if you have GPU support
```

### Running the Application

#### Linux/macOS
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Start the server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# For production (without reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Windows
```cmd
# Make sure virtual environment is activated
.venv\Scripts\activate

# Start the server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# For production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Access the Application
- **API Server**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs (Swagger UI)
- **Alternative Docs**: http://127.0.0.1:8000/redoc

## API Usage

### Core Endpoints

#### Upload and Transcribe Audio
```bash
# Upload audio file for transcription
curl -X POST "http://127.0.0.1:8000/transcription/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/audio.wav" \
  -F "language=en"
```

#### Check Job Status
```bash
# Get transcription job status
curl -X GET "http://127.0.0.1:8000/transcription/jobs/{job_id}/status"
```

#### Download Results
```bash
# Download transcription results
curl -X GET "http://127.0.0.1:8000/transcription/jobs/{job_id}/download" \
  -o transcription.vtt

# Download processed video with subtitles
curl -X GET "http://127.0.0.1:8000/api/downloads/download_video/{job_id}" \
  -o processed_video.mkv

# Download subtitles for specific language
curl -X GET "http://127.0.0.1:8000/api/downloads/download_subtitles/{job_id}/{language}" \
  -o subtitles.vtt

# Get summaries for a job
curl -X GET "http://127.0.0.1:8000/api/downloads/summaries/{job_id}"
```

### Supported File Formats
- **Audio**: WAV, MP3, FLAC, OGG, M4A
- **Video**: MP4, AVI, MOV, MKV (audio will be extracted)

## Testing

### Run Tests
```bash
# Make sure virtual environment is activated
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_transcription.py

# Run with verbose output
pytest -v
```

### Test Structure
```
tests/
├── test_api/              # API endpoint tests
├── test_services/         # Service layer tests
├── test_repositories/     # Repository tests
└── test_data/            # Test data files
```

## Configuration

### Environment Variables
Key configuration options in `app/.env`:

```env
# Server Configuration
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=true

# File Storage
DATA_DIR=./data
MAX_FILE_SIZE=100MB
ALLOWED_EXTENSIONS=wav,mp3,flac,ogg,m4a,mp4,avi,mov,mkv

# AI Model Settings
MODEL_NAME=openai/whisper-base
DEVICE=cpu
BATCH_SIZE=16
MAX_AUDIO_LENGTH=1800  # 30 minutes

# Database
DATABASE_URL=sqlite:///./database/app.db
```

### Performance Tuning

#### For GPU Support (NVIDIA)
```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update .env
DEVICE=cuda
```

#### For Apple Silicon (M1/M2)
```bash
# Install PyTorch with MPS support
pip install torch torchvision torchaudio

# Update .env
DEVICE=mps
```

### Model Caching

AI models are automatically downloaded and cached by Hugging Face Transformers. By default, models are stored in:

- **Linux/macOS**: `~/.cache/huggingface/`
- **Windows**: `%USERPROFILE%\.cache\huggingface\`

The application uses the default Hugging Face cache directory, which provides several benefits:
- **Automatic management**: Models are automatically downloaded and cached
- **Shared storage**: Models are shared between different projects using the same models
- **Efficient storage**: Duplicate models are avoided across projects
- **Standard location**: Follows Hugging Face conventions

You can customize the cache location using the `HF_HOME` environment variable:
```bash
export HF_HOME=/path/to/custom/cache
```

## Troubleshooting

### Common Issues

#### FFmpeg Not Found
**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution**:
- **Linux**: `sudo apt install ffmpeg`
- **Windows**: Add FFmpeg to PATH or reinstall

#### Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Make sure you're in the project root directory
pwd  # Linux/macOS
cd   # Windows

# Verify virtual environment is activated
which python  # Linux/macOS
where python   # Windows
```

#### Memory Issues
**Error**: Out of memory errors during transcription

**Solution**:
- Reduce `BATCH_SIZE` in environment config
- Use smaller model (e.g., `whisper-tiny` instead of `whisper-base`)
- Process shorter audio files

#### Permission Errors (Windows)
**Error**: PowerShell execution policy errors

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Logs and Debugging
```bash
# Enable debug logging
export DEBUG=true  # Linux/macOS
set DEBUG=true     # Windows

# Check application logs
tail -f logs/app.log  # Linux/macOS
type logs\app.log     # Windows
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Submit a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black app/ tests/

# Run linting
flake8 app/ tests/
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

### Getting Help
- **Documentation**: Check this README and `/docs` endpoint
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

### System Information
When reporting issues, please include:
- Operating System and version
- Python version (`python --version`)
- Package versions (`pip list`)
- Error messages and logs
- Steps to reproduce

---

**Happy transcribing!**
