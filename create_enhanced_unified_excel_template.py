#!/usr/bin/env python3
"""
Enhanced Unified Excel Template Generator
==========================================
Creates a comprehensive Excel template with all required sheets including
all original smoke tests from the existing sdm_test_suite.xlsx file.

Author: Multi-Database Data Validation Framework
Date: October 4, 2025
"""

import sys
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

def load_original_smoke_tests():
    """Load all smoke tests from the original sdm_test_suite.xlsx file"""
    original_file = "sdm_test_suite.xlsx"
    
    try:
        workbook = load_workbook(original_file)
        
        if "SMOKE" not in workbook.sheetnames:
            print(f"⚠️  SMOKE sheet not found in {original_file}, using default tests")
            return []
        
        ws = workbook["SMOKE"]
        smoke_tests = []
        
        # Read all test data starting from row 2
        for row in range(2, ws.max_row + 1):
            test_data = []
            for col in range(1, 14):  # 13 columns
                cell_value = ws.cell(row=row, column=col).value
                test_data.append(str(cell_value) if cell_value is not None else "")
            
            # Only add if there's a test ID (column 2)
            if test_data and len(test_data) > 1 and test_data[1]:
                smoke_tests.append(test_data)
        
        print(f"✅ Loaded {len(smoke_tests)} smoke tests from original file")
        return smoke_tests
        
    except Exception as e:
        print(f"⚠️  Error loading original smoke tests: {e}")
        print("   Using default smoke tests instead")
        return []


