"""
Excel Test Suite Validation Module

This module provides comprehensive validation for Excel test suite files
to prevent user input errors and ensure data integrity.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path
import re
from enum import Enum


class ValidationSeverity(Enum):
    """Validation message severity levels"""
    ERROR = "ERROR"
    WARNING = "WARNING" 
    INFO = "INFO"


@dataclass
class ValidationMessage:
    """Represents a validation message"""
    severity: ValidationSeverity
    row: int
    column: str
    field: str
    message: str
    current_value: str
    suggested_value: Optional[str] = None


class ExcelTestSuiteValidator:
    """Validates Excel test suite data for correctness and consistency"""
    
    # Define valid values for each field
    VALID_PRIORITIES = {"HIGH", "MEDIUM", "LOW"}
    VALID_ENVIRONMENTS = {"DEV", "STAGING", "PROD", "TEST", "UAT"}
    VALID_APPLICATIONS = {"DUMMY", "MYAPP", "POSTGRES", "DATABASE"}
    VALID_EXPECTED_RESULTS = {"PASS", "FAIL", "SKIP"}
    VALID_BOOLEAN_VALUES = {True, False, "TRUE", "FALSE", "YES", "NO", "Y", "N", 1, 0}
    
    # Map test categories to their corresponding test methods
    VALID_TEST_CATEGORIES = {
        "SETUP": "test_environment_setup",
        "CONFIGURATION": "test_dummy_config_availability", 
        "SECURITY": "test_environment_credentials",
        "CONNECTION": "test_postgresql_connection",
        "QUERIES": "test_postgresql_basic_queries",
        "PERFORMANCE": "test_postgresql_connection_performance",
        "COMPATIBILITY": "test_compatibility",  # Not implemented yet
        "MONITORING": "test_monitoring",  # Future implementation
        "BACKUP": "test_backup_restore",  # Future implementation
        "TABLE_EXISTS": "smoke_test_table_exists",  # Table existence validation
        "TABLE_SELECT": "smoke_test_table_select_possible",  # Table SELECT accessibility
        "TABLE_ROWS": "smoke_test_table_has_rows",  # Table data validation
        "TABLE_STRUCTURE": "smoke_test_table_structure",  # Table structure validation
        # Data Validation Test Categories
        "SCHEMA_VALIDATION": "data_validation_schema_compare",  # Source vs Target schema comparison
        "ROW_COUNT_VALIDATION": "data_validation_row_count_compare",  # Source vs Target row count comparison
        "NULL_VALUE_VALIDATION": "data_validation_null_compare",  # Source vs Target NULL pattern comparison
        "DATA_QUALITY_VALIDATION": "data_validation_quality_compare",  # Data quality metrics comparison
        "COLUMN_COMPARE_VALIDATION": "data_validation_column_compare",  # Column-by-column data comparison
    }
    
    # Required headers in exact order
    REQUIRED_HEADERS = [
        "Enable", "Test_Case_ID", "Test_Case_Name", "Application_Name",
        "Environment_Name", "Priority", "Test_Category", "Expected_Result", 
        "Timeout_Seconds", "Description", "Prerequisites", "Tags", "Parameters"
    ]
    
    # Field constraints
    MIN_TIMEOUT_SECONDS = 5
    MAX_TIMEOUT_SECONDS = 3600  # 1 hour
    MAX_DESCRIPTION_LENGTH = 500
    MAX_PREREQUISITES_LENGTH = 1000
    
    def __init__(self):
        """Initialize the validator"""
        self.validation_messages: List[ValidationMessage] = []
    
    def validate_test_suite(self, workbook, worksheet_name: str = "SMOKE") -> Tuple[bool, List[ValidationMessage]]:
        """
        Validate the entire test suite
        
        Args:
            workbook: Loaded openpyxl workbook
            worksheet_name: Name of worksheet to validate
            
        Returns:
            Tuple of (is_valid, validation_messages)
        """
        self.validation_messages = []
        
        if worksheet_name not in workbook.sheetnames:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=0,
                column="",
                field="worksheet",
                message=f"Worksheet '{worksheet_name}' not found",
                current_value=str(workbook.sheetnames),
                suggested_value=worksheet_name
            ))
            return False, self.validation_messages
        
        ws = workbook[worksheet_name]
        
        # Validate headers
        self._validate_headers(ws)
        
        # Validate data rows
        self._validate_data_rows(ws)
        
        # Check for duplicates
        self._validate_duplicates(ws)
        
        # Validate business rules
        self._validate_business_rules(ws)
        
        # Determine if validation passed
        has_errors = any(msg.severity == ValidationSeverity.ERROR for msg in self.validation_messages)
        return not has_errors, self.validation_messages
    
    def _validate_headers(self, ws):
        """Validate that all required headers are present and in correct order"""
        actual_headers = []
        
        for col in range(1, len(self.REQUIRED_HEADERS) + 1):
            cell_value = ws.cell(row=1, column=col).value
            actual_headers.append(str(cell_value).strip() if cell_value else "")
        
        # Check for missing or incorrect headers
        for i, expected_header in enumerate(self.REQUIRED_HEADERS, 1):
            if i <= len(actual_headers):
                actual_header = actual_headers[i-1]
                if actual_header != expected_header:
                    self.validation_messages.append(ValidationMessage(
                        severity=ValidationSeverity.ERROR,
                        row=1,
                        column=self._get_column_letter(i),
                        field="header",
                        message=f"Header mismatch in column {i}",
                        current_value=actual_header,
                        suggested_value=expected_header
                    ))
            else:
                self.validation_messages.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    row=1,
                    column=self._get_column_letter(i),
                    field="header",
                    message=f"Missing required header",
                    current_value="",
                    suggested_value=expected_header
                ))
    
    def _validate_data_rows(self, ws):
        """Validate each data row"""
        row_num = 2
        test_ids_seen = set()
        
        while True:
            # Check if we've reached the end
            test_id = ws.cell(row=row_num, column=2).value  # Test_Case_ID column
            if not test_id:
                break
            
            # Validate each field in the row
            self._validate_row(ws, row_num, test_ids_seen)
            row_num += 1
    
    def _validate_row(self, ws, row_num: int, test_ids_seen: Set[str]):
        """Validate a single data row"""
        # Get row data
        row_data = {}
        for col, header in enumerate(self.REQUIRED_HEADERS, 1):
            cell_value = ws.cell(row=row_num, column=col).value
            row_data[header] = cell_value
        
        # Validate Enable field
        self._validate_boolean_field(row_num, "A", "Enable", row_data["Enable"])
        
        # Validate Test_Case_ID
        self._validate_test_case_id(row_num, "B", row_data["Test_Case_ID"], test_ids_seen)
        
        # Validate Test_Case_Name
        self._validate_required_string(row_num, "C", "Test_Case_Name", row_data["Test_Case_Name"])
        
        # Validate Application_Name
        self._validate_application_name(row_num, "D", row_data["Application_Name"])
        
        # Validate Environment_Name  
        self._validate_environment_name(row_num, "E", row_data["Environment_Name"])
        
        # Validate Priority
        self._validate_priority(row_num, "F", row_data["Priority"])
        
        # Validate Test_Category (CRITICAL - this determines which function to call)
        self._validate_test_category(row_num, "G", row_data["Test_Category"])
        
        # Validate Expected_Result
        self._validate_expected_result(row_num, "H", row_data["Expected_Result"])
        
        # Validate Timeout_Seconds
        self._validate_timeout_seconds(row_num, "I", row_data["Timeout_Seconds"])
        
        # Validate Description
        self._validate_description(row_num, "J", row_data["Description"])
        
        # Validate Prerequisites
        self._validate_prerequisites(row_num, "K", row_data["Prerequisites"])
        
        # Validate Tags
        self._validate_tags(row_num, "L", row_data["Tags"])
    
    def _validate_boolean_field(self, row: int, col: str, field: str, value):
        """Validate boolean fields like Enable"""
        if value not in self.VALID_BOOLEAN_VALUES:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field=field,
                message=f"Invalid boolean value",
                current_value=str(value),
                suggested_value="TRUE or FALSE"
            ))
    
    def _validate_test_case_id(self, row: int, col: str, value, test_ids_seen: Set[str]):
        """Validate Test_Case_ID field"""
        if not value:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field="Test_Case_ID",
                message="Test_Case_ID is required",
                current_value="",
                suggested_value="SMOKE_PG_XXX"
            ))
            return
        
        test_id = str(value).strip()
        
        # Check format (should match pattern like SMOKE_PG_001)
        if not re.match(r'^[A-Z_]+_\d{3}$', test_id):
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                row=row,
                column=col,
                field="Test_Case_ID",
                message="Test ID doesn't follow recommended pattern",
                current_value=test_id,
                suggested_value="SMOKE_PG_001 format"
            ))
        
        # Check for duplicates
        if test_id in test_ids_seen:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field="Test_Case_ID",
                message="Duplicate Test_Case_ID",
                current_value=test_id,
                suggested_value="Use unique identifier"
            ))
        else:
            test_ids_seen.add(test_id)
    
    def _validate_required_string(self, row: int, col: str, field: str, value):
        """Validate required string fields"""
        if not value or str(value).strip() == "":
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field=field,
                message=f"{field} is required",
                current_value=str(value) if value else "",
                suggested_value="Enter descriptive text"
            ))
    
    def _validate_application_name(self, row: int, col: str, value):
        """Validate Application_Name field"""
        if not value:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field="Application_Name",
                message="Application_Name is required",
                current_value="",
                suggested_value=", ".join(self.VALID_APPLICATIONS)
            ))
            return
        
        app_name = str(value).strip().upper()
        if app_name not in self.VALID_APPLICATIONS:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                row=row,
                column=col,
                field="Application_Name",
                message="Application not in predefined list",
                current_value=str(value),
                suggested_value=", ".join(self.VALID_APPLICATIONS)
            ))
    
    def _validate_environment_name(self, row: int, col: str, value):
        """Validate Environment_Name field"""
        if not value:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field="Environment_Name",
                message="Environment_Name is required",
                current_value="",
                suggested_value=", ".join(self.VALID_ENVIRONMENTS)
            ))
            return
        
        env_name = str(value).strip().upper()
        if env_name not in self.VALID_ENVIRONMENTS:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                row=row,
                column=col,
                field="Environment_Name",
                message="Environment not in predefined list",
                current_value=str(value),
                suggested_value=", ".join(self.VALID_ENVIRONMENTS)
            ))
    
    def _validate_priority(self, row: int, col: str, value):
        """Validate Priority field"""
        if not value:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                row=row,
                column=col,
                field="Priority",
                message="Priority not specified, defaulting to MEDIUM",
                current_value="",
                suggested_value=", ".join(self.VALID_PRIORITIES)
            ))
            return
        
        priority = str(value).strip().upper()
        if priority not in self.VALID_PRIORITIES:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field="Priority",
                message="Invalid priority value",
                current_value=str(value),
                suggested_value=", ".join(self.VALID_PRIORITIES)
            ))
    
    def _validate_test_category(self, row: int, col: str, value):
        """
        CRITICAL: Validate Test_Category field - this determines which function to call!
        This is the most important validation as wrong categories lead to wrong test execution.
        """
        if not value:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field="Test_Category",
                message="Test_Category is REQUIRED - determines which test function to execute",
                current_value="",
                suggested_value=", ".join(self.VALID_TEST_CATEGORIES.keys())
            ))
            return
        
        category = str(value).strip().upper()
        if category not in self.VALID_TEST_CATEGORIES:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field="Test_Category",
                message="INVALID Test_Category - No corresponding test function exists!",
                current_value=str(value),
                suggested_value=", ".join(self.VALID_TEST_CATEGORIES.keys())
            ))
        else:
            # Add info about which function will be called
            function_name = self.VALID_TEST_CATEGORIES[category]
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.INFO,
                row=row,
                column=col,
                field="Test_Category",
                message=f"Will execute function: {function_name}",
                current_value=category,
                suggested_value=f"✓ Maps to {function_name}()"
            ))
    
    def _validate_expected_result(self, row: int, col: str, value):
        """Validate Expected_Result field"""
        if not value:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                row=row,
                column=col,
                field="Expected_Result",
                message="Expected_Result not specified, defaulting to PASS",
                current_value="",
                suggested_value=", ".join(self.VALID_EXPECTED_RESULTS)
            ))
            return
        
        result = str(value).strip().upper()
        if result not in self.VALID_EXPECTED_RESULTS:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field="Expected_Result",
                message="Invalid expected result",
                current_value=str(value),
                suggested_value=", ".join(self.VALID_EXPECTED_RESULTS)
            ))
    
    def _validate_timeout_seconds(self, row: int, col: str, value):
        """Validate Timeout_Seconds field"""
        if value is None:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                row=row,
                column=col,
                field="Timeout_Seconds",
                message="Timeout not specified, defaulting to 60 seconds",
                current_value="",
                suggested_value="60"
            ))
            return
        
        try:
            timeout = int(value)
            if timeout < self.MIN_TIMEOUT_SECONDS:
                self.validation_messages.append(ValidationMessage(
                    severity=ValidationSeverity.WARNING,
                    row=row,
                    column=col,
                    field="Timeout_Seconds",
                    message=f"Timeout too low (minimum {self.MIN_TIMEOUT_SECONDS}s recommended)",
                    current_value=str(value),
                    suggested_value=str(self.MIN_TIMEOUT_SECONDS)
                ))
            elif timeout > self.MAX_TIMEOUT_SECONDS:
                self.validation_messages.append(ValidationMessage(
                    severity=ValidationSeverity.WARNING,
                    row=row,
                    column=col,
                    field="Timeout_Seconds",
                    message=f"Timeout very high (maximum {self.MAX_TIMEOUT_SECONDS}s recommended)",
                    current_value=str(value),
                    suggested_value=str(self.MAX_TIMEOUT_SECONDS)
                ))
        except (ValueError, TypeError):
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                row=row,
                column=col,
                field="Timeout_Seconds",
                message="Timeout must be a valid number",
                current_value=str(value),
                suggested_value="60"
            ))
    
    def _validate_description(self, row: int, col: str, value):
        """Validate Description field"""
        if value and len(str(value)) > self.MAX_DESCRIPTION_LENGTH:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                row=row,
                column=col,
                field="Description",
                message=f"Description too long (max {self.MAX_DESCRIPTION_LENGTH} chars)",
                current_value=f"{len(str(value))} characters",
                suggested_value=f"Shorten to {self.MAX_DESCRIPTION_LENGTH} chars"
            ))
    
    def _validate_prerequisites(self, row: int, col: str, value):
        """Validate Prerequisites field"""
        if value and len(str(value)) > self.MAX_PREREQUISITES_LENGTH:
            self.validation_messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                row=row,
                column=col,
                field="Prerequisites",
                message=f"Prerequisites too long (max {self.MAX_PREREQUISITES_LENGTH} chars)",
                current_value=f"{len(str(value))} characters",
                suggested_value=f"Shorten to {self.MAX_PREREQUISITES_LENGTH} chars"
            ))
    
    def _validate_tags(self, row: int, col: str, value):
        """Validate Tags field"""
        if not value:
            return
        
        tags_str = str(value).strip()
        if tags_str:
            # Check for valid tag format (comma-separated, no spaces in individual tags)
            tags = [tag.strip() for tag in tags_str.split(',')]
            for tag in tags:
                if ' ' in tag:
                    self.validation_messages.append(ValidationMessage(
                        severity=ValidationSeverity.WARNING,
                        row=row,
                        column=col,
                        field="Tags",
                        message="Tags should not contain spaces",
                        current_value=tag,
                        suggested_value=tag.replace(' ', '_')
                    ))
    
    def _validate_duplicates(self, ws):
        """Check for duplicate test case IDs"""
        test_ids = []
        row_num = 2
        
        while True:
            test_id = ws.cell(row=row_num, column=2).value
            if not test_id:
                break
            test_ids.append((str(test_id).strip(), row_num))
            row_num += 1
        
        # Find duplicates
        seen = set()
        for test_id, row in test_ids:
            if test_id in seen:
                self.validation_messages.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    row=row,
                    column="B",
                    field="Test_Case_ID",
                    message="Duplicate Test_Case_ID found",
                    current_value=test_id,
                    suggested_value="Use unique identifier"
                ))
            seen.add(test_id)
    
    def _validate_business_rules(self, ws):
        """Validate business rules and relationships"""
        # Example: Performance tests should have higher timeouts
        row_num = 2
        while True:
            test_id = ws.cell(row=row_num, column=2).value
            if not test_id:
                break
            
            category = ws.cell(row=row_num, column=7).value  # Test_Category
            timeout = ws.cell(row=row_num, column=9).value   # Timeout_Seconds
            
            if category and str(category).strip().upper() == "PERFORMANCE":
                try:
                    timeout_val = int(timeout) if timeout else 60
                    if timeout_val < 30:
                        self.validation_messages.append(ValidationMessage(
                            severity=ValidationSeverity.WARNING,
                            row=row_num,
                            column="I",
                            field="Timeout_Seconds",
                            message="Performance tests should have higher timeout (30s+ recommended)",
                            current_value=str(timeout),
                            suggested_value="60"
                        ))
                except (ValueError, TypeError):
                    pass
            
            row_num += 1
    
    def _get_column_letter(self, col_num: int) -> str:
        """Convert column number to Excel column letter"""
        result = ""
        while col_num > 0:
            col_num -= 1
            result = chr(65 + col_num % 26) + result
            col_num //= 26
        return result
    
    def generate_validation_report(self) -> str:
        """Generate a formatted validation report"""
        if not self.validation_messages:
            return "✅ All validations passed! Excel file is ready for test execution."
        
        report = []
        report.append("📋 EXCEL VALIDATION REPORT")
        report.append("=" * 50)
        
        # Count by severity
        errors = [msg for msg in self.validation_messages if msg.severity == ValidationSeverity.ERROR]
        warnings = [msg for msg in self.validation_messages if msg.severity == ValidationSeverity.WARNING]
        infos = [msg for msg in self.validation_messages if msg.severity == ValidationSeverity.INFO]
        
        report.append(f"📊 Summary: {len(errors)} Errors, {len(warnings)} Warnings, {len(infos)} Info")
        report.append("")
        
        if errors:
            report.append("❌ ERRORS (Must be fixed before execution):")
            report.append("-" * 45)
            for msg in errors:
                report.append(f"Row {msg.row}, Column {msg.column} ({msg.field}):")
                report.append(f"   Problem: {msg.message}")
                report.append(f"   Current: '{msg.current_value}'")
                if msg.suggested_value:
                    report.append(f"   Suggested: {msg.suggested_value}")
                report.append("")
        
        if warnings:
            report.append("⚠️  WARNINGS (Recommended to fix):")
            report.append("-" * 35)
            for msg in warnings:
                report.append(f"Row {msg.row}, Column {msg.column} ({msg.field}):")
                report.append(f"   {msg.message}")
                report.append(f"   Current: '{msg.current_value}'")
                if msg.suggested_value:
                    report.append(f"   Suggested: {msg.suggested_value}")
                report.append("")
        
        if infos:
            report.append("ℹ️  INFORMATION:")
            report.append("-" * 15)
            for msg in infos:
                report.append(f"Row {msg.row}: {msg.message}")
            report.append("")
        
        return "\n".join(report)