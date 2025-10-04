"""
Base class for test report generators
"""
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.test_result import TestResult


class BaseReportGenerator(ABC):
    """Abstract base class for all report generators"""

    def __init__(self, execution_id: str, excel_file: str):
        """Initialize the report generator"""
        self.execution_id = execution_id
        self.excel_file = excel_file

    @abstractmethod
    def generate_report(self, results: List[TestResult], output_dir: str) -> str:
        """Generate a report and return the file path"""
        pass

    def _ensure_output_dir(self, output_dir: str) -> Path:
        """Ensure the output directory exists and return Path object"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        return output_path

    def _get_timestamp(self) -> str:
        """Get formatted timestamp from execution ID"""
        return self.execution_id.replace("RUN_", "").replace("_", "-")

    def _calculate_statistics(self, results: List[TestResult]) -> dict:
        """Calculate common statistics from test results"""
        if not results:
            return {}

        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.status == "PASS")
        failed_tests = sum(1 for r in results if r.status in ["FAIL", "ERROR"])
        skipped_tests = sum(1 for r in results if r.status == "SKIP")
        total_duration = sum(r.duration_seconds for r in results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'total_duration': total_duration,
            'success_rate': success_rate
        }