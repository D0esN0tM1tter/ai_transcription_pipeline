import ffmpeg
import logging
from typing import Dict, List
from app.models.audio import Audio
from app.models.transcription_job import TranscriptionJob
from app.models.transcription import Transcription
from app.services.model_services.transcription_job_services import TranscriptionJobServices

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FfmpegUtils:
    def __init__(self, job_service: TranscriptionJobServices):
        self.job_service = job_service
        
    
    def extract_audio(self, job : TranscriptionJob , output_dir: str,
                  start: str = "00:00:00" ,
                  duration: str = None,
                  bitrate: str = "192k",
                  sampling_rate: int = 16000,
                  audio_format: str = 'wav'):

        logger.info("audio extraction is starting")

        # add english to the target languages if it is not the main language (for summarization) 
        if "english" not in job.target_languages : 
            job.target_languages.append("english")

        # save the input job to the database :
        self.job_service.create(entity=job)


        audio = Audio(
            job_id=job.id , 
            audio_filepath= None, 
            language=job.input_language
        )

        audio.audio_filepath = output_dir + f"/{audio.id}.{audio_format}"

        try:

            # input stream
            stream = ffmpeg.input(job.video_storage_path , ss = start) 

            # output options : 
            output_kwargs = {
                'format' : audio_format , 
                'ar' : sampling_rate , 
                'audio_bitrate' : bitrate , 
                'map' : '0:a:0'
            }

            # specify duration if provided : 
            if duration : 
                output_kwargs['t'] = duration
            
            (
                stream
                .output(audio.audio_filepath , **output_kwargs) 
                .overwrite_output()
                .run(quiet = False , capture_stdout=True , capture_stderr = True)
            )

            logger.info(f"Audio extraction was successful : {audio}")

            return audio

        except ffmpeg.Error as e:
            logger.error("Error during extraction: %s", e)
            logger.error("FFmpeg stdout:\n %s", e.stdout.decode('utf-8', errors='ignore'))
            logger.error("FFmpeg stdout:\n %s", e.stderr.decode('utf-8', errors='ignore'))

            raise
   
    def mux_subtitles(self, transcriptions_list: List[Transcription], output_dir: str) -> TranscriptionJob:
    
        # Validate input parameters
        if not transcriptions_list:
            raise ValueError("transcriptions_list cannot be empty")
        
        if not output_dir:
            raise ValueError("output_dir cannot be None or empty")
        
        # The video path should be extracted from the TranscriptionJob based on one of the transcriptions in the list passed as argument
        job_id = transcriptions_list[0].job_id
        
        if not job_id:
            raise ValueError("job_id cannot be None or empty")

        # extract the corresponding job:
        job: TranscriptionJob = self.job_service.find_one_by_field(
            field_name="job_id",
            value=job_id
        )
        
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")

        # extract the path where the video is stored:
        video_path = job.video_storage_path
        
        if not video_path:
            raise ValueError(f"Video storage path is None for job {job_id}")

        # extract the  paths as dictionary:
        vtt_paths = {}

        for transcription in transcriptions_list:
            if not transcription.filepath:
                raise ValueError(f"Subtitle filepath is None for transcription with job_id {transcription.job_id} and language {transcription.target_language}")
            
            if not transcription.target_language:
                raise ValueError(f"Target language is None for transcription with job_id {transcription.job_id}")
                
            vtt_paths[transcription.target_language] = transcription.filepath
        
        try:
            logger.info(f"Muxing process for video: {video_path} is starting ...")

            inputs = [ffmpeg.input(video_path)]

            for vtt_file in vtt_paths.values():
                inputs.append(ffmpeg.input(vtt_file))

            # Maps for video and audio
            map_args = ['-map', '0:v', '-map', '0:a']

            # Prepare output kwargs for metadata
            output_kwargs = {
                'c': 'copy',
                'movflags': '+faststart'
            }

            for idx, lang_code in enumerate(vtt_paths.keys(), start=1):
                map_args += ['-map', f'{idx}:0']

                # Set language metadata
                output_kwargs[f'metadata:s:s:{idx - 1}'] = f'language={lang_code}'

                # Set title metadata using the correct format
                map_args += ['-metadata:s:s:{}'.format(idx - 1), f'title={lang_code.capitalize()} Subtitles']
            
            output_path = f"{output_dir}/video_subtitled_{job_id}.mkv"

            job.processed_video_path = output_path
            
            # Build output with all inputs and metadata
            out = ffmpeg.output(*inputs, output_path, **output_kwargs)
            out = out.global_args(*map_args)
            out = out.overwrite_output()
            out.run(quiet=False)
            
            logger.info(f"Muxing completed successfully, output saved to: {output_path}")
            job.processed = True
            

            self.job_service.update_by_field(
                field_name="job_id",
                value=job_id,
                entity=job
            )

            return job


        except ffmpeg.Error as e:
            logger.error("Error during muxing: %s", e)
            logger.error("FFmpeg stdout:\n %s", e.stdout.decode('utf-8', errors='ignore'))
            logger.error("FFmpeg stderr:\n %s", e.stderr.decode('utf-8', errors='ignore'))
            raise