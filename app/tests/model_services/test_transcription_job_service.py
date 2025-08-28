import unittest
import os
import json
from app.repositories.transcription_job_repository import TranscriptionJobRepository
from app.models.transcription_job import TranscriptionJob
from app.services.model_services.transcription_job_services import TranscriptionJobServices


class TranscriptionServicesTests(unittest.TestCase):
    TEST_DB_PATH = "app/tests/repositories/test.json"

    def setUp(self):
        # Ensure test db file is clean before each test
        with open(self.TEST_DB_PATH, "w") as f:
            f.write("{}")
        self.repository = TranscriptionJobRepository(db_path=self.TEST_DB_PATH)
        self.services = TranscriptionJobServices(repository=self.repository)

    def tearDown(self):
        # Remove test file after tests
        if os.path.exists(self.TEST_DB_PATH):
            os.remove(self.TEST_DB_PATH)

    def test_create(self):
        job = TranscriptionJob(
            video_storage_path="video.mp4",
            input_language="en",
            target_languages=["fr"]
        )

        self.services.create(job)
        jobs = self.services.find_all()
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].id, job.id)

    def test_find_by_job_id(self):
        job = TranscriptionJob(
            video_storage_path="video.mp4",
            input_language="en",
            target_languages=["fr"]
        )
        self.services.create(job)

        found = self.services.find_one_by_field(
            field_name="job_id" , 
            value=job.id
        )
        self.assertIsNotNone(found)
        self.assertEqual(found.id, job.id)

    def test_update_by_job_id(self):

        job = TranscriptionJob(
            video_storage_path="video.mp4",
            input_language="en",
            target_languages=["fr"]
        )
        self.services.create(job)
        job.processed = True


        updated = self.services.update_by_field(
            field_name="job_id" , 
            value=job.id , 
            entity=job

        )
        self.assertTrue(updated)
        found = self.services.find_one_by_field(
            field_name="job_id" , 
            value=job.id
        )
        self.assertTrue(found.processed)


