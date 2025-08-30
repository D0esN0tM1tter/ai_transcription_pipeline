from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class ModelSize(str, Enum):
    """Available Whisper model sizes"""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

class TranscriptionRequest(BaseModel):
    """Request model for transcription processing"""
    
    asr_model_size: ModelSize = Field(
        default=ModelSize.SMALL,
        description="Whisper model size to use for transcription. Larger models are more accurate but slower."
    )
    input_language: str = Field(
        ...,
        description="Input language code (e.g., 'en', 'es', 'fr')"
    )
    target_languages: List[str] = Field(
        ...,
        description="List of target languages for translation"
    )

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "asr_model_size": "small",
                "input_language": "en",
                "target_languages": ["es", "fr"]
            }
        }
