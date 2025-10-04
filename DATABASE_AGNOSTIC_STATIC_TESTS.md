# Database-Agnostic Static Smoke Tests Class

## Overview

The `StaticDatabaseSmokeTests` class is an **immutable static generic database smoke test class** that provides smoke testing capabilities for multiple database types including PostgreSQL, MySQL, Oracle, and SQL Server. This class is designed to prevent accidental modifications and provide consistent, thread-safe test execution across different database environments.

## 🔒 Key Features

### Immutable Static Design
- **Cannot be instantiated** - All methods are static
- **Thread-safe execution** - No shared state between calls
- **Consistent results** - Same inputs always produce same outputs
- **Prevents accidental modifications** - No instance variables to modify

### Multi-Database Support
- **PostgreSQL** (postgres, postgresql)
- **MySQL** (mysql)
- **Oracle** (oracle)
- **SQL Server** (sqlserver, mssql)

### Auto-Detection and Configuration
- **Automatic database type detection** from environment variables
- **Flexible configuration priority** (environment variables → config file → defaults)
- **Database-specific environment variable support**

## 🗄️ Supported Database Types

| Database | Aliases | Default Port | Environment Prefix | Status |
|----------|---------|--------------|-------------------|---------|
| PostgreSQL | postgres, postgresql | 5432 | POSTGRES | ✅ Supported |
| MySQL | mysql | 3306 | MYSQL | ✅ Supported |
| Oracle | oracle | 1521 | ORACLE | ✅ Supported |
| SQL Server | sqlserver, mssql | 1433 | SQLSERVER | ✅ Supported |

## 🧪 Available Smoke Tests

1. **`test_environment_setup`** - Validate environment and configuration setup
2. **`test_configuration_availability`** - Verify database configuration is complete
3. **`test_environment_credentials`** - Test credential availability and validity
4. **`test_database_connection`** - Test basic database connection
5. **`test_database_basic_queries`** - Execute fundamental database queries
6. **`test_database_connection_performance`** - Test connection and query performance

## 🔧 Utility Methods

- **`run_all_smoke_tests`** - Execute all smoke tests and return summary
- **`get_test_info`** - Get class information and available tests
- **`get_supported_databases`** - Get detailed information about supported databases

## ⚙️ Configuration

### Environment Variables

#### Generic Configuration
```bash
# Database type and connection
DB_TYPE=postgresql          # Database type (postgresql, mysql, oracle, sqlserver)
DB_HOST=localhost          # Database host
DB_PORT=5432              # Database port
DB_DATABASE=mydb          # Database name
DB_SCHEMA=public          # Database schema (optional)
DB_USERNAME=user          # Database username
DB_PASSWORD=pass          # Database password

# Test environment
TEST_ENVIRONMENT=DEV      # Target environment (default: DEV)
TEST_APPLICATION=DUMMY    # Target application (default: DUMMY)
```

#### Database-Specific Configuration
```bash
# PostgreSQL
POSTGRES_HOST=postgres.company.com
POSTGRES_PORT=5432
POSTGRES_DATABASE=prod_db
POSTGRES_SCHEMA=public
POSTGRES_USERNAME=prod_user
POSTGRES_PASSWORD=prod_pass

# MySQL
MYSQL_HOST=mysql.company.com
MYSQL_PORT=3306
MYSQL_DATABASE=prod_db
MYSQL_USERNAME=prod_user
MYSQL_PASSWORD=prod_pass

# Oracle
ORACLE_HOST=oracle.company.com
ORACLE_PORT=1521
ORACLE_DATABASE=ORCL
ORACLE_USERNAME=prod_user
ORACLE_PASSWORD=prod_pass

# SQL Server
SQLSERVER_HOST=sqlserver.company.com
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=prod_db
SQLSERVER_USERNAME=prod_user
SQLSERVER_PASSWORD=prod_pass
```

### Configuration Priority

1. **Environment Variables** (highest priority)
   - Database-specific variables (POSTGRES_HOST, MYSQL_HOST, etc.)
   - Generic variables (DB_HOST, DB_PORT, etc.)

2. **Configuration File** (medium priority)
   - JSON configuration file: `config/db_config.json`
   - Supports environment and application-specific configurations

3. **Defaults** (lowest priority)
   - Default environment: DEV
   - Default application: DUMMY

## 📋 Usage Examples

### Basic Usage

```python
from src.tests.static_database_smoke_tests import StaticDatabaseSmokeTests

# Run environment setup test for PostgreSQL
result = StaticDatabaseSmokeTests.test_environment_setup("postgresql", "PROD", "MyApp")
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")

# Run all smoke tests
summary = StaticDatabaseSmokeTests.run_all_smoke_tests("mysql", "DEV", "TestApp")
print(f"Success Rate: {summary['execution_summary']['success_rate']:.1f}%")
```

### Auto-Detection Usage

```python
# Let the class detect database type from environment
result = StaticDatabaseSmokeTests.test_database_connection()

# Use defaults for environment and application
result = StaticDatabaseSmokeTests.test_configuration_availability()
```

### Integration with TestExecutor

```python
from src.core.test_executor import TestExecutor

# Create executor with static tests and specific database type
executor = TestExecutor(use_static_tests=True, db_type="postgresql")

# Get test information
info = executor.get_static_smoke_test_info()
print(f"Available tests: {len(info['available_tests'])}")

# Run all static smoke tests
results = executor.run_all_static_smoke_tests("PROD", "MyApp")
```

