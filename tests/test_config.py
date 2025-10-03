"""
Unit tests for database configuration loader
"""
import json
import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from src.config import DatabaseConfig, EnvironmentConfig, DatabaseConfigLoader


class TestDatabaseConfig:
    """Test DatabaseConfig dataclass"""
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_database_config_creation(self):
        """Test creating DatabaseConfig with required fields"""
        config = DatabaseConfig(
            db_type="oracle",
            host="localhost",
            port=1521,
            username="user",
            password="pass"
        )
        
        assert config.db_type == "oracle"
        assert config.host == "localhost"
        assert config.port == 1521
        assert config.username == "user"
        assert config.password == "pass"
        assert config.connection_timeout == 30  # Default
        assert config.query_timeout == 300  # Default
        assert config.max_connections == 10  # Default
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_database_config_with_optional_fields(self):
        """Test creating DatabaseConfig with optional fields"""
        config = DatabaseConfig(
            db_type="oracle",
            host="localhost",
            port=1521,
            username="user",
            password="pass",
            service_name="testdb",
            database="testdb",
            schema="test_schema",
            driver="oracle.jdbc.driver",
            driver_options={"autocommit": True},
            connection_timeout=60,
            query_timeout=600,
            max_connections=20
        )
        
        assert config.service_name == "testdb"
        assert config.database == "testdb"
        assert config.schema == "test_schema"
        assert config.driver == "oracle.jdbc.driver"
        assert config.driver_options == {"autocommit": True}
        assert config.connection_timeout == 60
        assert config.query_timeout == 600
        assert config.max_connections == 20


class TestEnvironmentConfig:
    """Test EnvironmentConfig dataclass"""
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_environment_config_creation(self):
        """Test creating EnvironmentConfig"""
        db_config = DatabaseConfig(
            db_type="oracle",
            host="localhost",
            port=1521,
            username="user",
            password="pass"
        )
        
        env_config = EnvironmentConfig(
            name="DEV",
            description="Development Environment",
            applications={"RED": db_config}
        )
        
        assert env_config.name == "DEV"
        assert env_config.description == "Development Environment"
        assert "RED" in env_config.applications
        assert env_config.applications["RED"] == db_config


