from app.models.transcription_job import TranscriptionJob
from datetime import datetime
from typing import Optional
from app.repositories.abstract_repository import AbstractRepository
class TranscriptionJobRepository(AbstractRepository[TranscriptionJob]):

    
    def __init__(self, db_path):
        super().__init__(db_path, table_name="jobs")
    
    def from_dict(self, data):

        return TranscriptionJob(
            job_id=data["job_id"],
            video_storage_path=data["original_video_path"],
            processed_video_path=data.get("processed_video_path", ""),
            input_language=data["input_language"],
            target_languages=data["target_languages"],
            upload_date=datetime.fromisoformat(data["upload_date"]),
            processed=data["processed"]
        )
    
    def to_dict(self, entity : TranscriptionJob):
         
         return {
            "job_id": entity.id,
            "original_video_path": entity.video_storage_path,
            "processed_video_path": entity.processed_video_path,
            "input_language": entity.input_language,
            "target_languages": entity.target_languages,
            "upload_date": entity.upload_date.isoformat(),
            "processed": entity.processed
        }
 