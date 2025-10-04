"""
Simplified unit tests for report generators focusing on testable methods
"""
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from src.reporting.html_report_generator import HtmlReportGenerator
from src.reporting.markdown_report_generator import MarkdownReportGenerator
from src.models.test_result import TestResult


class TestReportGeneratorsSimple(unittest.TestCase):
    """Simplified test cases for report generators"""

    def setUp(self):
        """Set up test fixtures"""
        self.execution_id = "RUN_20251003_120000"
        self.excel_file = "test_suite.xlsx"
        
        # Create sample test result
        self.test_result = TestResult(
            test_case_id="TEST_001",
            test_case_name="Sample Test",
            status="PASS",
            start_time=datetime(2025, 10, 3, 12, 0, 0),
            end_time=datetime(2025, 10, 3, 12, 0, 2),
            duration_seconds=2.0,
            error_message=None,
            environment="DEV",
            application="DUMMY",
            priority="HIGH",
            category="CONNECTION"
        )

    def test_html_generator_initialization(self):
        """Test HTML generator initialization"""
        generator = HtmlReportGenerator(self.execution_id, self.excel_file)
        self.assertEqual(generator.execution_id, self.execution_id)
        self.assertEqual(generator.excel_file, self.excel_file)

    def test_markdown_generator_initialization(self):
        """Test Markdown generator initialization"""
        generator = MarkdownReportGenerator(self.execution_id, self.excel_file)
        self.assertEqual(generator.execution_id, self.execution_id)
        self.assertEqual(generator.excel_file, self.excel_file)

    def test_html_generator_empty_results(self):
        """Test HTML generator with empty results"""
        generator = HtmlReportGenerator(self.execution_id, self.excel_file)
        result = generator.generate_report([], "test_output")
        self.assertEqual(result, "")

    def test_markdown_generator_empty_results(self):
        """Test Markdown generator with empty results"""
        generator = MarkdownReportGenerator(self.execution_id, self.excel_file)
        result = generator.generate_report([], "test_output")
        self.assertEqual(result, "")

    def test_html_statistics_calculation(self):
        """Test HTML generator statistics calculation"""
        generator = HtmlReportGenerator(self.execution_id, self.excel_file)
        stats = generator._calculate_statistics([self.test_result])
        
        self.assertEqual(stats['total_tests'], 1)
        self.assertEqual(stats['passed_tests'], 1)
        self.assertEqual(stats['failed_tests'], 0)
        self.assertEqual(stats['skipped_tests'], 0)
        self.assertEqual(stats['success_rate'], 100.0)

    def test_markdown_statistics_calculation(self):
        """Test Markdown generator statistics calculation"""
        generator = MarkdownReportGenerator(self.execution_id, self.excel_file)
        stats = generator._calculate_statistics([self.test_result])
        
        self.assertEqual(stats['total_tests'], 1)
        self.assertEqual(stats['passed_tests'], 1)
        self.assertEqual(stats['failed_tests'], 0)
        self.assertEqual(stats['skipped_tests'], 0)
        self.assertEqual(stats['success_rate'], 100.0)

    def test_markdown_header_generation(self):
        """Test Markdown header generation"""
        generator = MarkdownReportGenerator(self.execution_id, self.excel_file)
        header = generator._generate_header()
        
        # Should contain execution info (check for partial match)
        self.assertIn("Test Execution Report", header)

    def test_markdown_group_by_status(self):
        """Test Markdown result grouping by status"""
        generator = MarkdownReportGenerator(self.execution_id, self.excel_file)
        grouped = generator._group_results_by_status([self.test_result])
        
        self.assertIn("passed", grouped)  # lowercase key
        self.assertEqual(len(grouped["passed"]), 1)
        self.assertEqual(grouped["passed"][0], self.test_result)


if __name__ == '__main__':
    unittest.main()