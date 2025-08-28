import unittest
import os
import logging

from typing import Dict
from app.services.pipeline_services.ffmpeg_service import FfmpegUtils 
from app.models.transcription_job import TranscriptionJob
from app.models.audio import Audio
from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.services.model_services.transcription_job_services import TranscriptionJobServices

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

class TestAudioExtraction(unittest.TestCase): 

    def setUp(self):
        self.TEST_DB_PATH = "app/tests/database/test_db.json"
        self.OUTPUT_DIR = "app/tests/test_data/audios"
        self.OUT_AUDIO_PATH = None

        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        with open(self.TEST_DB_PATH, "w") as f:
            f.write("{}")

        self.repository = TranscriptionJobRepository(
            db_path=self.TEST_DB_PATH
        )
        self.job_service = TranscriptionJobServices(repository=self.repository)

        self.job = TranscriptionJob(
            video_storage_path="app/tests/test_data/videos/news_french.mp4", 
            input_language='french', 
            target_languages=["arabic", "english"]
        )  

        self.ffmpeg_service = FfmpegUtils(
            job_service=self.job_service
        )
    
    def tearDown(self):
        pass
       
    def test_audio_extraction(self):

        result: Audio = self.ffmpeg_service.extract_audio(
            job=self.job, 
            output_dir=self.OUTPUT_DIR ,
            duration="00:00:05"
        )

        self.OUT_AUDIO_PATH = result.audio_filepath

        self.assertIsNotNone(result.audio_filepath) 
        self.assertEqual(result.job_id, self.job.id)
