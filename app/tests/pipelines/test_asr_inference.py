import unittest
from app.services.pipeline_services.transcription_service import ASRModel
from app.services.pipeline_services.audio_service import AudioUtils
from app.models.audio import Audio
from app.models.transcription import Transcription


class TestSpeechRecognitionModel(unittest.TestCase):

    def setUp(self):
        audio = Audio(
            job_id="job_814bdfe3e0b640779939d0522aa08a0e",
            audio_filepath="app/tests/test_data/audios/app/tests/test_data/audios/audio_4788a9972eb94994b59a80f5b1d508d1_job_814bdfe3e0b640779939d0522aa08a0e.wav",
            language="french"
        )
        self.processed_audio = AudioUtils.load_resample_audio(audio)
        self.asr_model = ASRModel()

    def test_asr_model(self):
        result: Transcription = self.asr_model.transcribe(audio=self.processed_audio , model_size="base")
        print(f"{result.original_chunks}")
        self.assertTrue(len(result.original_text) > 0)
        self.assertEqual(result.job_id, self.processed_audio.job_id)
        self.assertEqual(result.input_language, self.processed_audio.language)
