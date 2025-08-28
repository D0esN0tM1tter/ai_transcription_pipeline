import unittest
import os
import json
from app.repositories.transcription_repository import TranscriptionRepository
from app.models.transcription import Transcription
from app.services.model_services.transcription_services import TranscriptionServices

class TranscriptionServicesTests(unittest.TestCase):
    TEST_DB_PATH = "app/tests/repositories/test_transcription.json"

    def setUp(self):
        # Ensure test db file is clean before each test
        with open(self.TEST_DB_PATH, "w") as f:
            f.write("{}")
        self.repository = TranscriptionRepository(db_path=self.TEST_DB_PATH)
        self.services = TranscriptionServices(repository=self.repository)

    def tearDown(self):
        # Remove test file after tests
        if os.path.exists(self.TEST_DB_PATH):
            os.remove(self.TEST_DB_PATH)

    def test_create(self):
        transcription = Transcription(
            original_text="Hello world",
            job_id="job123",
            original_chunks={"0": "Hello world"},
            input_language="en"
        )
        self.services.create(transcription)
        transcriptions = self.services.find_all()
        self.assertEqual(len(transcriptions), 1)
        self.assertEqual(transcriptions[0].id, transcription.id)

    def test_find_by_job_id(self):
        transcription = Transcription(
            original_text="Hello world",
            job_id="job123",
            original_chunks={"0": "Hello world"},
            input_language="en"
        )
        self.services.create(transcription)
        found = self.services.find_one_by_field(
            field_name="job_id",
            value=transcription.job_id
        )
        self.assertIsNotNone(found)
        self.assertEqual(found.id, transcription.id)

    def test_update_by_job_id(self):
        transcription = Transcription(
            original_text="Hello world",
            job_id="job123",
            original_chunks={"0": "Hello world"},
            input_language="en"
        )
        self.services.create(transcription)
        transcription.translated_text = "Bonjour le monde"
        updated = self.services.update_by_field(
            field_name="job_id",
            value=transcription.job_id,
            entity=transcription
        )
        self.assertTrue(updated)
        found = self.services.find_one_by_field(
            field_name="job_id",
            value=transcription.job_id
        )
        self.assertEqual(found.translated_text, "Bonjour le monde")
