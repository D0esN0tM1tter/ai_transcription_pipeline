import uuid
from datetime import datetime
from typing import List, Optional

class TranscriptionJob:
    def __init__(self,
                 video_storage_path: str,
                 input_language: str,
                 target_languages: List[str],
                 processed: bool = False,
                 job_id: Optional[str] = None,
                 processed_video_path: Optional[str] = "",
                 upload_date: Optional[datetime] = None):
        
        self.id = job_id or f"job_{uuid.uuid4().hex[:]}"
        self.video_storage_path = video_storage_path
        self.processed_video_path = processed_video_path or ""
        self.input_language = input_language
        self.target_languages = target_languages
        self.upload_date: datetime = upload_date or datetime.now()
        self.processed = processed
        self.video_storage_path = video_storage_path
        self.summary = ""




   

