from app.services.pipeline_services.ffmpeg_service import FfmpegUtils
from app.services.pipeline_services.audio_service import AudioUtils
#from app.services.pipeline_services.summarization_service import SummerizationModel
from app.services.pipeline_services.transcription_service import ASRModel
from app.services.pipeline_services.translation_service import TranslationModel
from app.services.pipeline_services.subtitle_formatter_service import SubtitleWriter
from app.services.pipeline_services.integration_service import IntegrationService
from app.containers.model_services_container import ModelServicesContainer
from app.config.app_config import AppConfig

class PipelineServicesContainer:
    def __init__(self, model_services_container: ModelServicesContainer , app_config : AppConfig ):
        self.model_services_container = model_services_container
        self._ffmpeg = None
        self._audio_utils = None
        self._asr_model = None
        self._translator = None
        self._subtitle_writer = None
        self._summarization_model = None
        self._integration_service = None
        self.app_config = app_config
        

    @property
    def ffmpeg(self):
        if self._ffmpeg is None:
            self._ffmpeg = FfmpegUtils(
                job_service=self.model_services_container.jobs_services
            )
        return self._ffmpeg

    @property
    def audio_utils(self):
        if self._audio_utils is None:
            self._audio_utils = AudioUtils
        return self._audio_utils

    @property
    def asr_model(self):
        if self._asr_model is None:
            self._asr_model = ASRModel()
        return self._asr_model

    @property
    
    def translator(self):
        if self._translator is None:
            self._translator = TranslationModel(
                job_service=self.model_services_container.jobs_services,
                transcription_service=self.model_services_container.transcription_services
            )
        return self._translator

    @property
    def subtitle_writer(self):
        if self._subtitle_writer is None:
            self._subtitle_writer = SubtitleWriter(
                transcription_service=self.model_services_container.transcription_services
            )
        return self._subtitle_writer
    
    """
    @property 
    def summarization_model(self) : 
        if self._summarization_model is None : 
            self.summarization_model = SummerizationModel()
        
        return self._summarization_model
    """

    @property
    def integration_service(self):
        if self._integration_service is None:
            self._integration_service = IntegrationService(
                ffmpeg=self.ffmpeg , 
                audio_utils=self.audio_utils , 
                asr_model=self.asr_model , 
                translator=self.translator , 
                writer=self.subtitle_writer ,
                app_config=self.app_config
            )
        return self._integration_service
