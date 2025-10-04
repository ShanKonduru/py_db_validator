"""
Enhanced Report Generator for Multi-Sheet Test Execution

Generates comprehensive HTML and Markdown reports for multi-sheet test suites.
Supports sheet-level breakdowns, execution summaries, and detailed test results.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class ReportGenerator:
    """Enhanced report generator for multi-sheet test executions"""
    
    def __init__(self):
        self.timestamp = datetime.now()
    
    def generate_html_report(
        self, 
        test_results: List[Any], 
        execution_id: str,
        excel_file: str,
        multi_sheet: bool = False,
        sheet_breakdown: Optional[Dict[str, List[Any]]] = None
    ) -> str:
        """Generate comprehensive HTML report"""
        
        # Calculate overall statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.status == "PASS")
        failed_tests = sum(1 for r in test_results if r.status == "FAIL")
        skipped_tests = sum(1 for r in test_results if r.status == "SKIP")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Start HTML document
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{'Multi-Sheet ' if multi_sheet else ''}Test Execution Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background-color: #f8f9fa;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .summary-card .label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .pass {{ color: #28a745; }}
        .fail {{ color: #dc3545; }}
        .skip {{ color: #ffc107; }}
        .total {{ color: #6c757d; }}
        
        .sheet-breakdown {{
            margin: 30px;
        }}
        .sheet-card {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .sheet-header {{
            background-color: #e9ecef;
            padding: 15px 20px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .sheet-name {{
            font-size: 1.3em;
            font-weight: 600;
            color: #495057;
        }}
        .sheet-stats {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .test-results {{
            margin: 30px;
        }}
        .test-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-table th {{
            background-color: #495057;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        .test-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        .test-table tr:last-child td {{
            border-bottom: none;
        }}
        .test-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .status {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .status.pass {{
            background-color: #d4edda;
            color: #155724;
        }}
        .status.fail {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .status.skip {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .execution-time {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        .progress-bar {{
            background-color: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            transition: width 0.3s ease;
        }}
        .footer {{
            background-color: #495057;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{'Multi-Sheet ' if multi_sheet else ''}Test Execution Report</h1>
            <div class="subtitle">
                Excel File: {excel_file} | Execution ID: {execution_id}
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="number total">{total_tests}</div>
                <div class="label">Total Tests</div>
            </div>
            <div class="summary-card">
                <div class="number pass">{passed_tests}</div>
                <div class="label">Passed</div>
            </div>
            <div class="summary-card">
                <div class="number fail">{failed_tests}</div>
                <div class="label">Failed</div>
            </div>
            <div class="summary-card">
                <div class="number skip">{skipped_tests}</div>
                <div class="label">Skipped</div>
            </div>
        </div>
        
        <div style="margin: 30px; text-align: center;">
            <h3>Success Rate: {success_rate:.1f}%</h3>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {success_rate}%;"></div>
            </div>
        </div>
"""

        # Add sheet breakdown for multi-sheet reports
        if multi_sheet and sheet_breakdown:
            html_content += """
        <div class="sheet-breakdown">
            <h2>Sheet Breakdown</h2>
"""
            for sheet_name, sheet_results in sheet_breakdown.items():
                sheet_total = len(sheet_results)
                sheet_passed = sum(1 for r in sheet_results if r.status == "PASS")
                sheet_failed = sum(1 for r in sheet_results if r.status == "FAIL")
                sheet_rate = (sheet_passed / sheet_total * 100) if sheet_total > 0 else 0
                
                html_content += f"""
            <div class="sheet-card">
                <div class="sheet-header">
                    <div class="sheet-name">{sheet_name}</div>
                    <div class="sheet-stats">
                        {sheet_total} tests | {sheet_passed} passed | {sheet_failed} failed | {sheet_rate:.1f}% success
                    </div>
                </div>
            </div>
"""
            html_content += """
        </div>
"""

        # Add detailed test results table
        html_content += """
        <div class="test-results">
            <h2>Detailed Test Results</h2>
            <table class="test-table">
                <thead>
                    <tr>
                        <th>Test ID</th>
"""
        
        if multi_sheet:
            html_content += "<th>Sheet</th>"
        
        html_content += """
                        <th>Description</th>
                        <th>Status</th>
                        <th>Execution Time</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody>
"""

        for result in test_results:
            status_class = result.status.lower()
            execution_time = getattr(result, 'execution_time', 'N/A')
            message = getattr(result, 'message', '') or ''
            if len(message) > 100:
                message = message[:97] + "..."
            
            html_content += f"""
                    <tr>
                        <td><strong>{result.test_id}</strong></td>
"""
            if multi_sheet:
                sheet_name = getattr(result, 'sheet_name', 'Unknown')
                html_content += f"<td>{sheet_name}</td>"
            
            html_content += f"""
                        <td>{result.description}</td>
                        <td><span class="status {status_class}">{result.status}</span></td>
                        <td class="execution-time">{execution_time}</td>
                        <td>{message}</td>
                    </tr>
"""

        html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Generated on {self.timestamp.strftime('%B %d, %Y at %I:%M %p')} | 
            Python PostgreSQL Test Framework
        </div>
    </div>
