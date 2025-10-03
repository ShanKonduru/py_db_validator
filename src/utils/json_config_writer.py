"""
Static utility class for writing database connection JSON configurations
"""
import json
from pathlib import Path
from typing import Dict, Any
from .database_connection import DatabaseConnection
from .json_config_reader import JsonConfigReader


class JsonConfigWriter:
    """Static utility class for writing database connection JSON configurations"""
    
    @staticmethod
    def write_config_file(config_data: Dict[str, Any], file_path: str, backup: bool = True) -> None:
        """
        Write configuration data to JSON file
        
        Args:
            config_data: Configuration dictionary to write
            file_path: Path to write the JSON file
            backup: Whether to create backup of existing file
            
        Raises:
            ValueError: If config_data is invalid
            OSError: If file cannot be written
        """
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary")
        
        if not file_path:
            raise ValueError("File path cannot be empty")
        
        # Validate configuration structure
        errors = JsonConfigReader.validate_config_structure(config_data)
        if errors:
            raise ValueError(f"Invalid configuration structure: {'; '.join(errors)}")
        
        path = Path(file_path)
        
        # Create backup if file exists and backup is requested
        if backup and path.exists():
            backup_path = path.with_suffix(f"{path.suffix}.backup")
            JsonConfigWriter._create_backup(path, backup_path)
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, indent=2, ensure_ascii=False, sort_keys=True)
        except OSError as e:
            raise OSError(f"Failed to write configuration file {file_path}: {str(e)}")
    
    @staticmethod
    def add_environment(config_data: Dict[str, Any], environment: str, applications: Dict[str, DatabaseConnection]) -> Dict[str, Any]:
        """
        Add new environment to configuration
        
        Args:
            config_data: Existing configuration dictionary
            environment: Environment name to add
            applications: Dictionary of application configurations
            
        Returns:
            Updated configuration dictionary
            
        Raises:
            ValueError: If environment already exists or data is invalid
        """
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary")
        
        if not environment:
            raise ValueError("Environment name cannot be empty")
        
        if not isinstance(applications, dict):
            raise ValueError("Applications must be a dictionary")
        
        if not applications:
            raise ValueError("Applications dictionary cannot be empty")
        
        # Initialize environments section if it doesn't exist
        if "environments" not in config_data:
            config_data["environments"] = {}
        
        environments = config_data["environments"]
        if environment in environments:
            raise ValueError(f"Environment '{environment}' already exists")
        
        # Convert DatabaseConnection objects to dictionaries
        env_config = {}
        for app_name, app_connection in applications.items():
            if isinstance(app_connection, DatabaseConnection):
                env_config[app_name] = app_connection.to_dict()
            elif isinstance(app_connection, dict):
                env_config[app_name] = app_connection
            else:
                raise ValueError(f"Invalid application configuration for '{app_name}'")
        
        environments[environment] = env_config
        return config_data
    
    @staticmethod
    def add_application(config_data: Dict[str, Any], environment: str, application: str, connection: DatabaseConnection) -> Dict[str, Any]:
        """
        Add new application to existing environment
        
        Args:
            config_data: Existing configuration dictionary
            environment: Environment name
            application: Application name to add
            connection: Database connection configuration
            
        Returns:
            Updated configuration dictionary
            
        Raises:
            KeyError: If environment doesn't exist
            ValueError: If application already exists or data is invalid
        """
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary")
        
        if "environments" not in config_data:
            raise KeyError(f"Environment '{environment}' not found in configuration")
        
        environments = config_data["environments"]
        if environment not in environments:
            raise KeyError(f"Environment '{environment}' not found in configuration")
        
        if not application:
            raise ValueError("Application name cannot be empty")
        
        if not isinstance(connection, DatabaseConnection):
            raise ValueError("Connection must be a DatabaseConnection object")
        
        env_data = environments[environment]
        if application in env_data:
            raise ValueError(f"Application '{application}' already exists in environment '{environment}'")
        
        env_data[application] = connection.to_dict()
        return config_data
    
    @staticmethod
    def remove_environment(config_data: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """
        Remove environment from configuration
        
        Args:
            config_data: Existing configuration dictionary
            environment: Environment name to remove
            
        Returns:
            Updated configuration dictionary
            
        Raises:
            KeyError: If environment doesn't exist
        """
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary")
        
        if "environments" not in config_data:
            raise KeyError(f"Environment '{environment}' not found in configuration")
        
        environments = config_data["environments"]
        if environment not in environments:
            raise KeyError(f"Environment '{environment}' not found in configuration")
        
        del environments[environment]
        return config_data
    
    @staticmethod
    def remove_application(config_data: Dict[str, Any], environment: str, application: str) -> Dict[str, Any]:
        """
        Remove application from environment
        
        Args:
            config_data: Existing configuration dictionary
            environment: Environment name
            application: Application name to remove
            
        Returns:
            Updated configuration dictionary
            
        Raises:
            KeyError: If environment or application doesn't exist
        """
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a dictionary")
        
        if "environments" not in config_data:
            raise KeyError(f"Environment '{environment}' not found in configuration")
        
        environments = config_data["environments"]
        if environment not in environments:
            raise KeyError(f"Environment '{environment}' not found in configuration")
        
        env_data = environments[environment]
        if application not in env_data:
            raise KeyError(f"Application '{application}' not found in environment '{environment}'")
        
        del env_data[application]
        return config_data
    
    @staticmethod
    def _create_backup(source_path: Path, backup_path: Path) -> None:
        """
        Create backup of existing file
        
        Args:
            source_path: Path to source file
            backup_path: Path for backup file
        """
        try:
            import shutil
            shutil.copy2(source_path, backup_path)
        except OSError:
            # Backup failed, but continue with write operation
            pass