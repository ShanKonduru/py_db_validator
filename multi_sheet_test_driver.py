#!/usr/bin/env python
"""
Multi-Sheet Excel Test Driver

Executes tests from multiple Excel sheets based on CONTROLLER sheet configuration.
Supports dynamic enabling/disabling of test suites for flexible test execution.

Usage:
    python multi_sheet_test_driver.py                          # Execute all enabled sheets
    python multi_sheet_test_driver.py --priority HIGH          # Filter by priority
    python multi_sheet_test_driver.py --reports                # Generate reports
    python multi_sheet_test_driver.py --list-sheets            # List sheet configuration
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.core.multi_sheet_controller import MultiSheetTestController
    from src.reporting.report_generator import ReportGenerator
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("   Make sure you're running from the project root directory")
    sys.exit(1)


def create_argument_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="Execute PostgreSQL tests from multiple Excel sheets based on CONTROLLER configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python multi_sheet_test_driver.py                                    # Execute all enabled sheets
  python multi_sheet_test_driver.py --reports                          # Execute with reports
  python multi_sheet_test_driver.py --excel-file my_suite.xlsx         # Use specific Excel file
  python multi_sheet_test_driver.py --priority HIGH --reports          # High priority tests only
  python multi_sheet_test_driver.py --category CONNECTION              # Connection tests only
  python multi_sheet_test_driver.py --environment DEV                  # DEV environment only
  python multi_sheet_test_driver.py --list-sheets                      # Show sheet configuration
  python multi_sheet_test_driver.py --sheet SMOKE --reports            # Execute specific sheet only

CONTROLLER Sheet Features:
  • Dynamic sheet enabling/disabling
  • Execution priority management
  • Descriptive sheet documentation
  • Centralized test suite control
        """
    )
    
    parser.add_argument(
        "--excel-file", "-f",
        default="sdm_test_suite.xlsx",
        help="Path to Excel test suite file (default: sdm_test_suite.xlsx)"
    )
    
    parser.add_argument(
        "--environment", "-e",
        help="Filter by environment (DEV, STAGING, PROD)"
    )
    
    parser.add_argument(
        "--application", "-a",
        help="Filter by application (DUMMY, MYAPP)"
    )
    
    parser.add_argument(
        "--priority", "-p",
        choices=["HIGH", "MEDIUM", "LOW"],
        help="Filter by priority level"
    )
    
    parser.add_argument(
        "--category", "-c",
        help="Filter by test category (CONNECTION, QUERIES, PERFORMANCE, etc.)"
    )
    
    parser.add_argument(
        "--tags", "-t",
        help="Filter by tags (comma-separated, e.g., smoke,db,integration)"
    )
    
    parser.add_argument(
        "--test-ids", "-i",
        help="Run specific test IDs (comma-separated, e.g., SMOKE_PG_001,SMOKE_PG_004)"
    )
    
    parser.add_argument(
        "--sheet", "-s",
        help="Execute tests from specific sheet only (ignores CONTROLLER)"
    )
    
    parser.add_argument(
        "--list-sheets", "-l",
        action="store_true",
        help="List sheet configuration from CONTROLLER and exit"
    )
    
    parser.add_argument(
        "--reports", "-r",
        action="store_true",
        help="Generate HTML and Markdown reports after execution"
    )
    
    parser.add_argument(
        "--report-dir",
        default="test_reports",
        help="Directory to save test reports (default: test_reports)"
    )
    
    return parser


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Check if Excel file exists
    excel_path = Path(args.excel_file)
    if not excel_path.exists():
        print(f"❌ Error: Excel file '{args.excel_file}' not found!")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Looking for: {excel_path.absolute()}")
        return 1
    
    # Initialize multi-sheet controller
    print(f"📊 Loading multi-sheet Excel test suite: {args.excel_file}")
    controller = MultiSheetTestController(args.excel_file)
    
    if not controller.load_workbook():
        print("❌ Failed to load Excel workbook")
        return 1
    
    # List sheets and exit if requested
    if args.list_sheets:
        if not controller.load_controller_data():
            print("❌ Failed to load CONTROLLER sheet data")
            return 1
        
        controller.print_controller_summary()
        print("\n💡 To execute tests, remove --list-sheets flag")
        return 0
    
    # Handle single sheet execution (bypass CONTROLLER)
    if args.sheet:
        print(f"🎯 Single sheet mode: Executing only '{args.sheet}' sheet")
        
        if args.sheet not in controller.workbook.sheetnames:
            print(f"❌ Sheet '{args.sheet}' not found in workbook")
            print(f"   Available sheets: {', '.join(controller.workbook.sheetnames)}")
            return 1
        
        # Execute single sheet (simulate controller with one enabled sheet)
        from src.core.multi_sheet_controller import SheetController
        single_controller = SheetController(
            enable=True,
            sheet_name=args.sheet,
            description=f"Single sheet execution of {args.sheet}"
        )
        controller.sheet_controllers = [single_controller]
        
        print(f"📊 Executing sheet: {args.sheet}")
    
    # Prepare filters
    filters = {}
    if args.environment:
        filters['environment'] = args.environment
    if args.application:
        filters['application'] = args.application
    if args.priority:
        filters['priority'] = args.priority
    if args.category:
        filters['category'] = args.category
    if args.test_ids:
        filters['test_ids'] = args.test_ids
    if args.tags:
        filters['tags'] = [tag.strip() for tag in args.tags.split(",")]
    
    # Execute tests
    print(f"\n🚀 Starting multi-sheet test execution")
    if filters:
        print(f"🔍 Applied filters: {filters}")
    
    execution_id = f"RUN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"🆔 Execution ID: {execution_id}")
    
    try:
        # Execute controlled tests
        all_results = controller.execute_controlled_tests(**filters)
        
        if not all_results:
            print("\n⚠️  No results generated. Check CONTROLLER configuration and filters.")
            return 1
        
        # Generate reports if requested
        if args.reports:
            print(f"\n{'='*80}")
            print(f"📊 GENERATING MULTI-SHEET TEST REPORTS")
            print(f"{'='*80}")
            
            # Flatten all results for report generation
            all_test_results = []
            for sheet_name, results in all_results.items():
                for result in results:
                    # Add sheet information to result
                    result.sheet_name = sheet_name
                    all_test_results.append(result)
            
            if all_test_results:
                # Generate reports
                report_generator = ReportGenerator()
                
                # Create report directory
                report_dir = Path(args.report_dir)
                report_dir.mkdir(exist_ok=True)
                
                # Generate timestamped report files
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                html_file = report_dir / f"multi_sheet_report_{timestamp}.html"
                md_file = report_dir / f"multi_sheet_report_{timestamp}.md"
                
                # Generate HTML report
                html_content = report_generator.generate_html_report(
                    all_test_results, 
                    execution_id,
                    args.excel_file,
                    multi_sheet=True,
                    sheet_breakdown=all_results
                )
                
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Generate Markdown report
                md_content = report_generator.generate_markdown_report(
                    all_test_results,
                    execution_id, 
                    args.excel_file,
                    multi_sheet=True,
                    sheet_breakdown=all_results
                )
                
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                print(f"📄 HTML Report: {html_file}")
                print(f"📝 Markdown Report: {md_file}")
                print(f"✅ Multi-sheet reports generated successfully in '{args.report_dir}' directory:")
                print(f"   • HTML: {html_file.name}")
                print(f"   • MARKDOWN: {md_file.name}")
                print(f"\n🌐 Open HTML report: file:///{html_file.absolute()}")
            else:
                print("⚠️  No test results to generate reports from")
        
        # Determine exit code based on test results
        total_tests = sum(len(results) for results in all_results.values())
        failed_tests = sum(1 for results in all_results.values() for r in results if r.status == "FAIL")
        
        if failed_tests > 0:
            print(f"\n❌ Test execution completed with {failed_tests} failures out of {total_tests} tests")
            return 1
        else:
            print(f"\n✅ All {total_tests} tests passed successfully!")
            return 0
            
    except Exception as e:
        print(f"\n❌ Error during test execution: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test execution cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)