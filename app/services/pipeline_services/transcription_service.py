import torch
import numpy as np
import gc
import librosa
import matplotlib.pyplot as plt
from app.models.transcription import Transcription
from app.services.pipeline_services.audio_service import AudioUtils

from transformers import (
    AutoModelForSpeechSeq2Seq,
    AutoProcessor,
    pipeline
)
import logging
import os
logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)

class ASRModel:
    """
    Automatic Speech Recognition Model wrapper for OpenAI Whisper.
    Handles loading, transcribing, and feature visualization.
    """

    def __init__(self):

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.pipeline = None
        logger.info(f"ASRModel initialized device={self.device}, dtype={self.dtype}")

    
    def _get_model(self , model_size : str) :
        whisper_models = {
            "tiny" : "openai/whisper-tiny" , 
            "base" : "openai/whisper-base" , 
            "small" : "openai/whisper-small" , 
            "medium" : "openai/whisper-medium" , 
            "large" : "openai/whisper-large"
        }
        
        if model_size not in whisper_models:
            available_sizes = list(whisper_models.keys())
            logger.warning(f"Invalid model size '{model_size}'. Available sizes: {available_sizes}. Defaulting to 'small'.")
            model_size = "small"
            
        model_id = whisper_models[model_size]
        logger.info(f"Selected Whisper model: {model_id}")
        return model_id

    def load(self , model_size : str):
        """Load ASR pipeline and save model/processor."""
        model_id = self._get_model(model_size)
        logger.info(f"Loading processor for model_id: {model_id}")
        processor = AutoProcessor.from_pretrained(model_id)
        try:
            logger.info(f"Loading model to device: {self.device}")
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype=self.dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True
            ).to(self.device)
        except torch.cuda.OutOfMemoryError:
            logger.warning("CUDA out of memory. Falling back to CPU.")
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                use_safetensors=True
            ).to("cpu")
            self.device = torch.device("cpu")
            self.dtype = torch.float32
        device_idx = 0 if str(self.device) == "cuda" else -1
        logger.info(f"Creating ASR pipeline on device_idx: {device_idx}")
        self.pipeline = pipeline(
            task="automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            device=device_idx
        )
        logger.info("ASR pipeline loaded successfully.")

    def unload(self):
        """Release pipeline and free memory."""
        logger.info("Unloading ASR pipeline and freeing memory.")
        self.pipeline = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("ASR pipeline unloaded.")

    def transcribe(self, audio: AudioUtils,model_size : str ,  translate_to_eng: bool = False) -> Transcription:
        """
        Transcribe audio using the loaded pipeline.
        Args:
            audio: AudioUtils instance with .array, .language, .job_id
            translate_to_eng: If True, translates to English
        Returns:
            Transcription object
        """
        logger.info(f"Starting transcription for job_id: {getattr(audio, 'job_id', None)}")
        if not isinstance(audio, AudioUtils):
            logger.error("audio must be AudioUtils instance")
            raise ValueError("audio must be AudioUtils instance")
        arr = getattr(audio, 'array', None)
        if arr is None or not isinstance(arr, np.ndarray) or arr.size == 0:
            logger.error("audio.array must be non-empty numpy array")
            raise ValueError("audio.array must be non-empty numpy array")
        if not getattr(audio, 'language', None):
            logger.error("audio.language missing")
            raise ValueError("audio.language missing")
        if not getattr(audio, 'job_id', None):
            logger.error("audio.job_id missing")
            raise ValueError("audio.job_id missing")

        self.load(model_size=model_size)

        logger.info(f"Transcribing audio (language={audio.language}, translate_to_eng={translate_to_eng})")
        kwargs = {"language": audio.language}
        if translate_to_eng:
            kwargs["task"] = "translate"
        result = self.pipeline(
            audio.array,
            return_timestamps=True,
            generate_kwargs=kwargs
        )
        logger.info("Transcription complete. Unloading pipeline.")
        self.unload()
        text = result.get("text", "")
        chunks = result.get("chunks", [])
        logger.info(f"Transcription result: text length={len(text)}, chunks={len(chunks)}")
        return Transcription(
            original_text=text,
            original_chunks=chunks,
            input_language=audio.language,
            job_id=audio.job_id
        )

    def visualize_features(self, output_path: str, audio: np.ndarray):
        """
        Save log-mel spectrogram of audio to output_path.
        Args:
            output_path: Path to save image
            audio: 1D numpy array
        """
        logger.info(f"Visualizing features for audio. Output path: {output_path}")
        if not output_path:
            logger.error("Output path required")
            raise ValueError("Output path required")
        if not isinstance(audio, np.ndarray) or audio.size == 0:
            logger.error("audio must be non-empty numpy array")
            raise ValueError("audio must be non-empty numpy array")
        if not self.pipeline:
            logger.error("Call load() before visualize_features")
            raise ValueError("Call load() before visualize_features")
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        processor = self.pipeline.feature_extractor
        inputs = processor(audio, 16000, return_tensor="pt")
        features = inputs.input_features[0]
        plt.figure(figsize=(12, 4))
        librosa.display.specshow(features, sr=16000, x_axis='time', y_axis='mel')
        plt.title("Log-Mel Spectrogram (Input Features)")
        plt.colorbar(format="%+2.0f dB")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        logger.info(f"Feature visualization saved to {output_path}")