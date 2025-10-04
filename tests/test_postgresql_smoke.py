#!/usr/bin/env python
"""
PostgreSQL Smoke Tests
Quick smoke tests to verify PostgreSQL connectivity and basic functionality
"""
import sys
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports - handle both pytest and standalone execution
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # Go up from tests/ to project root
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from utils.json_config_reader import JsonConfigReader
    from connectors.postgresql_connector import PostgreSQLConnector
except ImportError:
    # Fallback for different import scenarios
    sys.path.insert(0, str(project_root))
    from src.utils.json_config_reader import JsonConfigReader
    from src.connectors.postgresql_connector import PostgreSQLConnector


class TestPostgreSQLSmoke:
    """PostgreSQL smoke test suite for basic connectivity and functionality

    Configuration Priority (highest to lowest):
    1. Environment variables (POSTGRES_HOST, POSTGRES_PORT, etc.)
    2. Configuration file with specified environment/application
    3. Default DUMMY application in DEV environment

    Environment Variables Supported:
    - POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE, POSTGRES_SCHEMA
    - POSTGRES_USERNAME, POSTGRES_PASSWORD (or username_env_var/password_env_var)
    - TEST_ENVIRONMENT (default: DEV)
    - TEST_APPLICATION (default: DUMMY)
    """

    @classmethod
    def setup_class(cls):
        """Setup class-level resources for PostgreSQL smoke tests"""
        # Determine the correct base path for project root
        project_root = Path(__file__).resolve().parent.parent

        # Load environment variables
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            cls.env_loaded = True
        else:
            cls.env_loaded = False

        # Load database configuration
        config_file = project_root / "config" / "database_connections.json"
        cls.config_file_exists = config_file.exists()

        if cls.config_file_exists:
            cls.config_data = JsonConfigReader.read_config_file(str(config_file))
        else:
            cls.config_data = None

        # Determine which environment and application to test
        cls.test_environment = os.getenv("TEST_ENVIRONMENT", "DEV")
        cls.test_application = os.getenv("TEST_APPLICATION", "DUMMY")

        # Check if we can use direct environment variables
        cls.direct_config = cls._get_direct_config_from_env()

    @classmethod
    def _get_direct_config_from_env(cls):
        """Get PostgreSQL configuration directly from environment variables"""
        direct_config = {}

        # Check for direct PostgreSQL environment variables
        if os.getenv("POSTGRES_HOST"):
            direct_config["host"] = os.getenv("POSTGRES_HOST")
            direct_config["port"] = int(os.getenv("POSTGRES_PORT", "5432"))
            direct_config["database"] = os.getenv("POSTGRES_DATABASE", "postgres")
            direct_config["schema"] = os.getenv("POSTGRES_SCHEMA", "public")

            # Handle credentials
            if os.getenv("POSTGRES_USERNAME") and os.getenv("POSTGRES_PASSWORD"):
                direct_config["username"] = os.getenv("POSTGRES_USERNAME")
                direct_config["password"] = os.getenv("POSTGRES_PASSWORD")
            else:
                # Fall back to environment variable names
                direct_config["username_env_var"] = os.getenv(
                    "POSTGRES_USERNAME_VAR", "POSTGRES_USERNAME"
                )
                direct_config["password_env_var"] = os.getenv(
                    "POSTGRES_PASSWORD_VAR", "POSTGRES_PASSWORD"
                )

        return direct_config if direct_config else None

    @classmethod
    def _get_config_from_file(cls):
        """Get PostgreSQL configuration from configuration file"""
        if not cls.config_data:
            return None

        try:
            environments = cls.config_data.get("environments", {})
            if cls.test_environment not in environments:
                return None

            env_config = environments[cls.test_environment]

            # Check for application in either applications sub-key or directly
            if "applications" in env_config:
                applications = env_config["applications"]
                if cls.test_application not in applications:
                    return None
                return applications[cls.test_application]
            else:
                if cls.test_application not in env_config:
                    return None
                return env_config[cls.test_application]

        except Exception:
            return None

    @classmethod
    def _get_effective_config(cls):
        """Get the effective configuration using priority order"""
        # Priority 1: Direct environment variables
        if cls.direct_config:
            return cls.direct_config

        # Priority 2: Configuration file
        file_config = cls._get_config_from_file()
        if file_config:
            return file_config

        return None

    @pytest.mark.smoke
    @pytest.mark.db
    def test_environment_setup(self):
        """Test that environment and configuration are properly set up"""
        # Check if we have any valid configuration source
        effective_config = self._get_effective_config()

        # We should have at least one configuration source
        has_env_config = self.direct_config is not None
        has_file_config = self.config_file_exists and self.config_data is not None

        assert (
            has_env_config or has_file_config
        ), "Either environment variables (POSTGRES_HOST, etc.) or configuration file should be available"

        assert (
            effective_config is not None
        ), f"No valid PostgreSQL configuration found for environment '{self.test_environment}' and application '{self.test_application}'"

    @pytest.mark.smoke
    @pytest.mark.db
    def test_dummy_config_availability(self):
        """Test that PostgreSQL configuration is available and complete"""
        effective_config = self._get_effective_config()
        assert (
            effective_config is not None
        ), "PostgreSQL configuration must be available"

        # Validate required configuration fields
        if "username" in effective_config and "password" in effective_config:
            # Direct credentials configuration
            required_fields = [
                "host",
                "port",
                "database",
                "schema",
                "username",
                "password",
            ]
            for field in required_fields:
                assert (
                    field in effective_config
                ), f"Required field '{field}' should be present in PostgreSQL configuration"
        else:
            # Environment variable based credentials
            required_fields = [
                "host",
                "port",
                "database",
                "schema",
                "username_env_var",
                "password_env_var",
            ]
            for field in required_fields:
                assert (
                    field in effective_config
                ), f"Required field '{field}' should be present in PostgreSQL configuration"

    @pytest.mark.smoke
    @pytest.mark.db
    def test_environment_credentials(self):
        """Test that required credentials are available"""
        effective_config = self._get_effective_config()
        assert (
            effective_config is not None
        ), "PostgreSQL configuration must be available"

        if "username" in effective_config and "password" in effective_config:
            # Direct credentials
            username = effective_config.get("username")
            password = effective_config.get("password")

            assert username, "Username should be provided in configuration"
            assert password, "Password should be provided in configuration"
        else:
            # Environment variable based credentials
            username_var = effective_config.get("username_env_var")
            password_var = effective_config.get("password_env_var")

            assert (
                username_var
            ), "Username environment variable name should be specified"
            assert (
                password_var
            ), "Password environment variable name should be specified"

            username = os.getenv(username_var)
            password = os.getenv(password_var)

            assert (
                username
            ), f"Environment variable '{username_var}' should be set with username"
            assert (
                password
            ), f"Environment variable '{password_var}' should be set with password"

    @pytest.mark.smoke
    @pytest.mark.db
    @pytest.mark.integration
    def test_postgresql_connection(self):
        """Test PostgreSQL database connectivity using available configuration"""
        effective_config = self._get_effective_config()
        assert (
            effective_config is not None
        ), "PostgreSQL configuration must be available"

        # Get credentials
        if "username" in effective_config and "password" in effective_config:
            username = effective_config["username"]
            password = effective_config["password"]
        else:
            username = os.getenv(effective_config.get("username_env_var"))
            password = os.getenv(effective_config.get("password_env_var"))

        # Create PostgreSQL connector
        connector = PostgreSQLConnector(
            host=effective_config["host"],
            port=effective_config["port"],
            username=username,
            password=password,
            database=effective_config["database"],
        )

        # Test connection
        success, message = connector.connect()
        assert success, f"PostgreSQL connection should succeed: {message}"

        # Ensure cleanup
        connector.disconnect()

    @pytest.mark.smoke
    @pytest.mark.db
    @pytest.mark.integration
    def test_postgresql_basic_queries(self):
        """Test basic PostgreSQL queries for smoke testing"""
        effective_config = self._get_effective_config()
        assert (
            effective_config is not None
        ), "PostgreSQL configuration must be available"

        # Get credentials
        if "username" in effective_config and "password" in effective_config:
            username = effective_config["username"]
            password = effective_config["password"]
        else:
            username = os.getenv(effective_config.get("username_env_var"))
            password = os.getenv(effective_config.get("password_env_var"))

        # Create and connect PostgreSQL connector
        connector = PostgreSQLConnector(
            host=effective_config["host"],
            port=effective_config["port"],
            username=username,
            password=password,
            database=effective_config["database"],
        )

        success, message = connector.connect()
        assert success, f"PostgreSQL connection should succeed: {message}"

        try:
            # Test version query
            success, result = connector.execute_query("SELECT version();")
            assert success, "Version query should execute successfully"
            assert result, "Version query should return results"
            assert len(result) > 0, "Version query should return at least one row"

            # Test schema accessibility (if schema is specified)
            if effective_config.get("schema"):
                schema_query = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{effective_config['schema']}';"
                success, result = connector.execute_query(schema_query)
                assert success, "Schema query should execute successfully"

            # Test table listing (should not fail even if no tables exist)
            tables = connector.get_tables()
            assert isinstance(tables, list), "get_tables() should return a list"

        finally:
            # Ensure cleanup
            connector.disconnect()

    @pytest.mark.smoke
    @pytest.mark.db
    @pytest.mark.performance
    def test_postgresql_connection_performance(self):
        """Test that PostgreSQL connection establishes within reasonable time"""
        import time

        effective_config = self._get_effective_config()
        assert (
            effective_config is not None
        ), "PostgreSQL configuration must be available"

        # Get credentials
        if "username" in effective_config and "password" in effective_config:
            username = effective_config["username"]
            password = effective_config["password"]
        else:
            username = os.getenv(effective_config.get("username_env_var"))
            password = os.getenv(effective_config.get("password_env_var"))

        # Create PostgreSQL connector
        connector = PostgreSQLConnector(
            host=effective_config["host"],
            port=effective_config["port"],
            username=username,
            password=password,
            database=effective_config["database"],
        )

        # Measure connection time
        start_time = time.time()
        success, message = connector.connect()
        connection_time = time.time() - start_time

        try:
            assert success, f"PostgreSQL connection should succeed: {message}"
            assert (
                connection_time < 5.0
            ), f"Connection should establish within 5 seconds, took {connection_time:.2f}s"
        finally:
            # Ensure cleanup
            connector.disconnect()


# Standalone smoke test function for backwards compatibility
@pytest.mark.smoke
@pytest.mark.db
def test_postgresql_dummy_connection():
    """
    Standalone smoke test function for PostgreSQL connection
    This maintains backwards compatibility while integrating with pytest
    Works with any PostgreSQL configuration (environment variables or config file)
    """
    test_suite = TestPostgreSQLSmoke()
    test_suite.setup_class()

    # Run basic connectivity test
    test_suite.test_environment_setup()
    test_suite.test_dummy_config_availability()
    test_suite.test_environment_credentials()
    test_suite.test_postgresql_connection()

    # pytest functions should not return values
    assert True


if __name__ == "__main__":
    # Allow running as standalone script for backwards compatibility
    import sys

    print("=" * 60)
    print("PostgreSQL Database Smoke Tests")
    print("Testing PostgreSQL connectivity with available configuration")
    print("=" * 60)

    try:
        test_postgresql_dummy_connection()
        print("\n" + "=" * 60)
        print("🎉 PostgreSQL smoke tests PASSED!")
        print("✅ PostgreSQL configuration is working correctly")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ PostgreSQL smoke tests FAILED: {e}")
        print("🔧 Please check your configuration and credentials")
        print("=" * 60)
        sys.exit(1)
