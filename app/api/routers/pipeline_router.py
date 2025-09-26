import logging
from fastapi import APIRouter, HTTPException , UploadFile, File , Form , Depends, Response
from fastapi.responses import FileResponse
import os
from app.api.schemas.job_response import JobResponse
from app.api.schemas.transcription_request import ModelSize
from app.models.transcription_job import TranscriptionJob
from typing import List
from app.containers.factory import app_container
from app.services.pipeline_services.integration_service import IntegrationService
from app.config.app_config import AppConfig
from app.utils.video_saver import save_video

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize router
router = APIRouter(prefix="/pipeline")

# Directory for processed videos
PROCESSED_VIDEOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/videos/processed'))

# Endpoint to list processed videos
@router.get("/processed-videos", response_model=List[str])
async def list_processed_videos():
    try:
        files = [f for f in os.listdir(PROCESSED_VIDEOS_DIR) if os.path.isfile(os.path.join(PROCESSED_VIDEOS_DIR, f))]
        return files
    except Exception as e:
        logger.error(f"Error listing processed videos: {e}")
        raise HTTPException(status_code=500, detail="Could not list processed videos.")

# Endpoint to download a processed video
@router.get("/processed-videos/{filename}")
async def download_processed_video(filename: str):
    file_path = os.path.join(PROCESSED_VIDEOS_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Video not found.")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream',
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def get_integration_service() : 
    return app_container.pipeline_services_container.integration_service

def get_app_config() : 
    return app_container.app_config


@router.post("/process", response_model=JobResponse)
async def process(
    video: UploadFile = File(...),
    input_language: str = Form(...),
    target_languages: List[str] = Form(...),
    asr_model_size: ModelSize = Form(
        default=ModelSize.SMALL,
        description="Whisper model size: tiny, base, small, medium, or large. Larger models are more accurate but slower."
    ),
    integration_service : IntegrationService = Depends(get_integration_service) , 
    app_config : AppConfig = Depends(get_app_config) , 
):
    try:
        
        stored_path = save_video(video=video , uploads_dir=app_config.UPLOAD_DIR)

        # Create and process the job
        job = TranscriptionJob(
            video_storage_path=str(stored_path),
            input_language=input_language,
            target_languages=target_languages,
            processed=False
        )

        processed_job = integration_service.process(job=job , asr_model_size=asr_model_size.value)

        return JobResponse(
            job_id=processed_job.id,
            processed_video_url=processed_job.processed_video_path,
            processed=processed_job.processed , 
            target_languages=processed_job.target_languages , 
            input_language=processed_job.input_language
        )

    except Exception as e:
        logger.error(f"Error processing job: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

