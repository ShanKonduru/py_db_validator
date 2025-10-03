"""
Unit tests for SQLServerConnector
Tests: positive cases, negative cases, and edge cases
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connectors.sqlserver_connector import SQLServerConnector


@pytest.mark.unit
@pytest.mark.db
class TestSQLServerConnector:
    """Test cases for SQLServerConnector"""
    
    def setup_method(self):
        """Setup before each test"""
        self.connector = SQLServerConnector(
            host="localhost",
            port=1433,
            username="testuser",
            password="testpass",
            database="TestDB"
        )
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self.connector, 'connection') and self.connector.connection:
            self.connector.disconnect()
    
    # POSITIVE TEST CASES
    @pytest.mark.positive
    def test_connect_success(self):
        """Test successful connection"""
        mock_pyodbc = Mock()
        mock_connection = Mock()
        mock_pyodbc.connect.return_value = mock_connection
        
        with patch.dict('sys.modules', {'pyodbc': mock_pyodbc}):
            success, message = self.connector.connect()
        
        assert success is True
        assert "successfully" in message.lower()
        assert self.connector.is_connected is True
        assert self.connector.connection == mock_connection
        
        expected_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=TestDB;"
            "UID=testuser;"
            "PWD=testpass;"
            "TrustServerCertificate=yes;"
        )
        mock_pyodbc.connect.assert_called_once_with(expected_conn_str, timeout=10)
    
    def test_execute_query_success(self):
        """Test successful query execution"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("Users",), ("Orders",)]
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        success, result = self.connector.execute_query("SELECT table_name FROM information_schema.tables")
        
        assert success is True
        assert result == [("Users",), ("Orders",)]
        mock_cursor.execute.assert_called_once_with("SELECT table_name FROM information_schema.tables")
        mock_cursor.close.assert_called_once()
    
    def test_get_tables_success(self):
        """Test getting table names successfully"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("Users",), ("Orders",), ("Products",)]
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        tables = self.connector.get_tables()
        
        assert tables == ["Users", "Orders", "Products"]
        expected_query = (
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_type = 'BASE TABLE' ORDER BY table_name"
        )
        mock_cursor.execute.assert_called_once_with(expected_query)
    
    def test_table_exists_true(self):
        """Test table existence check returns True"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)]
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        exists = self.connector.table_exists("Users")
        
        assert exists is True
        expected_query = (
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_name = 'Users'"
        )
        mock_cursor.execute.assert_called_once_with(expected_query)
    
    def test_get_row_count_success(self):
        """Test getting row count successfully"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(250,)]
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        count = self.connector.get_row_count("Users")
        
        assert count == 250
        mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM [Users]")
    
    def test_disconnect_success(self):
        """Test successful disconnection"""
        mock_connection = Mock()
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        self.connector.disconnect()
        
        assert self.connector.is_connected is False
        mock_connection.close.assert_called_once()
    
    # NEGATIVE TEST CASES
    @pytest.mark.negative
    def test_connect_failure(self):
        """Test connection failure"""
        mock_pyodbc = Mock()
        mock_pyodbc.connect.side_effect = Exception("Login failed for user 'testuser'")
        
        with patch.dict('sys.modules', {'pyodbc': mock_pyodbc}):
            success, message = self.connector.connect()
        
        assert success is False
        assert "failed" in message.lower()
        assert "login failed" in message.lower()
        assert self.connector.is_connected is False
    
    def test_connect_import_error(self):
        """Test connection when pyodbc is not available"""
        # Remove only pyodbc module, not all modules to avoid access violations
        with patch.dict('sys.modules', {'pyodbc': None}):
            success, message = self.connector.connect()
            
            assert success is False
            assert "failed" in message.lower()
    
    def test_execute_query_not_connected(self):
        """Test query execution when not connected"""
        success, result = self.connector.execute_query("SELECT 1")
        
        assert success is False
        assert "not connected" in result.lower()
    
    def test_execute_query_failure(self):
        """Test query execution failure"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Invalid object name 'invalid_table'")
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        success, result = self.connector.execute_query("SELECT * FROM invalid_table")
        
        assert success is False
        assert "invalid object name" in result.lower()
    
    def test_table_exists_false(self):
        """Test table existence check returns False"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(0,)]
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        exists = self.connector.table_exists("nonexistent")
        
        assert exists is False
    
    def test_get_tables_not_connected(self):
        """Test getting tables when not connected"""
        tables = self.connector.get_tables()
        assert tables == []
    
    def test_get_row_count_not_connected(self):
        """Test getting row count when not connected"""
        count = self.connector.get_row_count("Users")
        assert count == 0
    
    # EDGE CASES
    def test_constructor_parameters(self):
        """Test constructor sets parameters correctly"""
        connector = SQLServerConnector(
            host="sql-server.company.com",
            port=1434,
            username="admin",
            password="secret123",
            database="ProductionDB"
        )
        
        assert connector.host == "sql-server.company.com"
        assert connector.port == 1434
        assert connector.username == "admin"
        assert connector.password == "secret123"
        assert connector.database == "ProductionDB"
        assert connector.is_connected is False
    
    def test_connection_string_construction(self):
        """Test connection string construction with special characters"""
        connector = SQLServerConnector(
            host="server;with,special\\chars",
            port=1433,
            username="user@domain",
            password="pass;word=test",
            database="DB-With-Dashes"
        )
        
        # Parameters should be stored as provided
        assert connector.host == "server;with,special\\chars"
        assert connector.username == "user@domain"
        assert connector.password == "pass;word=test"
        assert connector.database == "DB-With-Dashes"
    
    def test_disconnect_when_not_connected(self):
        """Test disconnect when connection is None"""
        self.connector.connection = None
        self.connector.disconnect()  # Should not raise error
        assert self.connector.is_connected is False
    
    def test_empty_query_result(self):
        """Test query with empty result"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        success, result = self.connector.execute_query("SELECT 1 WHERE 1=0")
        
        assert success is True
        assert result == []
    
    def test_multiple_connects(self):
        """Test multiple connection attempts"""
        mock_pyodbc = Mock()
        mock_connection = Mock()
        mock_pyodbc.connect.return_value = mock_connection
        
        with patch.dict('sys.modules', {'pyodbc': mock_pyodbc}):
            # First connection
            success1, _ = self.connector.connect()
            assert success1 is True
            
            # Second connection (should replace the first)
            success2, _ = self.connector.connect()
            assert success2 is True
            
            # Should have called pyodbc.connect twice
            assert mock_pyodbc.connect.call_count == 2
    
    def test_table_exists_query_failure(self):
        """Test table existence check when query fails"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database query failed")
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        exists = self.connector.table_exists("Users")
        
        assert exists is False
    
    def test_get_row_count_query_failure(self):
        """Test row count when query fails"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Table access denied")
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        count = self.connector.get_row_count("Users")
        
        assert count == 0
    
    def test_special_sql_server_errors(self):
        """Test handling of SQL Server specific errors"""
        mock_pyodbc = Mock()
        mock_pyodbc.connect.side_effect = Exception("Cannot open database")
        
        with patch.dict('sys.modules', {'pyodbc': mock_pyodbc}):
            success, message = self.connector.connect()
        
        assert success is False
        assert "cannot open database" in message.lower()
    
    def test_sql_injection_prevention(self):
        """Test that parameters are passed correctly (not preventing SQL injection at this level)"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(0,)]
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        # Test with potentially malicious table name
        malicious_table = "Users'; DROP TABLE Users; --"
        exists = self.connector.table_exists(malicious_table)
        
        # The connector should pass the string as-is to the query
        expected_query = (
            "SELECT COUNT(*) FROM information_schema.tables "
            f"WHERE table_name = '{malicious_table}'"
        )
        mock_cursor.execute.assert_called_once_with(expected_query)
        assert exists is False