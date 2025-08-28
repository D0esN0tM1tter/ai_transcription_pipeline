import os
from dotenv import load_dotenv

class AppConfig:

    def __init__(self):
        load_dotenv()

        self.DB_PATH = self._get_env("DB_PATH")
        self.AUDIOS_DIR = self._get_env("AUDIOS_DIR")
        self.PROCESSED_VID_DIR = self._get_env("PROCESSED_VID_DIR")
        self.TRANSCRIPTIONS_DIR = self._get_env("TRANSCRIPTIONS_DIR")
        self.UPLOAD_DIR = self._get_env("UPLOAD_DIR")

    def _get_env(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Missing required environment variable: {name}")
        return value
