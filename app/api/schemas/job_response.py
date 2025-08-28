from pydantic import BaseModel
from typing import List

class JobResponse(BaseModel) : 

    job_id : str 
    processed_video_url : str  # url for downloading the file from the servers storage
    processed : bool 
    target_languages : List[str] 
    input_language : str 


    class Config : 
        orm_mode = True