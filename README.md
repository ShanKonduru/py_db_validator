# Database Validation Framework

A comprehensive Python framework for validating data across Oracle, PostgreSQL, and SQL Server databases. Tests are defined in CSV files and executed against configurable database profiles with detailed reporting.

## Features

- **Multi-Database Support**: Oracle (oracledb), PostgreSQL (psycopg2), SQL Server (pyodbc)
- **CSV-Driven Configuration**: Define tests in simple CSV format
- **Multiple Test Types**: Connection, table existence, permissions, row counts, data comparisons
- **Flexible Reporting**: JSON, Markdown, HTML, and CSV output formats
- **Robust Error Handling**: Retry logic, timeouts, and detailed error reporting
- **Secure Credential Management**: Database credentials via environment variables

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd py_db_validator

# Create virtual environment (Windows)
001_env.bat

# Activate environment (Windows)  
002_activate.bat

# Install dependencies (Windows)
003_setup.bat
```

### 2. Configuration

Copy the example configuration files:

```bash
copy examples\.env.template .env
copy examples\db_profiles.json .
copy examples\sample_tests.csv .
```

Edit `.env` with your database credentials:
```bash
ORACLE_DB_USER=your_oracle_username
ORACLE_DB_PWD=your_oracle_password
POSTGRESQL_DB_USER=your_postgres_username  
POSTGRESQL_DB_PWD=your_postgres_password
SQLSERVER_DB_USER=your_sqlserver_username
SQLSERVER_DB_PWD=your_sqlserver_password
```

### 3. Run Tests

```bash
# Run all enabled tests (Windows)
004_run.bat

# Or run manually with options
python main.py --csv sample_tests.csv --profiles db_profiles.json --output reports
```

## Test Types

### Connection Test
Verifies database connectivity and measures connection time.

```csv
test_id,enabled,test_type,profile_src,table_src,column_src,filter_src,profile_tgt,table_tgt,column_tgt,comparison_keys,ignore_columns,tolerance,tags,report_level,notes,timeout_sec,retry_count
conn_oracle,Y,CONNECTION,oracle_dev,,,,,,,,,0.001,smoke,INFO,Test Oracle connection,60,1
```

### Table Existence Test  
Checks if specified tables exist and reports schema information.

```csv
table_customers,Y,TABLE_EXISTENCE,oracle_dev,customers,,,,,,,,0.001,smoke,INFO,Verify customers table exists,30,0
```

### Permissions Test
Verifies user permissions on database objects.

```csv
perm_customers,Y,PERMISSIONS,oracle_dev,customers,,,,,,,,0.001,permissions,INFO,"permissions: SELECT,INSERT",30,0
```

### Row Existence Test
Checks if rows exist matching specified criteria.

```csv
active_customers,Y,ROW_EXISTENCE,oracle_dev,customers,,"status = 'ACTIVE'",,,,,,0.001,data,INFO,Check for active customers,60,0
```

### Row Count Test
Counts rows in tables, optionally comparing source vs target.

```csv
count_orders,Y,ROW_COUNT,oracle_dev,orders,,,postgres_dev,orders_copy,,,0.05,migration,INFO,Compare order counts,300,1
```

## Configuration Files

### Database Profiles (`db_profiles.json`)

```json
[
  {
    "profile_id": "oracle_dev",
    "db_type": "oracle", 
    "host": "localhost",
    "port": 1521,
    "service_name": "XEPDB1"
  },
  {
    "profile_id": "postgres_dev",
    "db_type": "postgresql",
    "host": "localhost", 
    "port": 5432,
    "database": "testdb"
  }
]
```

### Test Definitions CSV

| Column | Description | Required |
|--------|-------------|----------|
| test_id | Unique test identifier | Yes |
| enabled | Y/N to enable/disable test | Yes |
| test_type | Type of test to run | Yes |
| profile_src | Source database profile ID | Yes |
| table_src | Source table name | Varies |
| filter_src | WHERE clause for filtering | No |
| profile_tgt | Target database profile ID | No |
| table_tgt | Target table name | No |
| tolerance | Numeric comparison tolerance | No |
| tags | Comma-separated tags | No |
| timeout_sec | Test timeout in seconds | No |
| retry_count | Number of retries on failure | No |

## Command Line Options

```bash
python main.py [OPTIONS]

