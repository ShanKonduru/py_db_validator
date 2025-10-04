# Table Validation Tests for Specific Tables

## Overview
Created comprehensive validation tests for your three specific tables:
- `public.products`
- `public.employees` 
- `public.orders`

## Generated Excel File
**File**: `table_validation_tests.xlsx`

## Test Coverage
Each table has **4 comprehensive validation tests**:

### 1. Table Existence Tests (TABLE_EXISTS)
- **SMOKE_PG_007**: Products Table Exists
- **SMOKE_PG_008**: Employees Table Exists  
- **SMOKE_PG_009**: Orders Table Exists

### 2. Table Access Tests (TABLE_SELECT)
- **SMOKE_PG_010**: Products Table Select Test
- **SMOKE_PG_011**: Employees Table Select Test
- **SMOKE_PG_012**: Orders Table Select Test

### 3. Data Validation Tests (TABLE_ROWS)
- **SMOKE_PG_013**: Products Table Has Data
- **SMOKE_PG_014**: Employees Table Has Data
- **SMOKE_PG_015**: Orders Table Has Data

### 4. Structure Validation Tests (TABLE_STRUCTURE)
- **SMOKE_PG_016**: Products Table Structure
- **SMOKE_PG_017**: Employees Table Structure
- **SMOKE_PG_018**: Orders Table Structure

## Test Parameters
All tests include proper schema qualification:
```
table_name=public.products
table_name=public.employees
table_name=public.orders
```

Data validation tests include minimum row requirements:
```
table_name=public.products,min_rows=1
table_name=public.employees,min_rows=1
table_name=public.orders,min_rows=1
```

## Test Priority Distribution
- **HIGH Priority**: Table existence and access tests (critical for functionality)
- **MEDIUM Priority**: Data validation tests (important for data integrity)
- **LOW Priority**: Structure validation tests (informational)

## What Each Test Validates

### TABLE_EXISTS Tests
- Queries `information_schema.tables` to verify table exists
- Checks both table name and schema
- Essential for ensuring database schema is properly deployed

### TABLE_SELECT Tests  
- Performs `SELECT 1 FROM table_name LIMIT 1`
- Validates read permissions and table accessibility
- Ensures applications can query the tables

### TABLE_ROWS Tests
- Executes `SELECT COUNT(*) FROM table_name`
- Verifies tables contain data (minimum 1 row by default)
- Critical for data-dependent functionality

### TABLE_STRUCTURE Tests
- Queries `information_schema.columns` for table metadata
- Validates column information and data types
- Useful for schema validation and documentation

## Ready for Execution
✅ All 18 tests (6 basic + 12 table-specific) are validation-ready
✅ Excel file includes proper dropdowns and formatting
✅ Parameters are correctly formatted for the test framework
✅ Tests follow consistent naming and organization patterns

You can now run these tests against your PostgreSQL database to validate that all three tables are properly accessible and contain data.