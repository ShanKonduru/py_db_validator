"""
Main Excel Test Driver class that orchestrates test execution and reporting
"""
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.test_result import TestResult
from src.core.test_executor import TestExecutor
from src.utils.excel_test_suite_reader import ExcelTestSuiteReader, TestCase
from src.reporting.html_report_generator import HtmlReportGenerator
from src.reporting.markdown_report_generator import MarkdownReportGenerator


class ExcelTestDriver:
    """Excel-driven test execution engine"""

    def __init__(self, excel_file: str = "sdm_test_suite.xlsx"):
        """Initialize the test driver"""
        self.excel_file = excel_file
        self.reader = ExcelTestSuiteReader(excel_file)
        self.executor = TestExecutor()
        self.results: List[TestResult] = []
        self.execution_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def load_test_suite(self) -> bool:
        """Load the Excel test suite"""
        print(f"📊 Loading Excel test suite: {self.excel_file}")
        
        try:
            test_cases = self.reader.get_all_test_cases()
            if not test_cases:
                print("❌ No test cases found in Excel file")
                return False
            
            # Print summary
            enabled_count = sum(1 for tc in test_cases if tc.enable)
            disabled_count = len(test_cases) - enabled_count
            
            print(f"✅ Successfully loaded {len(test_cases)} test cases")
            print(f"   - Enabled: {enabled_count}")
            print(f"   - Disabled: {disabled_count}")
            
            # Print statistics
            priorities = {}
            categories = {}
            environments = {}
            applications = {}
            
            for tc in test_cases:
                if tc.enable:
                    priorities[tc.priority] = priorities.get(tc.priority, 0) + 1
                    categories[tc.test_category] = categories.get(tc.test_category, 0) + 1
                    environments[tc.environment_name] = environments.get(tc.environment_name, 0) + 1
                    applications[tc.application_name] = applications.get(tc.application_name, 0) + 1
            
            print(f"   - Priorities: {priorities}")
            print(f"   - Categories: {categories}")
            print(f"   - Environments: {environments}")
            print(f"   - Applications: {applications}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to load Excel test suite: {e}")
            return False

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
        
        # Get filtered test cases
        if test_ids:
            test_cases = self.reader.get_test_cases_by_ids(test_ids)
        else:
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
            result = self.executor.execute_test_case(test_case)
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

    def save_reports(self, output_dir: str = "test_reports") -> Dict[str, str]:
        """Generate both HTML and Markdown reports"""
        if not self.results:
            return {}
        
        reports = {}
        
        try:
            html_generator = HtmlReportGenerator(self.execution_id, self.excel_file)
            html_file = html_generator.generate_report(self.results, output_dir)
            if html_file:
                reports['html'] = html_file
                print(f"📄 HTML Report: {html_file}")
        except Exception as e:
            print(f"❌ Error generating HTML report: {e}")
        
        try:
            md_generator = MarkdownReportGenerator(self.execution_id, self.excel_file)
            md_file = md_generator.generate_report(self.results, output_dir)
            if md_file:
                reports['markdown'] = md_file
                print(f"📝 Markdown Report: {md_file}")
        except Exception as e:
            print(f"❌ Error generating Markdown report: {e}")
        
        return reports