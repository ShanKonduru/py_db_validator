# Database Configuration Editor - Streamlit Application

A user-friendly web interface for editing database connection configurations without allowing users to modify key names, only values.

## Features

### 🔍 **View and Edit Existing Configurations**
- Browse environments and applications
- Edit connection parameters (host, port, credentials, timeouts)
- Update environment details (name, description)
- Real-time validation and error handling

### 🌍 **Add New Environments**
- Create new environments with custom names and descriptions
- Automatic validation to prevent duplicates

### 📱 **Add New Applications**
- Add database applications to existing environments
- Support for Oracle, PostgreSQL, and SQL Server
- Database-specific field validation
- Auto-generation of environment variable names

### 📋 **Metadata Management**
- Edit configuration metadata
- Manage supported environments and applications
- Version control information

### 💾 **File Operations**
- Load configuration files via file upload or default path
- Automatic backup creation before saving
- Unsaved changes tracking

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Installation

1. **Install dependencies:**
   ```bash
   # Windows
   .\scripts\run_streamlit_editor.bat
   
   # Linux/Mac
   chmod +x ./scripts/run_streamlit_editor.sh
   ./scripts/run_streamlit_editor.sh
   ```

2. **Manual installation:**
   ```bash
   pip install streamlit pandas
   ```

### Running the Application

#### Option 1: Use the provided scripts
```bash
# Windows
.\scripts\run_streamlit_editor.bat

# Linux/Mac
./scripts/run_streamlit_editor.sh
```

#### Option 2: Direct command
```bash
streamlit run streamlit_db_config_editor.py
```

The application will open in your default web browser at `http://localhost:8501`

## Usage Guide

### 1. Loading Configuration
- **Upload File**: Use the sidebar file uploader to load any JSON configuration file
- **Default Config**: Click "Load Default Config" to load `config/database_connections.json`

### 2. Viewing and Editing
- **Configuration Overview**: See metrics for environments, applications, and database types
- **View/Edit Tab**: 
  - Select an environment to view its details
  - Choose an application to edit its connection parameters
  - Update environment names and descriptions
  - Modify database connection settings

### 3. Adding New Environments
- **Add Environment Tab**:
  - Enter environment code (e.g., PROD, STAGE)
  - Provide display name and description
  - Environment will be created with empty applications list

### 4. Adding New Applications
- **Add Application Tab**:
  - Select target environment
  - Enter application code and database details
  - Configure connection parameters
  - Set environment variables for credentials

### 5. Managing Metadata
- **Metadata Tab**:
  - Update configuration version and creation date
  - Edit description and supported environments
  - Manage supported applications list

### 6. Saving Changes
- Use the "Save Configuration" button in the sidebar
- Automatic backup creation before saving
- Unsaved changes indicator

## Configuration Structure

The application works with JSON configuration files following this structure:

```json
{
  "metadata": {
    "config_version": "1.0",
    "created_date": "2025-10-03",
    "description": "Database configuration",
    "supported_environments": ["DEV", "QA", "PROD"],
    "supported_applications": {
      "RED": "Oracle Database",
      "TPS": "PostgreSQL Database"
    }
  },
  "environments": {
    "DEV": {
      "name": "Development",
      "description": "Development environment",
      "applications": {
        "RED": {
          "db_type": "oracle",
          "host": "dev-oracle.company.com",
          "port": 1521,
          "service_name": "REDDEV",
          "schema": "RED_SCHEMA",
          "username_env_var": "DEV_RED_USERNAME",
          "password_env_var": "DEV_RED_PASSWORD",
          "connection_timeout": 30,
          "query_timeout": 300,
          "max_connections": 5
        }
      }
    }
  }
}
```

## Database Types Supported

### Oracle
Required fields: `db_type`, `host`, `port`, `service_name`
Optional fields: `schema`, credentials, timeouts

### PostgreSQL  
Required fields: `db_type`, `host`, `port`, `database`
Optional fields: `schema`, credentials, timeouts

### SQL Server
Required fields: `db_type`, `host`, `port`, `database`
Optional fields: `schema`, credentials, timeouts

## Security Features

- **Read-only key names**: Users cannot modify field names, only values
- **Input validation**: Proper validation for ports, timeouts, and required fields
- **Backup creation**: Automatic backups before saving changes
- **Environment variable naming**: Secure credential management through environment variables

## Error Handling

- File loading errors with detailed messages
- Validation errors for required fields
- Duplicate detection for environments and applications
- Network timeout configuration validation

## Troubleshooting

### Common Issues

1. **Import errors**: Install required packages with `pip install streamlit pandas`
2. **File not found**: Ensure the configuration file path is correct
3. **JSON parsing errors**: Validate JSON syntax in external tools
4. **Port conflicts**: Change the port in the startup command if 8501 is in use

### Tips
- Always backup your configuration files before editing
- Use the unsaved changes indicator to track modifications
- Test database connections after making changes
- Keep environment variable names consistent

## Development

To extend the application:
1. Add new database types to `supported_db_types` list
2. Implement custom validation rules in the form handlers
3. Add new tabs for additional functionality
4. Customize styling in the CSS section

## File Structure

```
py_db_validator/
├── streamlit_db_config_editor.py    # Main Streamlit application
├── config/
│   └── database_connections.json    # Default configuration file
├── scripts/
│   ├── run_streamlit_editor.bat     # Windows startup script
│   └── run_streamlit_editor.sh      # Linux/Mac startup script
└── requirements_streamlit.txt       # Streamlit dependencies
```