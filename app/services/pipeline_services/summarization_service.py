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
import re

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
        
        # Configuration for text segmentation
        self.max_input_length = 1024  # BART's typical max input length
        self.segment_overlap = 100    # Overlap between segments to maintain context
        self.min_segment_length = 200 # Minimum length for a segment to be meaningful


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

    def configure_segmentation(self, max_input_length: int = None, segment_overlap: int = None, min_segment_length: int = None):
        """
        Configure segmentation parameters.
        
        Args:
            max_input_length: Maximum number of words per segment
            segment_overlap: Number of words to overlap between segments
            min_segment_length: Minimum number of words for a meaningful segment
        """
        if max_input_length is not None:
            self.max_input_length = max_input_length
            logger.info(f"Updated max_input_length to {max_input_length}")
        
        if segment_overlap is not None:
            self.segment_overlap = segment_overlap
            logger.info(f"Updated segment_overlap to {segment_overlap}")
        
        if min_segment_length is not None:
            self.min_segment_length = min_segment_length
            logger.info(f"Updated min_segment_length to {min_segment_length}")

    def _get_transcription(self, job: TranscriptionJob) -> Optional[Transcription]:
        """Get the English transcription for the job"""
        transcriptions = self.transcription_services.find_by_field("job_id", job.id)
        
        # Look for English transcription first
        for transcription in transcriptions:
            if transcription.target_language == "english":
                return transcription
        
        # If no English transcription found, return the first one
        return transcriptions[0] if transcriptions else None

    def _segment_text(self, text: str) -> List[str]:
        """
        Segment long text into chunks that fit within the model's capacity.
        Uses sentence boundaries for cleaner segmentation.
        """
        # Quick check if segmentation is needed
        if len(text.split()) <= self.max_input_length:
            return [text]
        
        logger.info(f"Text is too long ({len(text.split())} words), segmenting...")
        
        # Split text into sentences using common sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        segments = []
        current_segment = ""
        current_word_count = 0
        
        for sentence in sentences:
            sentence_word_count = len(sentence.split())
            
            # If adding this sentence would exceed the limit, finalize current segment
            if current_word_count + sentence_word_count > self.max_input_length and current_segment:
                if current_word_count >= self.min_segment_length:
                    segments.append(current_segment.strip())
                    
                    # Start new segment with overlap from previous segment
                    overlap_words = current_segment.split()[-self.segment_overlap:]
                    current_segment = " ".join(overlap_words) + " " + sentence
                    current_word_count = len(overlap_words) + sentence_word_count
                else:
                    # Current segment is too short, just add the sentence
                    current_segment += " " + sentence
                    current_word_count += sentence_word_count
            else:
                # Add sentence to current segment
                if current_segment:
                    current_segment += " " + sentence
                else:
                    current_segment = sentence
                current_word_count += sentence_word_count
        
        # Add the last segment if it has content
        if current_segment.strip():
            segments.append(current_segment.strip())
        
        logger.info(f"Text segmented into {len(segments)} chunks")
        return segments

    def _combine_segment_summaries(self, segment_summaries: List[str], target_length: str = "medium") -> str:
        """
        Combine summaries from multiple segments into a coherent final summary.
        If the combined summaries are still too long, recursively summarize them.
        """
        if not segment_summaries:
            return ""
        
        if len(segment_summaries) == 1:
            return segment_summaries[0]
        
        # Combine all segment summaries
        combined_text = " ".join(segment_summaries)
        
        # If the combined text is still too long, summarize it again
        if len(combined_text.split()) > self.max_input_length:
            logger.info("Combined summaries are too long, performing recursive summarization")
            return self.summarize_text(combined_text, target_length)
        else:
            # Always summarize the combined text for better coherence, regardless of length
            logger.info("Summarizing combined segment summaries for coherence")
            return self.summarize_text(combined_text, target_length)

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
        base_summary = self._summarize_with_segmentation(transcription_text, target_length="medium")
        
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

    def _summarize_with_segmentation(self, text: str, target_length: str = "medium") -> str:
        """
        Summarize text with automatic segmentation for long texts.
        """
        # Check if text needs segmentation
        text_segments = self._segment_text(text)
        
        if len(text_segments) == 1:
            # Text is short enough, use regular summarization
            return self.summarize_text(text, target_length)
        
        # Process each segment
        segment_summaries = []
        for i, segment in enumerate(text_segments):
            logger.info(f"Processing segment {i+1}/{len(text_segments)}")
            try:
                segment_summary = self.summarize_text(segment, target_length)
                segment_summaries.append(segment_summary)
            except Exception as e:
                logger.error(f"Failed to summarize segment {i+1}: {e}")
                # Continue with other segments even if one fails
                continue
        
        if not segment_summaries:
            raise RuntimeError("Failed to summarize any segments")
        
        # Combine segment summaries into final summary
        final_summary = self._combine_segment_summaries(segment_summaries, target_length)
        
        logger.info(f"Successfully created summary from {len(text_segments)} segments")
        return final_summary

    def summarize_text(self, text: str, target_length: str = "medium") -> str:
        config = self.length_config.get(target_length, self.length_config["medium"])
        
        # Log input text statistics for debugging
        word_count = len(text.split())
        logger.debug(f"Summarizing text with {word_count} words, target length: {target_length}")

        try:
            result = self.pipeline( 
                text, 
                max_length=config["max_length"], 
                min_length=config["min_length"], 
                do_sample=False, 
                truncation=True
            )

            summary = result[0]["summary_text"]
            logger.debug(f"Generated summary with {len(summary.split())} words")
            return summary

        except Exception as e:
            logger.error(f"Error while summarizing the text: {e}")
            logger.error(f"Text length: {word_count} words, Target config: {config}")
            raise e
            
    def evaluate_summary(self, original: str, summary: str):
        """Placeholder for summary evaluation logic"""
        pass