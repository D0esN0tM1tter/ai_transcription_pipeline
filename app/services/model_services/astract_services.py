from typing import TypeVar , Generic, List, Any, Optional
from app.repositories.abstract_repository import AbstractRepository
from abc import ABC , abstractmethod

T = TypeVar("T")

class AbstractServices(Generic[T]) :

    def __init__(self , repository : AbstractRepository[T]):
        self.repository = repository

    def create(self , entity : T) -> int : 
        return self.repository.create(entity=entity)

    def create_many(self , entities : List[T]) -> int : 
        return self.repository.create_many(entities=entities)

    def find_one_by_field(self , field_name : str , value : Any) -> Optional[T] : 
        return self.repository.find_one_by_field(field_name=field_name , value=value)
    
    def find_by_field(self , field_name : str , value : Any) -> List[T] :
        return self.repository.find_by_field(field_name=field_name , value=value)

    def update_by_field(self , field_name : str, value : Any , entity : T ) -> bool : 
        return self.repository.update_by_field(field_name=field_name , value=value , entity=entity)
    
    def find_all(self) -> List[T] : 
        return self.repository.get_all()