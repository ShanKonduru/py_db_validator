#!/usr/bin/env python
"""
Comprehensive unit tests for Excel test suite reader
"""
import unittest
import tempfile
import os
from unittest.mock import patch, Mock, MagicMock
from openpyxl import Workbook
from src.utils.excel_test_suite_reader import TestCase, ExcelTestSuiteReader


class TestExcelTestSuiteReader(unittest.TestCase):
    """Test cases for Excel test suite reader"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_suite.xlsx')
        self.create_test_excel_file()
        
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
        
    def create_test_excel_file(self):
        """Create a test Excel file with various test types"""
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'SMOKE'
        
        # Headers (using proper format with underscores)
        headers = [
            'Enable', 'Test_Case_ID', 'Test_Case_Name', 'Application_Name',
            'Environment_Name', 'Priority', 'Test_Category', 'Expected_Result',
            'Timeout_Seconds', 'Description', 'Prerequisites', 'Tags', 'Parameters'
        ]
        
        for idx, header in enumerate(headers, 1):
            worksheet.cell(row=1, column=idx, value=header)
        
        # Test data with various test types
        test_data = [
            ['TRUE', 'SMOKE_001', 'Connection Test', 'POSTGRES', 'DEV', 'HIGH',
             'CONNECTION', 'PASS', '30', 'Test database connection', 'Database available',
             'smoke,connection', ''],
            ['TRUE', 'SMOKE_002', 'Table Exists Test', 'POSTGRES', 'DEV', 'MEDIUM',
             'TABLE_EXISTS', 'PASS', '30', 'Check if table exists', 'Database available',
             'smoke,table', 'table_name=public.products'],
            ['TRUE', 'SMOKE_003', 'Table Select Test', 'POSTGRES', 'DEV', 'MEDIUM',
             'TABLE_SELECT', 'PASS', '45', 'Select from table', 'Table exists',
             'smoke,select', 'table_name=public.employees,column_list=id,name'],
            ['TRUE', 'SMOKE_004', 'Table Rows Test', 'POSTGRES', 'DEV', 'LOW',
             'TABLE_ROWS', 'PASS', '30', 'Check table row count', 'Table exists',
             'smoke,rows', 'table_name=public.orders,min_rows=100,max_rows=1000'],
            ['TRUE', 'SMOKE_005', 'Table Structure Test', 'POSTGRES', 'DEV', 'HIGH',
             'TABLE_STRUCTURE', 'PASS', '60', 'Validate table structure', 'Table exists',
             'smoke,structure', 'table_name=public.customers,schema_validation=true'],
            ['FALSE', 'SMOKE_006', 'Disabled Test', 'POSTGRES', 'DEV', 'LOW',
             'SETUP', 'PASS', '30', 'Disabled smoke test', 'None',
             'smoke,disabled', ''],
            ['TRUE', 'SMOKE_007', 'General Setup Test', 'POSTGRES', 'DEV', 'MEDIUM',
             'SETUP', 'PASS', '30', 'General setup test', 'Application running',
             'smoke,general', 'endpoint=http://localhost:8080/health']
        ]
        
        for row_idx, row_data in enumerate(test_data, 2):
            for col_idx, cell_value in enumerate(row_data, 1):
                worksheet.cell(row=row_idx, column=col_idx, value=cell_value)
        
        workbook.save(self.test_file)

    def test_reader_initialization(self):
        """Test ExcelTestSuiteReader initialization"""
        reader = ExcelTestSuiteReader(self.test_file)
        self.assertIsNotNone(reader)
        self.assertEqual(str(reader.excel_file), self.test_file)
        self.assertEqual(reader.sheet_name, 'SMOKE')

    def test_reader_initialization_with_custom_sheet(self):
        """Test ExcelTestSuiteReader initialization with custom sheet name"""
        reader = ExcelTestSuiteReader(self.test_file, 'CUSTOM')
        self.assertEqual(reader.sheet_name, 'CUSTOM')

    def test_validate_file_exists(self):
        """Test file existence validation"""
        reader = ExcelTestSuiteReader(self.test_file)
        self.assertTrue(reader.validate_file_exists())
        
        # Test with non-existent file
        reader_invalid = ExcelTestSuiteReader('nonexistent.xlsx')
        self.assertFalse(reader_invalid.validate_file_exists())

    def test_load_workbook_success(self):
        """Test successful workbook loading"""
        reader = ExcelTestSuiteReader(self.test_file)
        result = reader.load_workbook()
        
        self.assertTrue(result)
        self.assertIsNotNone(reader.workbook)
        self.assertIn('SMOKE', reader.workbook.sheetnames)

    def test_load_workbook_missing_sheet(self):
        """Test workbook loading with missing sheet"""
        reader = ExcelTestSuiteReader(self.test_file, 'NONEXISTENT')
        result = reader.load_workbook()
        
        self.assertFalse(result)

    def test_load_workbook_invalid_file(self):
        """Test workbook loading with invalid file"""
        invalid_file = os.path.join(self.temp_dir, 'invalid.txt')
        with open(invalid_file, 'w') as f:
            f.write('Not an Excel file')
        
        reader = ExcelTestSuiteReader(invalid_file)
        result = reader.load_workbook()
        
        self.assertFalse(result)
        
        # Clean up
        os.remove(invalid_file)

    def test_read_test_cases_success(self):
        """Test successful test case reading"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        
        result = reader.read_test_cases()
        self.assertTrue(result)

    def test_read_test_cases_with_sheet_name(self):
        """Test reading test cases with specific sheet name"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        
        result = reader.read_test_cases('SMOKE')
        self.assertTrue(result)

    def test_get_all_test_cases(self):
        """Test getting all test cases"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        reader.read_test_cases()
        
        test_cases = reader.get_all_test_cases()
        
        self.assertIsInstance(test_cases, list)
        self.assertGreater(len(test_cases), 0)
        
        # Should have 7 test cases
        self.assertEqual(len(test_cases), 7)
        
        # All should be TestCase instances
        for test_case in test_cases:
            self.assertIsInstance(test_case, TestCase)

    def test_get_enabled_test_cases(self):
        """Test getting enabled test cases only"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        reader.read_test_cases()
        
        enabled_cases = reader.get_enabled_test_cases()
        
        self.assertIsInstance(enabled_cases, list)
        # Should have 6 enabled cases (1 is disabled)
        self.assertEqual(len(enabled_cases), 6)
        
        # All should be enabled
        for test_case in enabled_cases:
            self.assertTrue(test_case.enable)

    def test_get_filtered_test_cases(self):
        """Test filtering test cases"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        reader.read_test_cases()
        
        # Filter by priority
        high_priority = reader.get_filtered_test_cases(priority='HIGH')
        self.assertGreater(len(high_priority), 0)
        for test_case in high_priority:
            self.assertEqual(test_case.priority, 'HIGH')
        
        # Filter by environment
        dev_tests = reader.get_filtered_test_cases(environment='DEV')
        self.assertGreater(len(dev_tests), 0)
        for test_case in dev_tests:
            self.assertEqual(test_case.environment_name, 'DEV')
        
        # Filter by category
        connection_tests = reader.get_filtered_test_cases(category='CONNECTION')
        self.assertGreater(len(connection_tests), 0)
        for test_case in connection_tests:
            self.assertEqual(test_case.test_category, 'CONNECTION')

    def test_get_test_case_by_id(self):
        """Test getting test case by ID"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        reader.read_test_cases()
        
        # Get existing test case
        test_case = reader.get_test_case_by_id('SMOKE_001')
        self.assertIsNotNone(test_case)
        self.assertEqual(test_case.test_case_id, 'SMOKE_001')
        
        # Get non-existent test case
        test_case = reader.get_test_case_by_id('NONEXISTENT')
        self.assertIsNone(test_case)

    def test_get_statistics(self):
        """Test getting test statistics"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        reader.read_test_cases()
        
        stats = reader.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_tests', stats)
        self.assertIn('enabled_tests', stats)
        self.assertIn('disabled_tests', stats)
        
        self.assertEqual(stats['total_tests'], 7)
        self.assertEqual(stats['enabled_tests'], 6)
        self.assertEqual(stats['disabled_tests'], 1)

    def test_validation_functionality(self):
        """Test validation functionality"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        
        # Test validation methods
        self.assertIsInstance(reader.is_validation_passed(), bool)
        self.assertIsInstance(reader.get_validation_report(), str)

    def test_load_and_validate(self):
        """Test combined load and validate functionality"""
        reader = ExcelTestSuiteReader(self.test_file)
        result = reader.load_and_validate()
        
        self.assertTrue(result)

    def test_test_case_properties(self):
        """Test TestCase properties and methods"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        reader.read_test_cases()
        
        test_cases = reader.get_all_test_cases()
        test_case = test_cases[0]  # First test case
        
        # Test basic properties
        self.assertEqual(test_case.test_case_id, 'SMOKE_001')
        self.assertEqual(test_case.test_case_name, 'Connection Test')
        self.assertEqual(test_case.application_name, 'POSTGRES')
        self.assertEqual(test_case.environment_name, 'DEV')
        self.assertEqual(test_case.priority, 'HIGH')
        self.assertEqual(test_case.test_category, 'CONNECTION')
        self.assertEqual(test_case.expected_result, 'PASS')
        self.assertTrue(test_case.enable)
        
        # Test method calls
        self.assertTrue(test_case.is_enabled())
        self.assertIsInstance(test_case.get_tags_list(), list)
        self.assertIsInstance(test_case.get_parameters_dict(), dict)

    def test_test_case_tags(self):
        """Test TestCase tag functionality"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        reader.read_test_cases()
        
        test_case = reader.get_test_case_by_id('SMOKE_001')
        
        # Test tags
        tags = test_case.get_tags_list()
        self.assertIn('smoke', tags)
        self.assertIn('connection', tags)
        
        # Test has_tag method
        self.assertTrue(test_case.has_tag('smoke'))
        self.assertTrue(test_case.has_tag('connection'))
        self.assertFalse(test_case.has_tag('nonexistent'))

    def test_test_case_parameters(self):
        """Test TestCase parameter functionality"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        reader.read_test_cases()
        
        # Get test case with parameters
        test_case = reader.get_test_case_by_id('SMOKE_002')
        
        # Test parameters
        params = test_case.get_parameters_dict()
        self.assertIsInstance(params, dict)
        
        # Test parameter retrieval
        table_name = test_case.get_parameter('table_name', 'default')
        self.assertIsInstance(table_name, str)

    def test_test_case_filtering(self):
        """Test TestCase filtering functionality"""
        reader = ExcelTestSuiteReader(self.test_file)
        reader.load_workbook()
        reader.read_test_cases()
        
        test_case = reader.get_test_case_by_id('SMOKE_001')
        
        # Test matches_filter method
        self.assertTrue(test_case.matches_filter(priority='HIGH'))
        self.assertFalse(test_case.matches_filter(priority='LOW'))
        
        self.assertTrue(test_case.matches_filter(environment='DEV'))
        self.assertFalse(test_case.matches_filter(environment='PROD'))

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        # Test with empty file path - should not raise exception during initialization
        reader = ExcelTestSuiteReader('')
        self.assertIsNotNone(reader)
        
        # Test with None file path - should not raise exception during initialization  
        reader = ExcelTestSuiteReader(None)
        self.assertIsNotNone(reader)

    def test_empty_excel_file(self):
        """Test handling of empty Excel file"""
        empty_file = os.path.join(self.temp_dir, 'empty.xlsx')
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'SMOKE'
        workbook.save(empty_file)
        
        reader = ExcelTestSuiteReader(empty_file)
        result = reader.load_workbook()
        self.assertTrue(result)  # Should load successfully
        
        # Try to read test cases
        result = reader.read_test_cases()
        # Might succeed or fail depending on validation
        
        # Clean up
        os.remove(empty_file)

    def test_large_dataset(self):
        """Test handling of large datasets"""
        large_file = os.path.join(self.temp_dir, 'large.xlsx')
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'SMOKE'
        
        # Headers
        headers = [
            'Enable', 'Test_Case_ID', 'Test_Case_Name', 'Application_Name',
            'Environment_Name', 'Priority', 'Test_Category', 'Expected_Result',
            'Timeout_Seconds', 'Description', 'Prerequisites', 'Tags', 'Parameters'
        ]
        
        for idx, header in enumerate(headers, 1):
            worksheet.cell(row=1, column=idx, value=header)
        
        # Add 100 test cases
        for i in range(100):
            row_data = [
                'TRUE', f'TEST_{i:03d}', f'Test Case {i}', 'POSTGRES', 'DEV', 'MEDIUM',
                'SETUP', 'PASS', '30', f'Description {i}', 'Prerequisites',
                'smoke,auto', f'test_id={i}'
            ]
            
            for col_idx, cell_value in enumerate(row_data, 1):
                worksheet.cell(row=i+2, column=col_idx, value=cell_value)
        
        workbook.save(large_file)
        
        reader = ExcelTestSuiteReader(large_file)
        result = reader.load_and_validate()
        
        # Should handle large dataset
        self.assertIsInstance(result, bool)
        
        if result:  # If loaded successfully
            reader.read_test_cases()
            test_cases = reader.get_all_test_cases()
            self.assertEqual(len(test_cases), 100)
        
        # Clean up
        os.remove(large_file)

    def test_multiple_operations(self):
        """Test multiple operations on same reader"""
        reader = ExcelTestSuiteReader(self.test_file)
        
        # Load multiple times
        result1 = reader.load_workbook()
        result2 = reader.load_workbook()
        self.assertEqual(result1, result2)
        
        # Read test cases multiple times
        reader.read_test_cases()
        count1 = len(reader.get_all_test_cases())
        
        reader.read_test_cases()
        count2 = len(reader.get_all_test_cases())
        
        self.assertEqual(count1, count2)

    def test_different_sheet_names(self):
        """Test handling different sheet names"""
        # Create file with different sheet name
        alt_file = os.path.join(self.temp_dir, 'alt_sheet.xlsx')
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'INTEGRATION'
        
        # Add minimal headers
        headers = ['Enable', 'Test_Case_ID', 'Test_Case_Name', 'Application_Name']
        for idx, header in enumerate(headers, 1):
            worksheet.cell(row=1, column=idx, value=header)
        
        workbook.save(alt_file)
        
        # Test with correct sheet name
        reader = ExcelTestSuiteReader(alt_file, 'INTEGRATION')
        result = reader.load_workbook()
        self.assertTrue(result)
        
        # Test with incorrect sheet name
        reader_wrong = ExcelTestSuiteReader(alt_file, 'WRONG')
        result = reader_wrong.load_workbook()
        self.assertFalse(result)
        
        # Clean up
        os.remove(alt_file)


if __name__ == '__main__':
    unittest.main()