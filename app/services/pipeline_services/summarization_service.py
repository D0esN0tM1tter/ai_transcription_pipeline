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


class SummarizationModel : 
    
    """

    def __init__(self,
                 summary_services : AbstractServices[Summary] , 
                 translator : TranslationModel ,
                 job_services : AbstractServices[TranscriptionJob],
                 transcription_services : AbstractServices[Transcription] ,
                 model_name : str = "facebook/bart-large-cnn"):
    
        self.model_name = model_name
        self.pipeline = None
        self.job_services  = job_services
        self.translator = translator 
        self.transcripton_services = transcription_services
        self.summary_services = summary_services

        self.length_config = {

            "short" : {"max_length" : 50 , "min_length" : 30} , 
            "medium" : {"max_length" : 130 , "min_length" : 50} , 
            "long" : {"max_length" : 200 , "min_length" : 130} , 
        }


    def load(self) : 


        if self.pipeline is None : 

            try : 
                logger.info(f"Loading summarization model {self.model_name}")

                self.pipeline = pipeline(
                    task = "summarization" , 
                    model = self.model_name , 
                    tokenizer = self.model_name,
                    device = 0 if torch.cuda.is_available() else -1 
                )

                logger.info("Summarization model was loaded successfully")


            except Exception as e : 
                logger.error(f"Failed to load summarization model f {e}")
                raise RuntimeError(f"Could not load model {self.model_name}: {e}") from e
        

    def clear_memory(self) :

        if torch.cuda.is_available() :
            torch.cuda.empty_cache() 
            logger.debug("Cleared Cuda")
        
        gc.collect()
        logger.debug("Garbage Collected")
        

    def summarize(self , job : TranscriptionJob) -> TranscriptionJob :

        transcription : Optional[Transcription] = self._get_transcription()

        if transcription is not None :

            english_transcription = transcription.translated_text

        else :
            
            raise ValueError("English transcription does not exist in the database")
        
        self.load()

        summaries : List[Summary] = []

        for lang in job.target_languages :
            
            # English summarization
            english_summary = self.summarize_text(english_transcription , target_length="medium") 

            if not lang == "english" :

                # translate the summary text to the current language :
                trgt_lang = self.translation_services.__language_lookup(language=lang)

                translated_summary = self.translation_services._translate_text(
                    text= english_summary , 
                    src_lang= "en" , 
                    trgt_lang=trgt_lang 
                )

                summary = Summary(
                    job_id=job.id , 
                    text_content=translated_summary , 
                    language=lang
                )


            else :

                summary = Summary(

                    job_id=job.id , 

                    text_content=english_summary , 

                    language=lang
                )

            summaries.append(summary)
        
        self.summary_services.create_many(
            entities=summaries
        )


    def summarize_text(self , text : str , target_length : str) :

        config = self.length_config.get(target_length , self.length_config["medium"]) 

        try :

            result = self.pipeline( 
                text , 
                max_length = config["max_length"] , 
                min_length = config["min_length"] , 
                do_sample = False , 
                truncation = True
            )

            return result[0]["text_summary"]

        except Exception as e : 
            logging.error(f"Error while summarizing the text : {e}")
            
    def evaluate_summary(self , original : str , summary : str) : 
        pass
        """