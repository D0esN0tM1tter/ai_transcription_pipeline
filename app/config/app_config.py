import os
from dotenv import load_dotenv


class AppConfig:

    def __init__(self):
        load_dotenv()

        # Set BASE_DIR to the parent directory of this config file (i.e., /app)
        self.BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        self.DB_PATH = self._resolve_path(self._get_env("DB_PATH"))
        self.AUDIOS_DIR = self._resolve_path(self._get_env("AUDIOS_DIR"))
        self.PROCESSED_VID_DIR = self._resolve_path(self._get_env("PROCESSED_VID_DIR"))
        self.TRANSCRIPTIONS_DIR = self._resolve_path(self._get_env("TRANSCRIPTIONS_DIR"))
        self.UPLOAD_DIR = self._resolve_path(self._get_env("UPLOAD_DIR"))
        self.LLM_MODELS_DIR = self._resolve_path(self._get_env("LLM_MODELS_DIR"))

        # Create directories if they do not exist
        for directory in [
            os.path.dirname(self.DB_PATH),
            self.AUDIOS_DIR,
            self.PROCESSED_VID_DIR,
            self.TRANSCRIPTIONS_DIR,
            self.UPLOAD_DIR,
            self.LLM_MODELS_DIR
        ]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

    def _get_env(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ValueError(f"Missing required environment variable: {name}")
        return value

    def _resolve_path(self, path: str) -> str:
        # If path is absolute, return as is; else, join with BASE_DIR
        if os.path.isabs(path):
            return path
        return os.path.normpath(os.path.join(self.BASE_DIR, path))
