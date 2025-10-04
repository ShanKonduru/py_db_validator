"""
Markdown report generator for test results
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.reporting.base_report_generator import BaseReportGenerator
from src.models.test_result import TestResult


class MarkdownReportGenerator(BaseReportGenerator):
    """Generates Markdown test reports"""

    def generate_report(self, results: List[TestResult], output_dir: str) -> str:
        """Generate Markdown test report"""
        if not results:
            return ""

        # Create output directory and get file path
        output_path = self._ensure_output_dir(output_dir)
        timestamp = self._get_timestamp()
        md_filename = output_path / f"test_report_{timestamp}.md"
        
        # Calculate statistics
        stats = self._calculate_statistics(results)
        
        # Group results by status
        grouped_results = self._group_results_by_status(results)
        
        # Generate Markdown content
        md_content = self._generate_markdown_content(results, stats, grouped_results)
        
        # Write Markdown file
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(md_filename)

    def _group_results_by_status(self, results: List[TestResult]) -> dict:
        """Group test results by their status"""
        passed_results = [r for r in results if r.status == "PASS"]
        failed_results = [r for r in results if r.status in ["FAIL", "ERROR"]]
        skipped_results = [r for r in results if r.status == "SKIP"]
        
        return {
            'passed': passed_results,
            'failed': failed_results,
            'skipped': skipped_results
        }

    def _generate_markdown_content(self, results: List[TestResult], stats: dict, grouped_results: dict) -> str:
        """Generate the complete Markdown content"""
        content_parts = [
            self._generate_header(),
            self._generate_execution_summary(stats),
            self._generate_statistics_table(stats),
            self._generate_success_rate_analysis(stats['success_rate']),
            self._generate_detailed_results_table(results),
            self._generate_status_sections(grouped_results),
            self._generate_execution_timeline(results),
            self._generate_recommendations(grouped_results['failed']),
            self._generate_footer()
        ]
        
        return '\n'.join(content_parts)

    def _generate_header(self) -> str:
        """Generate the Markdown header"""
        return "# 📊 Test Execution Report"

    def _generate_execution_summary(self, stats: dict) -> str:
        """Generate the execution summary section"""
        return f"""## 📋 Execution Summary

- **Execution ID:** `{self.execution_id}`
- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Excel File:** `{self.excel_file}`
- **Total Duration:** {stats['total_duration']:.2f} seconds"""

    def _generate_statistics_table(self, stats: dict) -> str:
        """Generate the statistics table"""
        return f"""## 📈 Test Statistics

| Metric | Value | Percentage |
|--------|-------|------------|
| **Total Tests** | {stats['total_tests']} | 100.0% |
| **✅ Passed** | {stats['passed_tests']} | {(stats['passed_tests']/stats['total_tests']*100):.1f}% |
| **❌ Failed** | {stats['failed_tests']} | {(stats['failed_tests']/stats['total_tests']*100):.1f}% |
| **⏭️ Skipped** | {stats['skipped_tests']} | {(stats['skipped_tests']/stats['total_tests']*100):.1f}% |
| **📈 Success Rate** | {stats['success_rate']:.1f}% | - |"""

    def _generate_success_rate_analysis(self, success_rate: float) -> str:
        """Generate success rate analysis"""
        analysis = "## 🎯 Success Rate Analysis\n\n"
        
        if success_rate >= 95:
            analysis += "🟢 **Excellent** - Test suite is performing very well with minimal failures."
        elif success_rate >= 85:
            analysis += "🟡 **Good** - Test suite is mostly stable with some areas for improvement."
        elif success_rate >= 70:
            analysis += "🟠 **Fair** - Test suite needs attention to address recurring failures."
        else:
            analysis += "🔴 **Poor** - Test suite requires immediate investigation and fixes."
        
        return analysis

    def _generate_detailed_results_table(self, results: List[TestResult]) -> str:
        """Generate the detailed results table"""
        table_header = """## 📋 Detailed Test Results

