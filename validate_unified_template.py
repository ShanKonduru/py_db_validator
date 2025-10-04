#!/usr/bin/env python3
"""
Unified Excel Template Validator
===============================
Validate all sheets in the unified Excel template.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.excel_test_suite_reader import ExcelTestSuiteReader


def validate_unified_template(excel_file: str):
    """Validate all sheets in the unified Excel template"""
    
    print("🔍 UNIFIED EXCEL TEMPLATE VALIDATION")
    print("=" * 50)
    print(f"Excel File: {excel_file}")
    print()
    
    sheets_to_validate = ["SMOKE", "CONTROLLER", "DATAVALIDATIONS"]
    
    for sheet_name in sheets_to_validate:
        print(f"📋 Validating {sheet_name} sheet:")
        print("-" * 30)
        
        try:
            # Create reader for this sheet
            reader = ExcelTestSuiteReader(excel_file, sheet_name=sheet_name)
            
            # Load and validate
            if reader.load_workbook():
                reader.load_test_cases()
                test_cases = reader.get_all_test_cases()
                
                print(f"   ✅ Successfully loaded {len(test_cases)} test cases")
                
                # Show test breakdown
                enabled = len([tc for tc in test_cases if tc.enable])
                disabled = len([tc for tc in test_cases if not tc.enable])
                
                print(f"   📊 Enabled: {enabled} | Disabled: {disabled}")
                
                # Show categories
                categories = {}
                for tc in test_cases:
                    categories[tc.test_category] = categories.get(tc.test_category, 0) + 1
                
                if categories:
                    print(f"   📋 Categories: {dict(categories)}")
                
            else:
                print(f"   ❌ Failed to load {sheet_name} sheet")
        
        except Exception as e:
            print(f"   ❌ Error validating {sheet_name}: {e}")
        
        print()
    
    print("✅ UNIFIED TEMPLATE VALIDATION COMPLETE!")


def main():
    """Main execution function"""
    excel_file = sys.argv[1] if len(sys.argv) > 1 else "unified_sdm_test_suite.xlsx"
    validate_unified_template(excel_file)


if __name__ == "__main__":
    main()