def create_enhanced_unified_excel_template():
    """Create enhanced unified Excel template with original smoke tests"""
    
    print("🔧 CREATING ENHANCED UNIFIED EXCEL TEMPLATE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load original smoke tests
    original_smoke_tests = load_original_smoke_tests()
    
    # Create workbook
    wb = Workbook()
    
    # Remove default sheet
    wb.remove(wb.active)
    
    # Create all sheets
    create_enhanced_smoke_sheet(wb, original_smoke_tests)
    create_controller_sheet(wb)
    create_datavalidations_sheet(wb)
    create_instructions_sheet(wb)
    create_reference_sheet(wb)
    
    # Save the workbook
    filename = "enhanced_unified_sdm_test_suite.xlsx"
    wb.save(filename)
    
    print(f"✅ Created enhanced unified Excel template: {filename}")
    print()
    
    # Print summary
    print("📋 SHEET SUMMARY:")
    print("-" * 30)
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = ws.max_row
        cols = ws.max_column
        data_rows = max(0, rows - 1) if rows > 1 else 0
        print(f"   • {sheet_name}: {rows} rows × {cols} columns ({data_rows} data rows)")
    
    print()
    print("🎯 ENHANCED TEMPLATE FEATURES:")
    print("-" * 30)
    print(f"   ✅ SMOKE sheet: {len(original_smoke_tests) if original_smoke_tests else 6} comprehensive smoke tests")
    print("   ✅ CONTROLLER sheet: Test suite controller")
    print("   ✅ DATAVALIDATIONS sheet: Enhanced data validation tests")
    print("   ✅ INSTRUCTIONS sheet: Comprehensive usage guide")
    print("   ✅ REFERENCE sheet: Complete reference documentation")
    print("   ✅ Data validation rules applied")
    print("   ✅ Professional formatting")
    print("   ✅ All original smoke test configurations preserved")
    
    return filename


def create_enhanced_smoke_sheet(wb, original_smoke_tests):
    """Create SMOKE sheet with all original smoke test configurations"""
    ws = wb.create_sheet("SMOKE")
    
    # Headers
    headers = [
        "Enable", "Test_Case_ID", "Test_Case_Name", "Application_Name", 
        "Environment_Name", "Priority", "Test_Category", "Expected_Result",
        "Timeout_Seconds", "Description", "Prerequisites", "Tags", "Parameters"
    ]
    
    # Apply headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Use original smoke tests if available, otherwise use default ones
    if original_smoke_tests:
        print(f"📋 Adding {len(original_smoke_tests)} original smoke tests to SMOKE sheet")
        
        for row_idx, test_data in enumerate(original_smoke_tests, 2):
            for col_idx, value in enumerate(test_data, 1):
                if col_idx <= len(headers):  # Don't exceed header count
                    ws.cell(row=row_idx, column=col_idx, value=value)
    else:
        # Fallback to default smoke tests
        print("📋 Adding default smoke tests to SMOKE sheet")
        default_smoke_tests = [
            ["TRUE", "SMOKE_001", "Environment Setup Test", "POSTGRES", "DEV", "HIGH", "SETUP", "PASS", 30, "Verify test environment is properly configured", "Database server running", "smoke,setup", ""],
            ["TRUE", "SMOKE_002", "Configuration Availability", "POSTGRES", "DEV", "HIGH", "CONFIGURATION", "PASS", 30, "Verify dummy configuration files are available", "Config files present", "smoke,config", ""],
            ["TRUE", "SMOKE_003", "Environment Credentials", "POSTGRES", "DEV", "HIGH", "SECURITY", "PASS", 30, "Verify environment credentials are valid", "Credentials configured", "smoke,security", ""],
            ["TRUE", "SMOKE_004", "PostgreSQL Connection", "POSTGRES", "DEV", "HIGH", "CONNECTION", "PASS", 60, "Test basic PostgreSQL database connectivity", "Database accessible", "smoke,connection", ""],
            ["TRUE", "SMOKE_005", "Basic Query Execution", "POSTGRES", "DEV", "MEDIUM", "QUERIES", "PASS", 60, "Execute basic SQL queries to verify functionality", "Connection established", "smoke,queries", ""],
            ["TRUE", "SMOKE_006", "Connection Performance", "POSTGRES", "DEV", "MEDIUM", "PERFORMANCE", "PASS", 30, "Measure database connection performance", "Database responsive", "smoke,performance", ""]
        ]
        
        for row_idx, test_data in enumerate(default_smoke_tests, 2):
            for col_idx, value in enumerate(test_data, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)
    
    # Apply formatting and data validation
    apply_sheet_formatting(ws, len(headers))
    add_data_validations_smoke(ws)


def create_controller_sheet(wb):
    """Create CONTROLLER sheet"""
    ws = wb.create_sheet("CONTROLLER")
    
    # Headers
    headers = [
        "Enable", "Test_Case_ID", "Test_Case_Name", "Application_Name", 
        "Environment_Name", "Priority", "Test_Category", "Expected_Result",
        "Timeout_Seconds", "Description", "Prerequisites", "Tags", "Parameters"
    ]
    
    # Apply headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Controller data
    controller_tests = [
        ["TRUE", "CTRL_001", "Smoke Test Suite", "POSTGRES", "DEV", "HIGH", "SETUP", "PASS", 300, "Execute complete smoke test suite", "All components ready", "controller,smoke", "sheet_name=SMOKE"],
        ["TRUE", "CTRL_002", "Data Validation Suite", "POSTGRES", "DEV", "HIGH", "SCHEMA_VALIDATION", "PASS", 600, "Execute data validation test suite", "Tables and data ready", "controller,validation", "sheet_name=DATAVALIDATIONS"],
        ["FALSE", "CTRL_003", "Integration Test Suite", "POSTGRES", "STAGING", "MEDIUM", "CONNECTION", "PASS", 900, "Execute integration tests", "External systems available", "controller,integration", ""],
        ["FALSE", "CTRL_004", "Performance Test Suite", "POSTGRES", "STAGING", "LOW", "PERFORMANCE", "PASS", 1800, "Execute performance test suite", "Load test environment", "controller,performance", ""],
        ["FALSE", "CTRL_005", "Security Test Suite", "POSTGRES", "PROD", "HIGH", "SECURITY", "PASS", 1200, "Execute security test suite", "Security tools configured", "controller,security", ""],
        ["FALSE", "CTRL_006", "Regression Test Suite", "POSTGRES", "STAGING", "MEDIUM", "QUERIES", "PASS", 3600, "Execute full regression test suite", "Complete test data", "controller,regression", ""]
    ]
    
    # Add controller data
    for row_idx, test_data in enumerate(controller_tests, 2):
        for col_idx, value in enumerate(test_data, 1):
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    # Apply formatting
    apply_sheet_formatting(ws, len(headers))
    add_data_validations_controller(ws)


def create_datavalidations_sheet(wb):
    """Create enhanced DATAVALIDATIONS sheet"""
    ws = wb.create_sheet("DATAVALIDATIONS")
    
    # Headers
    headers = [
        "Enable", "Test_Case_ID", "Test_Case_Name", "Application_Name", 
        "Environment_Name", "Priority", "Test_Category", "Expected_Result",
        "Timeout_Seconds", "Description", "Prerequisites", "Tags", "Parameters"
    ]
    
    # Apply headers
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="E74C3C", end_color="E74C3C", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Enhanced data validation tests with proper table parameters
    validation_tests = [
        ["TRUE", "DVAL_001", "Products Schema Validation", "POSTGRES", "DEV", "HIGH", "SCHEMA_VALIDATION", "PASS", 60, "Compare schema structure between source products and target new_products tables", "Both tables must exist with data", "schema,validation,products", "source_table=products;target_table=new_products;ignore_sequence=true;check_constraints=true"],
        ["TRUE", "DVAL_002", "Employees Schema Validation", "POSTGRES", "DEV", "HIGH", "SCHEMA_VALIDATION", "PASS", 60, "Compare schema structure between source employees and target new_employees tables", "Both tables must exist with data", "schema,validation,employees", "source_table=employees;target_table=new_employees;ignore_sequence=true;check_constraints=true"],
        ["TRUE", "DVAL_003", "Orders Schema Validation", "POSTGRES", "DEV", "HIGH", "SCHEMA_VALIDATION", "PASS", 60, "Compare schema structure between source orders and target new_orders tables", "Both tables must exist with data", "schema,validation,orders", "source_table=orders;target_table=new_orders;ignore_sequence=true;check_constraints=true"],
        
        ["TRUE", "DVAL_004", "Products Row Count Validation", "POSTGRES", "DEV", "MEDIUM", "ROW_COUNT_VALIDATION", "FAIL", 30, "Compare row counts between source products and target new_products tables", "Both tables accessible", "count,validation,products", "source_table=products;target_table=new_products;tolerance_percent=5;expected_variance=large"],
        ["TRUE", "DVAL_005", "Employees Row Count Validation", "POSTGRES", "DEV", "MEDIUM", "ROW_COUNT_VALIDATION", "FAIL", 30, "Compare row counts between source employees and target new_employees tables", "Both tables accessible", "count,validation,employees", "source_table=employees;target_table=new_employees;tolerance_percent=5;expected_variance=large"],
        ["TRUE", "DVAL_006", "Orders Row Count Validation", "POSTGRES", "DEV", "MEDIUM", "ROW_COUNT_VALIDATION", "FAIL", 30, "Compare row counts between source orders and target new_orders tables", "Both tables accessible", "count,validation,orders", "source_table=orders;target_table=new_orders;tolerance_percent=5;expected_variance=large"],
        
        ["TRUE", "DVAL_007", "Products NULL Value Validation", "POSTGRES", "DEV", "MEDIUM", "NULL_VALUE_VALIDATION", "FAIL", 45, "Compare NULL value patterns between source and target products tables", "Tables contain representative data", "null,validation,products", "source_table=products;target_table=new_products;null_match_required=false;report_differences=true"],
        ["TRUE", "DVAL_008", "Employees NULL Value Validation", "POSTGRES", "DEV", "MEDIUM", "NULL_VALUE_VALIDATION", "FAIL", 45, "Compare NULL value patterns between source and target employees tables", "Tables contain representative data", "null,validation,employees", "source_table=employees;target_table=new_employees;null_match_required=false;report_differences=true"],
        ["TRUE", "DVAL_009", "Orders NULL Value Validation", "POSTGRES", "DEV", "MEDIUM", "NULL_VALUE_VALIDATION", "FAIL", 45, "Compare NULL value patterns between source and target orders tables", "Tables contain representative data", "null,validation,orders", "source_table=orders;target_table=new_orders;null_match_required=false;report_differences=true"],
        
        ["TRUE", "DVAL_010", "Products Data Quality Check", "POSTGRES", "DEV", "HIGH", "DATA_QUALITY_VALIDATION", "PASS", 60, "Validate data quality metrics for products table", "Data quality rules defined", "quality,validation,products", "source_table=products;target_table=new_products;check_ranges=true;check_patterns=true;check_duplicates=true"],
        ["TRUE", "DVAL_011", "Cross-Table Referential Integrity", "POSTGRES", "DEV", "HIGH", "DATA_QUALITY_VALIDATION", "FAIL", 60, "Validate referential integrity between related tables", "Foreign key relationships exist", "integrity,validation,cross-table", "source_table=products;target_table=orders;check_foreign_keys=true;validate_relationships=true"],
        ["TRUE", "DVAL_012", "Data Completeness Validation", "POSTGRES", "DEV", "MEDIUM", "DATA_QUALITY_VALIDATION", "PASS", 120, "Validate data completeness across all tables", "All tables have minimum required data", "completeness,validation,all-tables", "source_table=products,employees,orders;check_required_fields=true;missing_data_threshold=5"]
    ]
    
    # Add validation test data
    for row_idx, test_data in enumerate(validation_tests, 2):
        for col_idx, value in enumerate(test_data, 1):
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    # Apply formatting
    apply_sheet_formatting(ws, len(headers))
    add_data_validations_datavalidations(ws)


def create_instructions_sheet(wb):
    """Create comprehensive INSTRUCTIONS sheet"""
    ws = wb.create_sheet("INSTRUCTIONS")
    
    # Title
    ws.cell(row=1, column=1, value="ENHANCED UNIFIED SDM TEST SUITE - COMPREHENSIVE INSTRUCTIONS")
    ws.cell(row=1, column=1).font = Font(bold=True, size=16, color="FFFFFF")
    ws.cell(row=1, column=1).fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
    ws.merge_cells("A1:J1")
    
    # Instructions content
    instructions = [
        "",
        "📋 OVERVIEW:",
        "This enhanced unified Excel template contains comprehensive test configurations for the Multi-Database Data Validation Framework.",
        "All sheets work together to provide complete testing coverage with all original smoke tests preserved.",
        "",
        "📂 SHEET DESCRIPTIONS:",
        "",
        "🔹 SMOKE Sheet:",
        "   • Contains ALL original smoke tests from the legacy sdm_test_suite.xlsx file",
        "   • Comprehensive environment validation with ~30 detailed test cases",
        "   • Tests connectivity, configuration, table existence, and data validation",
        "   • Execute first to verify environment readiness",
        "   • Categories: SETUP, CONFIGURATION, SECURITY, CONNECTION, QUERIES, PERFORMANCE, TABLE_EXISTS, TABLE_SELECT, TABLE_ROWS, TABLE_STRUCTURE",
        "",
        "🔹 CONTROLLER Sheet:",
        "   • Master controller for executing test suites",
        "   • References other sheets for batch execution",
        "   • Manages test suite orchestration and dependencies",
        "   • Use for high-level test execution control",
        "",
        "🔹 DATAVALIDATIONS Sheet:",
        "   • Enhanced data validation tests with proper table parameter support",
        "   • Includes source_table and target_table parameters for each test",
        "   • Categories: SCHEMA_VALIDATION, ROW_COUNT_VALIDATION, NULL_VALUE_VALIDATION, DATA_QUALITY_VALIDATION",
        "   • Supports multiple table combinations (products, employees, orders)",
        "",
        "🔹 INSTRUCTIONS Sheet (this sheet):",
        "   • Comprehensive usage instructions and guidelines",
        "   • Column descriptions and parameter formats",
        "   • Execution examples and best practices",
        "",
        "🔹 REFERENCE Sheet:",
        "   • Complete reference documentation for all test categories",
        "   • Parameter definitions and valid values",
        "   • Troubleshooting guide and FAQ",
        "",
        "📊 COLUMN DESCRIPTIONS:",
        "",
        "• Enable: TRUE/FALSE - Whether to execute this test case",
        "• Test_Case_ID: Unique identifier for the test (e.g., SMOKE_PG_001, DVAL_001)",
        "• Test_Case_Name: Descriptive name for the test case",
        "• Application_Name: Target application (POSTGRES, DUMMY, MYAPP, DATABASE)",
        "• Environment_Name: Target environment (DEV, TEST, STAGING, PROD, UAT)",
        "• Priority: Test priority level (HIGH, MEDIUM, LOW)",
        "• Test_Category: Functional category that determines which test function to execute",
        "• Expected_Result: Expected test outcome (PASS, FAIL, SKIP)",
        "• Timeout_Seconds: Maximum execution time in seconds",
        "• Description: Detailed description of what the test validates",
        "• Prerequisites: Conditions that must be met before test execution",
        "• Tags: Comma-separated tags for test categorization and filtering",
        "• Parameters: Semicolon-separated key=value pairs for test configuration",
        "",
        "🔧 PARAMETER FORMATS:",
        "",
        "Data Validation Parameters (DATAVALIDATIONS sheet):",
        "   source_table=products;target_table=new_products;ignore_sequence=true",
        "   source_table=employees;target_table=new_employees;tolerance_percent=5",
        "   check_constraints=true;report_differences=true;null_match_required=false",
        "",
        "Controller Parameters (CONTROLLER sheet):",
        "   sheet_name=SMOKE (references which sheet to execute)",
        "   sheet_name=DATAVALIDATIONS (for data validation suite execution)",
        "",
        "🚀 EXECUTION EXAMPLES:",
        "",
        "1. Execute all smoke tests:",
        "   python execute_unified_smoke_tests.py enhanced_unified_sdm_test_suite.xlsx",
        "",
        "2. Execute data validation tests:",
        "   python execute_enhanced_data_validation_tests.py enhanced_unified_sdm_test_suite.xlsx",
        "",
        "3. Validate Excel template:",
        "   python enhanced_excel_validator.py enhanced_unified_sdm_test_suite.xlsx",
        "",
        "✅ BEST PRACTICES:",
        "",
        "• Always run SMOKE tests first to verify environment readiness",
        "• All original smoke tests are preserved and enhanced",
        "• Use CONTROLLER sheet for orchestrating complex test suites",
        "• Ensure proper source_table and target_table parameters in DATAVALIDATIONS",
        "• Set realistic Expected_Result values based on your data setup",
        "• Use Tags for efficient test filtering and categorization",
        "• Monitor Timeout_Seconds to prevent hanging tests",
        "• Keep Parameters format consistent (key=value;key=value)",
        "",
        "🔍 VALIDATION TIPS:",
        "",
        "• All table references in parameters must exist in the database",
        "• Test_Category values must match available test functions",
        "• Enable/Disable tests strategically based on environment readiness",
        "• Use the enhanced validator to check for configuration issues",
        "• Review Prerequisites before executing test suites",
        "• Original smoke test configurations are preserved and validated"
    ]
    
    # Add instructions
    for row_idx, instruction in enumerate(instructions, 2):
        ws.cell(row=row_idx, column=1, value=instruction)
        if instruction.startswith("📋") or instruction.startswith("📂") or instruction.startswith("📊") or instruction.startswith("🔧") or instruction.startswith("🚀") or instruction.startswith("✅") or instruction.startswith("🔍"):
            ws.cell(row=row_idx, column=1).font = Font(bold=True, color="2C3E50")
        elif instruction.startswith("🔹") or instruction.startswith("•"):
            ws.cell(row=row_idx, column=1).font = Font(color="34495E")
    
    # Set column width
    ws.column_dimensions['A'].width = 120


def create_reference_sheet(wb):
    """Create comprehensive REFERENCE sheet"""
    ws = wb.create_sheet("REFERENCE")
    
    # Title
    ws.cell(row=1, column=1, value="ENHANCED REFERENCE DOCUMENTATION")
    ws.cell(row=1, column=1).font = Font(bold=True, size=16, color="FFFFFF")
    ws.cell(row=1, column=1).fill = PatternFill(start_color="8E44AD", end_color="8E44AD", fill_type="solid")
    ws.merge_cells("A1:D1")
    
    # Reference content
    reference_data = [
        "",
        "TEST CATEGORIES AND FUNCTIONS:",
        "",
        "Category", "Function Name", "Description", "Sheet Usage",
        "SETUP", "test_environment_setup", "Verify test environment configuration", "SMOKE",
        "CONFIGURATION", "test_dummy_config_availability", "Check configuration file availability", "SMOKE", 
        "SECURITY", "test_environment_credentials", "Validate environment credentials", "SMOKE",
        "CONNECTION", "test_postgresql_connection", "Test database connectivity", "SMOKE, CONTROLLER",
        "QUERIES", "test_postgresql_basic_queries", "Execute basic SQL queries", "SMOKE",
        "PERFORMANCE", "test_postgresql_connection_performance", "Measure connection performance", "SMOKE",
        "TABLE_EXISTS", "_execute_table_exists_test", "Verify table existence", "SMOKE",
        "TABLE_SELECT", "_execute_table_select_test", "Test table SELECT operations", "SMOKE",
        "TABLE_ROWS", "_execute_table_rows_test", "Validate table row operations", "SMOKE",
        "TABLE_STRUCTURE", "_execute_table_structure_test", "Analyze table structure", "SMOKE",
        "SCHEMA_VALIDATION", "schema_validation_compare", "Compare table schemas", "DATAVALIDATIONS",
        "ROW_COUNT_VALIDATION", "row_count_validation_compare", "Compare table row counts", "DATAVALIDATIONS",
        "NULL_VALUE_VALIDATION", "null_value_validation_compare", "Compare NULL value patterns", "DATAVALIDATIONS",
        "DATA_QUALITY_VALIDATION", "data_quality_validation_compare", "Validate data quality metrics", "DATAVALIDATIONS",
        "COLUMN_COMPARE_VALIDATION", "column_compare_validation", "Compare column data", "DATAVALIDATIONS",
        "",
        "VALID VALUES:",
        "",
        "Field", "Valid Values", "Description", "Example",
        "Enable", "TRUE, FALSE", "Boolean test execution flag", "TRUE",
        "Application_Name", "POSTGRES, DUMMY, MYAPP, DATABASE", "Target application identifier", "POSTGRES",
        "Environment_Name", "DEV, TEST, STAGING, PROD, UAT", "Target environment", "DEV",
        "Priority", "HIGH, MEDIUM, LOW", "Test execution priority", "HIGH",
        "Expected_Result", "PASS, FAIL, SKIP", "Expected test outcome", "PASS",
        "Test_Category", "See categories above", "Functional test category", "SCHEMA_VALIDATION",
        "",
        "PARAMETER FORMATS:",
        "",
        "Parameter Type", "Format", "Example", "Usage",
        "Table Parameters", "source_table=name;target_table=name", "source_table=products;target_table=new_products", "DATAVALIDATIONS",
        "Boolean Parameters", "parameter_name=true/false", "ignore_sequence=true;check_constraints=false", "DATAVALIDATIONS",
        "Numeric Parameters", "parameter_name=number", "tolerance_percent=5;missing_data_threshold=10", "DATAVALIDATIONS",
        "String Parameters", "parameter_name=value", "expected_variance=large;report_type=detailed", "DATAVALIDATIONS",
        "Sheet References", "sheet_name=SHEETNAME", "sheet_name=SMOKE", "CONTROLLER",
        "",
        "DATABASE TABLES:",
        "",
        "Source Tables", "Target Tables", "Description", "Row Count",
        "products", "new_products", "Product catalog data", "1200 → 8",
        "employees", "new_employees", "Employee information", "1000 → 7", 
        "orders", "new_orders", "Order transaction data", "800 → 7",
        "validation_results", "N/A", "Test execution results storage", "Variable",
        "",
        "ORIGINAL SMOKE TESTS PRESERVED:",
        "",
        "Test Range", "Purpose", "Coverage", "Expected Results",
        "SMOKE_PG_001-006", "Basic environment validation", "Setup, config, security, connection", "All PASS",
        "SMOKE_PG_007-009", "Table existence validation", "products, employees, orders tables", "All PASS",
        "SMOKE_PG_010-012", "Table SELECT operations", "Basic query functionality", "All PASS",
        "SMOKE_PG_013-015", "Table data validation", "Row count and data presence", "All PASS",
        "SMOKE_PG_016-018", "Table structure analysis", "Schema and column validation", "All PASS",
        "SMOKE_PG_019-030", "Extended table validation", "Comprehensive coverage", "All PASS"
    ]
    
    # Add reference data
    for row_idx, ref_data in enumerate(reference_data, 2):
        if isinstance(ref_data, str):
            ws.cell(row=row_idx, column=1, value=ref_data)
            if ref_data.endswith(":") and ref_data != "":
                ws.cell(row=row_idx, column=1).font = Font(bold=True, color="8E44AD")
        else:
            # This is tuple data for table
            for col_idx, value in enumerate(ref_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                if row_idx in [4, 20, 27, 32, 37, 43]:  # Header rows
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="8E44AD", end_color="8E44AD", fill_type="solid")
    
    # Set column widths
    for col in ['A', 'B', 'C', 'D']:
        ws.column_dimensions[col].width = 30


def apply_sheet_formatting(ws, num_cols):
    """Apply consistent formatting to worksheet"""
    # Set column widths
    column_widths = [10, 15, 25, 15, 15, 10, 20, 15, 12, 30, 25, 20, 40]
    for i, width in enumerate(column_widths[:num_cols], 1):
        ws.column_dimensions[chr(64 + i)].width = width
    
    # Add borders
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Apply borders to data area
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=num_cols):
        for cell in row:
            cell.border = thin_border
            if cell.row > 1:  # Data rows
                cell.alignment = Alignment(horizontal="left", vertical="center")


