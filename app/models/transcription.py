import uuid
from datetime import datetime
from typing import Dict, Optional


class Transcription:
    def __init__(self,
                 original_text: str,
                 job_id: str,
                 original_chunks: Dict,
                 input_language: str,
                 tr_text: Optional[str] = None,
                 tr_chunks: Optional[Dict] = None,
                 target_language: Optional[str] = None,
                 filepath: Optional[str] = None,
                 creation_datetime: Optional[datetime] = None,
                 transcription_id: Optional[str] = None):
        
        self.id = transcription_id or f"transcription_{uuid.uuid4().hex[:]}_{job_id}"
        self.job_id = job_id
        self.original_text = original_text
        self.original_chunks = original_chunks
        self.translated_text = tr_text
        self.translated_chunks = tr_chunks
        self.input_language = input_language
        self.target_language = target_language
        self.filepath = filepath
        self.creation_datetime: datetime = creation_datetime or datetime.now()

   