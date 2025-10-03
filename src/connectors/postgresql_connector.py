"""
PostgreSQL Database Connector
Implementation of DatabaseConnectionBase for PostgreSQL databases
"""
from typing import List, Any, Tuple
from .database_connection_base import DatabaseConnectionBase


class PostgreSQLConnector(DatabaseConnectionBase):
    """PostgreSQL database connector"""
    
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        super().__init__(host, port, username, password)
        self.database = database
    
    def connect(self) -> Tuple[bool, str]:
        """Connect to PostgreSQL database"""
        try:
            import psycopg2
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                connect_timeout=10
            )
            self.is_connected = True
            return True, "Connected to PostgreSQL successfully"
        except Exception as e:
            return False, f"PostgreSQL connection failed: {str(e)}"
    
    def disconnect(self) -> None:
        """Disconnect from PostgreSQL"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
    
    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """Execute PostgreSQL query"""
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
        """Get PostgreSQL table names"""
        success, result = self.execute_query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        if success:
            return [row[0] for row in result]
        return []
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in PostgreSQL"""
        success, result = self.execute_query(
            f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
        )
        return success and result and result[0][0] > 0
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for PostgreSQL table"""
        success, result = self.execute_query(f"SELECT COUNT(*) FROM {table_name}")
        if success and result:
            return result[0][0]
        return 0