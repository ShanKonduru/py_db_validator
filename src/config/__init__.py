"""
Database Configuration Loader
Loads database connection configurations from JSON and environment variables
"""
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    db_type: str
    host: str
    port: int
    username: str
    password: str
    connection_timeout: int = 30
    query_timeout: int = 300
    max_connections: int = 10
    
    # Database-specific fields
    service_name: Optional[str] = None  # Oracle
    database: Optional[str] = None      # PostgreSQL, SQL Server
    schema: Optional[str] = None        # All databases
    driver: Optional[str] = None        # SQL Server
    driver_options: Optional[Dict[str, Any]] = None


@dataclass
class EnvironmentConfig:
    """Environment configuration containing multiple application databases"""
    name: str
    description: str
    applications: Dict[str, DatabaseConfig]


class DatabaseConfigLoader:
    """Loads and manages database configurations"""
    
    def __init__(self, config_file: str = "config/database_connections.json"):
        """
        Initialize the configuration loader
        
        Args:
            config_file: Path to the JSON configuration file
        """
        self.config_file = Path(config_file)
        self.config_data: Dict = {}
        self.environments: Dict[str, EnvironmentConfig] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config_data = json.load(f)
            self._parse_environments()
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _parse_environments(self) -> None:
        """Parse environments from configuration data"""
        environments_data = self.config_data.get("environments", {})
        defaults = self.config_data.get("connection_defaults", {})
        
        for env_name, env_data in environments_data.items():
            applications = {}
            
            for app_name, app_data in env_data.get("applications", {}).items():
                # Get credentials from environment variables
                username = self._get_env_var(app_data.get("username_env_var"))
                password = self._get_env_var(app_data.get("password_env_var"))
                
                # Apply defaults for database type
                db_type = app_data.get("db_type")
                type_defaults = defaults.get(db_type, {})
                
                # Create database configuration
                db_config = DatabaseConfig(
                    db_type=db_type,
                    host=app_data.get("host"),
                    port=app_data.get("port", type_defaults.get("port")),
                    username=username,
                    password=password,
                    connection_timeout=app_data.get("connection_timeout", type_defaults.get("connection_timeout", 30)),
                    query_timeout=app_data.get("query_timeout", type_defaults.get("query_timeout", 300)),
                    max_connections=app_data.get("max_connections", type_defaults.get("max_connections", 10)),
                    service_name=app_data.get("service_name"),
                    database=app_data.get("database"),
                    schema=app_data.get("schema"),
                    driver=app_data.get("driver", type_defaults.get("driver")),
                    driver_options=app_data.get("driver_options", type_defaults.get("driver_options"))
                )
                
                applications[app_name] = db_config
            
            self.environments[env_name] = EnvironmentConfig(
                name=env_data.get("name", env_name),
                description=env_data.get("description", ""),
                applications=applications
            )
    
    def _get_env_var(self, var_name: str) -> str:
        """Get environment variable value"""
        if not var_name:
            return ""
        
        value = os.getenv(var_name)
        if not value:
            raise ValueError(f"Environment variable not found: {var_name}")
        return value
    
    def get_environments(self) -> List[str]:
        """Get list of available environments"""
        return list(self.environments.keys())
    
    def get_applications(self, environment: str) -> List[str]:
        """Get list of applications for an environment"""
        if environment not in self.environments:
            raise ValueError(f"Environment not found: {environment}")
        return list(self.environments[environment].applications.keys())
    
    def get_database_config(self, environment: str, application: str) -> DatabaseConfig:
        """
        Get database configuration for specific environment and application
        
        Args:
            environment: Environment name (DEV, QA, ACC, NP1, PRE_PROD)
            application: Application name (RED, MREE, SADB, TPS, MDW)
            
        Returns:
            DatabaseConfig object with connection details
            
        Raises:
            ValueError: If environment or application not found
        """
        if environment not in self.environments:
            raise ValueError(f"Environment not found: {environment}. Available: {self.get_environments()}")
        
        env_config = self.environments[environment]
        if application not in env_config.applications:
            raise ValueError(f"Application not found: {application}. Available in {environment}: {self.get_applications(environment)}")
        
        return env_config.applications[application]
    
    def get_environment_config(self, environment: str) -> EnvironmentConfig:
        """Get full environment configuration"""
        if environment not in self.environments:
            raise ValueError(f"Environment not found: {environment}")
        return self.environments[environment]
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """
        Validate configuration for missing credentials or invalid settings
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "missing_credentials": [],
            "invalid_configs": [],
            "warnings": []
        }
        
        for env_name, env_config in self.environments.items():
            for app_name, db_config in env_config.applications.items():
                config_id = f"{env_name}.{app_name}"
                
                # Check for missing credentials
                if not db_config.username:
                    results["missing_credentials"].append(f"{config_id}: username")
                if not db_config.password:
                    results["missing_credentials"].append(f"{config_id}: password")
                
                # Check for invalid configurations
                if not db_config.host:
                    results["invalid_configs"].append(f"{config_id}: missing host")
                if not db_config.port or db_config.port <= 0:
                    results["invalid_configs"].append(f"{config_id}: invalid port")
                
                # Database-specific validations
                if db_config.db_type == "oracle" and not db_config.service_name:
                    results["invalid_configs"].append(f"{config_id}: Oracle requires service_name")
                if db_config.db_type in ["postgresql", "sqlserver"] and not db_config.database:
                    results["invalid_configs"].append(f"{config_id}: {db_config.db_type} requires database name")
                
                # Warnings for timeouts
                if db_config.connection_timeout > 120:
                    results["warnings"].append(f"{config_id}: high connection timeout ({db_config.connection_timeout}s)")
        
        return results
    
    def get_supported_databases(self) -> Dict[str, str]:
        """Get mapping of applications to database types"""
        return self.config_data.get("metadata", {}).get("supported_applications", {})
    
    def get_config_metadata(self) -> Dict[str, Any]:
        """Get configuration metadata"""
        return self.config_data.get("metadata", {})