from app.services.pipeline_services.subtitle_formatter_service import SubtitleWriter
from app.repositories.transcription_repository import TranscriptionRepository
from app.services.model_services.transcription_services import TranscriptionServices
from app.models.transcription import Transcription
from typing import List
import unittest

class TestSubtitlesFormatting(unittest.TestCase) : 
    
    def setUp(self):

        self.TEST_DB_PATH = "app/tests/database/test_db.json"
        self.SUB_DIR = "app/tests/test_data/transcriptions"

        self.repository = TranscriptionRepository(
            db_path=self.TEST_DB_PATH
        )
        self.transcription_service = TranscriptionServices(repository=self.repository)
        self.formatter = SubtitleWriter(
            transcription_service=self.transcription_service
        )

        transcription_1 = Transcription(
            transcription_id="transcription_4b1b7c2bed9c4126ae6011ac775f5335_job_814bdfe3e0b640779939d0522aa08a0e",
            job_id="job_814bdfe3e0b640779939d0522aa08a0e",
            original_text="Bonjour, bienvenu.",
            original_chunks=[
                {
                    "timestamp": [0.0, 5.0],
                    "text": "Bonjour, bienvenu."
                }
            ],
            tr_text="app/tests/test_data/transcriptions/transcription_61a08c08f32543e0a532dac63c0365f7_job_83cc2d09aa2a4614bd644969d1e3c1da_french.vtt",
            tr_chunks=[],
            input_language="french",
            target_language="french",
            filepath="app/tests/test_data/transcriptions/transcription_61a08c08f32543e0a532dac63c0365f7_job_83cc2d09aa2a4614bd644969d1e3c1da_french.vtt",
        )

        transcription_2 = Transcription(

            transcription_id="transcription_a26f1717524f44aca8c51c6db3c8e28a_job_814bdfe3e0b640779939d0522aa08a0e",
            job_id="job_814bdfe3e0b640779939d0522aa08a0e",
            original_text="Bonjour, bienvenu.",
            original_chunks=[
                {
                    "timestamp": [0.0, 5.0],
                    "text": "Bonjour, bienvenu."
                }
            ],
            tr_text="مرحباً، مرحباً، مرحباً.",
            tr_chunks=[
                {
                    "timestamp": [0.0, 5.0],
                    "text": "مرحباً، مرحباً، مرحباً."
                }
            ],
            input_language="french",
            target_language="arabic",
            filepath="app/tests/test_data/transcriptions/transcription_0395b849729e48dfa4a7718cc94f163e_job_83cc2d09aa2a4614bd644969d1e3c1da_arabic.vtt",
        )
        
        transcription_3 = Transcription(

            transcription_id="transcription_a2aeef3b318a453396cd9e249be8caba_job_814bdfe3e0b640779939d0522aa08a0e",
            job_id="job_814bdfe3e0b640779939d0522aa08a0e",
            original_text="Bonjour, bienvenu.",
            original_chunks=[
                {
                    "timestamp": [0.0, 5.0],
                    "text": "Bonjour, bienvenu."
                }
            ],
            tr_text="Hello, welcome.",
            tr_chunks=[
                {
                    "timestamp": [0.0, 5.0],
                    "text": "Hello, welcome."
                }
            ],
            input_language="french",
            target_language="english",
            filepath="app/tests/test_data/transcriptions/transcription_54259f2a72e845fb858f8e2ecef25b66_job_83cc2d09aa2a4614bd644969d1e3c1da_english.vtt",
        )

        self.transcriptions = [transcription_1 , transcription_2 , transcription_3]

    def test_vtt_formatting(self) :
        
        result : List[Transcription] = self.formatter.batch_save(
            transcription_list=self.transcriptions , 
            output_dir=self.SUB_DIR
        )

        for t in result : 
            self.assertIsNotNone(t.filepath)