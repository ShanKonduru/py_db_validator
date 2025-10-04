#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static PostgreSQL Smoke Tests Class
==================================
Immutable static class containing all PostgreSQL smoke test methods.
This class provides a stable interface that prevents accidental modifications.

Author: Multi-Database Data Validation Framework
Date: October 4, 2025
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Add src to path for imports
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
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


class StaticPostgreSQLSmokeTests:
    """
    🔒 IMMUTABLE STATIC SMOKE TEST CLASS
    
    This class contains all PostgreSQL smoke test methods as static methods.
    It is designed to be immutable and prevent accidental modifications.
    
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
    
    # Class constants - immutable configuration
    _DEFAULT_ENVIRONMENT = "DEV"
    _DEFAULT_APPLICATION = "DUMMY"
    _CONFIG_FILE_PATH = "config/db_config.json"
    _PERFORMANCE_THRESHOLD_SECONDS = 2.0
    
    # Prevent instantiation
    def __new__(cls):
        raise TypeError(f"{cls.__name__} is a static class and cannot be instantiated")
    
    @staticmethod
    def _load_environment_config() -> Dict[str, Any]:
        """Load PostgreSQL configuration from environment variables (immutable)"""
        project_root = Path(__file__).resolve().parent.parent
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        
        env_config = {}
        
        # Direct configuration from environment
        if all(key in os.environ for key in ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DATABASE"]):
            env_config = {
                "host": os.environ.get("POSTGRES_HOST"),
                "port": int(os.environ.get("POSTGRES_PORT", 5432)),
                "database": os.environ.get("POSTGRES_DATABASE"),
                "schema": os.environ.get("POSTGRES_SCHEMA", "public"),
            }
            
            # Handle credentials - either direct or environment variable references
            if "POSTGRES_USERNAME" in os.environ and "POSTGRES_PASSWORD" in os.environ:
                env_config.update({
                    "username": os.environ.get("POSTGRES_USERNAME"),
                    "password": os.environ.get("POSTGRES_PASSWORD")
                })
            else:
                env_config.update({
                    "username_env_var": "POSTGRES_USERNAME",
                    "password_env_var": "POSTGRES_PASSWORD"
                })
        
        return env_config
    
    @staticmethod
    def _load_config_file(environment: str = None, application: str = None) -> tuple:
        """Load configuration from JSON file (immutable)"""
        project_root = Path(__file__).resolve().parent.parent
        config_file_path = project_root / StaticPostgreSQLSmokeTests._CONFIG_FILE_PATH
        
        config_file_exists = config_file_path.exists()
        config_data = None
        
        if config_file_exists:
            try:
                reader = JsonConfigReader(str(config_file_path))
                config_data = reader.get_database_config(
                    "postgresql",
                    environment or StaticPostgreSQLSmokeTests._DEFAULT_ENVIRONMENT,
                    application or StaticPostgreSQLSmokeTests._DEFAULT_APPLICATION
                )
            except Exception:
                config_data = None
        
        return config_file_exists, config_data
    
    @staticmethod
    def _get_effective_config(environment: str = None, application: str = None) -> Optional[Dict[str, Any]]:
        """Get effective configuration with priority order (immutable)"""
        # Priority 1: Environment variables
        direct_config = StaticPostgreSQLSmokeTests._load_environment_config()
        if direct_config:
            return direct_config
        
        # Priority 2: Configuration file
        _, config_data = StaticPostgreSQLSmokeTests._load_config_file(environment, application)
        if config_data:
            return config_data
        
        return None
    
    @staticmethod
    def test_environment_setup(environment: str = None, application: str = None) -> Dict[str, Any]:
        """
        🧪 STATIC TEST: Environment Setup Validation
        
        Test that environment and configuration are properly set up.
        Returns test result with status and details.
        """
        result = {
            "test_name": "Environment Setup Validation",
            "status": "FAIL",
            "message": "",
            "details": {}
        }
        
        try:
            # Check if we have any valid configuration source
            effective_config = StaticPostgreSQLSmokeTests._get_effective_config(environment, application)
            direct_config = StaticPostgreSQLSmokeTests._load_environment_config()
            config_file_exists, config_data = StaticPostgreSQLSmokeTests._load_config_file(environment, application)
            
            # We should have at least one configuration source
            has_env_config = bool(direct_config)
            has_file_config = config_file_exists and config_data is not None
            
            if not (has_env_config or has_file_config):
                result["message"] = "Either environment variables (POSTGRES_HOST, etc.) or configuration file should be available"
                return result
            
            if effective_config is None:
                env = environment or StaticPostgreSQLSmokeTests._DEFAULT_ENVIRONMENT
                app = application or StaticPostgreSQLSmokeTests._DEFAULT_APPLICATION
                result["message"] = f"No valid PostgreSQL configuration found for environment '{env}' and application '{app}'"
                return result
            
            result["status"] = "PASS"
            result["message"] = "Environment setup validation successful"
            result["details"] = {
                "has_env_config": has_env_config,
                "has_file_config": has_file_config,
                "config_source": "environment" if has_env_config else "file"
            }
            
        except Exception as e:
            result["message"] = f"Environment setup test failed: {str(e)}"
        
        return result
    
    @staticmethod
    def test_configuration_availability(environment: str = None, application: str = None) -> Dict[str, Any]:
        """
        🧪 STATIC TEST: Configuration Availability
        
        Test that PostgreSQL configuration is available and complete.
        Returns test result with status and details.
        """
        result = {
            "test_name": "Configuration Availability",
            "status": "FAIL",
            "message": "",
            "details": {}
        }
        
        try:
            effective_config = StaticPostgreSQLSmokeTests._get_effective_config(environment, application)
            
            if effective_config is None:
                result["message"] = "PostgreSQL configuration must be available"
                return result
            
            # Validate required configuration fields
            if "username" in effective_config and "password" in effective_config:
                # Direct credentials configuration
                required_fields = ["host", "port", "database", "schema", "username", "password"]
            else:
                # Environment variable based credentials
                required_fields = ["host", "port", "database", "schema", "username_env_var", "password_env_var"]
            
            missing_fields = []
            for field in required_fields:
                if field not in effective_config:
                    missing_fields.append(field)
            
            if missing_fields:
                result["message"] = f"Missing required fields: {', '.join(missing_fields)}"
                return result
            
            result["status"] = "PASS"
            result["message"] = "Configuration availability validation successful"
            result["details"] = {
                "config_fields": list(effective_config.keys()),
                "credential_type": "direct" if "username" in effective_config else "env_var"
            }
            
        except Exception as e:
            result["message"] = f"Configuration availability test failed: {str(e)}"
        
        return result
    
    @staticmethod
    def test_environment_credentials(environment: str = None, application: str = None) -> Dict[str, Any]:
        """
        🧪 STATIC TEST: Environment Credentials Validation
        
        Test that database credentials are valid and accessible.
        Returns test result with status and details.
        """
        result = {
            "test_name": "Environment Credentials Validation",
            "status": "FAIL",
            "message": "",
            "details": {}
        }
        
        try:
            effective_config = StaticPostgreSQLSmokeTests._get_effective_config(environment, application)
            
            if effective_config is None:
                result["message"] = "Configuration must be available for credential validation"
                return result
            
            # Get credentials based on configuration type
            if "username" in effective_config and "password" in effective_config:
                # Direct credentials
                username = effective_config["username"]
                password = effective_config["password"]
                credential_source = "direct"
            else:
                # Environment variable credentials
                username_env = effective_config.get("username_env_var", "POSTGRES_USERNAME")
                password_env = effective_config.get("password_env_var", "POSTGRES_PASSWORD")
                
                username = os.environ.get(username_env)
                password = os.environ.get(password_env)
                credential_source = f"env_vars:{username_env},{password_env}"
                
                if not username or not password:
                    result["message"] = f"Credentials not found in environment variables: {username_env}, {password_env}"
                    return result
            
            # Validate credentials are not empty
            if not username or not password:
                result["message"] = "Username and password must not be empty"
                return result
            
            result["status"] = "PASS"
            result["message"] = "Environment credentials validation successful"
            result["details"] = {
                "credential_source": credential_source,
                "username_available": bool(username),
                "password_available": bool(password)
            }
            
        except Exception as e:
            result["message"] = f"Environment credentials test failed: {str(e)}"
        
        return result
    
    @staticmethod
    def test_postgresql_connection(environment: str = None, application: str = None) -> Dict[str, Any]:
        """
        🧪 STATIC TEST: PostgreSQL Connection
        
        Test basic database connection functionality.
        Returns test result with status and details.
        """
        result = {
            "test_name": "PostgreSQL Connection Test",
            "status": "FAIL",
            "message": "",
            "details": {}
        }
        
        connector = None
        start_time = time.time()
        
        try:
            effective_config = StaticPostgreSQLSmokeTests._get_effective_config(environment, application)
            
            if effective_config is None:
                result["message"] = "Configuration must be available for connection test"
                return result
            
            # Create connector and test connection
            connector = PostgreSQLConnector()
            connection_successful = connector.connect(
                host=effective_config["host"],
                port=effective_config["port"],
                database=effective_config["database"],
                schema=effective_config["schema"],
                username=effective_config.get("username"),
                password=effective_config.get("password"),
                username_env_var=effective_config.get("username_env_var"),
                password_env_var=effective_config.get("password_env_var")
            )
            
            connection_time = time.time() - start_time
            
            if not connection_successful:
                result["message"] = "Failed to establish PostgreSQL connection"
                result["details"]["connection_time"] = connection_time
                return result
            
            # Test basic connection properties
            is_connected = connector.is_connected()
            if not is_connected:
                result["message"] = "Connection established but is_connected() returned False"
                return result
            
            result["status"] = "PASS"
            result["message"] = "PostgreSQL connection test successful"
            result["details"] = {
                "connection_time": connection_time,
                "host": effective_config["host"],
                "port": effective_config["port"],
                "database": effective_config["database"],
                "schema": effective_config["schema"]
            }
            
        except Exception as e:
            connection_time = time.time() - start_time
            result["message"] = f"PostgreSQL connection test failed: {str(e)}"
            result["details"]["connection_time"] = connection_time
        finally:
            if connector:
                try:
                    connector.disconnect()
                except:
                    pass
        
        return result
    
    @staticmethod
    def test_postgresql_basic_queries(environment: str = None, application: str = None) -> Dict[str, Any]:
        """
        🧪 STATIC TEST: PostgreSQL Basic Queries
        
        Test basic database query functionality.
        Returns test result with status and details.
        """
        result = {
            "test_name": "PostgreSQL Basic Queries Test",
            "status": "FAIL",
            "message": "",
            "details": {}
        }
        
        connector = None
        start_time = time.time()
        
        try:
            effective_config = StaticPostgreSQLSmokeTests._get_effective_config(environment, application)
            
            if effective_config is None:
                result["message"] = "Configuration must be available for query test"
                return result
            
            # Create connector and connect
            connector = PostgreSQLConnector()
            connection_successful = connector.connect(
                host=effective_config["host"],
                port=effective_config["port"],
                database=effective_config["database"],
                schema=effective_config["schema"],
                username=effective_config.get("username"),
                password=effective_config.get("password"),
                username_env_var=effective_config.get("username_env_var"),
                password_env_var=effective_config.get("password_env_var")
            )
            
            if not connection_successful:
                result["message"] = "Failed to establish connection for query test"
                return result
            
            # Test basic queries
            queries_executed = []
            
            # Test 1: SELECT version
            version_result = connector.execute_query("SELECT version()")
            if version_result and len(version_result) > 0:
                queries_executed.append({"query": "SELECT version()", "rows": len(version_result)})
            
            # Test 2: SELECT current_database
            db_result = connector.execute_query("SELECT current_database()")
            if db_result and len(db_result) > 0:
                queries_executed.append({"query": "SELECT current_database()", "rows": len(db_result)})
            
            # Test 3: SELECT current_timestamp
            time_result = connector.execute_query("SELECT current_timestamp")
            if time_result and len(time_result) > 0:
                queries_executed.append({"query": "SELECT current_timestamp", "rows": len(time_result)})
            
            query_time = time.time() - start_time
            
            if len(queries_executed) < 3:
                result["message"] = f"Only {len(queries_executed)}/3 basic queries executed successfully"
                result["details"] = {"queries_executed": queries_executed, "query_time": query_time}
                return result
            
            result["status"] = "PASS"
            result["message"] = "PostgreSQL basic queries test successful"
            result["details"] = {
                "queries_executed": queries_executed,
                "query_time": query_time,
                "total_queries": len(queries_executed)
            }
            
        except Exception as e:
            query_time = time.time() - start_time
            result["message"] = f"PostgreSQL basic queries test failed: {str(e)}"
            result["details"]["query_time"] = query_time
        finally:
            if connector:
                try:
                    connector.disconnect()
                except:
                    pass
        
        return result
    
    @staticmethod
    def test_postgresql_connection_performance(environment: str = None, application: str = None) -> Dict[str, Any]:
        """
        🧪 STATIC TEST: PostgreSQL Connection Performance
        
        Test database connection performance and response time.
        Returns test result with status and details.
        """
        result = {
            "test_name": "PostgreSQL Connection Performance Test",
            "status": "FAIL",
            "message": "",
            "details": {}
        }
        
        connector = None
        
        try:
            effective_config = StaticPostgreSQLSmokeTests._get_effective_config(environment, application)
            
            if effective_config is None:
                result["message"] = "Configuration must be available for performance test"
                return result
            
            # Measure connection time
            connection_start = time.time()
            connector = PostgreSQLConnector()
            connection_successful = connector.connect(
                host=effective_config["host"],
                port=effective_config["port"],
                database=effective_config["database"],
                schema=effective_config["schema"],
                username=effective_config.get("username"),
                password=effective_config.get("password"),
                username_env_var=effective_config.get("username_env_var"),
                password_env_var=effective_config.get("password_env_var")
            )
            connection_time = time.time() - connection_start
            
            if not connection_successful:
                result["message"] = "Failed to establish connection for performance test"
                result["details"]["connection_time"] = connection_time
                return result
            
            # Measure query performance
            query_start = time.time()
            query_result = connector.execute_query("SELECT 1 as test_query")
            query_time = time.time() - query_start
            
            total_time = connection_time + query_time
            
            # Check performance thresholds
            performance_status = "GOOD"
            if total_time > StaticPostgreSQLSmokeTests._PERFORMANCE_THRESHOLD_SECONDS:
                performance_status = "SLOW"
            
            if not query_result or len(query_result) == 0:
                result["message"] = "Performance test query failed to return results"
                return result
            
            result["status"] = "PASS"
            result["message"] = f"PostgreSQL connection performance test successful - {performance_status}"
            result["details"] = {
                "connection_time": connection_time,
                "query_time": query_time,
                "total_time": total_time,
                "performance_status": performance_status,
                "threshold": StaticPostgreSQLSmokeTests._PERFORMANCE_THRESHOLD_SECONDS,
                "query_result_count": len(query_result)
            }
            
        except Exception as e:
            result["message"] = f"PostgreSQL connection performance test failed: {str(e)}"
        finally:
            if connector:
                try:
                    connector.disconnect()
                except:
                    pass
        
        return result
    
    @staticmethod
    def run_all_smoke_tests(environment: str = None, application: str = None) -> Dict[str, Any]:
        """
        🧪 STATIC METHOD: Run All Smoke Tests
        
        Execute all smoke tests and return comprehensive results.
        Returns aggregated test results with summary.
        """
        start_time = time.time()
        
        # Define all smoke test methods
        smoke_tests = [
            StaticPostgreSQLSmokeTests.test_environment_setup,
            StaticPostgreSQLSmokeTests.test_configuration_availability,
            StaticPostgreSQLSmokeTests.test_environment_credentials,
            StaticPostgreSQLSmokeTests.test_postgresql_connection,
            StaticPostgreSQLSmokeTests.test_postgresql_basic_queries,
            StaticPostgreSQLSmokeTests.test_postgresql_connection_performance
        ]
        
        results = []
        passed = 0
        failed = 0
        
        # Execute all tests
        for test_method in smoke_tests:
            try:
                test_result = test_method(environment, application)
                results.append(test_result)
                
                if test_result["status"] == "PASS":
                    passed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                error_result = {
                    "test_name": f"{test_method.__name__}",
                    "status": "FAIL",
                    "message": f"Test execution error: {str(e)}",
                    "details": {}
                }
                results.append(error_result)
                failed += 1
        
        total_time = time.time() - start_time
        total_tests = len(results)
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "execution_summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "success_rate": success_rate,
                "total_time": total_time,
                "environment": environment or StaticPostgreSQLSmokeTests._DEFAULT_ENVIRONMENT,
                "application": application or StaticPostgreSQLSmokeTests._DEFAULT_APPLICATION
            },
            "test_results": results
        }
        
        return summary
    
    @staticmethod
    def get_test_info() -> Dict[str, Any]:
        """
        📋 STATIC METHOD: Get Test Information
        
        Returns information about available tests and class configuration.
        """
        return {
            "class_name": "StaticPostgreSQLSmokeTests",
            "class_type": "IMMUTABLE_STATIC",
            "version": "1.0.0",
            "default_environment": StaticPostgreSQLSmokeTests._DEFAULT_ENVIRONMENT,
            "default_application": StaticPostgreSQLSmokeTests._DEFAULT_APPLICATION,
            "performance_threshold": StaticPostgreSQLSmokeTests._PERFORMANCE_THRESHOLD_SECONDS,
            "available_tests": [
                "test_environment_setup",
                "test_configuration_availability", 
                "test_environment_credentials",
                "test_postgresql_connection",
                "test_postgresql_basic_queries",
                "test_postgresql_connection_performance"
            ],
            "utility_methods": [
                "run_all_smoke_tests",
                "get_test_info"
            ]
        }


# Prevent module-level modifications
__all__ = ['StaticPostgreSQLSmokeTests']