"""
Unit tests for JsonConfigReader utility class
"""

import json
import os
import tempfile
import pytest
from pathlib import Path

from src.utils.json_config_reader import JsonConfigReader
from src.utils.database_connection import DatabaseConnection


class TestJsonConfigReader:
    """Test JsonConfigReader utility class"""

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
                        "password_env": "DEV_RED_PASSWORD",
                    },
                    "TPS": {
                        "db_type": "postgresql",
                        "host": "dev-postgres.example.com",
                        "port": 5432,
                        "database": "tpsdev",
                        "username_env": "DEV_TPS_USERNAME",
                        "password_env": "DEV_TPS_PASSWORD",
                    },
                },
                "QA": {
                    "RED": {
                        "db_type": "oracle",
                        "host": "qa-oracle.example.com",
                        "port": 1521,
                        "database": "redqa",
                        "schema": "red_schema",
                        "username_env": "QA_RED_USERNAME",
                        "password_env": "QA_RED_PASSWORD",
                    }
                },
            }
        }

    @pytest.fixture
    def temp_config_file(self, sample_config):
        """Create temporary config file for testing"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(sample_config, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        try:
            os.unlink(temp_path)
        except OSError:
            pass

    @pytest.mark.unit
    @pytest.mark.positive
    def test_read_config_file_success(self, temp_config_file, sample_config):
        """Test successfully reading config file"""
        result = JsonConfigReader.read_config_file(temp_config_file)
        assert result == sample_config

    @pytest.mark.unit
    @pytest.mark.negative
    def test_read_config_file_not_found(self):
        """Test reading non-existent config file"""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            JsonConfigReader.read_config_file("non_existent_file.json")

    @pytest.mark.unit
    @pytest.mark.negative
    def test_read_config_file_empty_path(self):
        """Test reading config file with empty path"""
        with pytest.raises(ValueError, match="File path cannot be empty"):
            JsonConfigReader.read_config_file("")

    @pytest.mark.unit
    @pytest.mark.negative
    def test_read_config_file_directory(self, tmp_path):
        """Test reading config file that is actually a directory"""
        with pytest.raises(ValueError, match="Path is not a file"):
            JsonConfigReader.read_config_file(str(tmp_path))

    @pytest.mark.unit
    @pytest.mark.negative
    def test_read_config_file_empty_file(self, tmp_path):
        """Test reading empty config file"""
        empty_file = tmp_path / "empty.json"
        empty_file.touch()

        with pytest.raises(ValueError, match="Configuration file is empty"):
            JsonConfigReader.read_config_file(str(empty_file))

    @pytest.mark.unit
    @pytest.mark.negative
    def test_read_config_file_invalid_json(self, tmp_path):
        """Test reading config file with invalid JSON"""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{invalid json")

        with pytest.raises(json.JSONDecodeError, match="Invalid JSON"):
            JsonConfigReader.read_config_file(str(invalid_file))

    @pytest.mark.unit
    @pytest.mark.negative
    def test_read_config_file_non_object(self, tmp_path):
        """Test reading config file with non-object JSON"""
        array_file = tmp_path / "array.json"
        array_file.write_text("[1, 2, 3]")

        with pytest.raises(
            ValueError, match="Configuration file must contain a JSON object"
        ):
            JsonConfigReader.read_config_file(str(array_file))

    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_environments(self, sample_config):
        """Test getting list of environments"""
        environments = JsonConfigReader.get_environments(sample_config)
        assert set(environments) == {"DEV", "QA"}

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_environments_invalid_data(self):
        """Test getting environments with invalid data"""
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            JsonConfigReader.get_environments("not a dict")

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_environments_invalid_structure(self):
        """Test getting environments with invalid structure"""
        config = {"environments": "not a dict"}
        with pytest.raises(
            ValueError, match="Environments section must be a dictionary"
        ):
            JsonConfigReader.get_environments(config)

    @pytest.mark.unit
    @pytest.mark.edge
    def test_get_environments_missing_section(self):
        """Test getting environments with missing environments section"""
        config = {"other_section": {}}
        environments = JsonConfigReader.get_environments(config)
        assert environments == []

    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_applications(self, sample_config):
        """Test getting list of applications for environment"""
        applications = JsonConfigReader.get_applications(sample_config, "DEV")
        assert set(applications) == {"RED", "TPS"}

        applications = JsonConfigReader.get_applications(sample_config, "QA")
        assert set(applications) == {"RED"}

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_applications_invalid_data(self):
        """Test getting applications with invalid data"""
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            JsonConfigReader.get_applications("not a dict", "DEV")

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_applications_environment_not_found(self, sample_config):
        """Test getting applications for non-existent environment"""
        with pytest.raises(KeyError, match="Environment 'NONEXISTENT' not found"):
            JsonConfigReader.get_applications(sample_config, "NONEXISTENT")

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_applications_invalid_environment_data(self):
        """Test getting applications with invalid environment data"""
        config = {"environments": {"DEV": "not a dict"}}
        with pytest.raises(
            ValueError, match="Environment 'DEV' data must be a dictionary"
        ):
            JsonConfigReader.get_applications(config, "DEV")

    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_connection_config(self, sample_config):
        """Test getting connection configuration"""
        conn = JsonConfigReader.get_connection_config(sample_config, "DEV", "RED")

        assert isinstance(conn, DatabaseConnection)
        assert conn.db_type == "oracle"
        assert conn.host == "dev-oracle.example.com"
        assert conn.port == 1521
        assert conn.database == "reddev"
        assert conn.schema == "red_schema"
        assert conn.username_env == "DEV_RED_USERNAME"
        assert conn.password_env == "DEV_RED_PASSWORD"

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_connection_config_invalid_data(self):
        """Test getting connection config with invalid data"""
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            JsonConfigReader.get_connection_config("not a dict", "DEV", "RED")

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_connection_config_environment_not_found(self, sample_config):
        """Test getting connection config for non-existent environment"""
        with pytest.raises(KeyError, match="Environment 'NONEXISTENT' not found"):
            JsonConfigReader.get_connection_config(sample_config, "NONEXISTENT", "RED")

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_connection_config_application_not_found(self, sample_config):
        """Test getting connection config for non-existent application"""
        with pytest.raises(
            KeyError, match="Application 'NONEXISTENT' not found in environment 'DEV'"
        ):
            JsonConfigReader.get_connection_config(sample_config, "DEV", "NONEXISTENT")

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_connection_config_invalid_app_config(self):
        """Test getting connection config with invalid application config"""
        config = {"environments": {"DEV": {"RED": "not a dict"}}}
        with pytest.raises(
            ValueError, match="Application 'RED' configuration must be a dictionary"
        ):
            JsonConfigReader.get_connection_config(config, "DEV", "RED")

    @pytest.mark.unit
    @pytest.mark.negative
    def test_get_connection_config_missing_required_field(self):
        """Test getting connection config with missing required field"""
        config = {
            "environments": {
                "DEV": {
                    "RED": {
                        "db_type": "oracle",
                        "host": "localhost",
                        # Missing port and database
                    }
                }
            }
        }
        with pytest.raises(
            ValueError, match="Missing required field 'port' in DEV.RED configuration"
        ):
            JsonConfigReader.get_connection_config(config, "DEV", "RED")

    @pytest.mark.unit
    @pytest.mark.positive
    def test_validate_config_structure_valid(self, sample_config):
        """Test validating valid configuration structure"""
        errors = JsonConfigReader.validate_config_structure(sample_config)
        assert errors == []

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_not_dict(self):
        """Test validating non-dictionary configuration"""
        errors = JsonConfigReader.validate_config_structure("not a dict")
        assert "Configuration data must be a dictionary" in errors

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_missing_environments(self):
        """Test validating configuration missing environments section"""
        config = {"other_section": {}}
        errors = JsonConfigReader.validate_config_structure(config)
        assert "Missing required 'environments' section" in errors

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_invalid_environments(self):
        """Test validating configuration with invalid environments section"""
        config = {"environments": "not a dict"}
        errors = JsonConfigReader.validate_config_structure(config)
        assert "'environments' section must be a dictionary" in errors

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_empty_environments(self):
        """Test validating configuration with empty environments section"""
        config = {"environments": {}}
        errors = JsonConfigReader.validate_config_structure(config)
        assert "'environments' section cannot be empty" in errors

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_invalid_environment(self):
        """Test validating configuration with invalid environment"""
        config = {"environments": {"DEV": "not a dict"}}
        errors = JsonConfigReader.validate_config_structure(config)
        assert "Environment 'DEV' must be a dictionary" in errors

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_empty_environment(self):
        """Test validating configuration with empty environment"""
        config = {"environments": {"DEV": {}}}
        errors = JsonConfigReader.validate_config_structure(config)
        assert "Environment 'DEV' cannot be empty" in errors

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_invalid_application(self):
        """Test validating configuration with invalid application"""
        config = {"environments": {"DEV": {"RED": "not a dict"}}}
        errors = JsonConfigReader.validate_config_structure(config)
        assert "Application 'DEV.RED' must be a dictionary" in errors

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_missing_required_fields(self):
        """Test validating configuration with missing required fields"""
        config = {
            "environments": {
                "DEV": {
                    "RED": {
                        "db_type": "oracle"
                        # Missing host, port, database
                    }
                }
            }
        }
        errors = JsonConfigReader.validate_config_structure(config)
        assert any(
            "Missing required field 'host' in DEV.RED" in error for error in errors
        )
        assert any(
            "Missing required field 'port' in DEV.RED" in error for error in errors
        )
        assert any(
            "Missing required field 'database' in DEV.RED" in error for error in errors
        )

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_invalid_port_type(self):
        """Test validating configuration with invalid port type"""
        config = {
            "environments": {
                "DEV": {
                    "RED": {
                        "db_type": "oracle",
                        "host": "localhost",
                        "port": "not an int",
                        "database": "testdb",
                    }
                }
            }
        }
        errors = JsonConfigReader.validate_config_structure(config)
        assert "Port must be an integer in DEV.RED" in errors

    @pytest.mark.unit
    @pytest.mark.negative
    def test_validate_config_structure_invalid_db_type(self):
        """Test validating configuration with invalid db_type"""
        config = {
            "environments": {
                "DEV": {
                    "RED": {
                        "db_type": 123,
                        "host": "localhost",
                        "port": 1521,
                        "database": "testdb",
                    }
                }
            }
        }
        errors = JsonConfigReader.validate_config_structure(config)
        assert "db_type must be a string in DEV.RED" in errors

    @pytest.mark.unit
    @pytest.mark.positive
    def test_get_config_metadata(self, sample_config):
        """Test getting configuration metadata"""
        metadata = JsonConfigReader.get_config_metadata(sample_config)

        assert metadata["total_environments"] == 2
        assert metadata["total_applications"] == 3
        assert set(metadata["database_types"]) == {"oracle", "postgresql"}
        assert set(metadata["environments"]) == {"DEV", "QA"}
        assert metadata["applications_per_environment"]["DEV"] == 2
        assert metadata["applications_per_environment"]["QA"] == 1

    @pytest.mark.unit
    @pytest.mark.edge
    def test_get_config_metadata_invalid_data(self):
        """Test getting metadata with invalid data"""
        metadata = JsonConfigReader.get_config_metadata("not a dict")
        expected = {
            "total_environments": 0,
            "total_applications": 0,
            "database_types": set(),
            "environments": [],
            "applications_per_environment": {},
        }
        assert metadata == expected

    @pytest.mark.unit
    @pytest.mark.edge
    def test_get_config_metadata_missing_environments(self):
        """Test getting metadata with missing environments section"""
        config = {"other_section": {}}
        metadata = JsonConfigReader.get_config_metadata(config)
        assert metadata["total_environments"] == 0
        assert metadata["total_applications"] == 0
