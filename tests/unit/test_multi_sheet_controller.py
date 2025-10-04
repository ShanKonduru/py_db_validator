#!/usr/bin/env python
"""
Comprehensive unit tests for multi-sheet controller
"""
import unittest
import tempfile
import os
from unittest.mock import patch, Mock, MagicMock
from openpyxl import Workbook
from src.core.multi_sheet_controller import MultiSheetTestController
from src.utils.excel_test_suite_reader import TestCase


class TestMultiSheetController(unittest.TestCase):
    """Test cases for multi-sheet controller"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'multi_sheet_test.xlsx')
        self.create_test_excel_file()
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
        
    def create_test_excel_file(self):
        """Create a test Excel file with multiple sheets"""
        workbook = Workbook()
        
        # Create SMOKE sheet
        smoke_sheet = workbook.active
        smoke_sheet.title = 'SMOKE'
        
        headers = [
            'Enable', 'Test Case ID', 'Test Case Name', 'Application Name',
            'Environment Name', 'Priority', 'Test Category', 'Expected Result',
            'Timeout (seconds)', 'Description', 'Prerequisites', 'Tags', 'Parameters'
        ]
        
        for idx, header in enumerate(headers, 1):
            smoke_sheet.cell(row=1, column=idx, value=header)
        
        # Add smoke test data
        smoke_data = [
            ['TRUE', 'SMOKE_001', 'Connection Test', 'App1', 'DEV', 'HIGH',
             'CONNECTION_TEST', 'PASS', '30', 'Test connection', 'DB available',
             'smoke,connection', ''],
            ['TRUE', 'SMOKE_002', 'Table Test', 'App1', 'DEV', 'MEDIUM',
             'TABLE_EXISTS', 'PASS', '30', 'Test table', 'DB available',
             'smoke,table', 'table_name=public.products']
        ]
        
        for row_idx, row_data in enumerate(smoke_data, 2):
            for col_idx, cell_value in enumerate(row_data, 1):
                smoke_sheet.cell(row=row_idx, column=col_idx, value=cell_value)
        
        # Create FUNCTIONAL sheet
        functional_sheet = workbook.create_sheet(title='FUNCTIONAL')
        
        for idx, header in enumerate(headers, 1):
            functional_sheet.cell(row=1, column=idx, value=header)
        
        # Add functional test data
        functional_data = [
            ['TRUE', 'FUNC_001', 'Data Validation Test', 'App1', 'DEV', 'HIGH',
             'DATA_VALIDATION', 'PASS', '60', 'Test data validation', 'Data available',
             'functional,validation', 'table_name=public.orders'],
            ['FALSE', 'FUNC_002', 'Performance Test', 'App1', 'DEV', 'LOW',
             'PERFORMANCE_TEST', 'PASS', '120', 'Test performance', 'Load data',
             'functional,performance', 'query_timeout=30']
        ]
        
        for row_idx, row_data in enumerate(functional_data, 2):
            for col_idx, cell_value in enumerate(row_data, 1):
                functional_sheet.cell(row=row_idx, column=col_idx, value=cell_value)
        
        workbook.save(self.test_file)

    def test_multi_sheet_controller_initialization(self):
        """Test MultiSheetTestController initialization"""
        controller = MultiSheetTestController(self.test_file)
        self.assertIsNotNone(controller)

    def test_read_all_sheets(self):
        """Test reading all sheets"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        self.assertIsInstance(all_sheets, dict)
        self.assertIn('SMOKE', all_sheets)
        self.assertIn('FUNCTIONAL', all_sheets)

    def test_read_specific_sheet(self):
        """Test reading a specific sheet"""
        controller = MultiSheetTestController(self.test_file)
        smoke_tests = controller.read_sheet('SMOKE')
        
        self.assertIsInstance(smoke_tests, list)
        self.assertEqual(len(smoke_tests), 2)
        self.assertEqual(smoke_tests[0].test_case_id, 'SMOKE_001')

    def test_read_nonexistent_sheet(self):
        """Test reading a non-existent sheet"""
        controller = MultiSheetTestController(self.test_file)
        result = controller.read_sheet('NONEXISTENT')
        
        self.assertEqual(result, [])

    def test_get_sheet_names(self):
        """Test getting sheet names"""
        controller = MultiSheetTestController(self.test_file)
        sheet_names = controller.get_sheet_names()
        
        self.assertIn('SMOKE', sheet_names)
        self.assertIn('FUNCTIONAL', sheet_names)

    def test_filter_by_category(self):
        """Test filtering by test category"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        connection_tests = controller.filter_by_category(all_sheets, 'CONNECTION_TEST')
        self.assertEqual(len(connection_tests), 1)
        self.assertEqual(connection_tests[0].test_case_id, 'SMOKE_001')

    def test_filter_by_priority(self):
        """Test filtering by priority"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        high_priority = controller.filter_by_priority(all_sheets, 'HIGH')
        self.assertEqual(len(high_priority), 2)

    def test_filter_by_environment(self):
        """Test filtering by environment"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        dev_tests = controller.filter_by_environment(all_sheets, 'DEV')
        self.assertEqual(len(dev_tests), 4)  # All test cases in our sample

    def test_filter_by_tag(self):
        """Test filtering by tag"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        smoke_tagged = controller.filter_by_tag(all_sheets, 'smoke')
        self.assertEqual(len(smoke_tagged), 2)

    def test_filter_enabled_only(self):
        """Test filtering enabled tests only"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        enabled_tests = controller.filter_enabled_only(all_sheets)
        self.assertEqual(len(enabled_tests), 3)  # FUNC_002 is disabled

    def test_get_test_statistics(self):
        """Test getting test statistics"""
        controller = MultiSheetTestController(self.test_file)
        stats = controller.get_test_statistics()
        
        self.assertIn('total_tests', stats)
        self.assertIn('enabled_tests', stats)
        self.assertIn('disabled_tests', stats)
        self.assertIn('sheets', stats)
        
        self.assertEqual(stats['total_tests'], 4)
        self.assertEqual(stats['enabled_tests'], 3)
        self.assertEqual(stats['disabled_tests'], 1)

    def test_find_test_by_id(self):
        """Test finding a test by ID across all sheets"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        test_case = controller.find_test_by_id(all_sheets, 'FUNC_001')
        self.assertIsNotNone(test_case)
        self.assertEqual(test_case.test_case_id, 'FUNC_001')
        
        # Test non-existent ID
        missing_case = controller.find_test_by_id(all_sheets, 'MISSING_001')
        self.assertIsNone(missing_case)

    def test_group_by_application(self):
        """Test grouping tests by application"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        grouped = controller.group_by_application(all_sheets)
        self.assertIn('App1', grouped)
        self.assertEqual(len(grouped['App1']), 4)

    def test_group_by_environment(self):
        """Test grouping tests by environment"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        grouped = controller.group_by_environment(all_sheets)
        self.assertIn('DEV', grouped)
        self.assertEqual(len(grouped['DEV']), 4)

    def test_invalid_file_handling(self):
        """Test handling of invalid file"""
        invalid_file = os.path.join(self.temp_dir, 'nonexistent.xlsx')
        
        controller = MultiSheetTestController(invalid_file)
        result = controller.read_all_sheets()
        
        # Should return empty dict for invalid file
        self.assertEqual(result, {})

    def test_empty_sheet_handling(self):
        """Test handling of empty sheets"""
        # Create a file with an empty sheet
        workbook = Workbook()
        empty_sheet = workbook.active
        empty_sheet.title = 'EMPTY'
        
        empty_file = os.path.join(self.temp_dir, 'empty.xlsx')
        workbook.save(empty_file)
        
        controller = MultiSheetTestController(empty_file)
        result = controller.read_sheet('EMPTY')
        
        self.assertEqual(result, [])
        
        # Clean up
        os.remove(empty_file)

    def test_sheet_with_invalid_headers(self):
        """Test handling of sheet with invalid headers"""
        # Create a file with invalid headers
        workbook = Workbook()
        invalid_sheet = workbook.active
        invalid_sheet.title = 'INVALID'
        
        # Add wrong headers
        invalid_headers = ['Wrong', 'Headers', 'Here']
        for idx, header in enumerate(invalid_headers, 1):
            invalid_sheet.cell(row=1, column=idx, value=header)
        
        invalid_file = os.path.join(self.temp_dir, 'invalid.xlsx')
        workbook.save(invalid_file)
        
        controller = MultiSheetTestController(invalid_file)
        result = controller.read_sheet('INVALID')
        
        # Should handle gracefully and return empty list
        self.assertEqual(result, [])
        
        # Clean up
        os.remove(invalid_file)

    def test_complex_filtering_combinations(self):
        """Test complex filtering combinations"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        # Filter by multiple criteria
        enabled_tests = controller.filter_enabled_only(all_sheets)
        high_priority_enabled = controller.filter_by_priority(enabled_tests, 'HIGH')
        
        self.assertEqual(len(high_priority_enabled), 2)

    def test_parameter_extraction(self):
        """Test parameter extraction from test cases"""
        controller = MultiSheetTestController(self.test_file)
        all_sheets = controller.read_all_sheets()
        
        # Find test with parameters
        table_test = None
        for sheet_tests in all_sheets.values():
            for test in sheet_tests:
                if test.test_case_id == 'SMOKE_002':
                    table_test = test
                    break
        
        self.assertIsNotNone(table_test)
        self.assertEqual(table_test.get_parameter('table_name'), 'public.products')

    def test_error_recovery(self):
        """Test error recovery in various scenarios"""
        controller = MultiSheetTestController(self.test_file)
        
        # Test with None filename
        controller_none = MultiSheetTestController(None)
        result = controller_none.read_all_sheets()
        self.assertEqual(result, {})
        
        # Test with empty filename
        controller_empty = MultiSheetTestController("")
        result = controller_empty.read_all_sheets()
        self.assertEqual(result, {})

    def test_large_dataset_handling(self):
        """Test handling of larger datasets"""
        # Create a file with more test data
        workbook = Workbook()
        large_sheet = workbook.active
        large_sheet.title = 'LARGE'
        
        headers = [
            'Enable', 'Test Case ID', 'Test Case Name', 'Application Name',
            'Environment Name', 'Priority', 'Test Category', 'Expected Result',
            'Timeout (seconds)', 'Description', 'Prerequisites', 'Tags', 'Parameters'
        ]
        
        for idx, header in enumerate(headers, 1):
            large_sheet.cell(row=1, column=idx, value=header)
        
        # Add 100 test cases
        for i in range(100):
            row_data = [
                'TRUE', f'TEST_{i:03d}', f'Test Case {i}', 'LargeApp', 'TEST',
                'MEDIUM', 'SMOKE_TEST', 'PASS', '30', f'Description {i}',
                'Prerequisites', 'large,test', ''
            ]
            for col_idx, cell_value in enumerate(row_data, 1):
                large_sheet.cell(row=i+2, column=col_idx, value=cell_value)
        
        large_file = os.path.join(self.temp_dir, 'large.xlsx')
        workbook.save(large_file)
        
        controller = MultiSheetTestController(large_file)
        result = controller.read_sheet('LARGE')
        
        self.assertEqual(len(result), 100)
        
        # Clean up
        os.remove(large_file)


if __name__ == '__main__':
    unittest.main()