import uuid
from typing import Optional



class Summary : 

    def __init__(self , 
                 job_id : str , 
                 text_content : str , 
                 language : str , 
                 id : Optional[str] = None , 
):
        
        self.summary_id = id or  f"summary{uuid.uuid4().hex[:]}_{job_id}"
        self.job_id = job_id
        self.text_content = text_content
        self.language = language