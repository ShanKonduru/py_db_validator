#!/usr/bin/env python
"""
Excel-Driven Test Suite Driver
Executes PostgreSQL smoke tests based on sdm_test_suite.xlsx configuration

Now supports both single-sheet and multi-sheet execution modes:
- Single Sheet: Traditional execution from specific sheet (SMOKE, etc.)
- Multi-Sheet: Controller-based execution from multiple sheets via CONTROLLER sheet

Usage:
  python excel_test_driver.py                              # Single sheet mode (SMOKE)
  python excel_test_driver.py --multi-sheet                # Multi-sheet controller mode
  python excel_test_driver.py --sheet SMOKE --reports      # Specific sheet with reports
"""
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.excel_test_driver import ExcelTestDriver


def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Execute PostgreSQL smoke tests from Excel test suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python excel_test_driver.py                              # Run all enabled tests
  python excel_test_driver.py --reports                    # Run tests and generate reports
  python excel_test_driver.py --environment DEV            # Run DEV environment tests
  python excel_test_driver.py --priority HIGH --reports    # Run high priority tests with reports
  python excel_test_driver.py --category CONNECTION        # Run connection tests only
  python excel_test_driver.py --tags smoke,db              # Run tests with specific tags
  python excel_test_driver.py --test-ids SMOKE_PG_001,SMOKE_PG_004 --reports  # Run specific tests with reports
  python excel_test_driver.py --excel-file my_tests.xlsx --report-dir custom_reports  # Custom files and directories
        """,
    )

    parser.add_argument(
        "--excel-file",
        "-f",
        default="sdm_test_suite.xlsx",
        help="Path to Excel test suite file (default: sdm_test_suite.xlsx)",
    )

    parser.add_argument(
        "--environment",
        "-e",
        help="Filter by environment (DEV, STAGING, PROD)",
    )

    parser.add_argument(
        "--application",
        "-a",
        help="Filter by application (DUMMY, MYAPP)",
    )

    parser.add_argument(
        "--priority",
        "-p",
        choices=["HIGH", "MEDIUM", "LOW"],
        help="Filter by priority level",
    )

    parser.add_argument(
        "--category",
        "-c",
        help="Filter by test category (CONNECTION, QUERIES, PERFORMANCE, etc.)",
    )

    parser.add_argument(
        "--tags",
        "-t",
        help="Filter by tags (comma-separated, e.g., smoke,db,integration)",
    )

    parser.add_argument(
        "--test-ids",
        "-i",
        help="Run specific test IDs (comma-separated, e.g., SMOKE_PG_001,SMOKE_PG_004)",
    )

    parser.add_argument(
        "--sheet",
        "-s",
        help="Specify sheet name to execute (SMOKE, INTEGRATION, etc.). Default: SMOKE",
    )

    parser.add_argument(
        "--multi-sheet",
        "-m",
        action="store_true",
        help="Use multi-sheet controller mode (executes based on CONTROLLER sheet)",
    )

    parser.add_argument(
        "--list-tests",
        "-l",
        action="store_true",
        help="List available tests without executing them",
    )

    parser.add_argument(
        "--reports",
        "-r",
        action="store_true",
        help="Generate HTML and Markdown reports after execution",
    )

    parser.add_argument(
        "--report-dir",
        default="test_reports",
        help="Directory to save test reports (default: test_reports)",
    )

    return parser


def main():
    """Main entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Check for multi-sheet mode
    if args.multi_sheet:
        print("🔄 Multi-sheet mode detected - delegating to multi_sheet_test_driver.py")
        
        # Build command for multi-sheet driver
        import subprocess
        cmd = [sys.executable, "multi_sheet_test_driver.py"]
        
        # Pass through relevant arguments
        if args.excel_file != "sdm_test_suite.xlsx":
            cmd.extend(["--excel-file", args.excel_file])
        if args.environment:
            cmd.extend(["--environment", args.environment])
        if args.application:
            cmd.extend(["--application", args.application])
        if args.priority:
            cmd.extend(["--priority", args.priority])
        if args.category:
            cmd.extend(["--category", args.category])
        if args.tags:
            cmd.extend(["--tags", args.tags])
        if args.test_ids:
            cmd.extend(["--test-ids", args.test_ids])
        if args.reports:
            cmd.append("--reports")
        if args.report_dir != "test_reports":
            cmd.extend(["--report-dir", args.report_dir])
        
        print(f"🚀 Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        return result.returncode

    # Single sheet mode - original behavior
    # Create test driver with specific sheet if provided
    sheet_name = args.sheet or "SMOKE"
    driver = ExcelTestDriver(args.excel_file, sheet_name=sheet_name)

    # Load test suite with validation
    if not driver.load_test_suite():
        print("❌ Failed to load Excel test suite")
        print("\n💡 TIP: Run 'python validate_excel.py' to check for data validation errors")
        print("💡 TIP: Run 'python validate_excel.py --fix-suggestions' for detailed help")
        return 1

    # Parse tags
    tags = None
    if args.tags:
        tags = [tag.strip() for tag in args.tags.split(",")]

    # Parse test IDs
    test_ids = None
    if args.test_ids:
        test_ids = [tid.strip() for tid in args.test_ids.split(",")]

    # List tests mode
    if args.list_tests:
        test_cases = driver.reader.get_filtered_test_cases(
            environment=args.environment,
            application=args.application,
            priority=args.priority,
            category=args.category,
            tags=tags,
            enabled_only=True,
        )

        print(f"\n📋 Available Tests ({len(test_cases)} found):")
        print("-" * 80)

        for tc in test_cases:
            print(f"🧪 {tc.test_case_id}: {tc.test_case_name}")
            print(
                f"   Environment: {tc.environment_name} | Application: {tc.application_name}"
            )
            print(f"   Priority: {tc.priority} | Category: {tc.test_category}")
            print(f"   Tags: {tc.tags}")
            print(f"   Enabled: {'✅' if tc.enable else '❌'}")
            print()

        return 0

    # Execute tests
    try:
        results = driver.execute_test_suite(
            environment=args.environment,
            application=args.application,
            priority=args.priority,
            category=args.category,
            tags=tags,
            test_ids=test_ids,
        )

        # Print summary
        driver.print_summary()

        # Generate reports if requested
        if args.reports:
            print("\n" + "=" * 80)
            print("📊 GENERATING TEST REPORTS")
            print("=" * 80)
            
            reports = driver.save_reports(args.report_dir)
            
            if reports:
                print(f"✅ Reports generated successfully in '{args.report_dir}' directory:")
                for report_type, filepath in reports.items():
                    print(f"   • {report_type.upper()}: {filepath}")
                
                # Show quick access info
                if 'html' in reports:
                    print(f"\n🌐 Open HTML report: file:///{Path(reports['html']).absolute()}")
            else:
                print("❌ No reports were generated")

        # Return appropriate exit code
        if not results:
            return 1

        failed_count = sum(1 for r in results if r.status in ["FAIL", "ERROR"])
        return 1 if failed_count > 0 else 0

    except KeyboardInterrupt:
        print("\n⚠️ Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Unexpected error during test execution: {e}")
        return 1


if __name__ == "__main__":
    exit(main())