class TestDatabaseConfigLoader:
    """Test DatabaseConfigLoader class"""
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data for testing"""
        return {
            "environments": {
                "DEV": {
                    "name": "Development",
                    "description": "Development environment",
                    "applications": {
                        "RED": {
                            "db_type": "oracle",
                            "host": "dev-oracle.example.com",
                            "port": 1521,
                            "service_name": "reddev",
                            "schema": "red_schema",
                            "username_env_var": "DEV_RED_USERNAME",
                            "password_env_var": "DEV_RED_PASSWORD"
                        },
                        "TPS": {
                            "db_type": "postgresql",
                            "host": "dev-postgres.example.com",
                            "port": 5432,
                            "database": "tpsdev",
                            "username_env_var": "DEV_TPS_USERNAME",
                            "password_env_var": "DEV_TPS_PASSWORD"
                        }
                    }
                },
                "QA": {
                    "name": "Quality Assurance",
                    "description": "QA environment",
                    "applications": {
                        "RED": {
                            "db_type": "oracle",
                            "host": "qa-oracle.example.com",
                            "port": 1521,
                            "service_name": "redqa",
                            "schema": "red_schema",
                            "username_env_var": "QA_RED_USERNAME",
                            "password_env_var": "QA_RED_PASSWORD",
                            "connection_timeout": 60
                        }
                    }
                }
            },
            "connection_defaults": {
                "oracle": {
                    "port": 1521,
                    "connection_timeout": 30,
                    "query_timeout": 300,
                    "max_connections": 10
                },
                "postgresql": {
                    "port": 5432,
                    "connection_timeout": 30,
                    "query_timeout": 300,
                    "max_connections": 10
                }
            },
            "metadata": {
                "supported_applications": {
                    "RED": "oracle",
                    "TPS": "postgresql"
                },
                "version": "1.0"
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config_data):
        """Create temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config_data, f)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        try:
            os.unlink(temp_path)
        except OSError:
            pass
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_loader_initialization_success(self, temp_config_file):
        """Test successful initialization of DatabaseConfigLoader"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'dev_red_user',
            'DEV_RED_PASSWORD': 'dev_red_pass',
            'DEV_TPS_USERNAME': 'dev_tps_user',
            'DEV_TPS_PASSWORD': 'dev_tps_pass',
            'QA_RED_USERNAME': 'qa_red_user',
            'QA_RED_PASSWORD': 'qa_red_pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            assert len(loader.environments) == 2
            assert "DEV" in loader.environments
            assert "QA" in loader.environments
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_loader_file_not_found(self):
        """Test initialization with non-existent config file"""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            DatabaseConfigLoader("nonexistent_file.json")
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_loader_invalid_json(self, tmp_path):
        """Test initialization with invalid JSON file"""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid json")
        
        with pytest.raises(ValueError, match="Invalid JSON in configuration file"):
            DatabaseConfigLoader(str(invalid_file))
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_environments(self, temp_config_file):
        """Test getting list of environments"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            environments = loader.get_environments()
            
            assert set(environments) == {"DEV", "QA"}
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_applications(self, temp_config_file):
        """Test getting list of applications for environment"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            dev_apps = loader.get_applications("DEV")
            assert set(dev_apps) == {"RED", "TPS"}
            
            qa_apps = loader.get_applications("QA")
            assert set(qa_apps) == {"RED"}
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_applications_invalid_environment(self, temp_config_file):
        """Test getting applications for non-existent environment"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            with pytest.raises(ValueError, match="Environment not found: NONEXISTENT"):
                loader.get_applications("NONEXISTENT")
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_database_config(self, temp_config_file):
        """Test getting database configuration"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'dev_red_user',
            'DEV_RED_PASSWORD': 'dev_red_pass',
            'DEV_TPS_USERNAME': 'dev_tps_user',
            'DEV_TPS_PASSWORD': 'dev_tps_pass',
            'QA_RED_USERNAME': 'qa_red_user',
            'QA_RED_PASSWORD': 'qa_red_pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            config = loader.get_database_config("DEV", "RED")
            
            assert config.db_type == "oracle"
            assert config.host == "dev-oracle.example.com"
            assert config.port == 1521
            assert config.service_name == "reddev"
            assert config.schema == "red_schema"
            assert config.username == "dev_red_user"
            assert config.password == "dev_red_pass"
            assert config.connection_timeout == 30  # From defaults
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_database_config_invalid_environment(self, temp_config_file):
        """Test getting database config for non-existent environment"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            with pytest.raises(ValueError, match="Environment not found: NONEXISTENT"):
                loader.get_database_config("NONEXISTENT", "RED")
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_database_config_invalid_application(self, temp_config_file):
        """Test getting database config for non-existent application"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            with pytest.raises(ValueError, match="Application not found: NONEXISTENT"):
                loader.get_database_config("DEV", "NONEXISTENT")
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_environment_config(self, temp_config_file):
        """Test getting full environment configuration"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            env_config = loader.get_environment_config("DEV")
            
            assert env_config.name == "Development"
            assert env_config.description == "Development environment"
            assert len(env_config.applications) == 2
            assert "RED" in env_config.applications
            assert "TPS" in env_config.applications
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_environment_config_invalid(self, temp_config_file):
        """Test getting environment config for non-existent environment"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            with pytest.raises(ValueError, match="Environment not found: NONEXISTENT"):
                loader.get_environment_config("NONEXISTENT")
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_missing_environment_variable(self, temp_config_file):
        """Test initialization with missing environment variables"""
        # Only provide some environment variables
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass'
            # Missing DEV_TPS_USERNAME, DEV_TPS_PASSWORD, QA_RED_USERNAME, QA_RED_PASSWORD
        }, clear=True):
            with pytest.raises(ValueError, match="Environment variable not found"):
                DatabaseConfigLoader(temp_config_file)
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_validate_configuration_valid(self, temp_config_file):
        """Test validation of valid configuration"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            results = loader.validate_configuration()
            
            assert len(results["missing_credentials"]) == 0
            assert len(results["invalid_configs"]) == 0
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_configuration_missing_credentials(self, temp_config_file):
        """Test validation with missing credentials"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            # Manually set empty credentials to test validation
            loader.environments["DEV"].applications["RED"].username = ""
            loader.environments["DEV"].applications["TPS"].password = ""
            
            results = loader.validate_configuration()
            
            assert "DEV.RED: username" in results["missing_credentials"]
            assert "DEV.TPS: password" in results["missing_credentials"]
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_supported_databases(self, temp_config_file):
        """Test getting supported databases mapping"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            supported = loader.get_supported_databases()
            
            assert supported["RED"] == "oracle"
            assert supported["TPS"] == "postgresql"
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_config_metadata(self, temp_config_file):
        """Test getting configuration metadata"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            metadata = loader.get_config_metadata()
            
            assert metadata["version"] == "1.0"
            assert "supported_applications" in metadata
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_defaults_application(self, temp_config_file):
        """Test that defaults are applied correctly"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            # TPS doesn't specify port, should get default
            tps_config = loader.get_database_config("DEV", "TPS")
            assert tps_config.port == 5432  # PostgreSQL default
            
            # QA RED specifies connection_timeout, should override default
            qa_red_config = loader.get_database_config("QA", "RED")
            assert qa_red_config.connection_timeout == 60  # Overridden value
    
    @pytest.mark.unit
    @pytest.mark.edge
    def test_empty_env_var_name(self, temp_config_file):
        """Test handling of empty environment variable names"""
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass',
            'DEV_TPS_USERNAME': 'user',
            'DEV_TPS_PASSWORD': 'pass',
            'QA_RED_USERNAME': 'user',
            'QA_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(temp_config_file)
            
            # Test _get_env_var with empty string
            result = loader._get_env_var("")
            assert result == ""
    
    @pytest.mark.unit
    @pytest.mark.edge
    def test_config_without_environments(self, tmp_path):
        """Test configuration file without environments section"""
        config_data = {"metadata": {"version": "1.0"}}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        loader = DatabaseConfigLoader(str(config_file))
        
        assert len(loader.environments) == 0
        assert loader.get_environments() == []
    
    @pytest.mark.unit
    @pytest.mark.edge
    def test_config_without_defaults(self, tmp_path):
        """Test configuration file without connection defaults"""
        config_data = {
            "environments": {
                "DEV": {
                    "applications": {
                        "RED": {
                            "db_type": "oracle",
                            "host": "localhost",
                            "port": 1521,
                            "service_name": "testdb",
                            "username_env_var": "DEV_RED_USERNAME",
                            "password_env_var": "DEV_RED_PASSWORD"
                        }
                    }
                }
            }
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))
        
        with patch.dict(os.environ, {
            'DEV_RED_USERNAME': 'user',
            'DEV_RED_PASSWORD': 'pass'
        }):
            loader = DatabaseConfigLoader(str(config_file))
            config = loader.get_database_config("DEV", "RED")
            
            # Should use built-in defaults
            assert config.connection_timeout == 30
            assert config.query_timeout == 300
            assert config.max_connections == 10