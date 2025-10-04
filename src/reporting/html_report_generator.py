"""
HTML report generator for test results
"""
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.reporting.base_report_generator import BaseReportGenerator
from src.models.test_result import TestResult


class HtmlReportGenerator(BaseReportGenerator):
    """Generates HTML test reports"""

    def generate_report(self, results: List[TestResult], output_dir: str) -> str:
        """Generate HTML test report"""
        if not results:
            return ""

        # Create output directory and get file path
        output_path = self._ensure_output_dir(output_dir)
        timestamp = self._get_timestamp()
        html_filename = output_path / f"test_report_{timestamp}.html"
        
        # Calculate statistics
        stats = self._calculate_statistics(results)
        
        # Generate HTML content
        html_content = self._generate_html_content(results, stats)
        
        # Write HTML file
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_filename)

    def _generate_html_content(self, results: List[TestResult], stats: dict) -> str:
        """Generate the complete HTML content"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Execution Report - {self.execution_id}</title>
    <style>
        {self._get_css_styles(stats['success_rate'])}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header()}
        {self._generate_stats_grid(stats)}
        {self._generate_results_table(results)}
        {self._generate_footer()}
    </div>
</body>
</html>"""

    def _get_css_styles(self, success_rate: float) -> str:
        """Get CSS styles for the HTML report"""
        success_color = '#28a745' if success_rate >= 90 else '#ffc107' if success_rate >= 70 else '#dc3545'
        
        return f"""
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
        }}
        .header h1 {{
            color: #007acc;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .execution-info {{
            color: #666;
            margin-top: 10px;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f0f8ff, #e6f3ff);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007acc;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007acc;
            margin-bottom: 5px;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .pass {{ color: #28a745; }}
        .fail {{ color: #dc3545; }}
        .skip {{ color: #ffc107; }}
        .success-rate {{
            font-size: 1.5em;
            font-weight: bold;
            color: {success_color};
        }}
        .results-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .results-table th {{
            background: #007acc;
            color: white;
            padding: 15px 10px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #005a9c;
        }}
        .results-table td {{
            padding: 12px 10px;
            border-bottom: 1px solid #eee;
        }}
        .results-table tr:hover {{
            background-color: #f8f9fa;
        }}
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-pass {{
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .status-fail {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .status-skip {{
            background-color: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }}
        .status-error {{
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .duration {{
            font-family: 'Courier New', monospace;
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .error-message {{
            color: #dc3545;
            font-style: italic;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }}
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            .results-table {{
                font-size: 0.85em;
            }}
        }}
        """

    def _generate_header(self) -> str:
        """Generate the HTML header section"""
        return f"""
        <div class="header">
            <h1>📊 Test Execution Report</h1>
            <div class="execution-info">
                <strong>Execution ID:</strong> {self.execution_id}<br>
                <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                <strong>Excel File:</strong> {self.excel_file}
            </div>
        </div>"""

    def _generate_stats_grid(self, stats: dict) -> str:
        """Generate the statistics grid section"""
        return f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['total_tests']}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value pass">{stats['passed_tests']}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value fail">{stats['failed_tests']}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value skip">{stats['skipped_tests']}</div>
                <div class="stat-label">Skipped</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['total_duration']:.2f}s</div>
                <div class="stat-label">Total Duration</div>
            </div>
            <div class="stat-card">
                <div class="stat-value success-rate">{stats['success_rate']:.1f}%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        </div>"""

    def _generate_results_table(self, results: List[TestResult]) -> str:
        """Generate the results table section"""
        table_rows = ""
        for result in results:
            status_class = f"status-{result.status.lower()}"
            error_display = result.error_message if result.error_message else "-"
            
            table_rows += f"""
                <tr>
                    <td><strong>{result.test_case_id}</strong></td>
                    <td>{result.test_case_name}</td>
                    <td><span class="status-badge {status_class}">{result.status}</span></td>
                    <td><span class="duration">{result.duration_seconds:.2f}s</span></td>
                    <td>{result.environment}</td>
                    <td>{result.application}</td>
                    <td>{result.priority}</td>
                    <td>{result.category}</td>
                    <td><span class="error-message" title="{error_display}">{error_display}</span></td>
                </tr>"""

        return f"""
        <h2>📋 Detailed Test Results</h2>
        <table class="results-table">
            <thead>
                <tr>
                    <th>Test ID</th>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Environment</th>
                    <th>Application</th>
                    <th>Priority</th>
                    <th>Category</th>
                    <th>Error Message</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>"""

    def _generate_footer(self) -> str:
        """Generate the HTML footer section"""
        return f"""
        <div class="footer">
            Generated by Excel Test Driver | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>"""