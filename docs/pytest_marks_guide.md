# Pytest Marks Usage Guide for Report Generator Tests

## Overview

The `test_report_generator.py` file has been enhanced with comprehensive pytest marks to categorize tests by type, functionality, and complexity. This allows for targeted test execution and better test organization.

## Test Categories

### Primary Categories

#### 🟢 Positive Tests (`@pytest.mark.positive`)
Tests that verify expected behavior with valid inputs:
- Basic functionality tests
- Happy path scenarios  
- Standard use cases

#### 🔴 Negative Tests (`@pytest.mark.negative`) 
Tests that verify error handling with invalid inputs:
- Invalid parameters
- Malformed data
- Error conditions

#### 🟡 Edge Cases (`@pytest.mark.edge_case`)
Tests for boundary conditions and unusual scenarios:
- Empty inputs
- Extreme values
- Null/None values
- Special characters

#### ⚡ Performance Tests (`@pytest.mark.performance`)
Tests that verify performance and scalability:
- Large datasets
- Stress testing
- Memory usage

### Functional Categories

#### 📊 HTML Generation (`@pytest.mark.html_generation`)
Tests specific to HTML report generation functionality

#### 📝 Markdown Generation (`@pytest.mark.markdown_generation`) 
Tests specific to Markdown report generation functionality

#### 📋 Multi-Sheet (`@pytest.mark.multi_sheet`)
Tests for multi-sheet report functionality

#### 📈 Statistics (`@pytest.mark.statistics`)
Tests for statistical calculations and summary data

#### 🎨 Formatting (`@pytest.mark.formatting`)
Tests for output formatting and structure

### Specialized Categories

#### 🔍 Failure Analysis (`@pytest.mark.failure_analysis`)
Tests for failure analysis and error reporting features

#### ✅ Success Scenarios (`@pytest.mark.success_scenario`)
Tests for all-pass and successful execution scenarios

#### 🔤 Special Characters (`@pytest.mark.special_characters`)
Tests for handling special characters and symbols

#### 🌐 Unicode Handling (`@pytest.mark.unicode_handling`)
Tests for Unicode character support and internationalization

## Usage Examples

### Run All Tests
```bash
python -m pytest tests/unit/test_report_generator.py -v
```

### Run Only Positive Tests
```bash
python -m pytest tests/unit/test_report_generator.py -v -m "positive"
```

### Run Only Negative Tests
```bash
python -m pytest tests/unit/test_report_generator.py -v -m "negative"
```

### Run Only Edge Cases
```bash
python -m pytest tests/unit/test_report_generator.py -v -m "edge_case"
```

### Run Performance Tests
```bash
python -m pytest tests/unit/test_report_generator.py -v -m "performance"
```

### Run HTML Generation Tests
```bash
python -m pytest tests/unit/test_report_generator.py -v -m "html_generation"
```

### Run Markdown Generation Tests
```bash
python -m pytest tests/unit/test_report_generator.py -v -m "markdown_generation"
```

### Combine Multiple Marks (AND operation)
```bash
python -m pytest tests/unit/test_report_generator.py -v -m "html_generation and multi_sheet"
```

### Combine Multiple Marks (OR operation)
```bash
python -m pytest tests/unit/test_report_generator.py -v -m "positive or negative"
```

### Exclude Certain Marks
```bash
python -m pytest tests/unit/test_report_generator.py -v -m "not performance"
```

### Complex Mark Combinations
```bash
# Run positive tests for either HTML or Markdown generation
python -m pytest tests/unit/test_report_generator.py -v -m "positive and (html_generation or markdown_generation)"

# Run all edge cases except performance tests
python -m pytest tests/unit/test_report_generator.py -v -m "edge_case and not performance"

# Run multi-sheet tests that are not negative
python -m pytest tests/unit/test_report_generator.py -v -m "multi_sheet and not negative"
```

## Test Coverage by Category

### Positive Tests (10 tests)
- Initialization
- Basic HTML generation
- Basic Markdown generation
- Multi-sheet HTML generation
- Multi-sheet Markdown generation
- Statistics validation
- Structure validation
- Formatting validation
- Failure analysis
- Success scenarios

### Negative Tests (3 tests)
- Invalid execution ID
- Invalid Excel file
- Malformed test results

### Edge Cases (9 tests)
- Empty results
- None values
- Empty breakdowns
- Special characters
- Unicode characters
- Very long content
- Zero duration
- Extreme values
- Multiple edge conditions

### Performance Tests (2 tests)
- Large dataset processing
- Stress testing with many sheets

## Benefits of Using Pytest Marks

1. **Selective Testing**: Run only the tests you need during development
2. **CI/CD Optimization**: Run different test suites in different stages
3. **Debugging**: Isolate specific types of failures
4. **Documentation**: Marks serve as living documentation of test purposes
5. **Maintenance**: Easier to identify and update specific test categories
6. **Reporting**: Better test reporting and analysis

## Best Practices

1. **Use Multiple Marks**: Apply multiple relevant marks to each test
2. **Be Consistent**: Follow the established naming conventions
3. **Document Marks**: Keep this guide updated as new marks are added
4. **Test Combinations**: Regularly test different mark combinations
5. **CI Integration**: Use marks in CI/CD pipelines for efficient testing

## Mark Definitions in pytest.ini

All marks are properly registered in `tests/pytest.ini` to avoid warnings:

```ini
markers=
    positive: Positive tests to ensure expected behavior
    negative: Negative tests to ensure proper error handling
    edge_case: Tests for boundary conditions and unusual scenarios
    performance: Performance and load tests
    html_generation: Tests specific to HTML report generation
    markdown_generation: Tests specific to Markdown report generation
    multi_sheet: Tests for multi-sheet report functionality
    statistics: Tests for statistical calculations
    formatting: Tests for output formatting
    failure_analysis: Tests for failure analysis features
    success_scenario: Tests for all-pass scenarios
    special_characters: Tests for special character handling
    unicode_handling: Tests for Unicode character support
    large_dataset: Tests with large amounts of data
    stress_test: High-load stress testing
    # ... and more
```

This comprehensive marking system makes the test suite more maintainable, efficient, and easier to understand.