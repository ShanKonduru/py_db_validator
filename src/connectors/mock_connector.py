"""
Mock Database Connector
Implementation of DatabaseConnectionBase for testing without real databases
"""
from typing import List, Any, Tuple
from .database_connection_base import DatabaseConnectionBase


class MockDatabaseConnector(DatabaseConnectionBase):
    """Mock database connector for testing"""
    
    def __init__(self, host: str = "localhost", port: int = 0, username: str = "test", password: str = "test"):
        super().__init__(host, port, username, password)
        # Mock data
        self.mock_tables = ["users", "orders", "products"]
        self.mock_data = {
            "users": [("1", "Alice"), ("2", "Bob")],
            "orders": [("101", "order1"), ("102", "order2"), ("103", "order3")],
            "products": [("201", "laptop"), ("202", "mouse")]
        }
    
    def connect(self) -> Tuple[bool, str]:
        """Mock connection - always succeeds"""
        self.is_connected = True
        return True, "Connected to Mock database successfully"
    
    def disconnect(self) -> None:
        """Mock disconnect"""
        self.is_connected = False
    
    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """Mock query execution"""
        if not self.is_connected:
            return False, "Not connected to database"
        
        query_lower = query.lower()
        
        # Mock SELECT COUNT(*) FROM table
        if "select count(*)" in query_lower:
            for table in self.mock_tables:
                if table in query_lower:
                    return True, [(len(self.mock_data.get(table, [])),)]
            return True, [(0,)]
        
        # Mock table existence check
        if "information_schema" in query_lower:
            return True, [(table,) for table in self.mock_tables]
        
        # Default mock response
        return True, [("mock_result",)]
    
    def get_tables(self) -> List[str]:
        """Get mock table names"""
        return self.mock_tables.copy()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if mock table exists"""
        return table_name in self.mock_tables
    
    def get_row_count(self, table_name: str) -> int:
        """Get mock row count"""
        return len(self.mock_data.get(table_name, []))