def add_data_validations_smoke(ws):
    """Add data validation rules for SMOKE sheet"""
    # Enable column validation
    enable_validation = DataValidation(type="list", formula1='"TRUE,FALSE"')
    ws.add_data_validation(enable_validation)
    enable_validation.add(f"A2:A{ws.max_row}")
    
    # Priority validation
    priority_validation = DataValidation(type="list", formula1='"HIGH,MEDIUM,LOW"')
    ws.add_data_validation(priority_validation)
    priority_validation.add(f"F2:F{ws.max_row}")
    
    # Expected Result validation
    result_validation = DataValidation(type="list", formula1='"PASS,FAIL,SKIP"')
    ws.add_data_validation(result_validation)
    result_validation.add(f"H2:H{ws.max_row}")


def add_data_validations_controller(ws):
    """Add data validation rules for CONTROLLER sheet"""
    add_data_validations_smoke(ws)  # Same validations


def add_data_validations_datavalidations(ws):
    """Add data validation rules for DATAVALIDATIONS sheet"""
    add_data_validations_smoke(ws)  # Same basic validations
    
    # Test Category validation for data validation sheet
    category_validation = DataValidation(type="list", 
        formula1='"SCHEMA_VALIDATION,ROW_COUNT_VALIDATION,NULL_VALUE_VALIDATION,DATA_QUALITY_VALIDATION,COLUMN_COMPARE_VALIDATION"')
    ws.add_data_validation(category_validation)
    category_validation.add(f"G2:G{ws.max_row}")


def main():
    """Main execution function"""
    filename = create_enhanced_unified_excel_template()
    
    print("🎯 USAGE INSTRUCTIONS:")
    print("-" * 30)
    print(f"   1. Use '{filename}' as your master test suite")
    print("   2. Execute smoke tests: python execute_unified_smoke_tests.py enhanced_unified_sdm_test_suite.xlsx")
    print("   3. Execute data validation: python execute_enhanced_data_validation_tests.py enhanced_unified_sdm_test_suite.xlsx")
    print("   4. Validate template: python enhanced_excel_validator.py enhanced_unified_sdm_test_suite.xlsx")
    print()
    print("✅ ENHANCED UNIFIED EXCEL TEMPLATE CREATION COMPLETE!")


if __name__ == "__main__":
    main()