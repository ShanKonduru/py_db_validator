# Database Validation Framework

A comprehensive Python framework providing clean, testable database connectivity for Oracle, PostgreSQL, and SQL Server databases. Built with a robust connector architecture and extensive test coverage.

## 🎯 **Current Status: Database Connector Architecture Complete**

- ✅ **Clean Architecture**: Abstract base class with concrete database implementations
- ✅ **Multi-Database Support**: Oracle (oracledb), PostgreSQL (psycopg2), SQL Server (pyodbc)  
- ✅ **Mock Testing**: Complete mock connector for testing without real databases
- ✅ **Comprehensive Testing**: 79 unit tests with 95.9% code coverage
- ✅ **Pytest Markers**: Categorized tests for selective execution
- ✅ **HTML Coverage Reports**: Detailed line-by-line coverage analysis

## 🏗️ **Architecture Overview**

### Core Components

```text
src/
├── connectors/
│   ├── database_connection_base.py     # Abstract base class
│   ├── oracle_connector.py             # Oracle implementation (100% coverage)
│   ├── postgresql_connector.py         # PostgreSQL implementation (100% coverage)
│   ├── sqlserver_connector.py          # SQL Server implementation (100% coverage)
│   └── mock_connector.py               # Mock implementation (93.3% coverage)
│
tests/
├── test_oracle_connector.py            # 18 comprehensive tests
├── test_postgresql_connector.py        # 21 comprehensive tests  
├── test_sqlserver_connector.py         # 22 comprehensive tests
└── test_mock_connector.py              # 18 comprehensive tests
```

### Database Connector Features

- **Standardized Interface**: All connectors implement the same base methods
- **Connection Management**: Robust connect/disconnect with state tracking
- **Query Execution**: Safe SQL execution with error handling
- **Table Operations**: List tables, check existence, get row counts
- **Database Introspection**: Schema-aware queries for each database type

## 🧪 **Testing Framework**

### Pytest Markers for Test Categorization

```bash
@pytest.mark.unit        # All unit tests
@pytest.mark.db          # Database-related tests  
@pytest.mark.positive    # Positive test cases
@pytest.mark.negative    # Negative test cases
@pytest.mark.edge        # Edge case tests
@pytest.mark.security    # Security-related tests
```

### Test Execution Examples

```bash
# Run all tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Run specific test categories
pytest tests/ -m 'unit'           # All unit tests
pytest tests/ -m 'positive'       # Positive cases only  
pytest tests/ -m 'edge'           # Edge cases only
pytest tests/ -m 'not negative'   # All except negative cases

# Run tests for specific database
pytest tests/test_oracle_connector.py -v
pytest tests/test_postgresql_connector.py -v
pytest tests/test_sqlserver_connector.py -v
```

### Code Coverage Results

| File | Coverage | Lines Covered | Status |
|------|----------|---------------|--------|
| **Oracle Connector** | 100.0% | 43/43 lines | ✅ Complete |
| **PostgreSQL Connector** | 100.0% | 42/42 lines | ✅ Complete |
| **SQL Server Connector** | 100.0% | 44/44 lines | ✅ Complete |
| **Mock Connector** | 93.3% | 28/30 lines | ✅ Complete |
| **Base Class** | 78.6% | 22/28 lines | ✅ Abstract methods |

#### Total Coverage: 95.9% (185/193 lines)

## 🚀 **Quick Start**

### 1. Environment Setup

```bash
# Create and activate virtual environment (Windows)
001_env.bat
002_activate.bat

# Install dependencies
003_setup.bat
```

### 2. Run Tests

```bash
# Run all tests
005_run_test.bat

# Run with coverage analysis
005_run_code_cov.bat

# Generate coverage summary
python coverage_summary.py
```

### 3. Usage Example

```python
from src.connectors.postgresql_connector import PostgreSQLConnector

# Create connector
connector = PostgreSQLConnector(
    host="localhost",
    port=5432,
    username="postgres",
    password="password",
    database="testdb"
)

# Connect and use
success, message = connector.connect()
if success:
    tables = connector.get_tables()
    row_count = connector.get_row_count("users")
    connector.disconnect()
```

## 🔧 **Database Connector API**

### DatabaseConnectionBase (Abstract)

