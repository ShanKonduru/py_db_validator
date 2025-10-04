"""
Unit tests for DatabaseConnection data class
"""

import pytest
from src.utils.database_connection import DatabaseConnection


class TestDatabaseConnection:
    """Test DatabaseConnection data class"""

    @pytest.mark.unit
    def test_database_connection_creation(self):
        """Test creating DatabaseConnection object"""
        conn = DatabaseConnection(
            db_type="oracle",
            host="localhost",
            port=1521,
            database="testdb",
            schema="test_schema",
            username_env="DB_USER",
            password_env="DB_PASS",
        )

        assert conn.db_type == "oracle"
        assert conn.host == "localhost"
        assert conn.port == 1521
        assert conn.database == "testdb"
        assert conn.schema == "test_schema"
        assert conn.username_env == "DB_USER"
        assert conn.password_env == "DB_PASS"

    @pytest.mark.unit
    def test_database_connection_minimal(self):
        """Test creating DatabaseConnection with minimal required fields"""
        conn = DatabaseConnection(
            db_type="postgresql", host="localhost", port=5432, database="testdb"
        )

        assert conn.db_type == "postgresql"
        assert conn.host == "localhost"
        assert conn.port == 5432
        assert conn.database == "testdb"
        assert conn.schema is None
        assert conn.username_env is None
        assert conn.password_env is None

    @pytest.mark.unit
    def test_to_dict_full(self):
        """Test converting DatabaseConnection to dictionary with all fields"""
        conn = DatabaseConnection(
            db_type="oracle",
            host="localhost",
            port=1521,
            database="testdb",
            schema="test_schema",
            username_env="DB_USER",
            password_env="DB_PASS",
        )

        result = conn.to_dict()
        expected = {
            "db_type": "oracle",
            "host": "localhost",
            "port": 1521,
            "database": "testdb",
            "schema": "test_schema",
            "username_env": "DB_USER",
            "password_env": "DB_PASS",
        }

        assert result == expected

    @pytest.mark.unit
    def test_to_dict_minimal(self):
        """Test converting DatabaseConnection to dictionary with minimal fields"""
        conn = DatabaseConnection(
            db_type="postgresql", host="localhost", port=5432, database="testdb"
        )

        result = conn.to_dict()
        expected = {
            "db_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
        }

        assert result == expected

    @pytest.mark.unit
    def test_from_dict_full(self):
        """Test creating DatabaseConnection from dictionary with all fields"""
        data = {
            "db_type": "oracle",
            "host": "localhost",
            "port": 1521,
            "database": "testdb",
            "schema": "test_schema",
            "username_env": "DB_USER",
            "password_env": "DB_PASS",
        }

        conn = DatabaseConnection.from_dict(data)

        assert conn.db_type == "oracle"
        assert conn.host == "localhost"
        assert conn.port == 1521
        assert conn.database == "testdb"
        assert conn.schema == "test_schema"
        assert conn.username_env == "DB_USER"
        assert conn.password_env == "DB_PASS"

    @pytest.mark.unit
    def test_from_dict_minimal(self):
        """Test creating DatabaseConnection from dictionary with minimal fields"""
        data = {
            "db_type": "postgresql",
            "host": "localhost",
            "port": 5432,
            "database": "testdb",
        }

        conn = DatabaseConnection.from_dict(data)

        assert conn.db_type == "postgresql"
        assert conn.host == "localhost"
        assert conn.port == 5432
        assert conn.database == "testdb"
        assert conn.schema is None
        assert conn.username_env is None
        assert conn.password_env is None
