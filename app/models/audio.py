import uuid 
from typing import Optional


class Audio:

    def __init__(self,
                 job_id: str,
                 audio_filepath: str,
                 language : Optional[str] = None
                 ):
        
        self.id = f"audio_{uuid.uuid4().hex[:]}_{job_id}"
        self.job_id = job_id
        self.audio_filepath = audio_filepath
        self.language = language

    def __repr__(self):
        return (f"Audio(id='{self.id}', job_id='{self.job_id}', "
                f"audio_filepath='{self.audio_filepath}' "
               )