Options:
  -c, --csv TEXT          Path to test definitions CSV file [required]
  -p, --profiles TEXT     Path to database profiles JSON file [required]  
  -o, --output TEXT       Output directory for reports [default: reports]
  -t, --tags TEXT         Filter tests by tags (can specify multiple)
  --test-ids TEXT         Filter tests by IDs (can specify multiple)
  --include-disabled      Include disabled tests
  --log-level [DEBUG|INFO|WARNING|ERROR]  Set logging level [default: INFO]
  --fail-fast            Exit on first test failure
  --help                 Show this message and exit
```

### Examples

```bash
# Run all tests
python main.py -c tests.csv -p profiles.json

# Run only smoke tests
python main.py -c tests.csv -p profiles.json -t smoke

# Run specific tests with debug logging
python main.py -c tests.csv -p profiles.json --test-ids conn_oracle,table_customers --log-level DEBUG

# Run tests including disabled ones
python main.py -c tests.csv -p profiles.json --include-disabled
```

## Report Output

Reports are generated in timestamped directories under the output folder:

```
reports/
  run_20241002_143022/
    index.md              # Suite summary report
    summary.json          # Machine-readable summary
    summary.csv           # CSV summary for automation
    conn_oracle.json      # Individual test JSON report
    conn_oracle.md        # Individual test Markdown report
    table_customers.json  # More test reports...
    table_customers.md
    run_a1b2c3d4.log     # Execution log
```

### Report Contents

- **Suite Summary**: Overall results, success rates, timing
- **Individual Tests**: Detailed results, queries executed, error details
- **JSON Reports**: Machine-readable for CI/CD integration
- **Markdown Reports**: Human-readable with formatted results
- **CSV Summary**: Tabular data for spreadsheet analysis

## Development

### Project Structure

```
src/
  models.py           # Data models and enums
  exceptions.py       # Custom exception classes
  parser/             # Configuration and CSV parsing
    config_loader.py
    csv_parser.py
  adapters/           # Database connectivity
    base_adapter.py
    oracle_adapter.py
    postgres_adapter.py
    sqlserver_adapter.py
  tests/              # Test implementations
    base_test.py
    connection_test.py
    table_existence_test.py
    permissions_test.py
    row_existence_test.py
    row_count_test.py
  runner/             # Test orchestration
    orchestrator.py
  reporter/           # Report generation
    report_generator.py
  utils/              # Utilities
    compare_utils.py
    sql_utils.py
    logger.py
```

### Running Unit Tests

```bash
# Run unit tests (Windows)
005_run_test.bat

# Run with coverage (Windows)  
005_run_code_cov.bat

# Manual pytest execution
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

### Adding New Test Types

1. Create test class inheriting from `BaseTest`
2. Implement `_run()` and `_validate()` methods
3. Add to `TestFactory` 
4. Update CSV parser validation rules
5. Add unit tests

### Environment Management

```bash
# Initialize git and config (Windows)
000_init.bat

# Create virtual environment (Windows)
001_env.bat

# Activate environment (Windows)
002_activate.bat

# Install dependencies (Windows)
003_setup.bat

# Deactivate environment (Windows)
008_deactivate.bat
```

## Troubleshooting

### Database Connection Issues

1. **Oracle**: Ensure Oracle client is installed and `ORACLE_HOME` is set
2. **PostgreSQL**: Verify `pg_hba.conf` allows connections
3. **SQL Server**: Check ODBC driver installation and SQL Server configuration

### Common Errors

- **Missing credentials**: Check `.env` file format and variable names
- **Profile not found**: Verify profile IDs match between CSV and JSON files
- **Permission denied**: Ensure database user has required privileges
- **Timeout errors**: Increase `timeout_sec` values for slow queries

### Logging

Set `--log-level DEBUG` for detailed execution information. Logs are written to:
- Console (formatted for human reading)
- Log file (JSON format for machine processing)

## License

[Specify your license here]

## Contributing

[Explain how others can contribute to your project]

[Specify the project license, if any.]