</body>
</html>
"""
        return html_content
    
    def generate_markdown_report(
        self, 
        test_results: List[Any], 
        execution_id: str,
        excel_file: str,
        multi_sheet: bool = False,
        sheet_breakdown: Optional[Dict[str, List[Any]]] = None
    ) -> str:
        """Generate comprehensive Markdown report"""
        
        # Calculate statistics
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.status == "PASS")
        failed_tests = sum(1 for r in test_results if r.status == "FAIL")
        skipped_tests = sum(1 for r in test_results if r.status == "SKIP")
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        markdown_content = f"""# {'Multi-Sheet ' if multi_sheet else ''}Test Execution Report

**Excel File:** `{excel_file}`  
**Execution ID:** `{execution_id}`  
**Generated:** {self.timestamp.strftime('%B %d, %Y at %I:%M %p')}

## 📊 Executive Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Tests** | {total_tests} | 100.0% |
| **✅ Passed** | {passed_tests} | {(passed_tests/total_tests*100):.1f}% |
| **❌ Failed** | {failed_tests} | {(failed_tests/total_tests*100):.1f}% |
| **⏭️ Skipped** | {skipped_tests} | {(skipped_tests/total_tests*100):.1f}% |

**Overall Success Rate:** {success_rate:.1f}%

"""

        # Add sheet breakdown for multi-sheet reports
        if multi_sheet and sheet_breakdown:
            markdown_content += """## 📋 Sheet Breakdown

"""
            for sheet_name, sheet_results in sheet_breakdown.items():
                sheet_total = len(sheet_results)
                sheet_passed = sum(1 for r in sheet_results if r.status == "PASS")
                sheet_failed = sum(1 for r in sheet_results if r.status == "FAIL")
                sheet_skipped = sum(1 for r in sheet_results if r.status == "SKIP")
                sheet_rate = (sheet_passed / sheet_total * 100) if sheet_total > 0 else 0
                
                status_emoji = "✅" if sheet_failed == 0 else "❌"
                
                markdown_content += f"""### {status_emoji} {sheet_name}

- **Total:** {sheet_total} tests
- **Passed:** {sheet_passed} 
- **Failed:** {sheet_failed}
- **Skipped:** {sheet_skipped}
- **Success Rate:** {sheet_rate:.1f}%

"""

        # Add detailed results table
        markdown_content += """## 📝 Detailed Test Results

"""
        
        if multi_sheet:
            markdown_content += """| Test ID | Sheet | Description | Status | Execution Time | Message |
|---------|-------|-------------|--------|----------------|---------|
"""
        else:
            markdown_content += """| Test ID | Description | Status | Execution Time | Message |
|---------|-------------|--------|----------------|---------|
"""

        for result in test_results:
            status_emoji = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}.get(result.status, "❓")
            execution_time = getattr(result, 'execution_time', 'N/A')
            message = getattr(result, 'message', '') or ''
            
            # Escape markdown special characters in message
            message = message.replace('|', '\\|').replace('\n', ' ')
            if len(message) > 80:
                message = message[:77] + "..."
            
            if multi_sheet:
                sheet_name = getattr(result, 'sheet_name', 'Unknown')
                markdown_content += f"| `{result.test_id}` | {sheet_name} | {result.description} | {status_emoji} {result.status} | {execution_time} | {message} |\n"
            else:
                markdown_content += f"| `{result.test_id}` | {result.description} | {status_emoji} {result.status} | {execution_time} | {message} |\n"

        # Add failure analysis if there are failures
        if failed_tests > 0:
            markdown_content += f"""
## 🔍 Failure Analysis

**Failed Tests:** {failed_tests} out of {total_tests}

"""
            failed_results = [r for r in test_results if r.status == "FAIL"]
            for i, result in enumerate(failed_results[:10], 1):  # Show first 10 failures
                message = getattr(result, 'message', 'No error message available')
                markdown_content += f"""### {i}. {result.test_id}
**Description:** {result.description}  
**Error:** {message}

"""
            
            if len(failed_results) > 10:
                markdown_content += f"*... and {len(failed_results) - 10} more failures*\n\n"

        # Add recommendations
        if failed_tests > 0:
            markdown_content += """## 💡 Recommendations

- Review failed test cases and their error messages
- Check database connectivity and permissions
- Verify test data and expected results
- Consider running tests individually for detailed debugging
- Update test cases if business requirements have changed

"""
        else:
            markdown_content += """## 🎉 All Tests Passed!

Excellent work! All test cases executed successfully.

"""

        markdown_content += f"""## 🏷️ Test Execution Details

- **Framework:** Python PostgreSQL Test Framework
- **Report Format:** Markdown
- **Execution Mode:** {'Multi-Sheet Controller' if multi_sheet else 'Single Sheet'}
- **Timestamp:** {self.timestamp.isoformat()}

---
*This report was automatically generated by the PostgreSQL Test Framework*
"""

        return markdown_content