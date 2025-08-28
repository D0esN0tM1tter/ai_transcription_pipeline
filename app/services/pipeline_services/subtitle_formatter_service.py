from typing import List, Dict 
from app.models.transcription import Transcription
from app.services.model_services.transcription_services import TranscriptionServices
import logging
import os

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class SubtitleWriter:
    def __init__(self, transcription_service: TranscriptionServices):
        self.transcription_service = transcription_service
        

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format timestamp for VTT format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02}.{millis:03}"
    
    def save_chunks(self, chunks: List[Dict], output_path: str):
        # Validate chunks before processing
        if not chunks:
            logger.warning(f"No chunks to save for {output_path}")
            return
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write VTT header
            f.write("WEBVTT\n\n")
            
            valid_chunk_count = 0
            
            for i, chunk in enumerate(chunks, start=1):
                # Validate chunk structure
                if not isinstance(chunk, dict):
                    logger.warning(f"Invalid chunk format at index {i-1}: {chunk}")
                    continue
                
                if 'timestamp' not in chunk or 'text' not in chunk:
                    logger.warning(f"Missing required fields in chunk at index {i-1}: {chunk}")
                    continue
                
                timestamp = chunk['timestamp']
                text = chunk['text']
                
                # Validate timestamp format
                if not isinstance(timestamp, (list, tuple)) or len(timestamp) != 2:
                    logger.warning(f"Invalid timestamp format at index {i-1}: {timestamp}")
                    continue
                
                start_time, end_time = timestamp
                
                # Handle None or invalid timestamps (Whisper prediction issue)
                if start_time is None or end_time is None:
                    logger.warning(f"Missing timestamp data at index {i-1}: start={start_time}, end={end_time}")
                    continue
                
                # Ensure timestamps are valid numbers
                try:
                    start_time = float(start_time)
                    end_time = float(end_time)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid timestamp values at index {i-1}: start={start_time}, end={end_time}")
                    continue
                
                # Ensure end time is after start time
                if end_time <= start_time:
                    logger.warning(f"Invalid timestamp order at index {i-1}: start={start_time}, end={end_time}")
                    # Fix by adding a small duration
                    end_time = start_time + 0.1
                
                # Format timestamps and write to file
                start_ts = self._format_timestamp(start_time)
                end_ts = self._format_timestamp(end_time)
                
                valid_chunk_count += 1
                # VTT format: timestamp line followed by text (no sequence number needed)
                f.write(f"{start_ts} --> {end_ts}\n")
                f.write(f"{text.strip()}\n\n")
            
            logger.info(f"Saved {valid_chunk_count} valid chunks out of {len(chunks)} total chunks to {output_path}")

    def save_single_transcription(self, transcription: Transcription, output_dir: str):
        logger.info(f"Saving the transcription {transcription.id} content as vtt file.")
        
        # Validate inputs
        if not transcription.id:
            raise ValueError("Transcription ID cannot be None or empty")
        
        if not transcription.target_language:
            raise ValueError("Target language cannot be None or empty")
        
        if not output_dir:
            raise ValueError("Output directory cannot be None or empty")
        
        # Create the full output path with .vtt extension
        output_path = os.path.join(output_dir, f"{transcription.id}_{transcription.target_language}.vtt")
        
        # Set filepath to the complete file path, not just the directory
        transcription.filepath = output_path 

        # update the transcription in the database
        self.transcription_service.update_by_field(
            field_name="transcription_id",
            value=transcription.id,
            entity=transcription
        )


        # handling the original transcription
        if len(transcription.translated_text) < 1  or transcription.input_language.lower() == transcription.target_language.lower() :
            chunks = transcription.original_chunks
            logger.info(f"Using original_chunks: {len(chunks) if chunks else 0} chunks")
            logger.debug(f"Original chunks content: {chunks}")
        else : 
            chunks = transcription.translated_chunks
            logger.info(f"Using translated_chunks: {len(chunks) if chunks else 0} chunks")
            logger.debug(f"Translated chunks content: {chunks}")


        

        # Save chunks to file
        self.save_chunks(chunks, output_path)
        
        logger.info(f"Transcription {transcription.id} saved successfully to {output_path}")

    def batch_save(self, transcription_list: List[Transcription], output_dir: str) -> List[Transcription]:
        """Save multiple transcriptions and return list of file paths"""
        if not transcription_list:
            logger.warning("No transcriptions to save")
            return []
        
        results = []
        for transcription in transcription_list:
            try:
                self.save_single_transcription(transcription, output_dir)
                results.append(transcription)
            except Exception as e:
                logger.error(f"Failed to save transcription {transcription.id}: {e}")
                results.append(None)
        
        return results