#!/usr/bin/env python3
"""
Debug Parameters Script
======================
Debug script to check what parameters are being read from the Excel test suite.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.excel_test_suite_reader import ExcelTestSuiteReader


def main():
    """Debug parameters reading from Excel file"""
    excel_file = "enhanced_sdm_test_suite.xlsx"
    
    print("🔍 DEBUGGING EXCEL PARAMETERS")
    print("=" * 50)
    print(f"Excel File: {excel_file}")
    print()
    
    # Load test suite from DATAVALIDATIONS sheet
    reader = ExcelTestSuiteReader(excel_file, sheet_name="DATAVALIDATIONS")
    
    # Load the workbook and read test cases
    if not reader.load_workbook():
        print("❌ Failed to load workbook")
        return
    
    reader.load_test_cases()
    test_cases = reader.get_all_test_cases()
    
    data_validation_tests = [tc for tc in test_cases if tc.test_category in [
        'SCHEMA_VALIDATION', 'ROW_COUNT_VALIDATION', 
        'NULL_VALUE_VALIDATION', 'DATA_QUALITY_VALIDATION'
    ]]
    
    print(f"📋 Found {len(data_validation_tests)} data validation test cases:")
    print()
    
    for i, test_case in enumerate(data_validation_tests, 1):
        print(f"[{i}] {test_case.test_case_id} - {test_case.test_case_name}")
        print(f"    Category: {test_case.test_category}")
        print(f"    Parameters: '{test_case.parameters}'")
        
        # Parse parameters like the test executor does
        params = {}
        if test_case.parameters:
            for param in test_case.parameters.split(';'):
                if '=' in param:
                    key, value = param.strip().split('=', 1)
                    params[key.strip()] = value.strip()
        
        source_table = params.get('source_table', 'DEFAULT: products')
        target_table = params.get('target_table', 'DEFAULT: new_products')
        
        print(f"    Parsed source_table: {source_table}")
        print(f"    Parsed target_table: {target_table}")
        print()


if __name__ == "__main__":
    main()