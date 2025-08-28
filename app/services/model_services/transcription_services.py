from app.services.model_services.astract_services import AbstractServices
from app.models.transcription import Transcription
from app.repositories.abstract_repository import AbstractRepository


class TranscriptionServices(AbstractServices[Transcription]) : 

    def __init__(self, repository : AbstractRepository[Transcription]):
        super().__init__(repository)