All connectors inherit from this base class and implement:

```python
class DatabaseConnectionBase(ABC):
    def __init__(self, host: str, port: int, username: str, password: str, **kwargs)
    
    @abstractmethod
    def connect(self) -> Tuple[bool, str]
    
    @abstractmethod  
    def disconnect(self) -> None
    
    @abstractmethod
    def execute_query(self, query: str) -> Tuple[bool, Any]
    
    @abstractmethod
    def get_tables(self) -> List[str]
    
    @abstractmethod
    def table_exists(self, table_name: str) -> bool
    
    @abstractmethod
    def get_row_count(self, table_name: str) -> int
```

### Oracle Connector Specifics

- **Driver**: oracledb (thin client mode)
- **Connection String**: DSN format `host:port/service_name`
- **Schema Queries**: Uses `user_tables` view
- **Case Handling**: UPPER() for table name matching

### PostgreSQL Connector Specifics  

- **Driver**: psycopg2
- **Connection String**: Standard PostgreSQL format
- **Schema Queries**: Uses `information_schema.tables`
- **Features**: Full PostgreSQL compatibility

### SQL Server Connector Specifics

- **Driver**: pyodbc with ODBC drivers
- **Connection String**: ODBC format with 10-second timeout
- **Schema Queries**: Uses `sys.tables` with schema filtering
- **Table Names**: Bracket notation `[table_name]` for special characters

### Mock Connector

- **Purpose**: Testing without real database dependencies
- **Mock Data**: Predefined tables (users, orders, products) with sample data
- **Query Simulation**: Pattern matching for common SQL operations
- **Test Coverage**: Enables unit testing of database-dependent code

## 📊 **HTML Coverage Report**

Detailed line-by-line coverage analysis is available in the HTML report:

```bash
# Generate and view coverage report
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

## 🛠️ **Development Workflow**

### Adding New Database Support

1. **Create Connector Class**: Inherit from `DatabaseConnectionBase`
2. **Implement Required Methods**: All abstract methods must be implemented
3. **Add Database-Specific Logic**: Connection strings, queries, error handling
4. **Create Comprehensive Tests**: Positive, negative, edge, and security cases
5. **Add Pytest Markers**: Categorize tests for selective execution
6. **Update Coverage**: Aim for 100% line coverage

### Test Categories

- **Unit Tests**: Fast, isolated tests with mocked dependencies
- **Positive Tests**: Happy path scenarios with expected inputs
- **Negative Tests**: Error conditions and invalid inputs  
- **Edge Tests**: Boundary conditions and special cases
- **Security Tests**: SQL injection prevention and credential handling

## 📈 **Project Roadmap**

### ✅ Phase 1: Core Architecture (Complete)

- [x] Abstract base class design
- [x] Oracle, PostgreSQL, SQL Server connectors
- [x] Mock connector for testing
- [x] Comprehensive unit test suite
- [x] Code coverage analysis

### 🔄 Phase 2: Data Validation Framework (Next)

- [ ] CSV-driven test configuration
- [ ] Test orchestration engine
- [ ] Data comparison utilities
- [ ] Report generation system
- [ ] CLI interface

### 🔮 Phase 3: Advanced Features (Future)

- [ ] Connection pooling
- [ ] Async database operations  
- [ ] Performance benchmarking
- [ ] Integration testing
- [ ] CI/CD pipeline integration

## 🧰 **Development Tools**

### Batch Scripts (Windows)

```bash
000_init.bat          # Initialize git and config
001_env.bat           # Create virtual environment  
002_activate.bat      # Activate environment
003_setup.bat         # Install dependencies
004_run.bat           # Run main application
005_run_test.bat      # Run pytest tests
005_run_code_cov.bat  # Run with coverage
008_deactivate.bat    # Deactivate environment
```

### Configuration Files

- `pytest.ini` - Pytest configuration with custom markers
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore patterns
- `coverage_summary.py` - Coverage analysis script

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-connector`)
3. Add comprehensive tests with pytest markers
4. Ensure 100% code coverage for new features
5. Update documentation
6. Submit pull request

## 📝 **License**

[Specify your license here]

---

Built with Python 3.13+ | Tested with pytest | 95.9% Code Coverage
