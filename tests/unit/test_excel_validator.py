#!/usr/bin/env python
"""
Comprehensive unit tests for Excel validator
"""
import unittest
import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from openpyxl import Workbook
from src.validation.excel_validator import ExcelTestSuiteValidator, ValidationMessage, ValidationSeverity


class TestExcelValidator(unittest.TestCase):
    """Test cases for Excel validator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.valid_file = os.path.join(self.temp_dir, 'valid_test.xlsx')
        self.invalid_file = os.path.join(self.temp_dir, 'invalid_test.xlsx')
        self.create_test_files()
        
    def tearDown(self):
        """Clean up test fixtures"""
        for file_path in [self.valid_file, self.invalid_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.rmdir(self.temp_dir)
        
    def create_test_files(self):
        """Create test Excel files"""
        self.create_valid_excel_file()
        self.create_invalid_excel_file()
        
    def create_valid_excel_file(self):
        """Create a valid Excel test file"""
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'SMOKE'
        
        # Valid headers (matching REQUIRED_HEADERS)
        headers = [
            'Enable', 'Test_Case_ID', 'Test_Case_Name', 'Application_Name',
            'Environment_Name', 'Priority', 'Test_Category', 'Expected_Result',
            'Timeout_Seconds', 'Description', 'Prerequisites', 'Tags', 'Parameters'
        ]
        
        for idx, header in enumerate(headers, 1):
            worksheet.cell(row=1, column=idx, value=header)
        
        # Valid test data
        test_data = [
            ['TRUE', 'SMOKE_001', 'Valid Connection Test', 'POSTGRES', 'DEV', 'HIGH',
             'CONNECTION', 'PASS', '30', 'Valid test description', 'Database available',
             'smoke,connection', ''],
            ['TRUE', 'SMOKE_002', 'Valid Table Test', 'POSTGRES', 'DEV', 'MEDIUM',
             'TABLE_EXISTS', 'PASS', '30', 'Valid table test', 'Database available',
             'smoke,table', 'table_name=public.products'],
            ['FALSE', 'SMOKE_003', 'Disabled Test', 'POSTGRES', 'DEV', 'LOW',
             'SETUP', 'PASS', '30', 'Disabled test', 'None',
             'smoke,disabled', '']
        ]
        
        for row_idx, row_data in enumerate(test_data, 2):
            for col_idx, cell_value in enumerate(row_data, 1):
                worksheet.cell(row=row_idx, column=col_idx, value=cell_value)
        
        workbook.save(self.valid_file)
        
    def create_invalid_excel_file(self):
        """Create an invalid Excel test file"""
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'SMOKE'
        
        # Missing some required headers
        headers = [
            'Enable', 'Test_Case_ID', 'Invalid_Name', 'Application_Name',
            'Environment_Name', 'Priority'
            # Missing several required headers
        ]
        
        for idx, header in enumerate(headers, 1):
            worksheet.cell(row=1, column=idx, value=header)
        
        # Invalid test data
        test_data = [
            ['INVALID', 'INVALID_ID', '', 'INVALID_APP', 'INVALID_ENV', 'INVALID_PRIORITY'],
            ['TRUE', '', 'Test without ID', 'POSTGRES', 'DEV', 'HIGH']
        ]
        
        for row_idx, row_data in enumerate(test_data, 2):
            for col_idx, cell_value in enumerate(row_data, 1):
                worksheet.cell(row=row_idx, column=col_idx, value=cell_value)
        
        workbook.save(self.invalid_file)

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.initialization
    def test_validator_initialization(self):
        """Test ExcelTestSuiteValidator initialization"""
        validator = ExcelTestSuiteValidator()
        self.assertIsNotNone(validator)
        self.assertEqual(len(validator.validation_messages), 0)

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.excel_processing
    def test_validate_test_suite_valid_file(self):
        """Test validate_test_suite with valid file"""
        validator = ExcelTestSuiteValidator()
        
        from openpyxl import load_workbook
        workbook = load_workbook(self.valid_file)
        
        is_valid, messages = validator.validate_test_suite(workbook, 'SMOKE')
        
        # Check that validation passes (or has minimal warnings)
        error_messages = [msg for msg in messages if msg.severity == ValidationSeverity.ERROR]
        self.assertEqual(len(error_messages), 0, f"Unexpected errors: {[msg.message for msg in error_messages]}")

    @pytest.mark.negative
    @pytest.mark.validation
    @pytest.mark.excel_processing
    def test_validate_test_suite_invalid_file(self):
        """Test validate_test_suite with invalid file"""
        validator = ExcelTestSuiteValidator()
        
        from openpyxl import load_workbook
        workbook = load_workbook(self.invalid_file)
        
        is_valid, messages = validator.validate_test_suite(workbook, 'SMOKE')
        
        # Should have validation errors
        error_messages = [msg for msg in messages if msg.severity == ValidationSeverity.ERROR]
        self.assertGreater(len(error_messages), 0)
        self.assertFalse(is_valid)

    @pytest.mark.negative
    @pytest.mark.validation
    @pytest.mark.edge_case
    def test_validate_test_suite_missing_sheet(self):
        """Test validate_test_suite with missing sheet"""
        validator = ExcelTestSuiteValidator()
        
        from openpyxl import load_workbook
        workbook = load_workbook(self.valid_file)
        
        is_valid, messages = validator.validate_test_suite(workbook, 'NONEXISTENT')
        
        # Should fail due to missing sheet
        self.assertFalse(is_valid)
        self.assertGreater(len(messages), 0)
        self.assertIn('not found', messages[0].message)

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.data_structures
    def test_validation_message_structure(self):
        """Test ValidationMessage structure"""
        message = ValidationMessage(
            severity=ValidationSeverity.ERROR,
            row=1,
            column='A',
            field='test_field',
            message='Test message',
            current_value='current',
            suggested_value='suggested'
        )
        
        self.assertEqual(message.severity, ValidationSeverity.ERROR)
        self.assertEqual(message.row, 1)
        self.assertEqual(message.column, 'A')
        self.assertEqual(message.field, 'test_field')
        self.assertEqual(message.message, 'Test message')
        self.assertEqual(message.current_value, 'current')
        self.assertEqual(message.suggested_value, 'suggested')

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.enums
    def test_validation_severity_enum(self):
        """Test ValidationSeverity enum values"""
        self.assertEqual(ValidationSeverity.ERROR.value, "ERROR")
        self.assertEqual(ValidationSeverity.WARNING.value, "WARNING")
        self.assertEqual(ValidationSeverity.INFO.value, "INFO")

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.constants
    def test_validator_constants(self):
        """Test validator constants are properly defined"""
        validator = ExcelTestSuiteValidator()
        
        # Test constants exist
        self.assertIsInstance(validator.VALID_PRIORITIES, set)
        self.assertIsInstance(validator.VALID_ENVIRONMENTS, set)
        self.assertIsInstance(validator.VALID_APPLICATIONS, set)
        self.assertIsInstance(validator.VALID_EXPECTED_RESULTS, set)
        self.assertIsInstance(validator.VALID_TEST_CATEGORIES, dict)
        self.assertIsInstance(validator.REQUIRED_HEADERS, list)
        
        # Test specific values
        self.assertIn('HIGH', validator.VALID_PRIORITIES)
        self.assertIn('MEDIUM', validator.VALID_PRIORITIES)
        self.assertIn('LOW', validator.VALID_PRIORITIES)
        
        self.assertIn('DEV', validator.VALID_ENVIRONMENTS)
        self.assertIn('PROD', validator.VALID_ENVIRONMENTS)
        
        self.assertIn('PASS', validator.VALID_EXPECTED_RESULTS)
        self.assertIn('FAIL', validator.VALID_EXPECTED_RESULTS)

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.headers
    def test_required_headers_structure(self):
        """Test required headers structure"""
        validator = ExcelTestSuiteValidator()
        
        expected_headers = [
            "Enable", "Test_Case_ID", "Test_Case_Name", "Application_Name",
            "Environment_Name", "Priority", "Test_Category", "Expected_Result", 
            "Timeout_Seconds", "Description", "Prerequisites", "Tags", "Parameters"
        ]
        
        self.assertEqual(validator.REQUIRED_HEADERS, expected_headers)

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.constraints
    def test_timeout_constraints(self):
        """Test timeout constraints"""
        validator = ExcelTestSuiteValidator()
        
        self.assertEqual(validator.MIN_TIMEOUT_SECONDS, 5)
        self.assertEqual(validator.MAX_TIMEOUT_SECONDS, 3600)

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.constraints
    def test_length_constraints(self):
        """Test length constraints"""
        validator = ExcelTestSuiteValidator()
        
        self.assertEqual(validator.MAX_DESCRIPTION_LENGTH, 500)
        self.assertEqual(validator.MAX_PREREQUISITES_LENGTH, 1000)

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.categories
    def test_valid_test_categories(self):
        """Test valid test categories mapping"""
        validator = ExcelTestSuiteValidator()
        
        # Test that test categories map to method names
        self.assertIn('SETUP', validator.VALID_TEST_CATEGORIES)
        self.assertIn('CONNECTION', validator.VALID_TEST_CATEGORIES)
        self.assertIn('TABLE_EXISTS', validator.VALID_TEST_CATEGORIES)
        self.assertIn('TABLE_SELECT', validator.VALID_TEST_CATEGORIES)
        
        # Test that values are method names
        self.assertEqual(validator.VALID_TEST_CATEGORIES['SETUP'], 'test_environment_setup')
        self.assertEqual(validator.VALID_TEST_CATEGORIES['CONNECTION'], 'test_postgresql_connection')

    @pytest.mark.negative
    @pytest.mark.validation
    @pytest.mark.edge_case
    def test_empty_workbook_handling(self):
        """Test handling of empty workbook"""
        validator = ExcelTestSuiteValidator()
        
        # Create empty workbook
        workbook = Workbook()
        workbook.remove(workbook.active)  # Remove default sheet
        
        is_valid, messages = validator.validate_test_suite(workbook, 'SMOKE')
        
        self.assertFalse(is_valid)
        self.assertGreater(len(messages), 0)

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.functional
    def test_multiple_validation_runs(self):
        """Test that validator can be reused for multiple validations"""
        validator = ExcelTestSuiteValidator()
        
        from openpyxl import load_workbook
        workbook = load_workbook(self.valid_file)
        
        # First validation
        is_valid1, messages1 = validator.validate_test_suite(workbook, 'SMOKE')
        
        # Second validation - should reset messages
        is_valid2, messages2 = validator.validate_test_suite(workbook, 'SMOKE')
        
        # Both should have same results
        self.assertEqual(is_valid1, is_valid2)
        self.assertEqual(len(messages1), len(messages2))

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.messages
    def test_validation_messages_collection(self):
        """Test that validation messages are properly collected"""
        validator = ExcelTestSuiteValidator()
        
        from openpyxl import load_workbook
        workbook = load_workbook(self.invalid_file)
        
        is_valid, messages = validator.validate_test_suite(workbook, 'SMOKE')
        
        # Should have messages
        self.assertGreater(len(messages), 0)
        
        # All messages should be ValidationMessage instances
        for message in messages:
            self.assertIsInstance(message, ValidationMessage)
            self.assertIsInstance(message.severity, ValidationSeverity)

    @pytest.mark.positive
    @pytest.mark.validation
    @pytest.mark.boolean_logic
    def test_boolean_values_validation(self):
        """Test boolean values validation"""
        validator = ExcelTestSuiteValidator()
        
        # Test valid boolean representations
        valid_boolean_values = validator.VALID_BOOLEAN_VALUES
        
        self.assertIn(True, valid_boolean_values)
        self.assertIn(False, valid_boolean_values)
        self.assertIn("TRUE", valid_boolean_values)
        self.assertIn("FALSE", valid_boolean_values)
        self.assertIn(1, valid_boolean_values)
        self.assertIn(0, valid_boolean_values)

    @pytest.mark.negative
    @pytest.mark.validation
    @pytest.mark.edge_case
    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        validator = ExcelTestSuiteValidator()
        
        # Test with None workbook should raise an error
        with self.assertRaises(AttributeError):
            validator.validate_test_suite(None, 'SMOKE')

    @pytest.mark.performance
    @pytest.mark.validation
    @pytest.mark.excel_processing
    def test_large_dataset_validation(self):
        """Test validation with larger dataset"""
        # Create file with many test cases
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
        
        # Add 50 test cases
        for i in range(50):
            row_data = [
                'TRUE', f'TEST_{i:03d}', f'Test Case {i}', 'POSTGRES', 'DEV', 'MEDIUM',
                'SETUP', 'PASS', '30', f'Description {i}', 'Prerequisites',
                'smoke,auto', f'test_id={i}'
            ]
            
            for col_idx, cell_value in enumerate(row_data, 1):
                worksheet.cell(row=i+2, column=col_idx, value=cell_value)
        
        workbook.save(large_file)
        
        validator = ExcelTestSuiteValidator()
        workbook = Workbook()
        from openpyxl import load_workbook
        workbook = load_workbook(large_file)
        
        is_valid, messages = validator.validate_test_suite(workbook, 'SMOKE')
        
        # Should handle large dataset
        self.assertIsInstance(is_valid, bool)
        self.assertIsInstance(messages, list)
        
        # Clean up
        os.remove(large_file)


if __name__ == '__main__':
    unittest.main()