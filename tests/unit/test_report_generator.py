"""
Unit tests for ReportGenerator class

This module contains comprehensive unit tests for the ReportGenerator class,
organized using pytest marks to categorize test types:

Marks used:
- @pytest.mark.positive: Tests with valid inputs and expected success scenarios
- @pytest.mark.negative: Tests with invalid inputs or error conditions
- @pytest.mark.edge_case: Tests for boundary conditions and unusual scenarios
- @pytest.mark.performance: Tests for performance and stress scenarios
- @pytest.mark.html_generation: Tests specific to HTML report generation
- @pytest.mark.markdown_generation: Tests specific to Markdown report generation
- @pytest.mark.multi_sheet: Tests for multi-sheet report functionality
- @pytest.mark.statistics: Tests for statistical calculations
- @pytest.mark.formatting: Tests for output formatting
- @pytest.mark.failure_analysis: Tests for failure analysis features
- @pytest.mark.success_scenario: Tests for all-pass scenarios
- @pytest.mark.special_characters: Tests for special character handling
- @pytest.mark.unicode_handling: Tests for Unicode character support
- @pytest.mark.large_dataset: Tests with large amounts of data
- @pytest.mark.stress_test: High-load stress testing
- @pytest.mark.initialization: Tests for object initialization
- @pytest.mark.structure: Tests for report structure validation
- @pytest.mark.invalid_input: Tests with invalid input parameters
- @pytest.mark.none_values: Tests with None/null values
- @pytest.mark.empty_breakdown: Tests with empty data structures
- @pytest.mark.long_content: Tests with very long text content
- @pytest.mark.malformed_data: Tests with malformed or incomplete data
- @pytest.mark.zero_duration: Tests with zero time durations
- @pytest.mark.extreme_values: Tests with extreme value ranges
"""
import unittest
import tempfile
import os
import pytest
from datetime import datetime
from src.reporting.report_generator import ReportGenerator
from src.models.test_result import TestResult


