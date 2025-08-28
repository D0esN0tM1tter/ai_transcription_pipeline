from app.repositories.abstract_repository import AbstractRepository
from app.models.summary import Summary



class SummaryRepository(AbstractRepository[Summary]) : 

    def __init__(self, db_path):
        super().__init__(db_path, table_name="summaries")

    

    def from_dict(self, data):
        return Summary(
            id=data["summary_id"] , 
            job_id=data["job_id"] , 
            text_content=data["text_content"] , 
            language=data["language"]
        )
    
    def to_dict(self, entity : Summary):

        return {
            "summary_id" : entity.summary_id , 
            "job_id" : entity.job_id , 
            "language" : entity.language , 
            "text_content" : entity.text_content
        }
