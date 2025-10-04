"""
Simplified unit tests for ExcelTestDriver class focusing on testable methods
"""
import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from src.core.excel_test_driver import ExcelTestDriver


class TestExcelTestDriverSimple(unittest.TestCase):
    """Simplified test cases for ExcelTestDriver class"""

    def setUp(self):
        """Set up test fixtures"""
        self.excel_file = "test_suite.xlsx"
        self.driver = ExcelTestDriver(self.excel_file)

    def test_initialization(self):
        """Test ExcelTestDriver initialization"""
        self.assertEqual(self.driver.excel_file, "test_suite.xlsx")
        self.assertIsNotNone(self.driver.execution_id)
        self.assertTrue(self.driver.execution_id.startswith("RUN_"))

    def test_execution_id_format(self):
        """Test execution ID format"""
        execution_id = self.driver.execution_id
        
        # Should start with "RUN_" and be followed by timestamp
        self.assertTrue(execution_id.startswith("RUN_"))
        self.assertEqual(len(execution_id), 19)  # "RUN_" + "YYYYMMDD_HHMMSS"

    @patch('builtins.print')
    def test_print_summary_empty_results(self, mock_print):
        """Test summary printing with empty results"""
        self.driver.results = []
        self.driver.print_summary()
        
        # Should not print anything for empty results
        mock_print.assert_not_called()

    @patch('builtins.print')
    def test_print_summary_with_results(self, mock_print):
        """Test summary printing with mock results"""
        # Create mock results
        mock_result = Mock()
        mock_result.status = "PASS"
        mock_result.duration_seconds = 1.0
        mock_result.test_case_id = "TEST_001"
        mock_result.test_case_name = "Sample Test"
        mock_result.environment = "DEV"
        mock_result.application = "DUMMY"
        mock_result.error_message = None
        
        self.driver.results = [mock_result]
        self.driver.print_summary()
        
        # Verify print was called
        self.assertTrue(mock_print.called)

    def test_save_reports_empty_results(self):
        """Test report generation with empty results"""
        self.driver.results = []
        reports = self.driver.save_reports()
        
        # Should return empty dict for no results
        self.assertEqual(reports, {})

    @patch('src.core.excel_test_driver.HtmlReportGenerator')
    @patch('src.core.excel_test_driver.MarkdownReportGenerator')
    def test_save_reports_success(self, mock_md_gen, mock_html_gen):
        """Test successful report generation"""
        # Mock generators
        mock_html_instance = Mock()
        mock_html_instance.generate_report.return_value = "report.html"
        mock_html_gen.return_value = mock_html_instance
        
        mock_md_instance = Mock()
        mock_md_instance.generate_report.return_value = "report.md"
        mock_md_gen.return_value = mock_md_instance
        
        # Create mock results
        mock_result = Mock()
        self.driver.results = [mock_result]
        
        reports = self.driver.save_reports()
        
        self.assertEqual(reports['html'], "report.html")
        self.assertEqual(reports['markdown'], "report.md")


if __name__ == '__main__':
    unittest.main()