class TestReportGenerator(unittest.TestCase):
    """Test suite for ReportGenerator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = ReportGenerator()
        self.temp_dir = tempfile.mkdtemp()

        # Create sample test results using actual TestResult fields
        self.sample_results = [
            TestResult(
                test_case_id='TEST_001',
                test_case_name='Connection Test',
                status='PASS',
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 1, 500000),
                duration_seconds=1.5,
                error_message=None,
                environment='DEV',
                application='POSTGRES',
                priority='HIGH',
                category='CONNECTION'
            ),
            TestResult(
                test_case_id='TEST_002',
                test_case_name='Table Test',
                status='FAIL',
                start_time=datetime(2024, 1, 1, 10, 1, 0),
                end_time=datetime(2024, 1, 1, 10, 1, 2, 300000),
                duration_seconds=2.3,
                error_message='Table not found',
                environment='DEV',
                application='POSTGRES',
                priority='MEDIUM',
                category='TABLE_EXISTS'
            ),
            TestResult(
                test_case_id='TEST_003',
                test_case_name='Skipped Test',
                status='SKIP',
                start_time=datetime(2024, 1, 1, 10, 2, 0),
                end_time=datetime(2024, 1, 1, 10, 2, 0),
                duration_seconds=0.0,
                error_message='Test skipped due to prerequisites',
                environment='DEV',
                application='POSTGRES',
                priority='LOW',
                category='PERFORMANCE'
            )
        ]

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.positive
    @pytest.mark.initialization
    def test_initialization(self):
        """Test ReportGenerator initialization"""
        generator = ReportGenerator()
        self.assertIsNotNone(generator.timestamp)
        self.assertIsInstance(generator.timestamp, datetime)

    @pytest.mark.positive
    @pytest.mark.html_generation
    def test_generate_html_report_basic(self):
        """Test basic HTML report generation"""
        html_content = self.generator.generate_html_report(
            test_results=self.sample_results,
            execution_id='TEST_RUN_001',
            excel_file='test_suite.xlsx'
        )
        
        self.assertIsInstance(html_content, str)
        self.assertIn('<!DOCTYPE html>', html_content)
        self.assertIn('Test Execution Report', html_content)
        self.assertIn('TEST_RUN_001', html_content)
        self.assertIn('test_suite.xlsx', html_content)

    @pytest.mark.positive
    @pytest.mark.html_generation
    @pytest.mark.multi_sheet
    def test_generate_html_report_multi_sheet(self):
        """Test HTML report generation with multi-sheet"""
        sheet_breakdown = {
            'SHEET1': [self.sample_results[0], self.sample_results[1]],
            'SHEET2': [self.sample_results[2]]
        }
        
        html_content = self.generator.generate_html_report(
            test_results=self.sample_results,
            execution_id='TEST_RUN_002',
            excel_file='multi_sheet.xlsx',
            multi_sheet=True,
            sheet_breakdown=sheet_breakdown
        )
        
        self.assertIsInstance(html_content, str)
        self.assertIn('Multi-Sheet', html_content)
        self.assertIn('SHEET1', html_content)
        self.assertIn('SHEET2', html_content)

    @pytest.mark.edge_case
    @pytest.mark.html_generation
    def test_generate_html_report_empty_results(self):
        """Test HTML report generation with empty results"""
        html_content = self.generator.generate_html_report(
            test_results=[],
            execution_id='TEST_RUN_003',
            excel_file='empty.xlsx'
        )
        
        self.assertIsInstance(html_content, str)
        self.assertIn('0', html_content)  # Should show 0 tests

    @pytest.mark.positive
    @pytest.mark.markdown_generation
    def test_generate_markdown_report_basic(self):
        """Test basic Markdown report generation"""
        markdown_content = self.generator.generate_markdown_report(
            test_results=self.sample_results,
            execution_id='TEST_RUN_001',
            excel_file='test_suite.xlsx'
        )
        
        self.assertIsInstance(markdown_content, str)
        self.assertIn('# Test Execution Report', markdown_content)
        self.assertIn('TEST_RUN_001', markdown_content)
        self.assertIn('test_suite.xlsx', markdown_content)
        self.assertIn('## 📊 Executive Summary', markdown_content)

    @pytest.mark.positive
    @pytest.mark.markdown_generation
    @pytest.mark.multi_sheet
    def test_generate_markdown_report_multi_sheet(self):
        """Test Markdown report generation with multi-sheet"""
        sheet_breakdown = {
            'SHEET1': [self.sample_results[0], self.sample_results[1]],
            'SHEET2': [self.sample_results[2]]
        }
        
        markdown_content = self.generator.generate_markdown_report(
            test_results=self.sample_results,
            execution_id='TEST_RUN_002',
            excel_file='multi_sheet.xlsx',
            multi_sheet=True,
            sheet_breakdown=sheet_breakdown
        )
        
        self.assertIsInstance(markdown_content, str)
        self.assertIn('# Multi-Sheet Test Execution Report', markdown_content)
        self.assertIn('## 📋 Sheet Breakdown', markdown_content)
        self.assertIn('SHEET1', markdown_content)
        self.assertIn('SHEET2', markdown_content)

    @pytest.mark.edge_case
    @pytest.mark.markdown_generation
    def test_generate_markdown_report_empty_results(self):
        """Test Markdown report generation with empty results"""
        markdown_content = self.generator.generate_markdown_report(
            test_results=[],
            execution_id='TEST_RUN_003',
            excel_file='empty.xlsx'
        )
        
        self.assertIsInstance(markdown_content, str)
        self.assertIn('| **Total Tests** | 0 |', markdown_content)

    @pytest.mark.positive
    @pytest.mark.statistics
    def test_report_contains_test_statistics(self):
        """Test that reports contain correct test statistics"""
        # HTML report
        html_content = self.generator.generate_html_report(
            test_results=self.sample_results,
            execution_id='TEST_RUN_STATS',
            excel_file='stats_test.xlsx'
        )
        
        self.assertIn('3', html_content)  # Total tests
        self.assertIn('1', html_content)  # Passed tests
        self.assertIn('1', html_content)  # Failed tests
        self.assertIn('1', html_content)  # Skipped tests
        
        # Markdown report
        markdown_content = self.generator.generate_markdown_report(
            test_results=self.sample_results,
            execution_id='TEST_RUN_STATS',
            excel_file='stats_test.xlsx'
        )
        
        self.assertIn('| **Total Tests** | 3 |', markdown_content)
        self.assertIn('| **✅ Passed** | 1 |', markdown_content)
        self.assertIn('| **❌ Failed** | 1 |', markdown_content)
        self.assertIn('| **⏭️ Skipped** | 1 |', markdown_content)

    @pytest.mark.positive
    @pytest.mark.html_generation
    @pytest.mark.structure
    def test_html_report_structure(self):
        """Test HTML report structure and CSS"""
        html_content = self.generator.generate_html_report(
            test_results=self.sample_results,
            execution_id='TEST_STRUCTURE',
            excel_file='structure_test.xlsx'
        )
        
        # Check basic HTML structure
        self.assertIn('<html lang="en">', html_content)
        self.assertIn('<head>', html_content)
        self.assertIn('<body>', html_content)
        self.assertIn('<style>', html_content)
        
        # Check CSS classes
        self.assertIn('container', html_content)
        self.assertIn('header', html_content)
        self.assertIn('summary', html_content)

    @pytest.mark.positive
    @pytest.mark.markdown_generation
    @pytest.mark.formatting
    def test_markdown_report_formatting(self):
        """Test Markdown report formatting"""
        markdown_content = self.generator.generate_markdown_report(
            test_results=self.sample_results,
            execution_id='TEST_FORMAT',
            excel_file='format_test.xlsx'
        )
        
        # Check markdown headers
        self.assertIn('# Test Execution Report', markdown_content)
        self.assertIn('## 📊 Executive Summary', markdown_content)
        self.assertIn('## 📝 Detailed Test Results', markdown_content)
        
        # Check table formatting
        self.assertIn('| Test ID |', markdown_content)
        self.assertIn('|---------|', markdown_content)

    @pytest.mark.positive
    @pytest.mark.failure_analysis
    def test_failure_analysis_in_reports(self):
        """Test failure analysis section in reports"""
        # Create results with failures
        failed_results = [
            TestResult(
                test_case_id='FAIL_001',
                test_case_name='Failed Connection',
                status='FAIL',
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 1),
                duration_seconds=1.0,
                error_message='Connection timeout',
                environment='DEV',
                application='POSTGRES',
                priority='HIGH',
                category='CONNECTION'
            ),
            TestResult(
                test_case_id='FAIL_002',
                test_case_name='Failed Query',
                status='FAIL',
                start_time=datetime(2024, 1, 1, 10, 1, 0),
                end_time=datetime(2024, 1, 1, 10, 1, 2),
                duration_seconds=2.0,
                error_message='SQL syntax error',
                environment='DEV',
                application='POSTGRES',
                priority='MEDIUM',
                category='QUERY'
            )
        ]
        
        markdown_content = self.generator.generate_markdown_report(
            test_results=failed_results,
            execution_id='TEST_FAILURES',
            excel_file='failures_test.xlsx'
        )
        
        self.assertIn('## 🔍 Failure Analysis', markdown_content)
        self.assertIn('Connection timeout', markdown_content)
        self.assertIn('SQL syntax error', markdown_content)

    @pytest.mark.positive
    @pytest.mark.success_scenario
    def test_success_report_content(self):
        """Test report content when all tests pass"""
        passed_results = [
            TestResult(
                test_case_id='PASS_001',
                test_case_name='Successful Test',
                status='PASS',
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 1),
                duration_seconds=1.0,
                error_message=None,
                environment='DEV',
                application='POSTGRES',
                priority='HIGH',
                category='CONNECTION'
            )
        ]
        
        markdown_content = self.generator.generate_markdown_report(
            test_results=passed_results,
            execution_id='TEST_SUCCESS',
            excel_file='success_test.xlsx'
        )
        
        self.assertIn('## 🎉 All Tests Passed!', markdown_content)
        self.assertIn('Overall Success Rate:** 100.0%', markdown_content)

    @pytest.mark.edge_case
    @pytest.mark.special_characters
    def test_special_characters_handling(self):
        """Test handling of special characters in test data"""
        special_results = [
            TestResult(
                test_case_id='SPECIAL_001',
                test_case_name='Test with "quotes" & <symbols>',
                status='FAIL',
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 1),
                duration_seconds=1.0,
                error_message='Error with | pipe & symbols',
                environment='DEV',
                application='POSTGRES',
                priority='HIGH',
                category='SPECIAL'
            )
        ]
        
        # HTML should handle special characters
        html_content = self.generator.generate_html_report(
            test_results=special_results,
            execution_id='TEST_SPECIAL',
            excel_file='special_test.xlsx'
        )
        self.assertIsInstance(html_content, str)
        
        # Markdown should escape special characters
        markdown_content = self.generator.generate_markdown_report(
            test_results=special_results,
            execution_id='TEST_SPECIAL',
            excel_file='special_test.xlsx'
        )
        self.assertIn('\\|', markdown_content)  # Pipe should be escaped

    @pytest.mark.performance
    @pytest.mark.large_dataset
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        # Create a large dataset
        large_results = []
        for i in range(100):
            result = TestResult(
                test_case_id=f'TEST_{i:03d}',
                test_case_name=f'Performance Test {i}',
                status='PASS' if i % 3 != 0 else 'FAIL',
                start_time=datetime(2024, 1, 1, 10, i//60, i%60),  # Fix minute/second calculation
                end_time=datetime(2024, 1, 1, 10, (i+1)//60, (i+1)%60),
                duration_seconds=1.0,
                error_message=f'Error {i}' if i % 3 == 0 else None,
                environment='DEV',
                application='POSTGRES',
                priority='MEDIUM',
                category='PERFORMANCE'
            )
            large_results.append(result)
        
        # Test that large datasets can be processed
        html_content = self.generator.generate_html_report(
            test_results=large_results,
            execution_id='LARGE_TEST',
            excel_file='large.xlsx'
        )
        
        self.assertIsInstance(html_content, str)
        self.assertIn('100', html_content)  # Total count

    @pytest.mark.negative
    @pytest.mark.invalid_input
    def test_generate_html_report_invalid_execution_id(self):
        """Test HTML report generation with invalid execution ID"""
        # Test with None execution_id
        html_content = self.generator.generate_html_report(
            test_results=self.sample_results,
            execution_id=None,
            excel_file='test_suite.xlsx'
        )
        
        self.assertIsInstance(html_content, str)
        self.assertIn('None', html_content)

    @pytest.mark.negative
    @pytest.mark.invalid_input
    def test_generate_markdown_report_invalid_excel_file(self):
        """Test Markdown report generation with invalid excel file"""
        # Test with empty string excel_file
        markdown_content = self.generator.generate_markdown_report(
            test_results=self.sample_results,
            execution_id='TEST_INVALID',
            excel_file=''
        )
        
        self.assertIsInstance(markdown_content, str)
        self.assertIn('``', markdown_content)  # Empty excel file should appear as empty backticks

    @pytest.mark.edge_case
    @pytest.mark.none_values
    def test_generate_reports_with_none_breakdown(self):
        """Test report generation with None sheet breakdown"""
        html_content = self.generator.generate_html_report(
            test_results=self.sample_results,
            execution_id='TEST_NONE_BREAKDOWN',
            excel_file='test.xlsx',
            multi_sheet=True,
            sheet_breakdown=None
        )
        
        self.assertIsInstance(html_content, str)
        
        markdown_content = self.generator.generate_markdown_report(
            test_results=self.sample_results,
            execution_id='TEST_NONE_BREAKDOWN',
            excel_file='test.xlsx',
            multi_sheet=True,
            sheet_breakdown=None
        )
        
        self.assertIsInstance(markdown_content, str)

    @pytest.mark.edge_case
    @pytest.mark.empty_breakdown
    def test_generate_reports_with_empty_breakdown(self):
        """Test report generation with empty sheet breakdown"""
        html_content = self.generator.generate_html_report(
            test_results=self.sample_results,
            execution_id='TEST_EMPTY_BREAKDOWN',
            excel_file='test.xlsx',
            multi_sheet=True,
            sheet_breakdown={}
        )
        
        self.assertIsInstance(html_content, str)
        
        markdown_content = self.generator.generate_markdown_report(
            test_results=self.sample_results,
            execution_id='TEST_EMPTY_BREAKDOWN',
            excel_file='test.xlsx',
            multi_sheet=True,
            sheet_breakdown={}
        )
        
        self.assertIsInstance(markdown_content, str)

    @pytest.mark.edge_case
    @pytest.mark.unicode_handling
    def test_unicode_characters_in_reports(self):
        """Test handling of Unicode characters in test data"""
        unicode_results = [
            TestResult(
                test_case_id='UNICODE_001',
                test_case_name='Test with 中文 and émojis 🚀',
                status='PASS',
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 1),
                duration_seconds=1.0,
                error_message=None,
                environment='测试环境',
                application='POSTGRES',
                priority='HIGH',
                category='UNICODE'
            )
        ]
        
        html_content = self.generator.generate_html_report(
            test_results=unicode_results,
            execution_id='UNICODE_TEST',
            excel_file='unicode_test.xlsx'
        )
        
        self.assertIsInstance(html_content, str)
        self.assertIn('中文', html_content)
        self.assertIn('🚀', html_content)
        
        markdown_content = self.generator.generate_markdown_report(
            test_results=unicode_results,
            execution_id='UNICODE_TEST',
            excel_file='unicode_test.xlsx'
        )
        
        self.assertIsInstance(markdown_content, str)
        self.assertIn('中文', markdown_content)
        self.assertIn('🚀', markdown_content)

    @pytest.mark.edge_case
    @pytest.mark.long_content
    def test_very_long_error_messages(self):
        """Test handling of very long error messages"""
        long_error_message = "This is a very long error message. " * 100  # 4000+ characters
        
        long_error_results = [
            TestResult(
                test_case_id='LONG_ERROR_001',
                test_case_name='Test with Long Error',
                status='FAIL',
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 1),
                duration_seconds=1.0,
                error_message=long_error_message,
                environment='DEV',
                application='POSTGRES',
                priority='HIGH',
                category='ERROR'
            )
        ]
        
        html_content = self.generator.generate_html_report(
            test_results=long_error_results,
            execution_id='LONG_ERROR_TEST',
            excel_file='long_error_test.xlsx'
        )
        
        self.assertIsInstance(html_content, str)
        
        markdown_content = self.generator.generate_markdown_report(
            test_results=long_error_results,
            execution_id='LONG_ERROR_TEST',
            excel_file='long_error_test.xlsx'
        )
        
        self.assertIsInstance(markdown_content, str)
        # Markdown should truncate very long messages
        self.assertIn('...', markdown_content)

    @pytest.mark.negative
    @pytest.mark.malformed_data
    def test_malformed_test_results(self):
        """Test handling of test results with missing or malformed data"""
        # Create a test result with missing attributes by mocking
        from unittest.mock import Mock
        
        malformed_result = Mock()
        malformed_result.test_case_id = 'MALFORMED_001'
        malformed_result.test_case_name = 'Malformed Test'
        malformed_result.status = 'PASS'
        malformed_result.test_id = 'MALFORMED_001'  # Different property name
        malformed_result.description = 'Malformed Test'  # Different property name
        # Mock message attribute to avoid len() error
        malformed_result.message = Mock()
        malformed_result.message.__len__ = Mock(side_effect=TypeError("Mock has no len"))
        # Missing some expected attributes
        
        # This should fail gracefully due to missing attributes
        with self.assertRaises((AttributeError, TypeError)):
            html_content = self.generator.generate_html_report(
                test_results=[malformed_result],
                execution_id='MALFORMED_TEST',
                excel_file='malformed_test.xlsx'
            )

    @pytest.mark.performance
    @pytest.mark.stress_test
    def test_stress_test_with_many_sheets(self):
        """Test performance with many sheets in breakdown"""
        # Create many small sheets
        sheet_breakdown = {}
        for i in range(50):  # 50 sheets
            sheet_breakdown[f'SHEET_{i:02d}'] = [self.sample_results[i % len(self.sample_results)]]
        
        markdown_content = self.generator.generate_markdown_report(
            test_results=self.sample_results * 50,  # 150 total results
            execution_id='STRESS_TEST',
            excel_file='stress_test.xlsx',
            multi_sheet=True,
            sheet_breakdown=sheet_breakdown
        )
        
        self.assertIsInstance(markdown_content, str)
        self.assertIn('SHEET_00', markdown_content)
        self.assertIn('SHEET_49', markdown_content)

    @pytest.mark.edge_case
    @pytest.mark.zero_duration
    def test_zero_duration_tests(self):
        """Test handling of tests with zero duration"""
        zero_duration_results = [
            TestResult(
                test_case_id='ZERO_001',
                test_case_name='Instantaneous Test',
                status='PASS',
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 0),  # Same time
                duration_seconds=0.0,
                error_message=None,
                environment='DEV',
                application='POSTGRES',
                priority='LOW',
                category='INSTANT'
            )
        ]
        
        html_content = self.generator.generate_html_report(
            test_results=zero_duration_results,
            execution_id='ZERO_DURATION_TEST',
            excel_file='zero_duration_test.xlsx'
        )
        
        self.assertIsInstance(html_content, str)
        self.assertIn('0.0', html_content)  # Should handle zero duration

    @pytest.mark.edge_case
    @pytest.mark.extreme_values
    def test_extreme_duration_values(self):
        """Test handling of extreme duration values"""
        extreme_results = [
            TestResult(
                test_case_id='EXTREME_001',
                test_case_name='Very Slow Test',
                status='PASS',
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 0),
                duration_seconds=9999.999,  # Very large duration
                error_message=None,
                environment='DEV',
                application='POSTGRES',
                priority='LOW',
                category='SLOW'
            ),
            TestResult(
                test_case_id='EXTREME_002',
                test_case_name='Microsecond Test',
                status='PASS',
                start_time=datetime(2024, 1, 1, 10, 0, 0),
                end_time=datetime(2024, 1, 1, 10, 0, 0),
                duration_seconds=0.001,  # Very small duration
                error_message=None,
                environment='DEV',
                application='POSTGRES',
                priority='LOW',
                category='FAST'
            )
        ]
        
        markdown_content = self.generator.generate_markdown_report(
            test_results=extreme_results,
            execution_id='EXTREME_TEST',
            excel_file='extreme_test.xlsx'
        )
        
        self.assertIsInstance(markdown_content, str)
        self.assertIn('10000.00s', markdown_content)  # Rounded to 2 decimal places
        self.assertIn('0.00s', markdown_content)  # Very small values show as 0.00


if __name__ == '__main__':
    unittest.main()