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
    """PostgreSQL smoke test suite for basic connectivity and functionality"""

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

    @pytest.mark.smoke
    @pytest.mark.db
    def test_environment_setup(self):
        """Test that environment and configuration files are properly set up"""
        assert self.env_loaded, "Environment file (.env) should be present and loadable"
        assert self.config_file_exists, "Database configuration file should exist"
        assert self.config_data is not None, "Configuration data should be loadable"

    @pytest.mark.smoke
    @pytest.mark.db
    def test_dummy_config_availability(self):
        """Test that DUMMY application configuration is available in DEV environment"""
        assert self.config_data is not None, "Configuration data must be loaded"
        
        environments = self.config_data.get("environments", {})
        assert "DEV" in environments, "DEV environment should be configured"
        
        dev_env = environments["DEV"]
        
        # Check for DUMMY application in either applications sub-key or directly
        if "applications" in dev_env:
            applications = dev_env["applications"]
            assert "DUMMY" in applications, "DUMMY application should be configured in DEV.applications"
            dummy_config = applications["DUMMY"]
        else:
            assert "DUMMY" in dev_env, "DUMMY application should be configured in DEV"
            dummy_config = dev_env["DUMMY"]
        
        # Validate required configuration fields
        required_fields = ["db_type", "host", "port", "database", "schema", "username_env_var", "password_env_var"]
        for field in required_fields:
            assert field in dummy_config, f"Required field '{field}' should be present in DUMMY configuration"

    @pytest.mark.smoke
    @pytest.mark.db
    def test_environment_credentials(self):
        """Test that required environment variables for credentials are set"""
        assert self.config_data is not None, "Configuration data must be loaded"
        
        # Get DUMMY configuration
        environments = self.config_data.get("environments", {})
        dev_env = environments["DEV"]
        
        if "applications" in dev_env:
            dummy_config = dev_env["applications"]["DUMMY"]
        else:
            dummy_config = dev_env["DUMMY"]
        
        username_var = dummy_config.get("username_env_var")
        password_var = dummy_config.get("password_env_var")
        
        assert username_var, "Username environment variable name should be specified"
        assert password_var, "Password environment variable name should be specified"
        
        username = os.getenv(username_var)
        password = os.getenv(password_var)
        
        assert username, f"Environment variable '{username_var}' should be set with username"
        assert password, f"Environment variable '{password_var}' should be set with password"

    @pytest.mark.smoke
    @pytest.mark.db
    @pytest.mark.integration
    def test_postgresql_connection(self):
        """Test PostgreSQL database connectivity using DUMMY application configuration"""
        assert self.config_data is not None, "Configuration data must be loaded"
        
        # Get DUMMY configuration
        environments = self.config_data.get("environments", {})
        dev_env = environments["DEV"]
        
        if "applications" in dev_env:
            dummy_config = dev_env["applications"]["DUMMY"]
        else:
            dummy_config = dev_env["DUMMY"]
        
        # Get credentials from environment variables
        username = os.getenv(dummy_config.get("username_env_var"))
        password = os.getenv(dummy_config.get("password_env_var"))
        
        # Create PostgreSQL connector
        connector = PostgreSQLConnector(
            host=dummy_config["host"],
            port=dummy_config["port"],
            username=username,
            password=password,
            database=dummy_config["database"],
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
        assert self.config_data is not None, "Configuration data must be loaded"
        
        # Get DUMMY configuration
        environments = self.config_data.get("environments", {})
        dev_env = environments["DEV"]
        
        if "applications" in dev_env:
            dummy_config = dev_env["applications"]["DUMMY"]
        else:
            dummy_config = dev_env["DUMMY"]
        
        # Get credentials from environment variables
        username = os.getenv(dummy_config.get("username_env_var"))
        password = os.getenv(dummy_config.get("password_env_var"))
        
        # Create and connect PostgreSQL connector
        connector = PostgreSQLConnector(
            host=dummy_config["host"],
            port=dummy_config["port"],
            username=username,
            password=password,
            database=dummy_config["database"],
        )
        
        success, message = connector.connect()
        assert success, f"PostgreSQL connection should succeed: {message}"
        
        try:
            # Test version query
            success, result = connector.execute_query("SELECT version();")
            assert success, "Version query should execute successfully"
            assert result, "Version query should return results"
            assert len(result) > 0, "Version query should return at least one row"
            
            # Test schema accessibility
            schema_query = f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{dummy_config['schema']}';"
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
        
        assert self.config_data is not None, "Configuration data must be loaded"
        
        # Get DUMMY configuration
        environments = self.config_data.get("environments", {})
        dev_env = environments["DEV"]
        
        if "applications" in dev_env:
            dummy_config = dev_env["applications"]["DUMMY"]
        else:
            dummy_config = dev_env["DUMMY"]
        
        # Get credentials from environment variables
        username = os.getenv(dummy_config.get("username_env_var"))
        password = os.getenv(dummy_config.get("password_env_var"))
        
        # Create PostgreSQL connector
        connector = PostgreSQLConnector(
            host=dummy_config["host"],
            port=dummy_config["port"],
            username=username,
            password=password,
            database=dummy_config["database"],
        )
        
        # Measure connection time
        start_time = time.time()
        success, message = connector.connect()
        connection_time = time.time() - start_time
        
        try:
            assert success, f"PostgreSQL connection should succeed: {message}"
            assert connection_time < 5.0, f"Connection should establish within 5 seconds, took {connection_time:.2f}s"
        finally:
            # Ensure cleanup
            connector.disconnect()


# Standalone smoke test function for backwards compatibility
@pytest.mark.smoke
@pytest.mark.db
def test_postgresql_dummy_connection():
    """
    Standalone smoke test function for PostgreSQL DUMMY connection
    This maintains backwards compatibility while integrating with pytest
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
    print("Testing DUMMY application in DEV environment")
    print("=" * 60)
    
    try:
        test_postgresql_dummy_connection()
        print("\n" + "=" * 60)
        print("🎉 PostgreSQL smoke tests PASSED!")
        print("✅ The DUMMY application configuration is working correctly")
        print("=" * 60)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ PostgreSQL smoke tests FAILED: {e}")
        print("🔧 Please check your configuration and credentials")
        print("=" * 60)
        sys.exit(1)