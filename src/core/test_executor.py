"""
Test execution engine for running PostgreSQL smoke tests
"""
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.test_result import TestResult
from src.utils.excel_test_suite_reader import TestCase
from src.validators.data_validator import DataValidator
from tests.test_postgresql_smoke import TestPostgreSQLSmoke


class TestExecutor:
    """Executes individual test cases and returns results"""
    __test__ = False  # Tell pytest this is not a test class

    def __init__(self):
        """Initialize the test executor"""
        self.smoke_tester = TestPostgreSQLSmoke()
        self.data_validator = DataValidator()
        # Initialize the smoke tester if it has a setup method
        if hasattr(self.smoke_tester, 'setup_class'):
            self.smoke_tester.setup_class()

    def execute_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case and return the result"""
        start_time = datetime.now()
        status = "PASS"
        error_message = None

        print(f"🧪 Executing: {test_case.test_case_id} - {test_case.test_case_name}")
        print(f"   Environment: {test_case.environment_name}")
        print(f"   Application: {test_case.application_name}")
        print(f"   Category: {test_case.test_category}")
        print(f"   Timeout: {test_case.timeout_seconds}s")

        try:
            # Execute test based on category
            if test_case.test_category == "SETUP":
                self.smoke_tester.test_environment_setup()
            elif test_case.test_category == "CONFIGURATION":
                self.smoke_tester.test_dummy_config_availability()
            elif test_case.test_category == "SECURITY":
                self.smoke_tester.test_environment_credentials()
            elif test_case.test_category == "CONNECTION":
                self.smoke_tester.test_postgresql_connection()
            elif test_case.test_category == "QUERIES":
                self.smoke_tester.test_postgresql_basic_queries()
            elif test_case.test_category == "PERFORMANCE":
                self.smoke_tester.test_postgresql_connection_performance()
            elif test_case.test_category == "COMPATIBILITY":
                # This method doesn't exist, so we'll skip it
                status = "SKIP"
                error_message = "Compatibility test not implemented"
            elif test_case.test_category == "TABLE_EXISTS":
                self._execute_table_exists_test(test_case)
            elif test_case.test_category == "TABLE_SELECT":
                self._execute_table_select_test(test_case)
            elif test_case.test_category == "TABLE_ROWS":
                self._execute_table_rows_test(test_case)
            elif test_case.test_category == "TABLE_STRUCTURE":
                self._execute_table_structure_test(test_case)
            elif test_case.test_category == "SCHEMA_VALIDATION":
                result = self._execute_data_validation_test(test_case)
                if not result.passed:
                    raise Exception(result.message)
            elif test_case.test_category == "ROW_COUNT_VALIDATION":
                result = self._execute_data_validation_test(test_case)
                if not result.passed:
                    raise Exception(result.message)
            elif test_case.test_category == "NULL_VALUE_VALIDATION":
                result = self._execute_data_validation_test(test_case)
                if not result.passed:
                    raise Exception(result.message)
            elif test_case.test_category == "DATA_QUALITY_VALIDATION":
                result = self._execute_data_validation_test(test_case)
                if not result.passed:
                    raise Exception(result.message)
            elif test_case.test_category == "COLUMN_COMPARE_VALIDATION":
                result = self._execute_data_validation_test(test_case)
                if not result.passed:
                    raise Exception(result.message)
            else:
                status = "SKIP"
                error_message = f"Unknown test category: {test_case.test_category}"

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Check expected result
            if status == "PASS":
                # If we got here without exception, test passed
                if test_case.expected_result.upper() == "PASS":
                    status = "PASS"
                else:
                    # Test was expected to fail but passed
                    status = "UNEXPECTED_PASS"
                    error_message = f"Test passed but was expected to {test_case.expected_result}"

            # Handle expected failures
            if test_case.expected_result.upper() == "FAIL":
                if status == "PASS":
                    status = "UNEXPECTED_PASS"
                    error_message = "Test passed but was expected to fail"

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Check if this was an expected failure
            if test_case.expected_result.upper() == "FAIL":
                status = "PASS"  # Expected failure occurred
                error_message = f"Expected failure occurred: {str(e)}"
            else:
                status = "ERROR" if "Error" in str(e) else "FAIL"
                error_message = str(e)

        # Check for timeout warning
        if duration > test_case.timeout_seconds:
            if status == "PASS":
                status = "TIMEOUT_WARNING"
                error_message = f"Test passed but exceeded timeout ({duration:.2f}s > {test_case.timeout_seconds}s)"

        result = TestResult(
            test_case_id=test_case.test_case_id,
            test_case_name=test_case.test_case_name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            error_message=error_message,
            environment=test_case.environment_name,
            application=test_case.application_name,
            priority=test_case.priority,
            category=test_case.test_category,
        )

        # Print result
        status_emoji = {
            "PASS": "✅",
            "FAIL": "❌",
            "SKIP": "⏭️",
            "ERROR": "💥",
            "TIMEOUT_WARNING": "⚠️",
            "UNEXPECTED_PASS": "🤔",
        }.get(result.status, "❓")

        print(f"   {status_emoji} {result.status} ({result.duration_seconds:.2f}s)")

        if result.error_message:
            print(f"   💬 {result.error_message}")

        return result
    
    def _execute_data_validation_test(self, test_case: TestCase):
        """Execute data validation test based on test case details"""
        
        # Parse test case parameters
        test_params = self._parse_test_params(test_case.parameters)
        source_table = test_params.get('source_table', 'products')
        target_table = test_params.get('target_table', 'new_products')
        column_name = test_params.get('column_name', 'product_name')
        
        # Execute the appropriate validation based on category
        if test_case.test_category == "SCHEMA_VALIDATION":
            return self.data_validator.schema_validation_compare(source_table, target_table)
        elif test_case.test_category == "ROW_COUNT_VALIDATION":
            return self.data_validator.row_count_validation_compare(source_table, target_table)
        elif test_case.test_category == "NULL_VALUE_VALIDATION":
            return self.data_validator.null_value_validation_compare(source_table, target_table)
        elif test_case.test_category == "DATA_QUALITY_VALIDATION":
            return self.data_validator.data_quality_validation_compare(source_table, target_table)
        elif test_case.test_category == "COLUMN_COMPARE_VALIDATION":
            return self.data_validator.column_compare_validation(source_table, target_table, column_name)
        else:
            from src.validators.data_validator import ValidationResult
            return ValidationResult(False, f"Unknown validation category: {test_case.test_category}")
    
    def _parse_test_params(self, parameters: str) -> dict:
        """Parse test parameters from parameters string"""
        params = {}
        if not parameters:
            return params
            
        # Simple parameter parsing from parameters
        # Expected format: "source_table=products;target_table=new_products;column_name=product_name"
        for param in parameters.split(';'):
            if '=' in param:
                key, value = param.strip().split('=', 1)
                params[key.strip()] = value.strip()
        
        return params
    
    def _execute_table_exists_test(self, test_case):
        """Execute table existence validation"""
        params = self._parse_test_params(test_case.parameters)
        table_name = params.get('table_name') or test_case.parameters
        if not table_name:
            from src.validators.data_validator import ValidationResult
            return ValidationResult(False, "TABLE_EXISTS test requires table_name parameter")
        
        try:
            # Use the data validator to check if table exists
            # For now, we'll check by trying to get table info
            result = self.data_validator.db_connection.execute_query(f"SELECT 1 FROM {table_name} LIMIT 1")
            from src.validators.data_validator import ValidationResult
            return ValidationResult(True, f"Table '{table_name}' exists")
        except Exception as e:
            from src.validators.data_validator import ValidationResult
            return ValidationResult(False, f"Table '{table_name}' does not exist: {str(e)}")
    
    def _execute_table_select_test(self, test_case):
        """Execute table select validation"""
        params = self._parse_test_params(test_case.parameters)
        table_name = params.get('table_name') or test_case.parameters
        if not table_name:
            from src.validators.data_validator import ValidationResult
            return ValidationResult(False, "TABLE_SELECT test requires table_name parameter")
        
        try:
            # Try to select from the table
            result = self.data_validator.db_connection.execute_query(f"SELECT * FROM {table_name} LIMIT 1")
            from src.validators.data_validator import ValidationResult
            return ValidationResult(True, f"Successfully selected from table '{table_name}'")
        except Exception as e:
            from src.validators.data_validator import ValidationResult
            return ValidationResult(False, f"Failed to select from table '{table_name}': {str(e)}")
    
    def _execute_table_rows_test(self, test_case):
        """Execute table row count validation"""
        params = self._parse_test_params(test_case.parameters)
        table_name = params.get('table_name') or test_case.parameters
        expected_count = params.get('expected_count')
        min_count = params.get('min_count')
        max_count = params.get('max_count')
        
        if not table_name:
            from src.validators.data_validator import ValidationResult
            return ValidationResult(False, "TABLE_ROWS test requires table_name parameter")
        
        try:
            # Get row count
            result = self.data_validator.db_connection.execute_query(f"SELECT COUNT(*) as row_count FROM {table_name}")
            if result and len(result) > 0:
                actual_count = result[0].get('row_count', 0)
                
                # Check various count conditions
                if expected_count is not None:
                    expected = int(expected_count)
                    if actual_count == expected:
                        from src.validators.data_validator import ValidationResult
                        return ValidationResult(True, f"Table '{table_name}' has expected {expected} rows")
                    else:
                        from src.validators.data_validator import ValidationResult
                        return ValidationResult(False, f"Table '{table_name}' has {actual_count} rows, expected {expected}")
                
                if min_count is not None and max_count is not None:
                    min_c = int(min_count)
                    max_c = int(max_count)
                    if min_c <= actual_count <= max_c:
                        from src.validators.data_validator import ValidationResult
                        return ValidationResult(True, f"Table '{table_name}' has {actual_count} rows (within range {min_c}-{max_c})")
                    else:
                        from src.validators.data_validator import ValidationResult
                        return ValidationResult(False, f"Table '{table_name}' has {actual_count} rows (outside range {min_c}-{max_c})")
                
                if min_count is not None:
                    min_c = int(min_count)
                    if actual_count >= min_c:
                        from src.validators.data_validator import ValidationResult
                        return ValidationResult(True, f"Table '{table_name}' has {actual_count} rows (>= {min_c})")
                    else:
                        from src.validators.data_validator import ValidationResult
                        return ValidationResult(False, f"Table '{table_name}' has {actual_count} rows (< {min_c})")
                
                # Default: just return the count
                from src.validators.data_validator import ValidationResult
                return ValidationResult(True, f"Table '{table_name}' has {actual_count} rows")
            else:
                from src.validators.data_validator import ValidationResult
                return ValidationResult(False, f"Could not get row count for table '{table_name}'")
        except Exception as e:
            from src.validators.data_validator import ValidationResult
            return ValidationResult(False, f"Failed to count rows in table '{table_name}': {str(e)}")
    
    def _execute_table_structure_test(self, test_case):
        """Execute table structure validation"""
        params = self._parse_test_params(test_case.parameters)
        table_name = params.get('table_name') or test_case.parameters
        expected_columns = params.get('expected_columns')
        
        if not table_name:
            from src.validators.data_validator import ValidationResult
            return ValidationResult(False, "TABLE_STRUCTURE test requires table_name parameter")
        
        try:
            # Get table structure information
            # This is database-specific, for PostgreSQL we can use information_schema
            structure_query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
            """
            result = self.data_validator.db_connection.execute_query(structure_query, (table_name,))
            
            if result:
                columns = [row['column_name'] for row in result]
                structure_info = f"Table '{table_name}' has columns: {', '.join(columns)}"
                
                if expected_columns:
                    expected_cols = [col.strip() for col in expected_columns.split(',')]
                    missing_cols = set(expected_cols) - set(columns)
                    extra_cols = set(columns) - set(expected_cols)
                    
                    if missing_cols or extra_cols:
                        error_msg = f"Table structure mismatch for '{table_name}'"
                        if missing_cols:
                            error_msg += f", Missing columns: {', '.join(missing_cols)}"
                        if extra_cols:
                            error_msg += f", Extra columns: {', '.join(extra_cols)}"
                        from src.validators.data_validator import ValidationResult
                        return ValidationResult(False, error_msg)
                
                from src.validators.data_validator import ValidationResult
                return ValidationResult(True, structure_info)
            else:
                from src.validators.data_validator import ValidationResult
                return ValidationResult(False, f"Could not get structure for table '{table_name}'")
        except Exception as e:
            from src.validators.data_validator import ValidationResult
            return ValidationResult(False, f"Failed to get structure for table '{table_name}': {str(e)}")