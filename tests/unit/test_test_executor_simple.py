"""
Simplified unit tests for TestExecutor focusing on core functionality
"""
import unittest
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.core.test_executor import TestExecutor
from src.utils.excel_test_suite_reader import TestCase
from src.models.test_result import TestResult


class TestTestExecutorSimple(unittest.TestCase):
    """Simplified test cases for TestExecutor class"""

    def setUp(self):
        """Set up test fixtures"""
        self.executor = TestExecutor()
        
        self.sample_test_case = TestCase(
            enable=True,
            test_case_id="TEST_001",
            test_case_name="Sample Test",
            application_name="DUMMY",
            environment_name="DEV",
            priority="HIGH",
            test_category="CONNECTION",
            expected_result="PASS",
            timeout_seconds=30,
            description="Sample test description",
            prerequisites="None",
            tags="smoke"
        )

    @pytest.mark.positive
    @pytest.mark.initialization
    def test_initialization(self):
        """Test TestExecutor initialization"""
        self.assertIsInstance(self.executor, TestExecutor)

    @pytest.mark.positive
    @pytest.mark.functional
    @pytest.mark.test_execution
    def test_execute_test_case_returns_result(self, mock_smoke_class):
        """Test that execute_test_case returns a TestResult"""
        # Mock the smoke test class
        mock_smoke_instance = Mock()
        mock_smoke_class.return_value = mock_smoke_instance
        
        result = self.executor.execute_test_case(self.sample_test_case)
        
        # Should return a TestResult object
        self.assertIsInstance(result, TestResult)
        self.assertEqual(result.test_case_id, "TEST_001")
        self.assertEqual(result.test_case_name, "Sample Test")

    @patch('src.core.test_executor.TestPostgreSQLSmoke')
    def test_execute_test_case_with_different_categories(self, mock_smoke_class):
        """Test execute_test_case with different categories"""
        mock_smoke_instance = Mock()
        mock_smoke_class.return_value = mock_smoke_instance
        
        categories = ["CONNECTION", "SETUP", "QUERIES", "PERFORMANCE", "SECURITY"]
        
        for category in categories:
            with self.subTest(category=category):
                test_case = TestCase(
                    enable=True,
                    test_case_id=f"TEST_{category}",
                    test_case_name=f"{category} Test",
                    application_name="DUMMY",
                    environment_name="DEV",
                    priority="HIGH",
                    test_category=category,
                    expected_result="PASS",
                    timeout_seconds=30,
                    description=f"Test {category}",
                    prerequisites="None",
                    tags="smoke"
                )
                
                result = self.executor.execute_test_case(test_case)
                
                self.assertIsInstance(result, TestResult)
                self.assertEqual(result.test_case_id, f"TEST_{category}")

    def test_execute_test_case_basic_check(self):
        """Test basic execution functionality"""
        # This test just verifies that the method returns a result
        # without failing due to the disabled status check
        
        result = self.executor.execute_test_case(self.sample_test_case)
        
        self.assertIsInstance(result, TestResult)
        self.assertEqual(result.test_case_id, "TEST_001")


if __name__ == '__main__':
    unittest.main()