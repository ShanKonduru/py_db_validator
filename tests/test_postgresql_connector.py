"""
Unit tests for PostgreSQLConnector
Tests: positive cases, negative cases, and edge cases
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connectors.postgresql_connector import PostgreSQLConnector


@pytest.mark.unit
@pytest.mark.db
class TestPostgreSQLConnector:
    """Test cases for PostgreSQLConnector"""
    
    def setup_method(self):
        """Setup before each test"""
        self.connector = PostgreSQLConnector(
            host="localhost",
            port=5432,
            username="testuser",
            password="testpass",
            database="testdb"
        )
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self.connector, 'connection') and self.connector.connection:
            self.connector.disconnect()
    
    # POSITIVE TEST CASES
    @pytest.mark.positive
    def test_connect_success(self):
        """Test successful connection"""
        mock_psycopg2 = Mock()
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        with patch.dict('sys.modules', {'psycopg2': mock_psycopg2}):
            success, message = self.connector.connect()
        
        assert success is True
        assert "successfully" in message.lower()
        assert self.connector.is_connected is True
        assert self.connector.connection == mock_connection
    
    def test_execute_query_success(self):
        """Test successful query execution"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("users",), ("orders",)]
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        success, result = self.connector.execute_query("SELECT tablename FROM pg_tables")
        
        assert success is True
        assert result == [("users",), ("orders",)]
        mock_cursor.execute.assert_called_once_with("SELECT tablename FROM pg_tables")
        mock_cursor.close.assert_called_once()
    
    def test_get_tables_success(self):
        """Test getting table names successfully"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("users",), ("orders",), ("products",)]
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        tables = self.connector.get_tables()
        
        assert tables == ["users", "orders", "products"]
        expected_query = (
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public'"
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
        
        exists = self.connector.table_exists("users")
        
        assert exists is True
        expected_query = (
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_name = 'users'"
        )
        mock_cursor.execute.assert_called_once_with(expected_query)
    
    def test_get_row_count_success(self):
        """Test getting row count successfully"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(150,)]
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        count = self.connector.get_row_count("users")
        
        assert count == 150
        mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM users")
    
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
        mock_psycopg2 = Mock()
        mock_psycopg2.connect.side_effect = Exception("Connection refused")
        
        with patch.dict('sys.modules', {'psycopg2': mock_psycopg2}):
            success, message = self.connector.connect()
        
        assert success is False
        assert "failed" in message.lower()
        assert "connection refused" in message.lower()
        assert self.connector.is_connected is False
    
    def test_connect_import_error(self):
        """Test connection when psycopg2 is not available"""
        # Remove only psycopg2 module, not all modules to avoid access violations
        with patch.dict('sys.modules', {'psycopg2': None}):
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
        mock_cursor.execute.side_effect = Exception("relation \"invalid_table\" does not exist")
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        success, result = self.connector.execute_query("SELECT * FROM invalid_table")
        
        assert success is False
        assert "does not exist" in result.lower()
    
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
        count = self.connector.get_row_count("users")
        assert count == 0
    
    # EDGE CASES
    def test_constructor_parameters(self):
        """Test constructor sets parameters correctly"""
        connector = PostgreSQLConnector(
            host="pg-server.company.com",
            port=5433,
            username="admin",
            password="secret123",
            database="production"
        )
        
        assert connector.host == "pg-server.company.com"
        assert connector.port == 5433
        assert connector.username == "admin"
        assert connector.password == "secret123"
        assert connector.database == "production"
        assert connector.is_connected is False
    
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
        mock_psycopg2 = Mock()
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        with patch.dict('sys.modules', {'psycopg2': mock_psycopg2}):
            # First connection
            success1, _ = self.connector.connect()
            assert success1 is True
            
            # Second connection (should replace the first)
            success2, _ = self.connector.connect()
            assert success2 is True
            
            # Should have called psycopg2.connect twice
            assert mock_psycopg2.connect.call_count == 2
    
    def test_table_exists_query_failure(self):
        """Test table existence check when query fails"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database query failed")
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        exists = self.connector.table_exists("users")
        
        assert exists is False
    
    def test_get_row_count_query_failure(self):
        """Test row count when query fails"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Table access denied")
        
        self.connector.connection = mock_connection
        self.connector.is_connected = True
        
        count = self.connector.get_row_count("users")
        
        assert count == 0