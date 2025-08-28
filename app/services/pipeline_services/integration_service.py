from app.services.pipeline_services.audio_service import AudioUtils 
from app.services.pipeline_services.ffmpeg_service import FfmpegUtils
from app.services.pipeline_services.subtitle_formatter_service import SubtitleWriter
from app.services.pipeline_services.transcription_service import  ASRModel 
from app.services.pipeline_services.translation_service import TranslationModel
#from app.services.pipeline_services.summarization_service import SummerizationModel
from app.models.transcription import Transcription 
from app.models.transcription_job import TranscriptionJob
from app.models.audio import Audio
from typing import List
import logging
from app.config.app_config import AppConfig

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)




class IntegrationService:
    def __init__(
        self,
        ffmpeg: FfmpegUtils,
        audio_utils: AudioUtils,
        asr_model: ASRModel,
        translator: TranslationModel,
        writer: SubtitleWriter, 
        app_config : AppConfig
    ):
        self.ffmpeg = ffmpeg
        self.audio_utils = audio_utils
        self.asr_model = asr_model
        self.translator = translator
        self.writer = writer
        self.app_config : AppConfig = app_config

    

    def process(self , job : TranscriptionJob) -> TranscriptionJob: 

        # audio extraction : 
        extracted_audio : Audio = self.ffmpeg.extract_audio(
            job=job , 
            output_dir=self.app_config.AUDIOS_DIR
        )

        # preprocessing (if needed ) 
        extracted_audio = self.audio_utils.load_resample_audio(audio=extracted_audio)

        # speech recognition : 
        transcription : Transcription = self.asr_model.transcribe(
            audio=extracted_audio , 
            translate_to_eng=False
        )

        # translation : 
        transcriptions : List[Transcription] = self.translator.translate_transcription_to_multiple_languages(transcription=transcription)

        # subtitle formatting : 
        transcriptions : List[Transcription] = self.writer.batch_save(
            transcription_list=transcriptions , 
            output_dir= self.app_config.TRANSCRIPTIONS_DIR )

        # subtitle muxing : 
        job : TranscriptionJob = self.ffmpeg.mux_subtitles(
            transcriptions_list=transcriptions , 
            output_dir=self.app_config.PROCESSED_VID_DIR
        )

        # Summarization of the video : 

        return job


        
        

        