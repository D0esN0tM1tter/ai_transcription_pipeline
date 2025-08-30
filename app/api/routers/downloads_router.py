from fastapi import APIRouter , HTTPException , Depends
from app.containers.factory import app_container
from app.models.transcription_job import TranscriptionJob
from app.models.transcription import Transcription
from app.models.summary import Summary
from app.services.model_services.astract_services import AbstractServices
from app.api.schemas.summary_response import SummariesResponse, SummaryResponse
from pathlib import Path
from fastapi.responses import FileResponse
from typing import List


router = APIRouter(prefix="/downloads")

def get_jobs_service() : 
    return app_container.model_services_container.jobs_services

def get_transcriptions_service() : 
    return app_container.model_services_container.transcription_services

def get_summaries_service():
    return app_container.model_services_container.summary_services


import logging
logger = logging.getLogger(__name__)

@router.get("/download_video/{job_id}") 
async def download_video(job_id: str, jobs_services: AbstractServices[TranscriptionJob] = Depends(get_jobs_service)):

    job: TranscriptionJob = jobs_services.find_one_by_field(field_name="job_id", value=job_id)


    if not job or not job.processed_video_path:
        logger.warning(f"Job not found or processed_video_path missing for job_id: {job_id}")
        raise HTTPException(status_code=404, detail="Processed video was not found.")

    video_path = Path(job.processed_video_path)

    if not video_path.exists():
        logger.warning(f"Video file does not exist at path: {video_path}")
        raise HTTPException(status_code=404, detail="Video file was not found on the server.")

    return FileResponse(
        path=str(video_path),
        media_type="video/mkv",
        filename=video_path.name
    )


@router.get("/download_subtitles/{job_id}/{language}")

async def download_subtitle(
    job_id: str,
    language: str,
    transcriptions_services: AbstractServices[Transcription] = Depends(get_transcriptions_service)
):
    transcriptions: List[Transcription] = transcriptions_services.find_by_field(field_name="job_id", value=job_id)
    vtt_filepath: str = None

    if not transcriptions:
        logger.warning("No transcriptions found in the database.")
        raise HTTPException(status_code=404, detail="No transcriptions are found")

    for t in transcriptions:
        if t.target_language == language:
            subtitle_filepath = t.filepath
            break

    if not subtitle_filepath:
        logger.warning(f"No transcription found for language: {language}")
        raise HTTPException(status_code=404, detail="Subtitle for requested language not found.")

    filepath = Path(subtitle_filepath)
    if not filepath.exists():
        logger.warning("The filepath does not exist on the server's file system")
        raise HTTPException(status_code=404, detail="Subtitle filepath was not found on the server.")

    response =  FileResponse(
        path=str(filepath),
        media_type="text/vtt",
        filename=filepath.name
    )

    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5174"

    return response


@router.get("/summaries/{job_id}", response_model=SummariesResponse)
async def get_summaries(
    job_id: str,
    summaries_service: AbstractServices[Summary] = Depends(get_summaries_service),
    jobs_service: AbstractServices[TranscriptionJob] = Depends(get_jobs_service)
):
    """Get all summaries for a specific job"""
    try:
        # First verify the job exists
        job = jobs_service.find_one_by_field(field_name="job_id", value=job_id)
        if not job:
            logger.warning(f"Job not found for job_id: {job_id}")
            raise HTTPException(status_code=404, detail="Job not found")

        # Get summaries for this job
        summaries: List[Summary] = summaries_service.find_by_field(field_name="job_id", value=job_id)
        
        if not summaries:
            logger.info(f"No summaries found for job_id: {job_id}")
            return SummariesResponse(job_id=job_id, summaries=[])

        # Convert to response format
        summary_responses = [
            SummaryResponse(
                summary_id=summary.summary_id,
                job_id=summary.job_id,
                text_content=summary.text_content,
                language=summary.language
            )
            for summary in summaries
        ]

        return SummariesResponse(job_id=job_id, summaries=summary_responses)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving summaries for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve summaries")


