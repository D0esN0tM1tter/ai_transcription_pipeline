from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.services.pipeline_services.ffmpeg_service import FfmpegUtils
from app.services.model_services.transcription_job_services import TranscriptionJobServices
from app.models.transcription import Transcription
from app.models.transcription_job import TranscriptionJob
import unittest


class TestSubtitleMuxing(unittest.TestCase) :
    
    def setUp(self):

        self.TEST_DB_PATH = "app/tests/database/test_db.json"
        self.OUTPUT_DIR = "app/tests/test_data/audios"
        self.PROCESSED_VID = "app/tests/test_data/videos/processed"

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
            filepath="app/tests/test_data/transcriptions/transcription_4b1b7c2bed9c4126ae6011ac775f5335_job_814bdfe3e0b640779939d0522aa08a0e_french.vtt",
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
            filepath="app/tests/test_data/transcriptions/transcription_a26f1717524f44aca8c51c6db3c8e28a_job_814bdfe3e0b640779939d0522aa08a0e_arabic.vtt",
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
            filepath="app/tests/test_data/transcriptions/transcription_a2aeef3b318a453396cd9e249be8caba_job_814bdfe3e0b640779939d0522aa08a0e_english.vtt",
        )

        self.transcriptions = [transcription_1 , transcription_2 , transcription_3]


    def test_subtitle_muxing(self) : 

        result : TranscriptionJob = self.ffmpeg_service.mux_subtitles(

            transcriptions_list=self.transcriptions , 

            output_dir=self.PROCESSED_VID
        )

        self.assertEqual(result.id , self.transcriptions[0].job_id)
        self.assertIsNotNone(result.processed_video_path) 
        self.assertEqual(result.input_language , "french") 



        
