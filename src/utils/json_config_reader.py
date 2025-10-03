"""
Static utility class for reading database connection JSON configurations
"""
import json
from pathlib import Path
from typing import Dict, Any, List
from .database_connection import DatabaseConnection


class JsonConfigReader:
    """Static utility class for reading database connection JSON configurations"""
    
    @staticmethod
    def read_config_file(file_path: str) -> Dict[str, Any]:
        """
        Read and parse JSON configuration file
        
        Args:
            file_path: Path to the JSON configuration file
            
        Returns:
            Parsed JSON data as dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If file is empty or invalid format
        """
        if not file_path:
            raise ValueError("File path cannot be empty")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        if path.stat().st_size == 0:
            raise ValueError(f"Configuration file is empty: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            if not isinstance(data, dict):
                raise ValueError("Configuration file must contain a JSON object")
                
            return data
            
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in {file_path}: {str(e)}", e.doc, e.pos)
    
    @staticmethod
    def get_environments(config_data: Dict[str, Any]) -> List[str]:
        """
        Get list of available environments from configuration
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            List of environment names
        """
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary")
        
        environments = config_data.get("environments", {})
        if not isinstance(environments, dict):
            raise ValueError("Environments section must be a dictionary")
        
        return list(environments.keys())
    
    @staticmethod
    def get_applications(config_data: Dict[str, Any], environment: str) -> List[str]:
        """
        Get list of applications for a specific environment
        
        Args:
            config_data: Configuration dictionary
            environment: Environment name
            
        Returns:
            List of application names
            
        Raises:
            KeyError: If environment doesn't exist
        """
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary")
        
        environments = config_data.get("environments", {})
        if environment not in environments:
            raise KeyError(f"Environment '{environment}' not found in configuration")
        
        env_data = environments[environment]
        if not isinstance(env_data, dict):
            raise ValueError(f"Environment '{environment}' data must be a dictionary")
        
        return list(env_data.keys())
    
    @staticmethod
    def get_connection_config(config_data: Dict[str, Any], environment: str, application: str) -> DatabaseConnection:
        """
        Get database connection configuration for specific environment and application
        
        Args:
            config_data: Configuration dictionary
            environment: Environment name
            application: Application name
            
        Returns:
            DatabaseConnection object
            
        Raises:
            KeyError: If environment or application doesn't exist
            ValueError: If configuration is invalid
        """
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary")
        
        environments = config_data.get("environments", {})
        if environment not in environments:
            raise KeyError(f"Environment '{environment}' not found in configuration")
        
        env_data = environments[environment]
        if application not in env_data:
            raise KeyError(f"Application '{application}' not found in environment '{environment}'")
        
        app_config = env_data[application]
        if not isinstance(app_config, dict):
            raise ValueError(f"Application '{application}' configuration must be a dictionary")
        
        # Validate required fields
        required_fields = ["db_type", "host", "port", "database"]
        for field in required_fields:
            if field not in app_config:
                raise ValueError(f"Missing required field '{field}' in {environment}.{application} configuration")
        
        return DatabaseConnection.from_dict(app_config)
    
    @staticmethod
    def validate_config_structure(config_data: Dict[str, Any]) -> List[str]:
        """
        Validate the structure of configuration data
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not isinstance(config_data, dict):
            errors.append("Configuration data must be a dictionary")
            return errors
        
        # Check required top-level sections
        if "environments" not in config_data:
            errors.append("Missing required 'environments' section")
            return errors
        
        environments = config_data["environments"]
        if not isinstance(environments, dict):
            errors.append("'environments' section must be a dictionary")
            return errors
        
        if not environments:
            errors.append("'environments' section cannot be empty")
            return errors
        
        # Validate each environment
        for env_name, env_data in environments.items():
            if not isinstance(env_data, dict):
                errors.append(f"Environment '{env_name}' must be a dictionary")
                continue
            
            if not env_data:
                errors.append(f"Environment '{env_name}' cannot be empty")
                continue
            
            # Validate each application in environment
            for app_name, app_config in env_data.items():
                if not isinstance(app_config, dict):
                    errors.append(f"Application '{env_name}.{app_name}' must be a dictionary")
                    continue
                
                # Check required fields
                required_fields = ["db_type", "host", "port", "database"]
                for field in required_fields:
                    if field not in app_config:
                        errors.append(f"Missing required field '{field}' in {env_name}.{app_name}")
                
                # Validate data types
                if "port" in app_config and not isinstance(app_config["port"], int):
                    errors.append(f"Port must be an integer in {env_name}.{app_name}")
                
                if "db_type" in app_config and not isinstance(app_config["db_type"], str):
                    errors.append(f"db_type must be a string in {env_name}.{app_name}")
        
        return errors
    
    @staticmethod
    def get_config_metadata(config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from configuration
        
        Args:
            config_data: Configuration dictionary
            
        Returns:
            Dictionary containing metadata
        """
        metadata = {
            "total_environments": 0,
            "total_applications": 0,
            "database_types": set(),
            "environments": [],
            "applications_per_environment": {}
        }
        
        if not isinstance(config_data, dict) or "environments" not in config_data:
            return metadata
        
        environments = config_data["environments"]
        if not isinstance(environments, dict):
            return metadata
        
        metadata["total_environments"] = len(environments)
        metadata["environments"] = list(environments.keys())
        
        total_apps = 0
        for env_name, env_data in environments.items():
            if isinstance(env_data, dict):
                app_count = len(env_data)
                total_apps += app_count
                metadata["applications_per_environment"][env_name] = app_count
                
                # Collect database types
                for app_config in env_data.values():
                    if isinstance(app_config, dict) and "db_type" in app_config:
                        metadata["database_types"].add(app_config["db_type"])
        
        metadata["total_applications"] = total_apps
        metadata["database_types"] = list(metadata["database_types"])
        
        return metadata