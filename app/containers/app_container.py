from app.config.app_config import AppConfig 
from app.containers.repositories_container import RepositoriesContainer
from app.containers.model_services_container import ModelServicesContainer
from app.containers.pipeline_services_container import PipelineServicesContainer



class ApplicationContainer : 

    def __init__(self):
        
        self.app_config = AppConfig() 

        self._repositories_container : RepositoriesContainer = RepositoriesContainer(db_path=self.app_config.DB_PATH) 
        self._model_services_container : ModelServicesContainer = None 
        self._pipeline_services_container : PipelineServicesContainer = None

    @property
    def model_services_container(self) -> ModelServicesContainer : 

        if self._model_services_container is None : 
            self._model_services_container = ModelServicesContainer(repositories_container=self._repositories_container)
        
        return self._model_services_container
    
    @property
    def pipeline_services_container(self) -> PipelineServicesContainer : 

        if self._pipeline_services_container is None : 
            self._pipeline_services_container = PipelineServicesContainer(
                model_services_container=self.model_services_container , 
                app_config=self.app_config
            )
        
        return self._pipeline_services_container



