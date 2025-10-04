#!/usr/bin/env python
"""
Excel-Driven Test Suite Driver
Executes PostgreSQL smoke tests based on sdm_test_suite.xlsx configuration
"""
import sys
import os
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.excel_test_suite_reader import ExcelTestSuiteReader, TestCase
from tests.test_postgresql_smoke import TestPostgreSQLSmoke


@dataclass
class TestResult:
    """Data class for test execution results"""

    test_case_id: str
    test_case_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    error_message: str
    environment: str
    application: str


class ExcelTestDriver:
    """Excel-driven test execution engine"""

    def __init__(self, excel_file: str = "sdm_test_suite.xlsx"):
        """Initialize the test driver"""
        self.excel_file = excel_file
        self.reader = ExcelTestSuiteReader(excel_file)
        self.results: List[TestResult] = []
        self.execution_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def load_test_suite(self) -> bool:
        """Load and validate the Excel test suite"""
        return self.reader.load_and_validate()

    def execute_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case"""
        print(f"\n🧪 Executing: {test_case.test_case_id} - {test_case.test_case_name}")
        print(f"   Environment: {test_case.environment_name}")
        print(f"   Application: {test_case.application_name}")
        print(f"   Category: {test_case.test_category}")
        print(f"   Timeout: {test_case.timeout_seconds}s")

        start_time = datetime.now()
        status = "ERROR"
        error_message = ""

        try:
            # Set environment variables for test configuration
            if test_case.environment_name:
                os.environ["TEST_ENVIRONMENT"] = test_case.environment_name
            if test_case.application_name:
                os.environ["TEST_APPLICATION"] = test_case.application_name

            # Create test suite instance
            test_suite = TestPostgreSQLSmoke()
            test_suite.setup_class()

            # Map test categories to actual test methods
            test_method_map = {
                "SETUP": test_suite.test_environment_setup,
                "CONFIGURATION": test_suite.test_dummy_config_availability,
                "SECURITY": test_suite.test_environment_credentials,
                "CONNECTION": test_suite.test_postgresql_connection,
                "QUERIES": test_suite.test_postgresql_basic_queries,
                "PERFORMANCE": test_suite.test_postgresql_connection_performance,
                "COMPATIBILITY": self._run_compatibility_test,
            }

            # Execute the appropriate test method
            test_method = test_method_map.get(test_case.test_category.upper())
            if test_method:
                if test_case.test_category.upper() == "COMPATIBILITY":
                    test_method(test_suite)
                else:
                    test_method()

                # If we got here without exception, test passed
                status = (
                    "PASS"
                    if test_case.expected_result.upper() == "PASS"
                    else "UNEXPECTED_PASS"
                )

            else:
                status = "SKIP"
                error_message = f"Unknown test category: {test_case.test_category}"

        except AssertionError as e:
            if test_case.expected_result.upper() == "FAIL":
                status = "PASS"  # Expected failure
                error_message = f"Expected failure: {str(e)}"
            else:
                status = "FAIL"
                error_message = str(e)

        except Exception as e:
            status = "ERROR"
            error_message = f"Unexpected error: {str(e)}"

        finally:
            # Clean up environment variables
            if "TEST_ENVIRONMENT" in os.environ:
                del os.environ["TEST_ENVIRONMENT"]
            if "TEST_APPLICATION" in os.environ:
                del os.environ["TEST_APPLICATION"]

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Check timeout
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
        )

        # Print result
        status_emoji = {
            "PASS": "✅",
            "FAIL": "❌",
            "SKIP": "⏭️",
            "ERROR": "💥",
            "TIMEOUT_WARNING": "⚠️",
            "UNEXPECTED_PASS": "🤔",
        }.get(status, "❓")

        print(f"   {status_emoji} {status} ({duration:.2f}s)")
        if error_message:
            print(f"   💬 {error_message}")

        return result

    def _run_compatibility_test(self, test_suite: TestPostgreSQLSmoke):
        """Run the backwards compatibility test"""
        # Execute all the core tests in sequence
        test_suite.test_environment_setup()
        test_suite.test_dummy_config_availability()
        test_suite.test_environment_credentials()
        test_suite.test_postgresql_connection()

    def execute_test_suite(
        self,
        environment: Optional[str] = None,
        application: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        test_ids: Optional[List[str]] = None,
    ) -> List[TestResult]:
        """Execute test suite with optional filters"""

        # Get test cases to execute
        if test_ids:
            # Execute specific test IDs
            test_cases = []
            for test_id in test_ids:
                test_case = self.reader.get_test_case_by_id(test_id)
                if test_case:
                    if test_case.is_enabled():
                        test_cases.append(test_case)
                    else:
                        print(f"⚠️  Test {test_id} is disabled, skipping")
                else:
                    print(f"❌ Test {test_id} not found")
        else:
            # Use filters
            test_cases = self.reader.get_filtered_test_cases(
                environment=environment,
                application=application,
                priority=priority,
                category=category,
                tags=tags,
                enabled_only=True,
            )

        if not test_cases:
            print("❌ No test cases match the specified criteria")
            return []

        print(f"\n🚀 Starting test execution: {self.execution_id}")
        print(f"📊 Tests to execute: {len(test_cases)}")
        print("=" * 80)

        # Execute tests
        self.results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}]", end=" ")
            result = self.execute_test_case(test_case)
            self.results.append(result)

        return self.results

    def print_summary(self):
        """Print execution summary"""
        if not self.results:
            return

        print("\n" + "=" * 80)
        print(f"📋 TEST EXECUTION SUMMARY - {self.execution_id}")
        print("=" * 80)

        # Count results by status
        status_counts = {}
        total_duration = 0

        for result in self.results:
            status = result.status
            status_counts[status] = status_counts.get(status, 0) + 1
            total_duration += result.duration_seconds

        # Print statistics
        total_tests = len(self.results)
        passed_tests = status_counts.get("PASS", 0)
        failed_tests = status_counts.get("FAIL", 0) + status_counts.get("ERROR", 0)
        skipped_tests = status_counts.get("SKIP", 0)

        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏭️ Skipped: {skipped_tests}")
        print(f"⏱️ Total Duration: {total_duration:.2f}s")
        print(
            f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%"
            if total_tests > 0
            else ""
        )

        # Print detailed results
        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)

        for result in self.results:
            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌",
                "SKIP": "⏭️",
                "ERROR": "💥",
                "TIMEOUT_WARNING": "⚠️",
                "UNEXPECTED_PASS": "🤔",
            }.get(result.status, "❓")

            print(f"{status_emoji} {result.test_case_id}: {result.test_case_name}")
            print(
                f"   Status: {result.status} | Duration: {result.duration_seconds:.2f}s"
            )
            print(
                f"   Environment: {result.environment} | Application: {result.application}"
            )

            if result.error_message:
                print(f"   Message: {result.error_message}")
            print()

        print("=" * 80)


def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Execute PostgreSQL smoke tests from Excel test suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python excel_test_driver.py                              # Run all enabled tests
  python excel_test_driver.py --environment DEV            # Run DEV environment tests
  python excel_test_driver.py --priority HIGH              # Run high priority tests only
  python excel_test_driver.py --category CONNECTION        # Run connection tests only
  python excel_test_driver.py --tags smoke,db              # Run tests with specific tags
  python excel_test_driver.py --test-ids SMOKE_PG_001,SMOKE_PG_004  # Run specific tests
  python excel_test_driver.py --excel-file my_tests.xlsx   # Use custom Excel file
        """,
    )

    parser.add_argument(
        "--excel-file",
        "-f",
        default="sdm_test_suite.xlsx",
        help="Path to Excel test suite file (default: sdm_test_suite.xlsx)",
    )

    parser.add_argument(
        "--environment", "-e", help="Filter by environment (e.g., DEV, STAGING, PROD)"
    )

    parser.add_argument(
        "--application", "-a", help="Filter by application (e.g., DUMMY, MYAPP)"
    )

    parser.add_argument(
        "--priority",
        "-p",
        choices=["HIGH", "MEDIUM", "LOW"],
        help="Filter by priority level",
    )

    parser.add_argument(
        "--category",
        "-c",
        help="Filter by test category (e.g., CONNECTION, QUERIES, PERFORMANCE)",
    )

    parser.add_argument(
        "--tags",
        "-t",
        help="Filter by tags (comma-separated, e.g., smoke,db,integration)",
    )

    parser.add_argument(
        "--test-ids",
        "-i",
        help="Run specific test IDs (comma-separated, e.g., SMOKE_PG_001,SMOKE_PG_004)",
    )

    parser.add_argument(
        "--list-tests",
        "-l",
        action="store_true",
        help="List available tests without executing them",
    )

    return parser


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Create test driver
    driver = ExcelTestDriver(args.excel_file)

    # Load test suite
    if not driver.load_test_suite():
        print("❌ Failed to load Excel test suite")
        return 1

    # Parse tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",")]

    # Parse test IDs
    test_ids = None
    if args.test_ids:
        test_ids = [tid.strip() for tid in args.test_ids.split(",")]

    # List tests mode
    if args.list_tests:
        test_cases = driver.reader.get_filtered_test_cases(
            environment=args.environment,
            application=args.application,
            priority=args.priority,
            category=args.category,
            tags=tags,
            enabled_only=True,
        )

        print(f"\n📋 Available Tests ({len(test_cases)} found):")
        print("-" * 80)

        for tc in test_cases:
            print(f"🧪 {tc.test_case_id}: {tc.test_case_name}")
            print(
                f"   Environment: {tc.environment_name} | Application: {tc.application_name}"
            )
            print(f"   Priority: {tc.priority} | Category: {tc.test_category}")
            print(f"   Tags: {tc.tags}")
            print(f"   Enabled: {'✅' if tc.enable else '❌'}")
            print()

        return 0

    # Execute tests
    try:
        results = driver.execute_test_suite(
            environment=args.environment,
            application=args.application,
            priority=args.priority,
            category=args.category,
            tags=tags,
            test_ids=test_ids,
        )

        # Print summary
        driver.print_summary()

        # Return appropriate exit code
        if not results:
            return 1

        failed_count = sum(1 for r in results if r.status in ["FAIL", "ERROR"])
        return 1 if failed_count > 0 else 0

    except KeyboardInterrupt:
        print("\n⏹️ Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