### Environment Variable Control

```bash
# Use static tests with PostgreSQL
export USE_STATIC_SMOKE_TESTS=true
export DB_TYPE=postgresql
python execute_unified_smoke_tests.py test_suite.xlsx

# Use static tests with MySQL
export DB_TYPE=mysql
export MYSQL_HOST=mysql.company.com
python execute_unified_smoke_tests.py test_suite.xlsx
```

## 🚀 Migration from PostgreSQL-Specific Class

### Old PostgreSQL-Specific Usage
```python
from src.tests.static_postgresql_smoke_tests import StaticPostgreSQLSmokeTests

# Old method calls
result = StaticPostgreSQLSmokeTests.test_postgresql_connection("DEV", "DUMMY")
```

### New Database-Agnostic Usage
```python
from src.tests.static_database_smoke_tests import StaticDatabaseSmokeTests

# New method calls with database type parameter
result = StaticDatabaseSmokeTests.test_database_connection("postgresql", "DEV", "DUMMY")

# Or let it auto-detect the database type
result = StaticDatabaseSmokeTests.test_database_connection()
```

## 📊 Test Result Structure

All test methods return a consistent result structure:

```python
{
    "test_name": "Test Name",
    "status": "PASS" | "FAIL",
    "message": "Descriptive message",
    "details": {
        "database_type": "postgresql",
        "connection_time": 0.123,
        # Additional test-specific details
    }
}
```

### Summary Structure (run_all_smoke_tests)

```python
{
    "execution_summary": {
        "database_type": "postgresql",
        "total_tests": 6,
        "passed": 5,
        "failed": 1,
        "success_rate": 83.3,
        "total_time": 2.456,
        "environment": "PROD",
        "application": "MyApp"
    },
    "test_results": [
        # Array of individual test results
    ]
}
```

## 🔍 Class Information Methods

### Get Test Information
```python
info = StaticDatabaseSmokeTests.get_test_info()
print(f"Class Type: {info['class_type']}")
print(f"Supported Databases: {info['supported_databases']}")
print(f"Available Tests: {info['available_tests']}")
```

### Get Supported Databases
```python
databases = StaticDatabaseSmokeTests.get_supported_databases()
for db_type, details in databases.items():
    print(f"{db_type}: {details['connector_available']}")
```

## 🛠️ Integration Points

### With TestExecutor
- TestExecutor accepts `db_type` parameter
- Automatic integration with static test execution
- Dual-mode support (static vs instance tests)

### With Excel Test Execution
- Environment variable `DB_TYPE` controls database type
- Seamless integration with existing test suites
- Backward compatibility with PostgreSQL-only configurations

### With Configuration Management
- JSON configuration file support
- Environment-specific configurations
- Application-specific configurations

## ⚡ Performance Considerations

- **No instantiation overhead** - All methods are static
- **Thread-safe execution** - No shared state
- **Connection pooling** - Each test manages its own connections
- **Performance monitoring** - Built-in performance threshold checking (2.0s default)

## 🧪 Testing and Validation

### Manual Testing
```bash
# Test the demo script
python demo_database_agnostic_static_tests.py

# Test with specific database type
export DB_TYPE=mysql
python demo_database_agnostic_static_tests.py
```

### Integration Testing
```bash
# Test with Excel execution
export USE_STATIC_SMOKE_TESTS=true
export DB_TYPE=postgresql
python execute_unified_smoke_tests.py enhanced_unified_sdm_test_suite.xlsx
```

## 🔒 Security Considerations

- **Credential Management** - Supports both direct and environment variable-based credentials
- **No credential logging** - Sensitive information is not logged
- **Connection security** - Uses secure connection methods from connectors
- **Environment isolation** - Each test execution is isolated

## 📝 Error Handling

- **Graceful degradation** - Tests continue even if some fail
- **Detailed error messages** - Clear indication of failure reasons
- **Exception handling** - All exceptions are caught and reported
- **Rollback safety** - No persistent changes made during testing

## 🔄 Backward Compatibility

- **Legacy support** - Original PostgreSQL-specific class remains available
- **Migration path** - Clear upgrade path from PostgreSQL-only to multi-database
- **Environment variables** - Backward compatible with existing PostgreSQL configurations
- **API consistency** - Similar method signatures and return structures

## 📚 Additional Resources

- **Source Code**: `src/tests/static_database_smoke_tests.py`
- **Demo Script**: `demo_database_agnostic_static_tests.py`
- **Integration Example**: `execute_unified_smoke_tests.py`
- **Test Executor**: `src/core/test_executor.py`

## 🏆 Benefits Summary

✅ **Immutable Design** - Prevents accidental modifications  
✅ **Multi-Database Support** - Works with PostgreSQL, MySQL, Oracle, SQL Server  
✅ **Thread-Safe** - Consistent results in concurrent environments  
✅ **Auto-Detection** - Intelligent database type detection  
✅ **Flexible Configuration** - Multiple configuration sources and priorities  
✅ **Easy Integration** - Drop-in replacement for PostgreSQL-specific class  
✅ **Comprehensive Testing** - Full smoke test coverage  
✅ **Production Ready** - Robust error handling and performance monitoring