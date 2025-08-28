from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.repositories.transcription_repository import TranscriptionRepository
from app.repositories.abstract_repository import AbstractRepository
from app.models.transcription import Transcription
from app.models.transcription_job import TranscriptionJob


class RepositoriesContainer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._transcription_repo: AbstractRepository[Transcription] = None
        self._job_repo: AbstractRepository[TranscriptionJob] = None

    @property
    def jobs_repository(self) -> AbstractRepository[TranscriptionJob]:
        if self._job_repo is None:
            self._job_repo = TranscriptionJobRepository(db_path=self.db_path)
        return self._job_repo

    @property
    def transcriptions_repository(self) -> AbstractRepository[Transcription]:
        if self._transcription_repo is None:
            self._transcription_repo = TranscriptionRepository(db_path=self.db_path)
        return self._transcription_repo
