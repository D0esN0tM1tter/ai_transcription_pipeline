from transformers import MarianMTModel, MarianTokenizer 
from typing import Tuple
from app.models.transcription import Transcription
from app.models.transcription_job import TranscriptionJob
from typing import  List
import logging
from app.services.model_services.transcription_job_services import TranscriptionJobServices
from app.services.model_services.transcription_services import TranscriptionServices
import traceback
import torch
import gc

logging.basicConfig(level=logging.INFO) 

logger = logging.getLogger(__name__)

class TranslationModel : 

    def __init__(self, job_service: TranscriptionJobServices, transcription_service: TranscriptionServices):
        try:
            if not job_service:
                raise ValueError("TranscriptionJobServices cannot be None")
            self.job_service = job_service
            self.transcription_service = transcription_service

            self.models = {}
            
            logger.info("TranslationModel initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TranslationModel: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"TranslationModel initialization failed: {e}") from e


    def __Load_model(self , src_lang : str , trgt_lang : str) -> Tuple[MarianTokenizer , MarianMTModel] :  

        # Validate input parameters
        if not src_lang or not isinstance(src_lang, str):
            raise ValueError("Source language must be a non-empty string")
        if not trgt_lang or not isinstance(trgt_lang, str):
            raise ValueError("Target language must be a non-empty string")
        

        try:
            # format input language : 
            src_lang = self.__language_lookup(src_lang) 
            trgt_lang = self.__language_lookup(trgt_lang)

            if not src_lang:
                raise ValueError(f"Unsupported source language: {src_lang}")
            if not trgt_lang:
                raise ValueError(f"Unsupported target language: {trgt_lang}")

            logger.info("Initializing / Looking-up translation model %s to %s" , src_lang , trgt_lang)

            pair_key = f"{src_lang}-{trgt_lang}" 

            if pair_key not in self.models : 
                try:
                    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{trgt_lang}"
                    
                    logger.info(f"Loading tokenizer for model: {model_name}")
                    tokenizer = MarianTokenizer.from_pretrained(model_name)
                    
                    logger.info(f"Loading model: {model_name}")
                    model = MarianMTModel.from_pretrained(model_name)
                    
                    self.models[pair_key] = (tokenizer , model)
                    logger.info(f"Successfully loaded model pair: {pair_key}")
                    
                except Exception as e:
                    logger.error(f"Failed to load model {model_name}: {e}")
                    # Check if it's a model availability issue
                    if "404" in str(e) or "Repository not found" in str(e):
                        raise ValueError(f"Translation model not available for language pair {src_lang}-{trgt_lang}") from e
                    elif "Out of memory" in str(e) or isinstance(e, torch.cuda.OutOfMemoryError):
                        # Try to free memory and retry
                        gc.collect()
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                        raise RuntimeError(f"Out of memory loading model for {src_lang}-{trgt_lang}") from e
                    else:
                        raise RuntimeError(f"Failed to load translation model for {src_lang}-{trgt_lang}: {e}") from e
            
            return self.models[pair_key]
            
        except Exception as e:
            logger.error(f"Error in __Load_model: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def translate_transcription_to_multiple_languages(self , transcription : Transcription) -> List[Transcription] : 
        
        logger.info("Translation to multiple languages is starting ...")

        try:
            # extract the parent job :
            try:

                job: TranscriptionJob = self.job_service.find_one_by_field(
                    field_name="job_id",
                    value=transcription.job_id
                )
                
                if not job:
                    raise ValueError(f"Job with ID {transcription.job_id} not found")
                
            except Exception as e:

                logger.error(f"Failed to retrieve job {transcription.job_id}: {e}")
                raise RuntimeError(f"Cannot retrieve transcription job: {e}") from e

            # extract source language and target languages :
            src_lang = transcription.input_language

            # Handle both list and comma-separated string for target languages
            trgt_languages = job.target_languages
            if isinstance(trgt_languages, str):
                # Split by comma and strip whitespace
                trgt_languages = [lang.strip() for lang in trgt_languages.split(",") if lang.strip()]
            elif not isinstance(trgt_languages, list):
                logger.warning(f"Unexpected type for target_languages: {type(trgt_languages)}. Defaulting to empty list.")
                trgt_languages = []

            transcriptions_list: List[Transcription] = []

            # handle the original transcription first:
            try:
                transcription.translated_text = ""
                transcription.translated_chunks = []
                transcription.target_language = transcription.input_language

                transcriptions_list.append(transcription)
                logger.info(f"Added original transcription in {src_lang}")
            except Exception as e:
                logger.error(f"Error setting up original transcription: {e}")
                raise RuntimeError(f"Failed to setup original transcription: {e}") from e

            # Process each target language
            for language in trgt_languages:
                try:
                    if language.lower() == src_lang.lower():
                        logger.info(f"Skipping translation to same language: {language}")
                        continue

                    logger.info(f"Translating from {src_lang} to {language}")

                    # Validate original text before translation
                    if not transcription.original_text:
                        logger.warning(f"No original text to translate for language {language}")
                        translated_text = ""
                    else:
                        translated_text = self._translate_text(transcription.original_text, src_lang, language)

                    # Validate and translate chunks
                    if not transcription.original_chunks:
                        logger.warning(f"No original chunks to translate for language {language}")
                        translated_chunks = []
                    else:
                        translated_chunks = self._translate_chunks(transcription.original_chunks, src_lang, language)

                    translated_transcription = Transcription(
                        original_text=transcription.original_text,
                        original_chunks=transcription.original_chunks,
                        tr_text=translated_text,
                        tr_chunks=translated_chunks,
                        job_id=transcription.job_id,
                        input_language=src_lang,
                        target_language=language,
                        filepath=transcription.filepath,
                    )

                    transcriptions_list.append(translated_transcription)
                    logger.info(f"Successfully translated to {language}")
                except Exception as e:
                    logger.error(f"Failed to translate to {language}: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    # Continue with other languages instead of failing completely
                    continue

            logger.info(f"Translation process has finished. Generated {len(transcriptions_list)} transcriptions.")
            self.transcription_service.create_many(transcriptions_list)
            return transcriptions_list
            
        except Exception as e:
            logger.error(f"Error in translate_transcription_to_multiple_languages: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _translate_text(self, text : str, src_lang : str, trgt_lang : str) -> str: 
        
        # Validate inputs
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid text for translation: {text}")
            return ""
        if not src_lang or not isinstance(src_lang, str):
            raise ValueError("Source language must be a non-empty string")
        if not trgt_lang or not isinstance(trgt_lang, str):
            raise ValueError("Target language must be a non-empty string")
        # Skip translation if text is empty or whitespace only
        if not text.strip():
            logger.warning("Empty or whitespace-only text provided for translation")
            return ""
        try:
            logger.info("Translating input text from %s to %s", src_lang, trgt_lang)
            tokenizer, model = self.__Load_model(src_lang, trgt_lang)
            
            # Split text into segments if too long
            segments = self._split_text_for_translation(text, tokenizer, max_length=512)
            if not segments:
                return ""
            translated_segments = []
            for segment in segments:
                try:
                    inputs = tokenizer(segment, return_tensors="pt", padding=True, truncation=True, max_length=512)
                    with torch.no_grad():
                        outputs = model.generate(**inputs)
                    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    translated_segments.append(translated_text if translated_text else "")
                except torch.cuda.OutOfMemoryError as e:
                    logger.error(f"CUDA out of memory during translation: {e}")
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    raise RuntimeError(f"Translation failed due to memory constraints: {e}") from e
                except Exception as e:
                    logger.error(f"Error translating segment: {e}")
                    translated_segments.append("")
            return " ".join(translated_segments)
        except Exception as e:
            logger.error(f"Error in _translate_text: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _translate_chunks(self, chunks : List, src_lang : str, trgt_lang : str) -> List :

        # Validate inputs
        if not chunks:
            logger.warning("No chunks provided for translation")
            return []
        if not isinstance(chunks, list):
            raise ValueError("Chunks must be a list")
        if not src_lang or not isinstance(src_lang, str):
            raise ValueError("Source language must be a non-empty string")
        if not trgt_lang or not isinstance(trgt_lang, str):
            raise ValueError("Target language must be a non-empty string")

        try:
            translated_chunks = []
            
            for i, chunk in enumerate(chunks):
                try:
                    # Validate chunk structure
                    if not isinstance(chunk, dict):
                        logger.warning(f"Invalid chunk format at index {i}: {chunk}")
                        continue
                    
                    if "timestamp" not in chunk:
                        logger.warning(f"Missing timestamp in chunk at index {i}")
                        continue
                        
                    if "text" not in chunk:
                        logger.warning(f"Missing text in chunk at index {i}")
                        continue
                    
                    chunk_text = chunk["text"]
                    if not chunk_text or not isinstance(chunk_text, str):
                        logger.warning(f"Invalid text in chunk at index {i}: {chunk_text}")
                        translated_text = ""
                    else:
                        translated_text = self._translate_text(chunk_text, src_lang, trgt_lang)
                    
                    translated_chunk = {
                        "timestamp": chunk["timestamp"],
                        "text": translated_text
                    }
                    
                    translated_chunks.append(translated_chunk)
                    
                except Exception as e:
                    logger.error(f"Error translating chunk at index {i}: {e}")
                    # Continue with next chunk instead of failing completely
                    continue
            
            logger.info(f"Successfully translated {len(translated_chunks)} out of {len(chunks)} chunks")
            return translated_chunks
            
        except Exception as e:
            logger.error(f"Error in _translate_chunks: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def __language_lookup(self, language : str) -> str: 
        
        if not language or not isinstance(language, str):
            logger.warning(f"Invalid language for lookup: {language}")
            return ""
        try:
            lang_map = {
                "english": "en", "en": "en",
                "french": "fr", "fr": "fr",
                "arabic": "ar", "ar": "ar",
                "spanish": "es", "es": "es"
            }
            key = language.lower()
            result = lang_map.get(key, "")
            if not result:
                logger.warning(f"Unsupported language: {language}")
            return result
        except Exception as e:
            logger.error(f"Error in language lookup for '{language}': {e}")
            return ""
    
    def clear_models_cache(self):
        """Clear loaded models from memory"""
        try:
            logger.info("Clearing translation models cache")
            
            for pair_key in list(self.models.keys()):
                try:
                    tokenizer, model = self.models[pair_key]
                    del tokenizer
                    del model
                    del self.models[pair_key]
                except Exception as e:
                    logger.warning(f"Error clearing model {pair_key}: {e}")
            
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
            logger.info("Models cache cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing models cache: {e}")
            # Don't raise - cache clearing should be robust




    def _split_text_for_translation(self, text, tokenizer, max_length=512):
        """
        Splits text into segments of <= max_length tokens for translation.
        Returns a list of text segments.
        """
        if not text or not isinstance(text, str):
            return []
        # Tokenize the text into tokens
        tokens = tokenizer.tokenize(text)
        segments = []
        current_tokens = []
        for token in tokens:
            current_tokens.append(token)
            if len(current_tokens) >= max_length:
                segment = tokenizer.convert_tokens_to_string(current_tokens)
                segments.append(segment)
                current_tokens = []
        if current_tokens:
            segment = tokenizer.convert_tokens_to_string(current_tokens)
            segments.append(segment)
        return segments