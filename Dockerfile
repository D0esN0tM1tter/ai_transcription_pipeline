# Use the official Python 3.11 slim image as the base for our app
FROM python:3.11-slim

# Make Python output print statements directly (no buffering)
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container to /app
WORKDIR /app

# Install system dependencies needed for audio/video processing and downloading
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python packages listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app/ ./app/

# Copy database and data directories to ensure initial structure exists
COPY database/ ./database/
COPY data/ ./data/

# Create necessary directories if they don't exist
RUN mkdir -p /app/database /app/data/audios /app/data/videos/processed /app/data/transcriptions /app/data/videos/upload

# Set environment variables for file and database locations
ENV DB_PATH=/app/database/app.json \
    AUDIOS_DIR=/app/data/audios \
    PROCESSED_VID_DIR=/app/data/videos/processed \
    TRANSCRIPTIONS_DIR=/app/data/transcriptions \
    UPLOAD_DIR=/app/data/videos/upload

# Declare persistent volumes for database and all data directories
VOLUME ["/app/database", "/app/data"]

# Expose port 8000 so we can access the app from outside the container
EXPOSE 8000

# Start the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
