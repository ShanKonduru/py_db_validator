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
from tests.test_postgresql_smoke import TestPostgreSQLSmoke


class TestExecutor:
    """Executes individual test cases and returns results"""

    def __init__(self):
        """Initialize the test executor"""
        self.smoke_tester = TestPostgreSQLSmoke()

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
                self.smoke_tester.test_configuration_availability()
            elif test_case.test_category == "SECURITY":
                self.smoke_tester.test_credentials_validation()
            elif test_case.test_category == "CONNECTION":
                self.smoke_tester.test_database_connectivity()
            elif test_case.test_category == "QUERIES":
                self.smoke_tester.test_basic_database_queries()
            elif test_case.test_category == "PERFORMANCE":
                self.smoke_tester.test_connection_performance()
            elif test_case.test_category == "COMPATIBILITY":
                self.smoke_tester.test_backwards_compatibility()
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