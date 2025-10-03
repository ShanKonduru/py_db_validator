"""
Database Connection Base Class
Abstract base class defining the interface for all database connectors
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional


class DatabaseConnectionBase(ABC):
    """Base class for all database connections"""
    
    def __init__(self, host: str, port: int, username: str, password: str, **kwargs):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.is_connected = False
    
    @abstractmethod
    def connect(self) -> Tuple[bool, str]:
        """
        Connect to the database
        Returns: (success: bool, message: str)
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the database"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """
        Execute a SQL query
        Returns: (success: bool, result/error_message)
        """
        pass
    
    @abstractmethod
    def get_tables(self) -> List[str]:
        """Get list of table names"""
        pass
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists"""
        pass
    
    @abstractmethod
    def get_row_count(self, table_name: str) -> int:
        """Get row count for a table"""
        pass