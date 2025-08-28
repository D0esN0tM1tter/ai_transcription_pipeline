import torch
import numpy as np
import gc
import librosa
import matplotlib.pyplot as plt
from typing import Dict
from app.models.transcription import Transcription
from app.services.pipeline_services.audio_service import AudioUtils

from transformers import (
    AutoModelForSpeechSeq2Seq,
    AutoProcessor,
    AutomaticSpeechRecognitionPipeline,
    pipeline
)

from typing import Optional
import logging
import os
import traceback

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)

class ASRModel : 

    def __init__(self , model_size : str = "small" ) :

        self.model_id = f"openai/whisper-{model_size}" 
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.pipeline : Optional[AutomaticSpeechRecognitionPipeline] = None
        logger.info(f"ASR Model initialized with model_id: openai/whisper-{model_size}, device: {self.device}, dtype: {self.dtype}")
            
 
    
    
    
    def load(self) -> AutomaticSpeechRecognitionPipeline: 
        
        try : 
            logger.info("Loading processor for model : %s" , self.model_id)
            
            try:
                processor = AutoProcessor.from_pretrained(self.model_id)
            except Exception as e:
                logger.error(f"Failed to load processor for model {self.model_id}: {e}")
                raise RuntimeError(f"Processor loading failed: {e}") from e

            logger.info("Loading model to device : %s" , self.device)
            
            try:
                model = AutoModelForSpeechSeq2Seq.from_pretrained(

                    self.model_id, 
                    torch_dtype= self.dtype ,  
                    low_cpu_mem_usage = True,  
                    use_safetensors = True
                ).to(self.device)

            except torch.cuda.OutOfMemoryError as e:
                logger.error(f"CUDA out of memory while loading model: {e}")
                # Try to free memory and retry with CPU
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    gc.collect()
                logger.warning("Retrying model loading on CPU due to memory constraints")
                self.device = torch.device("cpu")
                self.dtype = torch.float32
                try:
                    model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        self.model_id , 
                        torch_dtype= self.dtype ,  
                        low_cpu_mem_usage = True,  
                        use_safetensors = True
                    ).to(self.device)
                except Exception as retry_e:
                    logger.error(f"Failed to load model even on CPU: {retry_e}")
                    raise RuntimeError(f"Model loading failed on both GPU and CPU: {retry_e}") from retry_e
            except Exception as e:
                logger.error(f"Failed to load model {self.model_id}: {e}")
                raise RuntimeError(f"Model loading failed: {e}") from e

            try:
                device_idx = 0 if str(self.device) == "cuda" else -1 
                logger.info("Loading pipeline for model : %s" , self.model_id) 

                self.pipeline = pipeline (
                    task = "automatic-speech-recognition" ,
                    model=model, 
                    tokenizer=processor.tokenizer, 
                    feature_extractor=processor.feature_extractor, 
                    device=device_idx
                )
            except Exception as e:
                logger.error(f"Failed to create pipeline: {e}")
                # Clean up loaded model before raising
                try:
                    del model
                    del processor
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except:
                    pass
                raise RuntimeError(f"Pipeline creation failed: {e}") from e

            logger.info("ASR pipeline initilized successfully")
            return self.pipeline
        
        except Exception as e : 
            logger.error("failed to load model or pipeline : %s" , e)
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Ensure cleanup on any failure
            self.unload()
            raise

    def unload(self):  
        logger.info("Unloading ASR model and freeing memory") 

        try: 
            if self.pipeline: 
                try:
                    del self.pipeline
                    self.pipeline = None
                except Exception as e:
                    logger.warning(f"Error deleting pipeline: {e}")

            try:
                gc.collect() 
            except Exception as e:
                logger.warning(f"Error during garbage collection: {e}")

            if torch.cuda.is_available(): 
                try:
                    torch.cuda.empty_cache() 
                except Exception as e:
                    logger.warning(f"Error clearing CUDA cache: {e}")

            logger.info("Resources released successfully") 

        except Exception as e: 
            logger.error("Error while unloading the model: %s", e)
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise here - unload should be robust and not fail

    def transcribe(self , audio : AudioUtils, translate_to_eng : bool = False )-> Transcription : 

        # Validate inputs
        if not isinstance(audio, AudioUtils):
            raise ValueError("Audio input must be an AudioUtils instance")
        
        if not hasattr(audio, 'array') or audio.array is None:
            raise ValueError("Audio array is None or missing")
            
        if not hasattr(audio, 'language') or not audio.language:
            raise ValueError("Audio language is None or missing")
            
        if not hasattr(audio, 'job_id') or not audio.job_id:
            raise ValueError("Audio job_id is None or missing")

        try:
            self.load()
        except Exception as e:
            logger.error(f"Failed to load model for transcription: {e}")
            raise RuntimeError(f"Model loading failed during transcription: {e}") from e

        try : 
            logger.info("transcribing audio input audio with language : %s" , audio.language)

            try:
                kwargs = {"language" : audio.language } 

                if translate_to_eng : 
                    kwargs["task"] = "translate"

                # Validate audio array
                if not isinstance(audio.array, np.ndarray):
                    raise ValueError("Audio array must be a numpy array")
                    
                if audio.array.size == 0:
                    raise ValueError("Audio array is empty")

                transcription_content = self.pipeline(
                    audio.array ,
                    return_timestamps = True ,
                    generate_kwargs = kwargs
                )
                
            except torch.cuda.OutOfMemoryError as e:
                logger.error(f"CUDA out of memory during transcription: {e}")
                self.unload()
                raise RuntimeError(f"Transcription failed due to memory constraints: {e}") from e
            except Exception as e:
                logger.error(f"Error during pipeline transcription: {e}")
                raise RuntimeError(f"Transcription pipeline failed: {e}") from e
            
            # Validate transcription output
            if not isinstance(transcription_content, dict):
                raise ValueError("Pipeline returned invalid transcription format")
                
            if "text" not in transcription_content:
                raise ValueError("Transcription output missing 'text' field")
                
            if "chunks" not in transcription_content:
                logger.warning("Transcription output missing 'chunks' field, using empty list")
                transcription_content["chunks"] = []

            self.unload()

            try:
                transcription =  Transcription(
                    original_text=transcription_content["text"] ,
                    original_chunks=transcription_content["chunks"] , 
                    input_language=audio.language, 
                    job_id = audio.job_id
                )
            except Exception as e:
                logger.error(f"Failed to create Transcription object: {e}")
                raise RuntimeError(f"Transcription object creation failed: {e}") from e
            return transcription
        
        except Exception as e : 
            self.unload()
            logger.error("Error while transcribing the audio : %s" , e)
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise 
    
    def visualize_features(self , output_path : str, audio : np.ndarray) :  

        # Validate inputs
        if not output_path:
            raise ValueError("Output path cannot be None or empty")
            
        if not isinstance(audio, np.ndarray):
            raise ValueError("Audio must be a numpy array")
            
        if audio.size == 0:
            raise ValueError("Audio array is empty")

        if not self.pipeline : 
            raise ValueError("pipeline not initialized. call load() method") 

        try:
            # Validate output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    logger.error(f"Failed to create output directory {output_dir}: {e}")
                    raise RuntimeError(f"Cannot create output directory: {e}") from e

            processor = self.pipeline.feature_extractor
            
            array , sr = audio , 16000 

            try:
                inputs = processor(array , sr  , return_tensor = "pt")
            except Exception as e:
                logger.error(f"Error processing audio features: {e}")
                raise RuntimeError(f"Feature extraction failed: {e}") from e

            if "input_features" not in inputs or len(inputs.input_features) == 0:
                raise ValueError("No input features generated from audio")

            features = inputs.input_features[0]

            try:
                plt.figure(figsize=(12, 4))

                librosa.display.specshow(features, sr=sr, x_axis='time', y_axis='mel')

                plt.title("Log-Mel Spectrogram (Input Features)")
                plt.colorbar(format="%+2.0f dB")
                plt.tight_layout()
                plt.savefig(output_path)  
                plt.close()
                
                logger.info(f"Features visualization saved to {output_path}")
                
            except Exception as e:
                logger.error(f"Error creating or saving visualization: {e}")
                # Ensure plot is closed even if saving fails
                try:
                    plt.close()
                except:
                    pass
                raise RuntimeError(f"Visualization creation failed: {e}") from e
                
        except Exception as e:
            logger.error(f"Error in visualize_features: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise