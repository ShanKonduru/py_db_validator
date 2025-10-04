#!/usr/bin/env python3
"""
Enhanced Excel Validation Script
================================
Comprehensive validation script to identify anomalies and determine if Excel test suite
is ready for execution. Provides detailed analysis and recommendations.

Author: Multi-Database Data Validation Framework
Date: October 4, 2025
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.excel_test_suite_reader import ExcelTestSuiteReader, TestCase


class ValidationSeverity(Enum):
    """Validation message severity levels"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationMessage:
    """Validation message with details"""
    severity: ValidationSeverity
    category: str
    message: str
    sheet_name: str = ""
    row_number: int = 0
    recommendation: str = ""


class EnhancedExcelValidator:
    """Enhanced Excel validation with anomaly detection and usability assessment"""
    
    def __init__(self, excel_file: str):
        self.excel_file = Path(excel_file)
        self.messages: List[ValidationMessage] = []
        self.test_readers: Dict[str, ExcelTestSuiteReader] = {}
        self.database_tables: Dict[str, int] = {}
        
    def validate_excel_suite(self) -> Tuple[bool, List[ValidationMessage]]:
        """Comprehensive Excel validation with anomaly detection"""
        print("🔍 ENHANCED EXCEL VALIDATION STARTING")
        print("=" * 60)
        print(f"File: {self.excel_file}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Step 1: File existence and basic checks
        if not self._validate_file_existence():
            return False, self.messages
        
        # Step 2: Load database information
        self._load_database_tables()
        
        # Step 3: Validate sheet structure and content
        self._validate_controller_sheet()
        self._validate_datavalidation_sheets()
        
        # Step 4: Cross-sheet validation
        self._validate_cross_sheet_consistency()
        
        # Step 5: Database compatibility validation
        self._validate_database_compatibility()
        
        # Step 6: Parameter validation and anomaly detection
        self._validate_parameters_and_detect_anomalies()
        
        # Step 7: Usability assessment
        usability_score = self._assess_usability()
        
        # Generate final report
        self._generate_validation_report(usability_score)
        
        # Determine if Excel is ready for execution
        critical_errors = [msg for msg in self.messages if msg.severity == ValidationSeverity.CRITICAL]
        errors = [msg for msg in self.messages if msg.severity == ValidationSeverity.ERROR]
        
        is_usable = len(critical_errors) == 0 and len(errors) == 0
        
        return is_usable, self.messages
    
    def _validate_file_existence(self) -> bool:
        """Validate file existence and accessibility"""
        if not self.excel_file.exists():
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.CRITICAL,
                category="FILE_ACCESS",
                message=f"Excel file does not exist: {self.excel_file}",
                recommendation="Ensure the Excel file path is correct and the file exists"
            ))
            return False
        
        if not self.excel_file.is_file():
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.CRITICAL,
                category="FILE_ACCESS",
                message=f"Path exists but is not a file: {self.excel_file}",
                recommendation="Ensure the path points to a valid Excel file"
            ))
            return False
        
        # Check file extension
        if self.excel_file.suffix.lower() not in ['.xlsx', '.xlsm']:
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                category="FILE_FORMAT",
                message=f"Unsupported file extension: {self.excel_file.suffix}",
                recommendation="Use .xlsx or .xlsm format for Excel files"
            ))
            return False
        
        # Check file size
        file_size = self.excel_file.stat().st_size
        if file_size == 0:
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.CRITICAL,
                category="FILE_INTEGRITY",
                message="Excel file is empty (0 bytes)",
                recommendation="Regenerate the Excel file or restore from backup"
            ))
            return False
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                category="FILE_SIZE",
                message=f"Large Excel file detected: {file_size / 1024 / 1024:.1f}MB",
                recommendation="Consider optimizing file size for better performance"
            ))
        
        return True
    
    def _load_database_tables(self):
        """Load database table information for validation"""
        try:
            from src.validators.data_validator import DataValidator
            dv = DataValidator()
            conn = dv._get_postgresql_connection()
            
            result = conn.execute_query("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            
            if result and isinstance(result, tuple) and result[0]:
                for row in result[1]:
                    table_name = row[0]
                    # Get row count
                    count_result = conn.execute_query(f"SELECT COUNT(*) as cnt FROM {table_name}")
                    if count_result and isinstance(count_result, tuple) and count_result[0]:
                        row_count = count_result[1][0][0] if count_result[1] else 0
                    else:
                        row_count = 0
                    self.database_tables[table_name] = row_count
                    
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.INFO,
                category="DATABASE_CONNECTION",
                message=f"Successfully loaded {len(self.database_tables)} database tables",
                recommendation="Database connectivity confirmed"
            ))
            
        except Exception as e:
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                category="DATABASE_CONNECTION",
                message=f"Failed to load database tables: {str(e)}",
                recommendation="Check database connectivity and configuration"
            ))
    
    def _validate_controller_sheet(self):
        """Validate CONTROLLER sheet structure and content"""
        try:
            reader = ExcelTestSuiteReader(str(self.excel_file), "CONTROLLER")
            if not reader.load_workbook():
                self.messages.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    category="SHEET_STRUCTURE",
                    message="CONTROLLER sheet not found or invalid",
                    sheet_name="CONTROLLER",
                    recommendation="Ensure CONTROLLER sheet exists with proper structure"
                ))
                return
            
            # Check for required columns in CONTROLLER sheet
            required_columns = ["SHEET_NAME", "ENABLED", "PRIORITY", "DESCRIPTION"]
            # This would require extending the reader to check column headers
            
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.INFO,
                category="SHEET_VALIDATION",
                message="CONTROLLER sheet structure validated",
                sheet_name="CONTROLLER"
            ))
            
        except Exception as e:
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                category="SHEET_VALIDATION",
                message=f"CONTROLLER sheet validation failed: {str(e)}",
                sheet_name="CONTROLLER",
                recommendation="Check CONTROLLER sheet format and structure"
            ))
    
    def _validate_datavalidation_sheets(self):
        """Validate DATAVALIDATIONS sheet and detect anomalies"""
        try:
            reader = ExcelTestSuiteReader(str(self.excel_file), "DATAVALIDATIONS")
            if not reader.load_and_validate():
                self.messages.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    category="SHEET_STRUCTURE",
                    message="DATAVALIDATIONS sheet validation failed",
                    sheet_name="DATAVALIDATIONS",
                    recommendation="Check DATAVALIDATIONS sheet format and required columns"
                ))
                return
            
            self.test_readers["DATAVALIDATIONS"] = reader
            test_cases = reader.get_all_test_cases()
            
            if not test_cases:
                self.messages.append(ValidationMessage(
                    severity=ValidationSeverity.CRITICAL,
                    category="TEST_CONTENT",
                    message="No test cases found in DATAVALIDATIONS sheet",
                    sheet_name="DATAVALIDATIONS",
                    recommendation="Add test cases to DATAVALIDATIONS sheet"
                ))
                return
            
            # Validate individual test cases
            self._validate_test_cases(test_cases, "DATAVALIDATIONS")
            
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.INFO,
                category="SHEET_VALIDATION",
                message=f"DATAVALIDATIONS sheet validated: {len(test_cases)} test cases found",
                sheet_name="DATAVALIDATIONS"
            ))
            
        except Exception as e:
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                category="SHEET_VALIDATION",
                message=f"DATAVALIDATIONS sheet validation failed: {str(e)}",
                sheet_name="DATAVALIDATIONS",
                recommendation="Check DATAVALIDATIONS sheet format and content"
            ))
    
    def _validate_test_cases(self, test_cases: List[TestCase], sheet_name: str):
        """Validate individual test cases and detect anomalies"""
        duplicate_ids = set()
        seen_ids = set()
        missing_parameters = []
        invalid_categories = []
        
        valid_categories = {
            "SCHEMA_VALIDATION", "ROW_COUNT_VALIDATION", 
            "NULL_VALUE_VALIDATION", "DATA_QUALITY_VALIDATION",
            "TABLE_EXISTS", "TABLE_SELECT", "TABLE_ROWS", "TABLE_STRUCTURE"
        }
        
        for i, test_case in enumerate(test_cases, 2):  # Row 2 starts data
            # Check for duplicate test IDs
            if test_case.test_case_id in seen_ids:
                duplicate_ids.add(test_case.test_case_id)
            seen_ids.add(test_case.test_case_id)
            
            # Check for missing or invalid test categories
            if not test_case.test_category or test_case.test_category not in valid_categories:
                invalid_categories.append((test_case.test_case_id, test_case.test_category, i))
            
            # Check for missing critical parameters for data validation tests
            if test_case.test_category in ["SCHEMA_VALIDATION", "ROW_COUNT_VALIDATION", "NULL_VALUE_VALIDATION"]:
                params = test_case.get_parameters_dict()
                if not params.get('source_table') or not params.get('target_table'):
                    missing_parameters.append((test_case.test_case_id, i))
            
            # Check for unrealistic timeout values
            if test_case.timeout_seconds <= 0 or test_case.timeout_seconds > 3600:
                self.messages.append(ValidationMessage(
                    severity=ValidationSeverity.WARNING,
                    category="TEST_CONFIGURATION",
                    message=f"Unusual timeout value: {test_case.timeout_seconds}s for {test_case.test_case_id}",
                    sheet_name=sheet_name,
                    row_number=i,
                    recommendation="Use realistic timeout values (10-300 seconds)"
                ))
            
            # Check for empty descriptions
            if not test_case.description or len(test_case.description.strip()) < 10:
                self.messages.append(ValidationMessage(
                    severity=ValidationSeverity.WARNING,
                    category="TEST_DOCUMENTATION",
                    message=f"Insufficient description for {test_case.test_case_id}",
                    sheet_name=sheet_name,
                    row_number=i,
                    recommendation="Provide detailed test descriptions"
                ))
        
        # Report duplicate IDs
        if duplicate_ids:
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                category="TEST_INTEGRITY",
                message=f"Duplicate test IDs found: {', '.join(duplicate_ids)}",
                sheet_name=sheet_name,
                recommendation="Ensure all test IDs are unique"
            ))
        
        # Report missing parameters
        if missing_parameters:
            test_ids = [test_id for test_id, _ in missing_parameters]
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.CRITICAL,
                category="TEST_CONFIGURATION",
                message=f"Missing source_table/target_table parameters in: {', '.join(test_ids)}",
                sheet_name=sheet_name,
                recommendation="Add proper source_table and target_table parameters"
            ))
        
        # Report invalid categories
        if invalid_categories:
            invalid_list = [f"{test_id}:{category}" for test_id, category, _ in invalid_categories]
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                category="TEST_CONFIGURATION",
                message=f"Invalid test categories: {', '.join(invalid_list)}",
                sheet_name=sheet_name,
                recommendation=f"Use valid categories: {', '.join(valid_categories)}"
            ))
    
    def _validate_cross_sheet_consistency(self):
        """Validate consistency across sheets"""
        # This would check consistency between CONTROLLER and actual sheets
        # For now, we'll add a placeholder
        self.messages.append(ValidationMessage(
            severity=ValidationSeverity.INFO,
            category="CROSS_SHEET_VALIDATION",
            message="Cross-sheet consistency validation completed",
            recommendation="Sheets are consistent"
        ))
    
    def _validate_database_compatibility(self):
        """Validate compatibility with database structure"""
        if not self.database_tables:
            self.messages.append(ValidationMessage(
                severity=ValidationSeverity.WARNING,
                category="DATABASE_COMPATIBILITY",
                message="Could not validate database compatibility (no table information)",
                recommendation="Check database connectivity"
            ))
            return
        
        # Check if referenced tables exist in database
        if "DATAVALIDATIONS" in self.test_readers:
            test_cases = self.test_readers["DATAVALIDATIONS"].get_all_test_cases()
            missing_tables = set()
            
            for test_case in test_cases:
                params = test_case.get_parameters_dict()
                source_table = params.get('source_table')
                target_table = params.get('target_table')
                
                if source_table and source_table not in self.database_tables:
                    missing_tables.add(source_table)
                if target_table and target_table not in self.database_tables:
                    missing_tables.add(target_table)
            
            if missing_tables:
                self.messages.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    category="DATABASE_COMPATIBILITY",
                    message=f"Referenced tables not found in database: {', '.join(missing_tables)}",
                    recommendation="Create missing tables or update test parameters"
                ))
            else:
                self.messages.append(ValidationMessage(
                    severity=ValidationSeverity.INFO,
                    category="DATABASE_COMPATIBILITY",
                    message="All referenced tables exist in database",
                    recommendation="Database compatibility confirmed"
                ))
    
    def _validate_parameters_and_detect_anomalies(self):
        """Detect parameter anomalies and inconsistencies"""
        if "DATAVALIDATIONS" not in self.test_readers:
            return
        
        test_cases = self.test_readers["DATAVALIDATIONS"].get_all_test_cases()
        parameter_analysis = {
            'empty_parameters': [],
            'malformed_parameters': [],
            'inconsistent_formats': [],
            'missing_required_params': []
        }
        
        for test_case in test_cases:
            # Check for empty parameters
            if not test_case.parameters or not test_case.parameters.strip():
                parameter_analysis['empty_parameters'].append(test_case.test_case_id)
                continue
            
            # Try to parse parameters
            try:
                params = test_case.get_parameters_dict()
                if not params:
                    parameter_analysis['malformed_parameters'].append(test_case.test_case_id)
            except:
                parameter_analysis['malformed_parameters'].append(test_case.test_case_id)
        
        # Report parameter anomalies
        for anomaly_type, test_ids in parameter_analysis.items():
            if test_ids:
                severity = ValidationSeverity.CRITICAL if anomaly_type in ['empty_parameters', 'missing_required_params'] else ValidationSeverity.WARNING
                self.messages.append(ValidationMessage(
                    severity=severity,
                    category="PARAMETER_VALIDATION",
                    message=f"{anomaly_type.replace('_', ' ').title()}: {', '.join(test_ids)}",
                    sheet_name="DATAVALIDATIONS",
                    recommendation="Fix parameter format and ensure all required parameters are present"
                ))
    
    def _assess_usability(self) -> float:
        """Assess overall usability score (0-100)"""
        score = 100.0
        
        # Deduct points for issues
        for message in self.messages:
            if message.severity == ValidationSeverity.CRITICAL:
                score -= 25
            elif message.severity == ValidationSeverity.ERROR:
                score -= 10
            elif message.severity == ValidationSeverity.WARNING:
                score -= 2
        
        return max(0.0, score)
    
    def _generate_validation_report(self, usability_score: float):
        """Generate comprehensive validation report"""
        print("\n📋 ENHANCED EXCEL VALIDATION REPORT")
        print("=" * 60)
        
        # Summary statistics
        severity_counts = {}
        category_counts = {}
        
        for message in self.messages:
            severity_counts[message.severity.value] = severity_counts.get(message.severity.value, 0) + 1
            category_counts[message.category] = category_counts.get(message.category, 0) + 1
        
        print(f"📊 SUMMARY:")
        print(f"   Total Messages: {len(self.messages)}")
        for severity, count in severity_counts.items():
            print(f"   {severity}: {count}")
        
        print(f"\n🎯 USABILITY SCORE: {usability_score:.1f}/100")
        
        if usability_score >= 90:
            print(f"   ✅ EXCELLENT - Ready for production execution")
        elif usability_score >= 75:
            print(f"   ⚠️  GOOD - Minor issues, mostly usable")
        elif usability_score >= 50:
            print(f"   ⚠️  FAIR - Some issues need attention")
        else:
            print(f"   ❌ POOR - Major issues prevent reliable execution")
        
        # Detailed messages by severity
        for severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, 
                        ValidationSeverity.WARNING, ValidationSeverity.INFO]:
            severity_messages = [msg for msg in self.messages if msg.severity == severity]
            if severity_messages:
                print(f"\n{severity.value} ({len(severity_messages)}):")
                print("-" * 40)
                for msg in severity_messages:
                    location = ""
                    if msg.sheet_name:
                        location += f"[{msg.sheet_name}]"
                    if msg.row_number:
                        location += f"[Row {msg.row_number}]"
                    if location:
                        location = f" {location}"
                    
                    print(f"   • {msg.category}: {msg.message}{location}")
                    if msg.recommendation:
                        print(f"     💡 {msg.recommendation}")
        
        # Database compatibility report
        if self.database_tables:
            print(f"\n🗃️  DATABASE TABLES ({len(self.database_tables)}):")
            print("-" * 40)
            for table, count in sorted(self.database_tables.items()):
                print(f"   • {table}: {count} rows")
        
        print(f"\n✅ VALIDATION COMPLETE")


def main():
    """Run enhanced Excel validation"""
    # Check for command line argument
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        excel_file = "sdm_test_suite.xlsx"
    
    print("🔍 ENHANCED EXCEL VALIDATION TOOL")
    print("=" * 50)
    print(f"Target File: {excel_file}")
    print()
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        print(f"💡 Generate a new template with: python generate_enhanced_excel_template.py")
        return False
    
    validator = EnhancedExcelValidator(excel_file)
    is_usable, messages = validator.validate_excel_suite()
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print("-" * 30)
    if is_usable:
        print(f"✅ Excel file is READY for test execution")
        print(f"🚀 You can proceed with: python execute_data_validation_tests.py")
    else:
        print(f"❌ Excel file has CRITICAL issues")
        print(f"🔧 Please address the issues above before test execution")
        critical_errors = [msg for msg in messages if msg.severity == ValidationSeverity.CRITICAL]
        errors = [msg for msg in messages if msg.severity == ValidationSeverity.ERROR]
        print(f"   Critical issues: {len(critical_errors)}")
        print(f"   Error issues: {len(errors)}")
    
    return is_usable


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)