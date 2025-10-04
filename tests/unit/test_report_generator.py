"""
Unit tests for ReportGenerator class
"""
import unittest
import tempfile
import os
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

    def test_initialization(self):
        """Test ReportGenerator initialization"""
        generator = ReportGenerator()
        self.assertIsNotNone(generator.timestamp)
        self.assertIsInstance(generator.timestamp, datetime)

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

    def test_generate_html_report_empty_results(self):
        """Test HTML report generation with empty results"""
        html_content = self.generator.generate_html_report(
            test_results=[],
            execution_id='TEST_RUN_003',
            excel_file='empty.xlsx'
        )
        
        self.assertIsInstance(html_content, str)
        self.assertIn('0', html_content)  # Should show 0 tests

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

    def test_generate_markdown_report_empty_results(self):
        """Test Markdown report generation with empty results"""
        markdown_content = self.generator.generate_markdown_report(
            test_results=[],
            execution_id='TEST_RUN_003',
            excel_file='empty.xlsx'
        )
        
        self.assertIsInstance(markdown_content, str)
        self.assertIn('| **Total Tests** | 0 |', markdown_content)

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


if __name__ == '__main__':
    unittest.main()