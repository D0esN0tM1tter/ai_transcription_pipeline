import unittest
from app.repositories.transcription_repository import TranscriptionRepository
from app.models.transcription import Transcription
import os
from datetime import datetime
from typing import List, Optional

class TranscriptionRepositoryTests(unittest.TestCase) :

    TEST_DB_PATH = "app/tests/repositories/test.json"

    def setUp(self):
        """
        Establishing the setup before each test
        """
        with open(self.TEST_DB_PATH , "w") as f :
            f.write("{}")
        self.repository = TranscriptionRepository(db_path=self.TEST_DB_PATH)

        self.mock_transcription = Transcription(
            original_text="This is the original text.",
            job_id="job_123",
            original_chunks={"0": "This is", "1": "the original text."},
            input_language="en",
            tr_text="Ceci est le texte original.",
            tr_chunks={"0": "Ceci est", "1": "le texte original."},
            target_language="fr",
            filepath="/path/to/subtitles.srt",
            creation_datetime=datetime.now(),
            transcription_id="transcription_abc123"
)

    def tearDown(self):
        """
        clearing any changes performed by the test
        """

        if os.path.exists(self.TEST_DB_PATH) :
            os.remove(self.TEST_DB_PATH)

    def test_create(self) : 
        created : int = self.repository.create(entity=self.mock_transcription) 
        found : List[Transcription] = self.repository.get_all() 
        self.assertEqual(created , 1)
        self.assertEqual(len(found) , 1) 
        self.assertEqual(self.mock_transcription.id , found[0].id)

    def test_find_by_transcription_id(self) :

        created : int = self.repository.create(self.mock_transcription) 

        found : Optional[Transcription] = self.repository.find_one_by_field(
            field_name="transcription_id" , 
            value=self.mock_transcription.id
        )

        self.assertEqual(created , 1)
        self.assertIsNotNone(found) 
        self.assertEqual(found.id , self.mock_transcription.id)

    def test_update_by_transcription_id(self) : 

        self.repository.create(self.mock_transcription) 

        self.mock_transcription.filepath = "MODIFIED" 

        updated : bool = self.repository.update_by_field(
            field_name="transcription_id" , 
            value=self.mock_transcription.id , 
            entity=self.mock_transcription
        )

        found : Optional[Transcription] = self.repository.find_one_by_field(
            field_name="transcription_id" , 
            value=self.mock_transcription.id , 

        )

        self.assertTrue(updated)
        self.assertEqual(found.filepath , "MODIFIED")
        


