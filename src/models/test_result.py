"""
TestResult data class for test execution results
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TestResult:
    """Data class for test execution results"""

    test_case_id: str
    test_case_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    error_message: Optional[str]
    environment: str
    application: str
    priority: str
    category: str

    @property
    def is_success(self) -> bool:
        """Check if the test was successful"""
        return self.status == "PASS"

    @property
    def is_failure(self) -> bool:
        """Check if the test failed"""
        return self.status in ["FAIL", "ERROR"]

    @property
    def is_skipped(self) -> bool:
        """Check if the test was skipped"""
        return self.status == "SKIP"

    @property
    def execution_time(self) -> str:
        """Get formatted execution time for compatibility with reports"""
        return f"{self.duration_seconds:.2f}s"

    @property 
    def test_id(self) -> str:
        """Get test ID for compatibility with reports"""
        return self.test_case_id

    @property
    def description(self) -> str:
        """Get test description for compatibility with reports"""
        return self.test_case_name

    @property
    def message(self) -> str:
        """Get error message for compatibility with reports"""
        return self.error_message or ""

    def to_dict(self) -> dict:
        """Convert TestResult to dictionary"""
        return {
            'test_case_id': self.test_case_id,
            'test_case_name': self.test_case_name,
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'environment': self.environment,
            'application': self.application,
            'priority': self.priority,
            'category': self.category
        }