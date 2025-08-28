from app.services.model_services.astract_services import AbstractServices
from app.models.transcription_job import TranscriptionJob
from app.repositories.abstract_repository import AbstractRepository


class TranscriptionJobServices(AbstractServices[TranscriptionJob]) : 

    def __init__(self, repository : AbstractRepository[TranscriptionJob]):
        super().__init__(repository)
    
