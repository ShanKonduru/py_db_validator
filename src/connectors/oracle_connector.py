"""
Oracle Database Connector
Implementation of DatabaseConnectionBase for Oracle databases
"""
from typing import List, Any, Tuple
from .database_connection_base import DatabaseConnectionBase


class OracleConnector(DatabaseConnectionBase):
    """Oracle database connector"""
    
    def __init__(self, host: str, port: int, username: str, password: str, service_name: str):
        super().__init__(host, port, username, password)
        self.service_name = service_name
    
    def connect(self) -> Tuple[bool, str]:
        """Connect to Oracle database"""
        try:
            import oracledb
            # Create DSN (Data Source Name)
            dsn = f"{self.host}:{self.port}/{self.service_name}"
            
            self.connection = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=dsn
            )
            self.is_connected = True
            return True, "Connected to Oracle successfully"
        except Exception as e:
            return False, f"Oracle connection failed: {str(e)}"
    
    def disconnect(self) -> None:
        """Disconnect from Oracle"""
        if self.connection:
            self.connection.close()
            self.is_connected = False
    
    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """Execute Oracle query"""
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
        """Get Oracle table names"""
        success, result = self.execute_query(
            "SELECT table_name FROM user_tables ORDER BY table_name"
        )
        if success:
            return [row[0] for row in result]
        return []
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in Oracle"""
        success, result = self.execute_query(
            f"SELECT COUNT(*) FROM user_tables WHERE table_name = UPPER('{table_name}')"
        )
        return success and result and result[0][0] > 0
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for Oracle table"""
        success, result = self.execute_query(f"SELECT COUNT(*) FROM {table_name}")
        if success and result:
            return result[0][0]
        return 0