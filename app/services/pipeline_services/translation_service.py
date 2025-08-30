from transformers import MarianMTModel, MarianTokenizer 
from typing import Tuple
from app.models.transcription import Transcription
from app.models.transcription_job import TranscriptionJob
from typing import  List
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app.services.model_services.transcription_job_services import TranscriptionJobServices
from app.services.model_services.transcription_services import TranscriptionServices
import traceback
import torch
class TranslationModel:
    """
    Translation model wrapper for Helsinki-NLP MarianMT.
    Handles loading, translating, and cleanup.
    """
    def __init__(self, job_service: TranscriptionJobServices, transcription_service: TranscriptionServices):
        logger.info("Initializing TranslationModel")
        if not job_service:
            logger.error("job_service required")
            raise ValueError("job_service required")
        self.job_service = job_service
        self.transcription_service = transcription_service
        self.models = {}
        logger.info("TranslationModel initialized")

    def _language_code(self, lang: str) -> str:
        lang_map = {"english": "en", "en": "en", "french": "fr", "fr": "fr", "arabic": "ar", "ar": "ar", "spanish": "es", "es": "es"}
        code = lang_map.get(str(lang).lower(), "")
        logger.info(f"Language lookup: {lang} -> {code}")
        return code

    def _load_model(self, src: str, tgt: str):
        src = self._language_code(src)
        tgt = self._language_code(tgt)
        if not src or not tgt:
            logger.error(f"Unsupported language pair: {src}-{tgt}")
            raise ValueError("Unsupported language pair")
        key = f"{src}-{tgt}"
        if key not in self.models:
            name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
            logger.info(f"Loading MarianMT model: {name}")
            tokenizer = MarianTokenizer.from_pretrained(name)
            model = MarianMTModel.from_pretrained(name)
            self.models[key] = (tokenizer, model)
            logger.info(f"Model loaded and cached for pair: {key}")
        return self.models[key]

    def translate_transcription_to_multiple_languages(self, transcription: Transcription) -> List[Transcription]:
        logger.info(f"Translating transcription for job_id: {transcription.job_id}")
        job = self.job_service.find_one_by_field(field_name="job_id", value=transcription.job_id)
        if not job:
            logger.error(f"Job {transcription.job_id} not found")
            raise ValueError(f"Job {transcription.job_id} not found")
        src = transcription.input_language
        targets = job.target_languages
        if isinstance(targets, str):
            targets = [lang.strip() for lang in targets.split(",") if lang.strip()]
        elif not isinstance(targets, list):
            targets = []
        result = []
        transcription.translated_text = ""
        transcription.translated_chunks = []
        transcription.target_language = src
        result.append(transcription)
        for tgt in targets:
            if tgt.lower() == src.lower():
                logger.info(f"Skipping translation to same language: {tgt}")
                continue
            logger.info(f"Translating from {src} to {tgt}")
            tr_text = self._translate_text(transcription.original_text, src, tgt) if transcription.original_text else ""
            tr_chunks = self._translate_chunks(transcription.original_chunks, src, tgt) if transcription.original_chunks else []
            result.append(Transcription(
                original_text=transcription.original_text,
                original_chunks=transcription.original_chunks,
                tr_text=tr_text,
                tr_chunks=tr_chunks,
                job_id=transcription.job_id,
                input_language=src,
                target_language=tgt,
                filepath=transcription.filepath,
            ))
            logger.info(f"Translation to {tgt} complete.")
        self.transcription_service.create_many(result)
        logger.info(f"Translation process finished. Total transcriptions: {len(result)}")
        return result

    def _translate_text(self, text: str, src: str, tgt: str) -> str:
        if not text or not isinstance(text, str) or not text.strip():
            logger.warning("No valid text to translate.")
            return ""
        logger.info(f"Translating text from {src} to {tgt}")
        tokenizer, model = self._load_model(src, tgt)
        segments = self._split_text(text, tokenizer, max_length=512)
        out = []
        for seg in segments:
            inputs = tokenizer(seg, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model.generate(**inputs)
            out.append(tokenizer.decode(outputs[0], skip_special_tokens=True))
        logger.info(f"Text translation complete. Segments: {len(segments)}")
        return " ".join(out)

    def _translate_chunks(self, chunks: List, src: str, tgt: str) -> List:
        logger.info(f"Translating {len(chunks)} chunks from {src} to {tgt}")
        result = []
        for chunk in chunks:
            if not isinstance(chunk, dict) or "timestamp" not in chunk or "text" not in chunk:
                logger.warning(f"Skipping invalid chunk: {chunk}")
                continue
            text = chunk["text"]
            tr_text = self._translate_text(text, src, tgt) if text and isinstance(text, str) else ""
            result.append({"timestamp": chunk["timestamp"], "text": tr_text})
        logger.info(f"Chunk translation complete. Translated: {len(result)}")
        return result

    def clear_models_cache(self):
        logger.info("Clearing translation models cache.")
        for key in list(self.models.keys()):
            del self.models[key]
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Models cache cleared.")

    def _split_text(self, text, tokenizer, max_length=512):
        tokens = tokenizer.tokenize(text)
        segments, current = [], []
        for token in tokens:
            current.append(token)
            if len(current) >= max_length:
                segments.append(tokenizer.convert_tokens_to_string(current))
                current = []
        if current:
            segments.append(tokenizer.convert_tokens_to_string(current))
        logger.info(f"Split text into {len(segments)} segments for translation.")
        return segments