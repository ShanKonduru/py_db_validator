#!/usr/bin/env python
"""
Simple unit tests for parameter functionality
"""
import unittest
import pytest
from src.utils.excel_test_suite_reader import TestCase


class TestParameterFunctionality(unittest.TestCase):
    """Test parameter parsing functionality"""

    def test_test_case_parameter_parsing(self):
        """Test TestCase parameter parsing methods"""
        # Test with key=value parameters
        tc1 = TestCase(
            enable=True,
            test_case_id='TEST_001',
            test_case_name='Test Parameters',
            application_name='TestApp',
            environment_name='DEV',
            priority='HIGH',
            test_category='TABLE_EXISTS',
            expected_result='PASS',
            timeout_seconds=30,
            description='Test description',
            prerequisites='Test prerequisites',
            tags='test,table',
            parameters='table_name=public.products,min_rows=5'
        )
        
        # Test parameter retrieval
        self.assertEqual(tc1.get_parameter('table_name'), 'public.products')
        self.assertEqual(tc1.get_parameter('min_rows'), '5')
        self.assertEqual(tc1.get_parameter('missing', 'default'), 'default')
        
        # Test parameters dictionary
        params = tc1.get_parameters_dict()
        self.assertEqual(params['table_name'], 'public.products')
        self.assertEqual(params['min_rows'], '5')
        self.assertEqual(len(params), 2)

    def test_simple_parameter_fallback(self):
        """Test fallback for simple parameter values"""
        tc = TestCase(
            enable=True,
            test_case_id='TEST_002',
            test_case_name='Simple Parameter',
            application_name='TestApp',
            environment_name='DEV',
            priority='HIGH',
            test_category='TABLE_EXISTS',
            expected_result='PASS',
            timeout_seconds=30,
            description='Test description',
            prerequisites='Test prerequisites',
            tags='test',
            parameters='simple_table'
        )
        
        # Should fall back to table_name
        self.assertEqual(tc.get_parameter('table_name'), 'simple_table')

    def test_empty_parameters(self):
        """Test handling of empty parameters"""
        tc = TestCase(
            enable=True,
            test_case_id='TEST_003',
            test_case_name='Empty Parameters',
            application_name='TestApp',
            environment_name='DEV',
            priority='HIGH',
            test_category='CONNECTION_TEST',
            expected_result='PASS',
            timeout_seconds=30,
            description='Test description',
            prerequisites='Test prerequisites',
            tags='test',
            parameters=''
        )
        
        self.assertEqual(tc.get_parameters_dict(), {})
        self.assertEqual(tc.get_parameter('any_param'), '')

    def test_test_case_basic_attributes(self):
        """Test basic TestCase attributes"""
        tc = TestCase(
            enable=True,
            test_case_id='TEST_004',
            test_case_name='Basic Test',
            application_name='TestApp',
            environment_name='PROD',
            priority='MEDIUM',
            test_category='SMOKE_TEST',
            expected_result='PASS',
            timeout_seconds=60,
            description='Basic test description',
            prerequisites='Basic prerequisites',
            tags='smoke,basic',
            parameters=''
        )
        
        self.assertTrue(tc.enable)
        self.assertEqual(tc.test_case_id, 'TEST_004')
        self.assertEqual(tc.test_case_name, 'Basic Test')
        self.assertEqual(tc.application_name, 'TestApp')
        self.assertEqual(tc.environment_name, 'PROD')
        self.assertEqual(tc.priority, 'MEDIUM')
        self.assertEqual(tc.test_category, 'SMOKE_TEST')
        self.assertEqual(tc.expected_result, 'PASS')
        self.assertEqual(tc.timeout_seconds, 60)
        self.assertEqual(tc.description, 'Basic test description')
        self.assertEqual(tc.prerequisites, 'Basic prerequisites')
        self.assertEqual(tc.tags, 'smoke,basic')


if __name__ == '__main__':
    unittest.main()