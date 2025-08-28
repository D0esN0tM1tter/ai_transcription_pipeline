from app.repositories.abstract_repository import AbstractRepository
from app.models.transcription import Transcription
from datetime import datetime
from typing import Optional,Dict

class TranscriptionRepository(AbstractRepository[Transcription]) : 
    
    def __init__(self, db_path):
        super().__init__(db_path, table_name="transcriptions")
    
    
    def from_dict(self , data: Dict) -> Transcription:
        return Transcription(
            transcription_id=data["transcription_id"],
            original_text=data["original_text"],
            job_id=data["job_id"],
            original_chunks=data["original_chunks"],
            input_language=data["input_language"],
            tr_text=data.get("translated_text"),
            tr_chunks=data.get("translated_chunks"),
            target_language=data.get("target_language"),
            filepath=data.get("filepath"),
            creation_datetime=datetime.fromisoformat(data["creation_datetime"]) if "creation_datetime" in data else None,
        )

    
    
    def to_dict(self , data : Transcription) :
        return {
            "transcription_id": data.id,
            "job_id": data.job_id,
            "original_text": data.original_text,
            "original_chunks": data.original_chunks,
            "translated_text": data.translated_text,
            "translated_chunks": data.translated_chunks,
            "input_language": data.input_language,
            "target_language": data.target_language,
            "filepath": data.filepath,
            "creation_datetime": data.creation_datetime.isoformat()
        }

 

