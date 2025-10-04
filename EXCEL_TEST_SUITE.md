# Excel-Driven Test Suite

A flexible test execution framework that reads test configurations from Excel files and executes PostgreSQL smoke tests based on the specified criteria.

## 📊 Overview

The Excel-driven test suite allows you to:
- Define test cases in an Excel spreadsheet (`sdm_test_suite.xlsx`)
- Execute tests with flexible filtering options
- Get detailed execution reports
- Maintain test configurations without touching code

## 🚀 Quick Start

### 1. Using the Excel Template

The `sdm_test_suite.xlsx` template is included in the repository with sample PostgreSQL smoke tests. You can modify it directly to add your own test cases.

### 2. Execute Tests

```bash
# Run all enabled tests
python excel_test_driver.py

# List available tests
python excel_test_driver.py --list-tests

# Run high priority tests only
python excel_test_driver.py --priority HIGH

# Run connection tests only
python excel_test_driver.py --category CONNECTION

# Run specific tests by ID
python excel_test_driver.py --test-ids SMOKE_PG_001,SMOKE_PG_004

# Run tests with specific tags
python excel_test_driver.py --tags smoke,db

# Run tests for specific environment/application
python excel_test_driver.py --environment DEV --application DUMMY
```

## 📋 Excel File Structure

### SMOKE Sheet Columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| **Enable** | Boolean | Test execution flag | TRUE/FALSE |
| **Test_Case_ID** | String | Unique test identifier | SMOKE_PG_001 |
| **Test_Case_Name** | String | Descriptive test name | PostgreSQL Connection Test |
| **Application_Name** | String | Target application | DUMMY, MYAPP |
| **Environment_Name** | String | Target environment | DEV, STAGING, PROD |
| **Priority** | String | Test priority level | HIGH, MEDIUM, LOW |
| **Test_Category** | String | Test category | CONNECTION, QUERIES, PERFORMANCE |
| **Expected_Result** | String | Expected outcome | PASS, FAIL |
| **Timeout_Seconds** | Number | Max execution time | 30, 60, 300 |
| **Description** | String | Test description | Validates PostgreSQL connectivity |
| **Prerequisites** | String | Required setup | Database must be running |
| **Tags** | String | Comma-separated tags | smoke,db,integration |

## 🎯 Test Categories

The driver supports these test categories:

- **SETUP** - Environment and configuration validation
- **CONFIGURATION** - Application config availability
- **SECURITY** - Credentials validation
- **CONNECTION** - Database connectivity tests
- **QUERIES** - Basic database query tests
- **PERFORMANCE** - Connection performance tests
- **COMPATIBILITY** - Backwards compatibility tests

## 📈 Sample Test Cases

The template includes these sample tests:

1. **SMOKE_PG_001** - Environment Setup Validation
2. **SMOKE_PG_002** - Configuration Availability
3. **SMOKE_PG_003** - Credentials Validation
4. **SMOKE_PG_004** - Database Connectivity
5. **SMOKE_PG_005** - Basic Database Queries
6. **SMOKE_PG_006** - Connection Performance
7. **SMOKE_PG_007** - Backwards Compatibility Test
8. **SMOKE_PG_008** - Production Environment Example (disabled)

## 🔧 Command Line Options

```bash
python excel_test_driver.py [OPTIONS]

Options:
  -f, --excel-file FILE     Excel file path (default: sdm_test_suite.xlsx)
  -e, --environment ENV     Filter by environment (DEV, STAGING, PROD)
  -a, --application APP     Filter by application (DUMMY, MYAPP)
  -p, --priority LEVEL      Filter by priority (HIGH, MEDIUM, LOW)
  -c, --category CAT        Filter by category (CONNECTION, QUERIES, etc.)
  -t, --tags TAGS           Filter by tags (comma-separated)
  -i, --test-ids IDS        Run specific test IDs (comma-separated)
  -l, --list-tests          List available tests without executing
  -h, --help                Show help message
```

## 📊 Execution Results

The driver provides:

- **Real-time progress** - Shows test execution status as it runs
- **Detailed summary** - Statistics and results breakdown
- **Success/failure tracking** - Clear pass/fail indicators
- **Performance metrics** - Execution times for each test
- **Error reporting** - Detailed error messages for failures

### Sample Output:

```
🚀 Starting test execution: RUN_20251003_222418
📊 Tests to execute: 5

[1/5] 🧪 Executing: SMOKE_PG_001 - Environment Setup Validation
   ✅ PASS (0.00s)

📋 TEST EXECUTION SUMMARY
📊 Total Tests: 5
✅ Passed: 5
❌ Failed: 0
📈 Success Rate: 100.0%
```

## 🛠️ Configuration

The test driver uses the same flexible configuration system as the smoke tests:

1. **Environment Variables** (highest priority)
2. **Configuration files** (lower priority)
3. **TEST_ENVIRONMENT and TEST_APPLICATION** overrides

See [POSTGRESQL_SMOKE_TESTS.md](POSTGRESQL_SMOKE_TESTS.md) for detailed configuration options.

## 🔄 Adding New Tests

1. Open `sdm_test_suite.xlsx`
2. Add new rows with test definitions
3. Set `Enable` to `TRUE`
4. Choose appropriate category, priority, and tags
5. Save the file
6. Run tests: `python excel_test_driver.py`

## 🎯 Benefits

- ✅ **Non-technical accessibility** - Test managers can modify tests without coding
- ✅ **Flexible filtering** - Run subsets of tests by various criteria
- ✅ **Clear reporting** - Detailed execution summaries and statistics
- ✅ **Version control friendly** - Excel files can be tracked in Git
- ✅ **Maintenance friendly** - Easy to enable/disable tests
- ✅ **CI/CD integration** - Command-line interface for automation
- ✅ **Scalable** - Easy to add new test categories and environments

## 🚦 Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed or execution error
- `130` - Execution interrupted by user (Ctrl+C)

## 🔗 Integration

The Excel driver integrates seamlessly with:
- CI/CD pipelines (GitHub Actions, Azure DevOps, Jenkins)
- Existing pytest smoke tests
- Database configuration system
- Environment variable management
- Docker containers and test environments