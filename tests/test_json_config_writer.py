"""
Unit tests for JsonConfigWriter utility class
"""
import json
import tempfile
import pytest
from pathlib import Path

from src.utils.json_config_writer import JsonConfigWriter
from src.utils.database_connection import DatabaseConnection


class TestJsonConfigWriter:
    """Test JsonConfigWriter utility class"""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup handled by OS for temp files
    
    @pytest.fixture
    def sample_connection(self):
        """Sample database connection for testing"""
        return DatabaseConnection(
            db_type="oracle",
            host="test-oracle.example.com",
            port=1521,
            database="testdb",
            schema="test_schema",
            username_env="TEST_USERNAME",
            password_env="TEST_PASSWORD"
        )
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            "environments": {
                "DEV": {
                    "RED": {
                        "db_type": "oracle",
                        "host": "dev-oracle.example.com",
                        "port": 1521,
                        "database": "reddev",
                        "schema": "red_schema",
                        "username_env": "DEV_RED_USERNAME",
                        "password_env": "DEV_RED_PASSWORD"
                    }
                }
            }
        }
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_write_config_file_success(self, temp_config_file, sample_config):
        """Test successfully writing configuration to file"""
        JsonConfigWriter.write_config_file(sample_config, temp_config_file)
        
        # Verify file was created and contains correct data
        with open(temp_config_file, 'r') as f:
            saved_config = json.load(f)
        
        assert saved_config == sample_config
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_write_config_file_invalid_config_type(self, temp_config_file):
        """Test writing invalid configuration type"""
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            JsonConfigWriter.write_config_file("not a dict", temp_config_file)
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_write_config_file_empty_path(self, sample_config):
        """Test writing with empty file path"""
        with pytest.raises(ValueError, match="File path cannot be empty"):
            JsonConfigWriter.write_config_file(sample_config, "")
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_write_config_file_invalid_structure(self, temp_config_file):
        """Test writing configuration with invalid structure"""
        invalid_config = {"environments": "not a dict"}
        with pytest.raises(ValueError, match="Invalid configuration structure"):
            JsonConfigWriter.write_config_file(invalid_config, temp_config_file)
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_write_config_file_create_parent_directory(self, sample_config, tmp_path):
        """Test writing config with automatic parent directory creation"""
        config_path = tmp_path / "new_dir" / "config.json"
        JsonConfigWriter.write_config_file(sample_config, str(config_path))
        
        assert config_path.exists()
        with open(config_path, 'r') as f:
            saved_config = json.load(f)
        assert saved_config == sample_config
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_add_environment(self, sample_config):
        """Test adding new environment"""
        applications = {
            "TPS": DatabaseConnection(
                db_type="postgresql",
                host="qa-postgres.example.com",
                port=5432,
                database="tpsqa",
                username_env="QA_TPS_USERNAME",
                password_env="QA_TPS_PASSWORD"
            )
        }
        
        updated_config = JsonConfigWriter.add_environment(sample_config.copy(), "QA", applications)
        
        assert "QA" in updated_config["environments"]
        assert "TPS" in updated_config["environments"]["QA"]
        assert "DEV" in updated_config["environments"]  # Original should still exist
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_environment_existing(self, sample_config):
        """Test adding existing environment"""
        applications = {"RED": DatabaseConnection(
            db_type="oracle",
            host="test.com",
            port=1521,
            database="test"
        )}
        
        with pytest.raises(ValueError, match="Environment 'DEV' already exists"):
            JsonConfigWriter.add_environment(sample_config, "DEV", applications)
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_environment_empty_name(self, sample_config):
        """Test adding environment with empty name"""
        applications = {"RED": DatabaseConnection(
            db_type="oracle",
            host="test.com",
            port=1521,
            database="test"
        )}
        
        with pytest.raises(ValueError, match="Environment name cannot be empty"):
            JsonConfigWriter.add_environment(sample_config, "", applications)
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_environment_invalid_applications_type(self, sample_config):
        """Test adding environment with invalid applications type"""
        with pytest.raises(ValueError, match="Applications must be a dictionary"):
            JsonConfigWriter.add_environment(sample_config, "QA", "not a dict")
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_environment_empty_applications(self, sample_config):
        """Test adding environment with empty applications"""
        with pytest.raises(ValueError, match="Applications dictionary cannot be empty"):
            JsonConfigWriter.add_environment(sample_config, "QA", {})
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_add_environment_missing_environments_section(self):
        """Test adding environment to config without environments section"""
        config = {"other_section": {}}
        applications = {"RED": DatabaseConnection(
            db_type="oracle",
            host="test.com",
            port=1521,
            database="test"
        )}
        
        updated_config = JsonConfigWriter.add_environment(config, "DEV", applications)
        
        assert "environments" in updated_config
        assert "DEV" in updated_config["environments"]
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_add_application(self, sample_config, sample_connection):
        """Test adding new application to environment"""
        updated_config = JsonConfigWriter.add_application(sample_config.copy(), "DEV", "TPS", sample_connection)
        
        assert "TPS" in updated_config["environments"]["DEV"]
        tps_config = updated_config["environments"]["DEV"]["TPS"]
        assert tps_config["db_type"] == "oracle"
        assert tps_config["host"] == "test-oracle.example.com"
        assert tps_config["port"] == 1521
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_application_environment_not_found(self, sample_config, sample_connection):
        """Test adding application to non-existent environment"""
        with pytest.raises(KeyError, match="Environment 'NONEXISTENT' not found"):
            JsonConfigWriter.add_application(sample_config, "NONEXISTENT", "TPS", sample_connection)
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_application_existing(self, sample_config, sample_connection):
        """Test adding existing application to environment"""
        with pytest.raises(ValueError, match="Application 'RED' already exists in environment 'DEV'"):
            JsonConfigWriter.add_application(sample_config, "DEV", "RED", sample_connection)
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_application_invalid_connection_type(self, sample_config):
        """Test adding application with invalid connection type"""
        with pytest.raises(ValueError, match="Connection must be a DatabaseConnection object"):
            JsonConfigWriter.add_application(sample_config, "DEV", "TPS", "not a connection")
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_application_empty_name(self, sample_config, sample_connection):
        """Test adding application with empty name"""
        with pytest.raises(ValueError, match="Application name cannot be empty"):
            JsonConfigWriter.add_application(sample_config, "DEV", "", sample_connection)
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_remove_environment(self, sample_config):
        """Test removing environment"""
        # Add another environment first
        config = sample_config.copy()
        config["environments"]["QA"] = {"RED": {"db_type": "oracle"}}
        
        updated_config = JsonConfigWriter.remove_environment(config, "QA")
        
        assert "QA" not in updated_config["environments"]
        assert "DEV" in updated_config["environments"]  # Other should remain
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_remove_environment_not_found(self, sample_config):
        """Test removing non-existent environment"""
        with pytest.raises(KeyError, match="Environment 'NONEXISTENT' not found"):
            JsonConfigWriter.remove_environment(sample_config, "NONEXISTENT")
    
    @pytest.mark.unit
    @pytest.mark.positive
    def test_remove_application(self, sample_config, sample_connection):
        """Test removing application from environment"""
        # Add another application first
        config = sample_config.copy()
        config = JsonConfigWriter.add_application(config, "DEV", "TPS", sample_connection)
        
        updated_config = JsonConfigWriter.remove_application(config, "DEV", "TPS")
        
        assert "TPS" not in updated_config["environments"]["DEV"]
        assert "RED" in updated_config["environments"]["DEV"]  # Other should remain
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_remove_application_not_found(self, sample_config):
        """Test removing non-existent application"""
        with pytest.raises(KeyError, match="Application 'NONEXISTENT' not found in environment 'DEV'"):
            JsonConfigWriter.remove_application(sample_config, "DEV", "NONEXISTENT")
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_environment_invalid_data(self):
        """Test adding environment with invalid config data"""
        applications = {"RED": DatabaseConnection(
            db_type="oracle",
            host="test.com",
            port=1521,
            database="test"
        )}
        
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            JsonConfigWriter.add_environment("not a dict", "DEV", applications)
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_application_invalid_data(self, sample_connection):
        """Test adding application with invalid config data"""
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            JsonConfigWriter.add_application("not a dict", "DEV", "TPS", sample_connection)
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_remove_environment_invalid_data(self):
        """Test removing environment with invalid config data"""
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            JsonConfigWriter.remove_environment("not a dict", "DEV")
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_remove_application_invalid_data(self):
        """Test removing application with invalid config data"""
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            JsonConfigWriter.remove_application("not a dict", "DEV", "TPS")
    
    @pytest.mark.unit
    @pytest.mark.edge
    def test_add_environment_with_dict_connection(self, sample_config):
        """Test adding environment with dictionary-based connection"""
        applications = {
            "TPS": {
                "db_type": "postgresql",
                "host": "test-postgres.com",
                "port": 5432,
                "database": "testdb"
            }
        }
        
        updated_config = JsonConfigWriter.add_environment(sample_config.copy(), "QA", applications)
        
        assert "QA" in updated_config["environments"]
        assert "TPS" in updated_config["environments"]["QA"]
        assert updated_config["environments"]["QA"]["TPS"]["db_type"] == "postgresql"
    
    @pytest.mark.unit
    @pytest.mark.negative
    def test_add_environment_invalid_application_config(self, sample_config):
        """Test adding environment with invalid application configuration"""
        applications = {
            "TPS": "not a dict or connection"
        }
        
        with pytest.raises(ValueError, match="Invalid application configuration for 'TPS'"):
            JsonConfigWriter.add_environment(sample_config, "QA", applications)