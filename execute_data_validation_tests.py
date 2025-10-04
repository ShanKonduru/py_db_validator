#!/usr/bin/env python3
"""
Data Validation Test Execution Script
=====================================
Executes data validation tests from the Excel test suite with detailed analysis and reporting.

Author: Multi-Database Data Validation Framework
Date: October 4, 2025
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.excel_test_suite_reader import ExcelTestSuiteReader, TestCase
from src.core.test_executor import TestExecutor
from src.validators.data_validator import DataValidator


def print_header():
    """Print execution header"""
    print("🔍 EXECUTING DATA VALIDATION TESTS FROM EXCEL TEST SUITE")
    print("=" * 64)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Suite: sdm_test_suite.xlsx")
    print(f"Target Sheet: DATAVALIDATIONS")
    print()


def analyze_test_failures(failed_tests):
    """Analyze and categorize test failures"""
    print("🔍 DETAILED FAILURE ANALYSIS:")
    print("-" * 50)
    
    failure_categories = {
        'Schema Differences': [],
        'Row Count Mismatches': [],
        'NULL Value Issues': [],
        'Data Quality Issues': [],
        'Connection Issues': [],
        'Other Issues': []
    }
    
    for test in failed_tests:
        error_msg = test.get('error', '').lower()
        test_name = test.get('name', 'Unknown')
        
        if 'schema differences' in error_msg:
            failure_categories['Schema Differences'].append(test)
        elif 'row count mismatch' in error_msg:
            failure_categories['Row Count Mismatches'].append(test)
        elif 'null value differences' in error_msg:
            failure_categories['NULL Value Issues'].append(test)
        elif 'data quality' in error_msg:
            failure_categories['Data Quality Issues'].append(test)
        elif 'connection' in error_msg or 'database' in error_msg:
            failure_categories['Connection Issues'].append(test)
        else:
            failure_categories['Other Issues'].append(test)
    
    for category, tests in failure_categories.items():
        if tests:
            print(f"\n📋 {category} ({len(tests)} tests):")
            for test in tests:
                print(f"   ❌ {test.get('name', 'Unknown')}")
                print(f"      💬 {test.get('error', 'No error message')}")


def analyze_data_validation_requirements(test_reader):
    """Analyze what data validation tests require"""
    print("📊 DATA VALIDATION TEST REQUIREMENTS ANALYSIS:")
    print("-" * 50)
    
    try:
        # Read test cases from DATAVALIDATIONS sheet (already loaded)
        test_cases = test_reader.get_all_test_cases()
        
        # Analyze test parameters and requirements
        tables_required = set()
        test_types = set()
        
        for test_case in test_cases:
            test_types.add(test_case.test_category)
            
            # Extract table names from parameters
            if hasattr(test_case, 'parameters') and test_case.parameters:
                params = test_case.parameters.lower()
                if 'products' in params:
                    tables_required.add('products')
                if 'employees' in params:
                    tables_required.add('employees')
                if 'orders' in params:
                    tables_required.add('orders')
                if 'new_products' in params:
                    tables_required.add('new_products')
        
        print(f"📋 Test Types Required: {len(test_types)}")
        for test_type in sorted(test_types):
            print(f"   • {test_type}")
        
        print(f"\n📋 Tables Required: {len(tables_required)}")
        for table in sorted(tables_required):
            print(f"   • {table}")
            
        return test_cases, tables_required, test_types
        
    except Exception as e:
        print(f"❌ Error analyzing requirements: {str(e)}")
        return [], set(), set()


def check_database_readiness(data_validator, tables_required):
    """Check if the database has the required tables and data"""
    print("\n🔍 DATABASE READINESS CHECK:")
    print("-" * 40)
    
    readiness_issues = []
    
    for table in sorted(tables_required):
        try:
            # Check if table exists
            result = data_validator.db_connection.execute_query(f"SELECT COUNT(*) as row_count FROM {table}")
            if result and len(result) > 0:
                row_count = result[0].get('row_count', 0)
                print(f"   ✅ {table}: {row_count} rows")
                
                if row_count == 0:
                    readiness_issues.append(f"Table '{table}' exists but has no data")
            else:
                print(f"   ❌ {table}: Could not get row count")
                readiness_issues.append(f"Table '{table}' exists but query failed")
                
        except Exception as e:
            print(f"   ❌ {table}: Table missing or inaccessible")
            readiness_issues.append(f"Table '{table}' does not exist: {str(e)}")
    
    if readiness_issues:
        print(f"\n⚠️  DATABASE READINESS ISSUES ({len(readiness_issues)}):")
        for issue in readiness_issues:
            print(f"   • {issue}")
    else:
        print(f"\n✅ DATABASE READY: All required tables are available with data")
    
    return len(readiness_issues) == 0


def execute_data_validation_tests():
    """Execute data validation tests with detailed reporting"""
    
    print_header()
    
    # Initialize components
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
        
        # Analyze requirements
        test_cases, tables_required, test_types = analyze_data_validation_requirements(test_reader)
        
        if not test_cases:
            print("❌ No data validation test cases found!")
            return False
        
        print(f"\n📊 Found {len(test_cases)} data validation test cases")
        
        # Initialize data validator
        data_validator = DataValidator()
        
        # Check database readiness
        db_ready = check_database_readiness(data_validator, tables_required)
        
        # Initialize test executor
        test_executor = TestExecutor()
        
        print(f"\n🚀 EXECUTING DATA VALIDATION TESTS")
        print("=" * 50)
        
        # Execute tests
        results = []
        passed = 0
        failed = 0
        start_time = time.time()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] 🧪 Executing: {test_case.test_case_id}")
            print(f"🧪 Executing: {test_case.test_case_id} - {test_case.test_case_name}")
            print(f"   Environment: {test_case.environment_name}")
            print(f"   Application: {test_case.application_name}")
            print(f"   Category: {test_case.test_category}")
            print(f"   Timeout: {test_case.timeout_seconds}s")
            
            test_start = time.time()
            
            try:
                result = test_executor.execute_test_case(test_case)
                test_duration = time.time() - test_start
                
                if result.is_success:
                    print(f"   ✅ PASS ({test_duration:.2f}s)")
                    print(f"      ✅ PASS ({test_duration:.2f}s)")
                    passed += 1
                    results.append({
                        'name': f"{test_case.test_case_id} - {test_case.test_case_name}",
                        'category': test_case.test_category,
                        'status': 'PASS',
                        'duration': test_duration,
                        'message': result.error_message or 'Test passed'
                    })
                else:
                    print(f"   ❌ FAIL ({test_duration:.2f}s)")
                    print(f"   💬 {result.error_message}")
                    print(f"      ❌ FAIL ({test_duration:.2f}s)")
                    print(f"      💬 {result.error_message}")
                    failed += 1
                    results.append({
                        'name': f"{test_case.test_case_id} - {test_case.test_case_name}",
                        'category': test_case.test_category,
                        'status': 'FAIL',
                        'duration': test_duration,
                        'error': result.error_message
                    })
                    
            except Exception as e:
                test_duration = time.time() - test_start
                error_msg = str(e)
                print(f"   ❌ ERROR ({test_duration:.2f}s)")
                print(f"   💬 {error_msg}")
                failed += 1
                results.append({
                    'name': f"{test_case.test_case_id} - {test_case.test_case_name}",
                    'category': test_case.test_category,
                    'status': 'ERROR',
                    'duration': test_duration,
                    'error': error_msg
                })
        
        total_duration = time.time() - start_time
        
        # Print summary
        print(f"\n📋 DATA VALIDATION TEST SUMMARY:")
        print("=" * 50)
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⏭️  Skipped: 0")
        print(f"   📈 Success Rate: {(passed / len(test_cases) * 100):.1f}%")
        print(f"   ⏱️  Total duration: {total_duration:.2f}s")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS:")
        print("-" * 40)
        
        passed_tests = [r for r in results if r['status'] == 'PASS']
        failed_tests = [r for r in results if r['status'] in ['FAIL', 'ERROR']]
        
        if passed_tests:
            print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
            for i, test in enumerate(passed_tests, 1):
                print(f"    {i}. {test['name']}")
                print(f"       Category: {test['category']} | Duration: {test['duration']:.3f}s")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for i, test in enumerate(failed_tests, 1):
                print(f"    {i}. {test['name']}")
                print(f"       Category: {test['category']} | Duration: {test['duration']:.3f}s")
                print(f"       Error: {test.get('error', 'Unknown error')}")
        
        # Failure analysis
        if failed_tests:
            print()
            analyze_test_failures(failed_tests)
        
        # Recommendations
        print(f"\n🎯 DATA VALIDATION TEST ANALYSIS:")
        print("-" * 45)
        if passed == len(test_cases):
            print("✅ All data validation tests passed!")
            print("📊 Data validation framework is fully operational")
        elif passed > 0:
            print(f"✅ Core data validation functionality: {passed}/{len(test_cases)} tests passing")
            print(f"⚠️  Data setup required: Review failed tests for data preparation needs")
        else:
            print("❌ Data validation framework needs attention")
            print("🔧 Review database setup and test data requirements")
        
        if not db_ready:
            print("💡 Recommendation: Set up test data in required tables")
        
        print(f"\n✅ DATA VALIDATION TEST EXECUTION COMPLETE!")
        
        return passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ Error during test execution: {str(e)}")
        return False


if __name__ == "__main__":
    success = execute_data_validation_tests()
    sys.exit(0 if success else 1)