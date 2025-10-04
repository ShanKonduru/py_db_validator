"""
Unit tests for TestResult model
"""
import unittest
from datetime import datetime

from src.models.test_result import TestResult


class TestTestResult(unittest.TestCase):
    """Test cases for TestResult class"""

    def setUp(self):
        """Set up test fixtures"""
        self.start_time = datetime(2025, 10, 3, 10, 0, 0)
        self.end_time = datetime(2025, 10, 3, 10, 0, 5)
        
        self.test_result = TestResult(
            test_case_id="TEST_001",
            test_case_name="Sample Test",
            status="PASS",
            start_time=self.start_time,
            end_time=self.end_time,
            duration_seconds=5.0,
            error_message=None,
            environment="DEV",
            application="DUMMY",
            priority="HIGH",
            category="CONNECTION"
        )

    def test_initialization(self):
        """Test TestResult initialization"""
        self.assertEqual(self.test_result.test_case_id, "TEST_001")
        self.assertEqual(self.test_result.test_case_name, "Sample Test")
        self.assertEqual(self.test_result.status, "PASS")
        self.assertEqual(self.test_result.start_time, self.start_time)
        self.assertEqual(self.test_result.end_time, self.end_time)
        self.assertEqual(self.test_result.duration_seconds, 5.0)
        self.assertIsNone(self.test_result.error_message)
        self.assertEqual(self.test_result.environment, "DEV")
        self.assertEqual(self.test_result.application, "DUMMY")
        self.assertEqual(self.test_result.priority, "HIGH")
        self.assertEqual(self.test_result.category, "CONNECTION")

    def test_is_success(self):
        """Test is_success property"""
        self.assertTrue(self.test_result.is_success)
        
        # Test failure case
        self.test_result.status = "FAIL"
        self.assertFalse(self.test_result.is_success)

    def test_is_failure(self):
        """Test is_failure property"""
        self.assertFalse(self.test_result.is_failure)
        
        # Test FAIL status
        self.test_result.status = "FAIL"
        self.assertTrue(self.test_result.is_failure)
        
        # Test ERROR status
        self.test_result.status = "ERROR"
        self.assertTrue(self.test_result.is_failure)

    def test_is_skipped(self):
        """Test is_skipped property"""
        self.assertFalse(self.test_result.is_skipped)
        
        # Test SKIP status
        self.test_result.status = "SKIP"
        self.assertTrue(self.test_result.is_skipped)

    def test_to_dict(self):
        """Test to_dict method"""
        result_dict = self.test_result.to_dict()
        
        expected_dict = {
            'test_case_id': 'TEST_001',
            'test_case_name': 'Sample Test',
            'status': 'PASS',
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': 5.0,
            'error_message': None,
            'environment': 'DEV',
            'application': 'DUMMY',
            'priority': 'HIGH',
            'category': 'CONNECTION'
        }
        
        self.assertEqual(result_dict, expected_dict)

    def test_with_error_message(self):
        """Test TestResult with error message"""
        result_with_error = TestResult(
            test_case_id="TEST_002",
            test_case_name="Failed Test",
            status="FAIL",
            start_time=self.start_time,
            end_time=self.end_time,
            duration_seconds=2.5,
            error_message="Connection timeout",
            environment="PROD",
            application="MYAPP",
            priority="LOW",
            category="PERFORMANCE"
        )
        
        self.assertFalse(result_with_error.is_success)
        self.assertTrue(result_with_error.is_failure)
        self.assertEqual(result_with_error.error_message, "Connection timeout")


if __name__ == '__main__':
    unittest.main()