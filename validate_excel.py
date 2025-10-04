#!/usr/bin/env python
"""
Excel Test Suite Validation Tool

This tool validates Excel test suite files before execution to catch user input errors.
Run this before executing tests to ensure data integrity and prevent execution failures.

Usage:
    python validate_excel.py [excel_file]
    python validate_excel.py sdm_test_suite.xlsx
    python validate_excel.py --help
"""
import sys
import argparse
from pathlib import Path
from openpyxl import load_workbook

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.validation.excel_validator import ExcelTestSuiteValidator, ValidationSeverity
except ImportError as e:
    print(f"❌ Error importing validation module: {e}")
    print("   Make sure you're running from the project root directory")
    sys.exit(1)


def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(
        description="Validate Excel test suite files for data integrity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_excel.py                           # Validate default file (sdm_test_suite.xlsx)
  python validate_excel.py my_tests.xlsx            # Validate specific file
  python validate_excel.py --worksheet INTEGRATION  # Validate specific worksheet
  python validate_excel.py --strict                 # Treat warnings as errors
  python validate_excel.py --fix-suggestions        # Show detailed fix suggestions
        """
    )
    
    parser.add_argument(
        "excel_file",
        nargs="?",
        default="sdm_test_suite.xlsx",
        help="Path to Excel test suite file (default: sdm_test_suite.xlsx)"
    )
    
    parser.add_argument(
        "--worksheet", "-w",
        default="SMOKE",
        help="Worksheet name to validate (default: SMOKE)"
    )
    
    parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="Treat warnings as errors (fail validation on any warning)"
    )
    
    parser.add_argument(
        "--fix-suggestions", "-f",
        action="store_true",
        help="Show detailed fix suggestions for each issue"
    )
    
    parser.add_argument(
        "--export-report", "-e",
        help="Export validation report to specified file (e.g., validation_report.txt)"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    excel_path = Path(args.excel_file)
    if not excel_path.exists():
        print(f"❌ Error: Excel file '{args.excel_file}' not found!")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Looking for: {excel_path.absolute()}")
        return 1
    
    print(f"🔍 Validating Excel file: {args.excel_file}")
    print(f"📊 Worksheet: {args.worksheet}")
    print("=" * 60)
    
    try:
        # Load workbook
        workbook = load_workbook(excel_path)
        
        # Initialize validator
        validator = ExcelTestSuiteValidator()
        
        # Run validation
        is_valid, validation_messages = validator.validate_test_suite(workbook, args.worksheet)
        
        # Generate report
        report = validator.generate_validation_report()
        print(report)
        
        # Export report if requested
        if args.export_report:
            with open(args.export_report, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report exported to: {args.export_report}")
        
        # Show detailed fix suggestions if requested
        if args.fix_suggestions:
            print("\n🔧 DETAILED FIX SUGGESTIONS:")
            print("=" * 40)
            
            for msg in validation_messages:
                if msg.severity in [ValidationSeverity.ERROR, ValidationSeverity.WARNING]:
                    print(f"\n📍 Row {msg.row}, Column {msg.column} - {msg.field}")
                    print(f"   Issue: {msg.message}")
                    print(f"   Current Value: '{msg.current_value}'")
                    if msg.suggested_value:
                        print(f"   💡 Suggestion: {msg.suggested_value}")
                    
                    # Add specific fix instructions based on field
                    fix_instructions = get_fix_instructions(msg.field, msg.current_value)
                    if fix_instructions:
                        print(f"   🛠️  How to fix: {fix_instructions}")
        
        # Determine exit code
        errors = [msg for msg in validation_messages if msg.severity == ValidationSeverity.ERROR]
        warnings = [msg for msg in validation_messages if msg.severity == ValidationSeverity.WARNING]
        
        if errors:
            print(f"\n❌ VALIDATION FAILED: {len(errors)} critical errors found!")
            print("   These MUST be fixed before test execution.")
            return 1
        elif warnings and args.strict:
            print(f"\n⚠️  VALIDATION FAILED (strict mode): {len(warnings)} warnings treated as errors!")
            return 1
        elif warnings:
            print(f"\n⚠️  VALIDATION PASSED with {len(warnings)} warnings.")
            print("   Consider fixing warnings for better test execution.")
            return 0
        else:
            print(f"\n✅ VALIDATION PASSED: Excel file is ready for test execution!")
            return 0
            
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return 1


def get_fix_instructions(field: str, current_value: str) -> str:
    """Get specific fix instructions for common field errors"""
    instructions = {
        "Test_Category": "Choose from: SETUP, CONFIGURATION, SECURITY, CONNECTION, QUERIES, PERFORMANCE, COMPATIBILITY. This determines which test function will be executed!",
        "Priority": "Use: HIGH, MEDIUM, or LOW (case-insensitive)",
        "Environment_Name": "Use: DEV, STAGING, PROD, TEST, or UAT (case-insensitive)",
        "Application_Name": "Use: DUMMY, MYAPP, POSTGRES, or DATABASE (case-insensitive)",
        "Expected_Result": "Use: PASS, FAIL, or SKIP (case-insensitive)",
        "Enable": "Use: TRUE, FALSE, YES, NO, Y, N, 1, or 0",
        "Test_Case_ID": "Use format like SMOKE_PG_001, SMOKE_PG_002, etc. Must be unique.",
        "Timeout_Seconds": "Enter a number between 5 and 3600 (seconds)",
        "Test_Case_Name": "Enter a descriptive name for the test case",
        "Description": "Enter a clear description of what the test validates",
    }
    
    return instructions.get(field, "Check the value and correct according to validation message")


def show_valid_categories_mapping():
    """Show mapping of test categories to functions"""
    print("\n📋 TEST CATEGORY → FUNCTION MAPPING:")
    print("=" * 45)
    
    mappings = {
        "SETUP": "test_environment_setup()",
        "CONFIGURATION": "test_dummy_config_availability()", 
        "SECURITY": "test_environment_credentials()",
        "CONNECTION": "test_postgresql_connection()",
        "QUERIES": "test_postgresql_basic_queries()",
        "PERFORMANCE": "test_postgresql_connection_performance()",
        "COMPATIBILITY": "test_compatibility() [Not implemented yet]",
        "MONITORING": "test_monitoring() [Future implementation]",
        "BACKUP": "test_backup_restore() [Future implementation]",
    }
    
    for category, function in mappings.items():
        status = "✅" if "Not implemented" not in function and "Future" not in function else "⚠️ "
        print(f"   {status} {category:<15} → {function}")
    
    print("\n💡 TIP: The Test_Category column is CRITICAL as it determines which")
    print("         test function gets executed. Wrong category = wrong test!")


if __name__ == "__main__":
    try:
        exit_code = main()
        
        if len(sys.argv) == 1:  # No arguments provided
            print("\n" + "=" * 60)
            show_valid_categories_mapping()
            print(f"\n🔍 To validate a different file: python {sys.argv[0]} your_file.xlsx")
            print(f"📖 For more options: python {sys.argv[0]} --help")
        
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Validation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)