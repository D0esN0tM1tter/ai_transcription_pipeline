from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from tinydb import TinyDB, Query
from tinydb.table import Document
from pathlib import Path
from typing import List
from  tinydb.storages import JSONStorage

# Generic type for entity models
T = TypeVar('T')

class AbstractRepository(ABC, Generic[T]):
    """
    Abstract base repository defining common database operations.
    This class provides the contract that all concrete repositories must implement.
    """
    
    def __init__(self, db_path: str, table_name: str):
        self.db_path = db_path
        self.table_name = table_name
        self._db: Optional[TinyDB] = None
        self._table = None
    
    @property
    def db(self) -> TinyDB:
        """Lazy initialization of database connection"""
        if self._db is None:
            # Ensure directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._db = TinyDB(self.db_path , storage = lambda p : JSONStorage(p , indent = 4))
        return self._db
    
    @property
    def table(self):
        """Get the table instance"""
        if self._table is None:
            self._table = self.db.table(self.table_name)
        return self._table
    
    @abstractmethod
    def to_dict(self, entity: T) -> Dict[str, Any]:
        """Convert entity to dictionary for storage"""
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> T:
        """Convert dictionary to entity"""
        pass
    
    def create(self, entity: T) -> int:
        """Create a new record and return its ID"""
        data = self.to_dict(entity)
        return self.table.insert(data)
    
    def create_many(self , entities : List[T]) -> int : 
        count = 0 
        for entity in entities : 
            count += self.create(entity=entity)
        
        return count
            
    def get_by_id(self, record_id: int) -> Optional[T]:
        """Get a record by its ID"""
        doc = self.table.get(doc_id=record_id)
        return self.from_dict(data=doc) if doc else None
    
    def get_all(self) -> List[T]:
        """Get all records"""
        docs = self.table.all()
        return [self.from_dict(data=doc) for doc in docs]
    
    def update(self, record_id: int, entity: T) -> bool:
        """Update a record by ID"""
        data = self.to_dict(entity)
        result = self.table.update(data, doc_ids=[record_id])
        return len(result) > 0
    
    def delete(self, record_id: int) -> bool:
        """Delete a record by ID"""
        result = self.table.remove(doc_ids=[record_id])
        return len(result) > 0
    
    def find_by_field(self, field_name: str, value: Any) -> List[T]:
        """Find records by a specific field value"""
        query = Query()
        docs = self.table.search(query[field_name] == value)
        return [self.from_dict(doc) for doc in docs]
    
    def find_one_by_field(self, field_name: str, value: Any) -> Optional[T]:
        """Find first record by a specific field value"""
        query = Query()
        doc = self.table.get(query[field_name] == value)
        return self.from_dict(doc) if doc else None
    
    def update_by_field(self, field_name : str , value : Any , entity : T )-> bool : 
        data = self.to_dict(entity)
        query = Query()
        result = self.table.update(data , query[field_name] == value) 
        return len(result) > 0

    def count(self) -> int:
        """Count total records"""
        return len(self.table)
    
    def exists(self, record_id: int) -> bool:
        """Check if a record exists by ID"""
        return self.table.contains(doc_id=record_id)
    
    def close(self):
        """Close database connection"""
        if self._db:
            self._db.close()
            self._db = None
            self._table = None

