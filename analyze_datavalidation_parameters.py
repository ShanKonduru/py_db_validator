#!/usr/bin/env python3
"""
Data Validation Test Analysis Script
====================================
Analyzes the DATAVALIDATIONS sheet to understand table references and parameters.
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.excel_test_suite_reader import ExcelTestSuiteReader, TestCase


def analyze_datavalidation_sheet():
    """Analyze the DATAVALIDATIONS sheet parameters in detail"""
    
    print("🔍 ANALYZING DATAVALIDATIONS SHEET PARAMETERS")
    print("=" * 60)
    
    excel_file = "sdm_test_suite.xlsx"
    if not os.path.exists(excel_file):
        print(f"❌ Error: Excel file '{excel_file}' not found!")
        return False
    
    try:
        # Initialize test reader for DATAVALIDATIONS sheet
        test_reader = ExcelTestSuiteReader(excel_file, "DATAVALIDATIONS")
        
        # Load and validate the test suite
        if not test_reader.load_and_validate():
            print("❌ Failed to load or validate Excel test suite!")
            return False
        
        # Get all test cases
        test_cases = test_reader.get_all_test_cases()
        
        if not test_cases:
            print("❌ No data validation test cases found!")
            return False
        
        print(f"\n📊 Found {len(test_cases)} data validation test cases")
        print("\n🔍 DETAILED PARAMETER ANALYSIS:")
        print("-" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}] 🧪 {test_case.test_case_id} - {test_case.test_case_name}")
            print(f"    Category: {test_case.test_category}")
            print(f"    Application: {test_case.application_name}")
            print(f"    Environment: {test_case.environment_name}")
            print(f"    Parameters: '{test_case.parameters}'")
            
            # Parse parameters if they exist
            if test_case.parameters:
                param_dict = test_case.get_parameters_dict()
                if param_dict:
                    print(f"    📋 Parsed Parameters:")
                    for key, value in param_dict.items():
                        print(f"       • {key}: {value}")
                else:
                    print(f"    📋 Raw Parameters: {test_case.parameters}")
            else:
                print(f"    ⚠️  No parameters specified!")
            
            print(f"    Expected Result: {test_case.expected_result}")
            print(f"    Description: {test_case.description}")
        
        # Analyze table references
        print(f"\n📊 TABLE REFERENCE ANALYSIS:")
        print("-" * 40)
        
        source_tables = set()
        target_tables = set()
        all_tables = set()
        
        for test_case in test_cases:
            if test_case.parameters:
                params_lower = test_case.parameters.lower()
                param_dict = test_case.get_parameters_dict()
                
                # Look for source/target table patterns
                for key, value in param_dict.items():
                    key_lower = key.lower()
                    if 'source' in key_lower and 'table' in key_lower:
                        source_tables.add(value)
                        all_tables.add(value)
                    elif 'target' in key_lower and 'table' in key_lower:
                        target_tables.add(value)
                        all_tables.add(value)
                    elif 'table' in key_lower:
                        all_tables.add(value)
                
                # Also check for table names directly in parameters string
                if 'products' in params_lower:
                    all_tables.add('products')
                if 'employees' in params_lower:
                    all_tables.add('employees')
                if 'orders' in params_lower:
                    all_tables.add('orders')
                if 'new_products' in params_lower:
                    all_tables.add('new_products')
        
        print(f"📋 Source Tables Referenced: {len(source_tables)}")
        for table in sorted(source_tables):
            print(f"   • {table}")
        
        print(f"\n📋 Target Tables Referenced: {len(target_tables)}")
        for table in sorted(target_tables):
            print(f"   • {table}")
        
        print(f"\n📋 All Tables Referenced: {len(all_tables)}")
        for table in sorted(all_tables):
            print(f"   • {table}")
        
        # Check if we have source/target pairs
        if len(source_tables) == 0 and len(target_tables) == 0:
            print(f"\n⚠️  WARNING: No explicit source/target table pairs found!")
            print(f"    This suggests the test configuration may be incomplete.")
            print(f"    Data validation typically requires both source and target tables.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = analyze_datavalidation_sheet()
    sys.exit(0 if success else 1)