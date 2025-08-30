from app.services.model_services.astract_services import AbstractServices
from app.services.model_services.transcription_job_services import TranscriptionJobServices
from app.services.model_services.transcription_services import TranscriptionServices
from app.services.model_services.summary_services import SummaryServices
from app.models.transcription import Transcription
from app.models.transcription_job import TranscriptionJob
from app.models.summary import Summary
from app.containers.repositories_container import RepositoriesContainer

class ModelServicesContainer:
    def __init__(self, repositories_container: RepositoriesContainer):
        self.repositories_container = repositories_container
        self._transcription_service: AbstractServices[Transcription] = None
        self._job_service: AbstractServices[TranscriptionJob] = None
        self._summary_service: AbstractServices[Summary] = None

    @property
    def transcription_services(self) -> AbstractServices[Transcription]:
        if self._transcription_service is None:
            self._transcription_service = TranscriptionServices(
                repository=self.repositories_container.transcriptions_repository
            )
        return self._transcription_service

    @property
    def jobs_services(self) -> AbstractServices[TranscriptionJob]:
        if self._job_service is None:
            self._job_service = TranscriptionJobServices(
                repository=self.repositories_container.jobs_repository
            )
        return self._job_service

    @property
    def summary_services(self) -> AbstractServices[Summary]:
        if self._summary_service is None:
            self._summary_service = SummaryServices(
                repository=self.repositories_container.summaries_repository
            )
        return self._summary_service

    
    
    
    
        