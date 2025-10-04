"""
Unit tests for OracleConnector
Tests: positive cases, negative cases, and edge cases
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connectors.oracle_connector import OracleConnector


@pytest.mark.unit
@pytest.mark.db
class TestOracleConnector:
    """Test cases for OracleConnector"""

    def setup_method(self):
        """Setup before each test"""
        self.connector = OracleConnector(
            host="localhost",
            port=1521,
            username="testuser",
            password="testpass",
            service_name="XE",
        )

    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self.connector, "connection") and self.connector.connection:
            self.connector.disconnect()

    # POSITIVE TEST CASES
    @pytest.mark.positive
    def test_connect_success(self):
        """Test successful connection"""
        mock_oracledb = Mock()
        mock_connection = Mock()
        mock_oracledb.connect.return_value = mock_connection

        with patch.dict("sys.modules", {"oracledb": mock_oracledb}):
            success, message = self.connector.connect()

        assert success is True
        assert "successfully" in message.lower()
        assert self.connector.is_connected is True
        assert self.connector.connection == mock_connection

        expected_dsn = "localhost:1521/XE"
        mock_oracledb.connect.assert_called_once_with(
            user="testuser", password="testpass", dsn=expected_dsn
        )

    def test_execute_query_success(self):
        """Test successful query execution"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("USERS",), ("ORDERS",)]

        self.connector.connection = mock_connection
        self.connector.is_connected = True

        success, result = self.connector.execute_query(
            "SELECT table_name FROM user_tables"
        )

        assert success is True
        assert result == [("USERS",), ("ORDERS",)]
        mock_cursor.execute.assert_called_once_with(
            "SELECT table_name FROM user_tables"
        )
        mock_cursor.close.assert_called_once()

    def test_get_tables_success(self):
        """Test getting table names successfully"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [("USERS",), ("ORDERS",), ("PRODUCTS",)]

        self.connector.connection = mock_connection
        self.connector.is_connected = True

        tables = self.connector.get_tables()

        assert tables == ["USERS", "ORDERS", "PRODUCTS"]
        expected_query = "SELECT table_name FROM user_tables ORDER BY table_name"
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
            "SELECT COUNT(*) FROM user_tables WHERE table_name = UPPER('users')"
        )
        mock_cursor.execute.assert_called_once_with(expected_query)

    def test_get_row_count_success(self):
        """Test getting row count successfully"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(100,)]

        self.connector.connection = mock_connection
        self.connector.is_connected = True

        count = self.connector.get_row_count("USERS")

        assert count == 100
        mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM USERS")

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
        mock_oracledb = Mock()
        mock_oracledb.connect.side_effect = Exception("ORA-12541: TNS:no listener")

        with patch.dict("sys.modules", {"oracledb": mock_oracledb}):
            success, message = self.connector.connect()

        assert success is False
        assert "failed" in message.lower()
        assert "ora-12541" in message.lower()
        assert self.connector.is_connected is False

    def test_connect_import_error(self):
        """Test connection when oracledb is not available"""
        # Remove only oracledb module, not all modules to avoid access violations
        with patch.dict("sys.modules", {"oracledb": None}):
            success, message = self.connector.connect()

            assert success is False
            assert "failed" in message.lower()

    def test_execute_query_not_connected(self):
        """Test query execution when not connected"""
        success, result = self.connector.execute_query("SELECT * FROM dual")

        assert success is False
        assert "not connected" in result.lower()

    def test_execute_query_failure(self):
        """Test query execution failure"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception(
            "ORA-00942: table or view does not exist"
        )

        self.connector.connection = mock_connection
        self.connector.is_connected = True

        success, result = self.connector.execute_query("SELECT * FROM invalid_table")

        assert success is False
        assert "ora-00942" in result.lower()

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
        count = self.connector.get_row_count("USERS")
        assert count == 0

    # EDGE CASES
    @pytest.mark.edge
    def test_constructor_parameters(self):
        """Test constructor sets parameters correctly"""
        connector = OracleConnector(
            host="custom_host",
            port=9999,
            username="custom_user",
            password="custom_pass",
            service_name="CUSTOM_SID",
        )

        assert connector.host == "custom_host"
        assert connector.port == 9999
        assert connector.username == "custom_user"
        assert connector.password == "custom_pass"
        assert connector.service_name == "CUSTOM_SID"
        assert connector.is_connected is False

    def test_dsn_construction(self):
        """Test DSN construction with different parameters"""
        connector = OracleConnector(
            host="prod-oracle.company.com",
            port=1521,
            username="user",
            password="pass",
            service_name="PRODDB",
        )

        # We can't directly test DSN construction without connecting,
        # but we can verify the parameters are stored correctly
        assert connector.host == "prod-oracle.company.com"
        assert connector.port == 1521
        assert connector.service_name == "PRODDB"

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

        success, result = self.connector.execute_query("SELECT * FROM dual WHERE 1=0")

        assert success is True
        assert result == []

    def test_table_case_sensitivity(self):
        """Test Oracle's case handling (converts to uppercase)"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,)]

        self.connector.connection = mock_connection
        self.connector.is_connected = True

        # Oracle should convert to uppercase in the query
        exists = self.connector.table_exists("users")

        expected_query = (
            "SELECT COUNT(*) FROM user_tables WHERE table_name = UPPER('users')"
        )
        mock_cursor.execute.assert_called_once_with(expected_query)

    def test_table_exists_query_failure(self):
        """Test table existence check when query fails"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Query failed")

        self.connector.connection = mock_connection
        self.connector.is_connected = True

        exists = self.connector.table_exists("users")

        assert exists is False

    def test_get_row_count_query_failure(self):
        """Test row count when query fails"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Query failed")

        self.connector.connection = mock_connection
        self.connector.is_connected = True

        count = self.connector.get_row_count("USERS")

        assert count == 0
