from app.services.pipeline_services.translation_service import TranslationModel
from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.repositories.transcription_repository import TranscriptionRepository
from app.services.model_services.transcription_job_services import TranscriptionJobServices
from app.services.model_services.transcription_services import TranscriptionServices
from app.models.transcription import Transcription
from typing import List
import unittest 



class TestTranslationModel(unittest.TestCase) : 

    def setUp(self):
        
        self.TEST_DB_PATH = "app/tests/database/test_db.json"

        self.tr_repo = TranscriptionRepository(db_path=self.TEST_DB_PATH)
        self.job_repo = TranscriptionJobRepository(db_path=self.TEST_DB_PATH)
        self.transcription_service = TranscriptionServices(repository=self.tr_repo)
        self.job_service = TranscriptionJobServices(repository=self.job_repo)
        self.translator = TranslationModel(
            job_service=self.job_service,
            transcription_service=self.transcription_service
        )

        self.transcription = Transcription(
            job_id="job_814bdfe3e0b640779939d0522aa08a0e",
            input_language="french",
            original_text="Bonjour, bienvenu.",
            original_chunks=
                [ {
                    "timestamp": (0.0, 5.0),
                    "text": "Bonjour, bienvenu."
                }]
        )
    
    def test_translation_model(self) :
        
        result : List[Transcription] = self.translator.translate_transcription_to_multiple_languages(
            transcription=self.transcription
        ) 


        self.assertIsInstance(result , List)
        self.assertEqual(len(result) , 3)
        
        for t in result : 
            self.assertEqual(t.job_id , self.transcription.job_id) 
            self.assertIsNotNone(t.translated_text)
            self.assertIsNotNone(t.translated_chunks) 
            self.assertIsNotNone(t.target_language)
            self.assertIn(t.target_language , ["french" , "english" , "arabic"])
              