| Test ID | Test Name | Status | Duration | Environment | Application | Priority | Category | Error Message |
|---------|-----------|--------|----------|-------------|-------------|----------|----------|---------------|"""
        
        table_rows = []
        for result in results:
            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌", 
                "SKIP": "⏭️",
                "ERROR": "💥"
            }.get(result.status, "❓")
            
            error_msg = result.error_message.replace('|', '\\|') if result.error_message else "-"
            if len(error_msg) > 50:
                error_msg = error_msg[:47] + "..."
            
            table_rows.append(f"| `{result.test_case_id}` | {result.test_case_name} | {status_emoji} {result.status} | {result.duration_seconds:.2f}s | {result.environment} | {result.application} | {result.priority} | {result.category} | {error_msg} |")
        
        return table_header + '\n' + '\n'.join(table_rows)

    def _generate_status_sections(self, grouped_results: dict) -> str:
        """Generate sections for each status type"""
        sections = []
        
        # Passed tests section
        if grouped_results['passed']:
            sections.append(f"## ✅ Passed Tests ({len(grouped_results['passed'])})\n")
            for result in grouped_results['passed']:
                sections.append(f"- **{result.test_case_id}**: {result.test_case_name} ({result.duration_seconds:.2f}s)")
        
        # Failed tests section
        if grouped_results['failed']:
            sections.append(f"\n## ❌ Failed Tests ({len(grouped_results['failed'])})\n")
            for result in grouped_results['failed']:
                sections.append(f"### {result.test_case_id}: {result.test_case_name}\n")
                sections.append(f"- **Status:** {result.status}")
                sections.append(f"- **Duration:** {result.duration_seconds:.2f}s")
                sections.append(f"- **Environment:** {result.environment}")
                sections.append(f"- **Application:** {result.application}")
                sections.append(f"- **Priority:** {result.priority}")
                sections.append(f"- **Category:** {result.category}")
                if result.error_message:
                    sections.append(f"- **Error:** `{result.error_message}`")
                sections.append("")
        
        # Skipped tests section
        if grouped_results['skipped']:
            sections.append(f"\n## ⏭️ Skipped Tests ({len(grouped_results['skipped'])})\n")
            for result in grouped_results['skipped']:
                sections.append(f"- **{result.test_case_id}**: {result.test_case_name}")
        
        return '\n'.join(sections)

    def _generate_execution_timeline(self, results: List[TestResult]) -> str:
        """Generate execution timeline section"""
        timeline = ["\n## ⏱️ Execution Timeline\n"]
        timeline.append("| Order | Test ID | Test Name | Start Time | Duration | Status |")
        timeline.append("|-------|---------|-----------|------------|----------|--------|")
        
        for i, result in enumerate(results, 1):
            start_time = result.start_time.strftime('%H:%M:%S')
            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌", 
                "SKIP": "⏭️",
                "ERROR": "💥"
            }.get(result.status, "❓")
            
            timeline.append(f"| {i} | `{result.test_case_id}` | {result.test_case_name} | {start_time} | {result.duration_seconds:.2f}s | {status_emoji} {result.status} |")
        
        return '\n'.join(timeline)

    def _generate_recommendations(self, failed_results: List[TestResult]) -> str:
        """Generate recommendations for failed tests"""
        if not failed_results:
            return ""
        
        recommendations = ["\n## 🔧 Recommendations\n"]
        
        # Group failures by category
        failure_categories = {}
        for result in failed_results:
            cat = result.category
            if cat not in failure_categories:
                failure_categories[cat] = []
            failure_categories[cat].append(result)
        
        for category, failures in failure_categories.items():
            recommendations.append(f"### {category} Issues ({len(failures)} failures)\n")
            for failure in failures:
                recommendations.append(f"- **{failure.test_case_id}**: Investigate {failure.test_case_name.lower()}")
            
            # Add category-specific recommendations
            if category == "CONNECTION":
                recommendations.extend([
                    "\n**Recommendations:**",
                    "- Verify database server is running and accessible",
                    "- Check network connectivity and firewall settings",
                    "- Validate connection credentials and permissions\n"
                ])
            elif category == "QUERIES":
                recommendations.extend([
                    "\n**Recommendations:**",
                    "- Check database schema and table structures",
                    "- Verify SQL syntax and compatibility",
                    "- Review database permissions for query execution\n"
                ])
            elif category == "PERFORMANCE":
                recommendations.extend([
                    "\n**Recommendations:**",
                    "- Monitor database server resources (CPU, memory, disk)",
                    "- Check for blocking queries or locks",
                    "- Review database configuration and indexing\n"
                ])
        
        return '\n'.join(recommendations)

    def _generate_footer(self) -> str:
        """Generate the Markdown footer"""
        return f"\n---\n\n**Report generated by Excel Test Driver on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**"