"""
Unit tests for MockDatabaseConnector
Tests: positive cases, negative cases, and edge cases
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connectors.mock_connector import MockDatabaseConnector


@pytest.mark.unit
@pytest.mark.db
class TestMockConnector:
    """Test cases for MockDatabaseConnector"""

    def setup_method(self):
        """Setup before each test"""
        self.connector = MockDatabaseConnector(
            host="localhost", port=5432, username="testuser", password="testpass"
        )

    def teardown_method(self):
        """Cleanup after each test"""
        if self.connector.is_connected:
            self.connector.disconnect()

    # POSITIVE TEST CASES
    @pytest.mark.positive
    def test_connect_success(self):
        """Test successful connection"""
        success, message = self.connector.connect()
        assert success is True
        assert "successfully" in message.lower()
        assert self.connector.is_connected is True

    @pytest.mark.positive
    def test_get_tables_when_connected(self):
        """Test getting table list when connected"""
        self.connector.connect()
        tables = self.connector.get_tables()

        assert isinstance(tables, list)
        assert len(tables) > 0
        assert "users" in tables
        assert "orders" in tables
        assert "products" in tables

    @pytest.mark.positive
    def test_table_exists_positive(self):
        """Test table existence check for existing table"""
        self.connector.connect()
        assert self.connector.table_exists("users") is True
        assert self.connector.table_exists("orders") is True
        assert self.connector.table_exists("products") is True

    @pytest.mark.positive
    def test_get_row_count_existing_table(self):
        """Test row count for existing table"""
        self.connector.connect()
        count = self.connector.get_row_count("users")
        assert count == 2  # Mock data has 2 users: Alice and Bob

    @pytest.mark.positive
    def test_execute_query_count(self):
        """Test executing a count query"""
        self.connector.connect()
        success, result = self.connector.execute_query("SELECT COUNT(*) FROM users")
        assert success is True
        assert result == [(2,)]  # Mock data has 2 users

    @pytest.mark.positive
    def test_disconnect_success(self):
        """Test successful disconnection"""
        self.connector.connect()
        assert self.connector.is_connected is True

        self.connector.disconnect()
        assert self.connector.is_connected is False

    # NEGATIVE TEST CASES
    @pytest.mark.negative
    def test_table_exists_nonexistent(self):
        """Test table existence check for non-existent table"""
        self.connector.connect()
        assert self.connector.table_exists("nonexistent_table") is False

    @pytest.mark.negative
    def test_get_row_count_nonexistent_table(self):
        """Test row count for non-existent table"""
        self.connector.connect()
        count = self.connector.get_row_count("nonexistent_table")
        assert count == 0

    @pytest.mark.negative
    def test_execute_query_when_disconnected(self):
        """Test query execution when not connected"""
        success, result = self.connector.execute_query("SELECT * FROM users")
        assert success is False
        assert "not connected" in result.lower()

    # EDGE CASES
    @pytest.mark.edge
    def test_multiple_connects(self):
        """Test multiple connection attempts"""
        success1, _ = self.connector.connect()
        success2, _ = self.connector.connect()
        assert success1 is True
        assert success2 is True
        assert self.connector.is_connected is True

    @pytest.mark.edge
    def test_disconnect_when_not_connected(self):
        """Test disconnect when not connected"""
        self.connector.disconnect()  # Should not raise error
        assert self.connector.is_connected is False

    @pytest.mark.edge
    def test_empty_table_name(self):
        """Test table operations with empty table name"""
        self.connector.connect()
        assert self.connector.table_exists("") is False
        assert self.connector.get_row_count("") == 0

    @pytest.mark.edge
    def test_case_sensitive_table_names(self):
        """Test table names with different cases"""
        self.connector.connect()
        assert self.connector.table_exists("USERS") is False  # Mock is case sensitive
        assert self.connector.table_exists("Users") is False
        assert self.connector.table_exists("users") is True

    @pytest.mark.security
    def test_special_characters_in_table_name(self):
        """Test table names with special characters"""
        self.connector.connect()
        assert self.connector.table_exists("user's_table") is False
        assert self.connector.table_exists("user-table") is False
        assert self.connector.table_exists("user table") is False

    @pytest.mark.security
    def test_sql_injection_attempt(self):
        """Test resistance to SQL injection"""
        self.connector.connect()
        malicious_table = "users'; DROP TABLE users; --"
        assert self.connector.table_exists(malicious_table) is False
        assert self.connector.get_row_count(malicious_table) == 0

    @pytest.mark.edge
    def test_very_long_query(self):
        """Test execution of very long query"""
        self.connector.connect()
        long_query = "SELECT * FROM users WHERE " + " AND ".join(
            [f"id = {i}" for i in range(100)]
        )
        success, result = self.connector.execute_query(long_query)
        assert success is True
        assert result == [
            ("mock_result",)
        ]  # Mock returns default result for complex queries

    @pytest.mark.edge
    def test_constructor_with_custom_parameters(self):
        """Test constructor with custom parameters"""
        custom_connector = MockDatabaseConnector(
            host="custom.host.com",
            port=9999,
            username="custom_user",
            password="custom_pass",
        )

        assert custom_connector.host == "custom.host.com"
        assert custom_connector.port == 9999
        assert custom_connector.username == "custom_user"
        assert custom_connector.password == "custom_pass"
        assert custom_connector.is_connected is False

    @pytest.mark.edge
    def test_get_tables_returns_copy(self):
        """Test that get_tables returns a copy, not reference"""
        self.connector.connect()
        tables1 = self.connector.get_tables()
        tables2 = self.connector.get_tables()

        # Modify one list
        tables1.append("new_table")

        # Other list should be unchanged
        assert "new_table" not in tables2
        assert len(tables1) != len(tables2)
