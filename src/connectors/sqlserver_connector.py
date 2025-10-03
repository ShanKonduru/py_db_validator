"""
SQL Server Database Connector
Implementation of DatabaseConnectionBase for SQL Server databases
"""
from typing import List, Any, Tuple
from .database_connection_base import DatabaseConnectionBase


class SQLServerConnector(DatabaseConnectionBase):
    """SQL Server database connector"""
    
    def __init__(self, host: str, port: int, username: str, password: str, database: str, driver: str = "ODBC Driver 17 for SQL Server"):
        super().__init__(host, port, username, password)
        self.database = database
        self.driver = driver
    
    def connect(self) -> Tuple[bool, str]:
        """Connect to SQL Server database"""
        try:
            import pyodbc
            
            # Create connection string
            connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.host},{self.port};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"TrustServerCertificate=yes;"
            )
            
            self.connection = pyodbc.connect(
                connection_string,
                timeout=10
            )
            self.is_connected = True
            return True, "Connected to SQL Server successfully"
        except Exception as e:
            return False, f"SQL Server connection failed: {str(e)}"
    
    def disconnect(self) -> None:
        """Disconnect from SQL Server"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
    
    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """Execute SQL Server query"""
        if not self.is_connected:
            return False, "Not connected to database"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return True, result
        except Exception as e:
            return False, str(e)
    
    def get_tables(self) -> List[str]:
        """Get SQL Server table names"""
        success, result = self.execute_query(
            "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' ORDER BY table_name"
        )
        if success:
            return [row[0] for row in result]
        return []
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in SQL Server"""
        success, result = self.execute_query(
            f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
        )
        return success and result and result[0][0] > 0
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for SQL Server table"""
        success, result = self.execute_query(f"SELECT COUNT(*) FROM [{table_name}]")
        if success and result:
            return result[0][0]
        return 0