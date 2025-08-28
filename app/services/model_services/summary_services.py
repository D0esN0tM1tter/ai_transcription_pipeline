from app.services.model_services.astract_services import AbstractServices
from app.repositories.abstract_repository import AbstractRepository
from app.models.summary import Summary


class SummaryServices(AbstractServices[Summary]) : 
    
    def __init__(self, repository : AbstractRepository[Summary]):
        super().__init__(repository)