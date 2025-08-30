from transformers import pipeline
from app.models.transcription_job import TranscriptionJob
from app.models.transcription import Transcription
from app.services.model_services.astract_services import AbstractServices
from app.services.pipeline_services.translation_service import TranslationModel
from app.models.summary import Summary
from typing import List
import gc
import torch
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)


class SummarizationModel:

    def __init__(self,
                 summary_services: AbstractServices[Summary], 
                 translator: TranslationModel,
                 job_services: AbstractServices[TranscriptionJob],
                 transcription_services: AbstractServices[Transcription],
                 model_name: str = "facebook/bart-large-cnn"):
    
        self.model_name = model_name
        self.pipeline = None
        self.job_services = job_services
        self.translator = translator 
        self.transcription_services = transcription_services
        self.summary_services = summary_services
        logger.info("SummarizationModel initialized")

        self.length_config = {
            "short": {"max_length": 50, "min_length": 30}, 
            "medium": {"max_length": 130, "min_length": 50}, 
            "long": {"max_length": 200, "min_length": 130}, 
        }


    def load(self):
        if self.pipeline is None:
            try: 
                logger.info(f"Loading summarization model {self.model_name}")

                self.pipeline = pipeline(
                    task="summarization", 
                    model=self.model_name, 
                    tokenizer=self.model_name,
                    device=0 if torch.cuda.is_available() else -1
                )

                logger.info("Summarization model was loaded successfully")

            except Exception as e:
                logger.error(f"Failed to load summarization model: {e}")
                raise RuntimeError(f"Could not load model {self.model_name}: {e}") from e
    def clear_memory(self):
        if torch.cuda.is_available():
            torch.cuda.empty_cache() 
            logger.debug("Cleared Cuda")
        
        gc.collect()
        logger.debug("Garbage Collected")

    def _get_transcription(self, job: TranscriptionJob) -> Optional[Transcription]:
        """Get the English transcription for the job"""
        transcriptions = self.transcription_services.find_by_field("job_id", job.id)
        
        # Look for English transcription first
        for transcription in transcriptions:
            if transcription.target_language == "english":
                return transcription
        
        # If no English transcription found, return the first one
        return transcriptions[0] if transcriptions else None

    def summarize(self, job: TranscriptionJob) -> TranscriptionJob:
        transcription: Optional[Transcription] = self._get_transcription(job)

        if transcription is None:
            raise ValueError("No transcription found for the job")
        
        # Use the transcription text (could be original or translated)
        transcription_text = transcription.translated_text if transcription.translated_text else transcription.original_text
        source_language = transcription.target_language or transcription.input_language

        if not transcription_text:
            raise ValueError("No transcription text available")
        
        self.load()

        summaries: List[Summary] = []

        # Create base summary (in the source language of the transcription)
        base_summary = self.summarize_text(transcription_text, target_length="medium")
        
        # Always create a summary in the base/source language first
        base_summary_obj = Summary(
            job_id=job.id, 
            text_content=base_summary, 
            language=source_language
        )
        summaries.append(base_summary_obj)
        logger.info(f"Created base summary in {source_language}")
        
        # Create summaries for target languages
        for lang in job.target_languages:
            # Skip if we already have a summary in this language (the base language)
            if lang.lower() == source_language.lower():
                logger.info(f"Skipping {lang} as base summary already exists")
                continue
                
            # Different language, translate the summary
            translated_summary = self._translate_summary(
                summary_text=base_summary,
                source_lang=source_language,
                target_lang=lang
            )
            
            summary = Summary(
                job_id=job.id, 
                text_content=translated_summary, 
                language=lang
            )
            summaries.append(summary)
            logger.info(f"Created translated summary in {lang}")
        
        # Save summaries to database
        self.summary_services.create_many(entities=summaries)
        
        return job

    def _translate_summary(self, summary_text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate a summary from source language to target language using the translation service.
        Falls back to original summary if translation fails.
        """
        try:
            # Get language codes for translation
            src_code = self.translator._language_code(source_lang)
            tgt_code = self.translator._language_code(target_lang)
            
            if not src_code or not tgt_code:
                logger.warning(f"Unsupported language pair for translation: {source_lang} -> {target_lang}")
                return summary_text
            
            logger.info(f"Translating summary from {source_lang} ({src_code}) to {target_lang} ({tgt_code})")
            
            translated_summary = self.translator._translate_text(
                text=summary_text, 
                src=src_code, 
                tgt=tgt_code 
            )
            
            if translated_summary and translated_summary.strip():
                return translated_summary
            else:
                logger.warning(f"Translation returned empty result for {source_lang} -> {target_lang}")
                return summary_text
                
        except Exception as e:
            logger.error(f"Failed to translate summary from {source_lang} to {target_lang}: {e}")
            # Fallback to original summary
            return summary_text

    def summarize_text(self, text: str, target_length: str = "medium") -> str:
        config = self.length_config.get(target_length, self.length_config["medium"]) 

        try:
            result = self.pipeline( 
                text, 
                max_length=config["max_length"], 
                min_length=config["min_length"], 
                do_sample=False, 
                truncation=True
            )

            return result[0]["summary_text"]

        except Exception as e:
            logger.error(f"Error while summarizing the text: {e}")
            raise e
            
    def evaluate_summary(self, original: str, summary: str):
        """Placeholder for summary evaluation logic"""
        pass