"""
Excel Template Generator with Data Validation Dropdowns

This module creates Excel templates with data validation dropdowns to prevent
user input errors and ensure data consistency.
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.validation.excel_validator import ExcelTestSuiteValidator


class ExcelTemplateGenerator:
    """Generates Excel templates with data validation dropdowns"""
    
    def __init__(self):
        """Initialize the template generator"""
        self.validator = ExcelTestSuiteValidator()
        
        # Define dropdown options for each column
        self.dropdown_options = {
            "Enable": ["TRUE", "FALSE"],
            "Priority": list(self.validator.VALID_PRIORITIES),
            "Test_Category": list(self.validator.VALID_TEST_CATEGORIES.keys()),
            "Expected_Result": list(self.validator.VALID_EXPECTED_RESULTS),
            "Environment_Name": list(self.validator.VALID_ENVIRONMENTS),
            "Application_Name": list(self.validator.VALID_APPLICATIONS),
        }
        
        # Column definitions with their properties
        self.column_definitions = [
            {"name": "Enable", "width": 12, "dropdown": True, "required": True},
            {"name": "Test_Case_ID", "width": 18, "dropdown": False, "required": True},
            {"name": "Test_Case_Name", "width": 30, "dropdown": False, "required": True},
            {"name": "Application_Name", "width": 18, "dropdown": True, "required": True},
            {"name": "Environment_Name", "width": 18, "dropdown": True, "required": True},
            {"name": "Priority", "width": 12, "dropdown": True, "required": True},
            {"name": "Test_Category", "width": 18, "dropdown": True, "required": True},
            {"name": "Expected_Result", "width": 16, "dropdown": True, "required": True},
            {"name": "Timeout_Seconds", "width": 16, "dropdown": False, "required": True},
            {"name": "Description", "width": 40, "dropdown": False, "required": False},
            {"name": "Prerequisites", "width": 30, "dropdown": False, "required": False},
            {"name": "Tags", "width": 20, "dropdown": False, "required": False},
        ]
    
    def create_template(self, filename: str = "test_suite_template.xlsx", 
                       include_sample_data: bool = True) -> bool:
        """
        Create Excel template with data validation dropdowns
        
        Args:
            filename: Output Excel file name
            include_sample_data: Whether to include sample test data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create workbook and worksheet
            wb = Workbook()
            ws = wb.active
            ws.title = "SMOKE"
            
            # Set up headers with styling
            self._create_headers(ws)
            
            # Add data validation dropdowns
            self._add_data_validations(ws)
            
            # Add sample data if requested
            if include_sample_data:
                self._add_sample_data(ws)
            
            # Create instructions worksheet
            self._create_instructions_worksheet(wb)
            
            # Create validation reference worksheet
            self._create_reference_worksheet(wb)
            
            # Save the file
            wb.save(filename)
            print(f"✅ Excel template created: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating Excel template: {e}")
            return False
    
    def _create_headers(self, ws):
        """Create and style headers"""
        # Header styling
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Add headers
        for col_idx, col_def in enumerate(self.column_definitions, 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = col_def["name"]
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border
            
            # Set column width
            column_letter = get_column_letter(col_idx)
            ws.column_dimensions[column_letter].width = col_def["width"]
        
        # Freeze header row
        ws.freeze_panes = "A2"
    
    def _add_data_validations(self, ws):
        """Add data validation dropdowns to appropriate columns"""
        # Define the range for data validation (rows 2 to 1000)
        start_row = 2
        end_row = 1000
        
        for col_idx, col_def in enumerate(self.column_definitions, 1):
            column_letter = get_column_letter(col_idx)
            
            if col_def["dropdown"] and col_def["name"] in self.dropdown_options:
                # Create dropdown validation
                options = self.dropdown_options[col_def["name"]]
                formula = f'"{",".join(options)}"'
                
                # Create data validation
                dv = DataValidation(
                    type="list",
                    formula1=formula,
                    allow_blank=not col_def["required"]
                )
                
                # Set error messages
                dv.error = f"Invalid value for {col_def['name']}"
                dv.errorTitle = "Invalid Input"
                dv.prompt = f"Please select from: {', '.join(options)}"
                dv.promptTitle = f"Select {col_def['name']}"
                
                # Apply to range
                range_string = f"{column_letter}{start_row}:{column_letter}{end_row}"
                dv.add(range_string)
                ws.add_data_validation(dv)
            
            elif col_def["name"] == "Timeout_Seconds":
                # Numeric validation for timeout
                dv = DataValidation(
                    type="whole",
                    operator="between",
                    formula1=5,
                    formula2=3600,
                    allow_blank=False
                )
                dv.error = "Timeout must be between 5 and 3600 seconds"
                dv.errorTitle = "Invalid Timeout"
                dv.prompt = "Enter timeout in seconds (5-3600)"
                dv.promptTitle = "Timeout Seconds"
                
                range_string = f"{column_letter}{start_row}:{column_letter}{end_row}"
                dv.add(range_string)
                ws.add_data_validation(dv)
    
    def _add_sample_data(self, ws):
        """Add sample test data"""
        sample_data = [
            [
                "TRUE", "SMOKE_PG_001", "Environment Setup Validation", "DUMMY", "DEV", 
                "HIGH", "SETUP", "PASS", 30, 
                "Validates that environment and configuration are properly set up",
                "Configuration file or environment variables must be available",
                "smoke,db,setup"
            ],
            [
                "TRUE", "SMOKE_PG_002", "Configuration Availability", "DUMMY", "DEV",
                "HIGH", "CONFIGURATION", "PASS", 30,
                "Checks if database configuration is available and accessible",
                "Environment setup must be completed",
                "smoke,db,config"
            ],
            [
                "TRUE", "SMOKE_PG_003", "Credentials Validation", "DUMMY", "DEV",
                "HIGH", "SECURITY", "PASS", 30,
                "Validates database credentials and authentication",
                "Valid credentials must be configured",
                "smoke,db,security"
            ],
            [
                "TRUE", "SMOKE_PG_004", "Database Connectivity", "DUMMY", "DEV",
                "HIGH", "CONNECTION", "PASS", 60,
                "Tests basic database connection functionality",
                "Database server must be running and accessible",
                "smoke,db,connection"
            ],
            [
                "TRUE", "SMOKE_PG_005", "Basic Database Queries", "DUMMY", "DEV",
                "HIGH", "QUERIES", "PASS", 60,
                "Tests basic SQL query execution capabilities",
                "Database connection must be established",
                "smoke,db,queries"
            ],
            [
                "FALSE", "SMOKE_PG_006", "Connection Performance", "DUMMY", "DEV",
                "MEDIUM", "PERFORMANCE", "PASS", 30,
                "Tests database connection performance metrics",
                "Database must be optimized for performance testing",
                "smoke,db,performance"
            ]
        ]
        
        # Add sample data rows
        for row_idx, row_data in enumerate(sample_data, 2):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.value = value
                
                # Add subtle styling to data rows
                if row_idx % 2 == 0:
                    cell.fill = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")
    
    def _create_instructions_worksheet(self, wb):
        """Create instructions worksheet"""
        ws = wb.create_sheet("INSTRUCTIONS")
        
        # Title
        ws['A1'] = "📋 Excel Test Suite Instructions"
        ws['A1'].font = Font(size=16, bold=True, color="366092")
        
        instructions = [
            "",
            "🎯 HOW TO USE THIS TEMPLATE:",
            "",
            "1. Use the 'SMOKE' worksheet to define your test cases",
            "2. Fill in each row with test case details",
            "3. Use DROPDOWNS for columns with validation (they have blue headers)",
            "4. Required fields are marked with * in the reference sheet",
            "",
            "📝 IMPORTANT NOTES:",
            "",
            "• Test_Case_ID must be unique (e.g., SMOKE_PG_001, SMOKE_PG_002)",
            "• Test_Category determines which test function will be executed",
            "• Use dropdowns to prevent data entry errors",
            "• Timeout_Seconds must be between 5-3600 seconds",
            "• Tags should be comma-separated without spaces",
            "",
            "🔍 VALIDATION:",
            "",
            "• Run 'python validate_excel.py' to check for errors",
            "• Fix all validation errors before running tests",
            "• Use 'python validate_excel.py --fix-suggestions' for help",
            "",
            "🚀 EXECUTION:",
            "",
            "• Run 'python excel_test_driver.py --reports' to execute tests",
            "• Use filters like --priority HIGH or --category CONNECTION",
            "• Generated reports will be saved in test_reports/ directory",
            "",
            "💡 TIPS:",
            "",
            "• Copy existing rows and modify instead of typing from scratch",
            "• Always validate before sharing the file with others",
            "• Check the REFERENCE sheet for valid values and mappings",
            "",
        ]
        
        for i, instruction in enumerate(instructions, 2):
            ws[f'A{i}'] = instruction
            if instruction.startswith(('🎯', '📝', '🔍', '🚀', '💡')):
                ws[f'A{i}'].font = Font(bold=True, color="D63384")
        
        # Set column width
        ws.column_dimensions['A'].width = 80
    
    def _create_reference_worksheet(self, wb):
        """Create reference worksheet with valid values"""
        ws = wb.create_sheet("REFERENCE")
        
        # Title
        ws['A1'] = "📚 Test Category Reference & Valid Values"
        ws['A1'].font = Font(size=16, bold=True, color="366092")
        
        # Test Category Mapping Table
        ws['A3'] = "🎯 TEST CATEGORY → FUNCTION MAPPING:"
        ws['A3'].font = Font(size=14, bold=True, color="D63384")
        
        # Headers for mapping table
        headers = ["Test_Category", "Python Function", "Status", "Description"]
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=5, column=col)
            cell.value = header
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        
        # Mapping data
        mappings = [
            ["SETUP", "test_environment_setup()", "✅ Available", "Validates environment setup"],
            ["CONFIGURATION", "test_dummy_config_availability()", "✅ Available", "Checks configuration availability"],
            ["SECURITY", "test_environment_credentials()", "✅ Available", "Validates credentials"],
            ["CONNECTION", "test_postgresql_connection()", "✅ Available", "Tests database connection"],
            ["QUERIES", "test_postgresql_basic_queries()", "✅ Available", "Tests SQL query execution"],
            ["PERFORMANCE", "test_postgresql_connection_performance()", "✅ Available", "Tests connection performance"],
            ["COMPATIBILITY", "test_compatibility()", "⚠️ Not implemented", "Backwards compatibility testing"],
            ["MONITORING", "test_monitoring()", "🔜 Future", "System monitoring tests"],
            ["BACKUP", "test_backup_restore()", "🔜 Future", "Backup and restore tests"],
        ]
        
        for row, mapping in enumerate(mappings, 6):
            for col, value in enumerate(mapping, 1):
                ws.cell(row=row, column=col, value=value)
        
        # Valid Values Section
        ws['A16'] = "📊 VALID VALUES FOR DROPDOWN FIELDS:"
        ws['A16'].font = Font(size=14, bold=True, color="D63384")
        
        row = 18
        for field, values in self.dropdown_options.items():
            ws[f'A{row}'] = f"{field}:"
            ws[f'A{row}'].font = Font(bold=True)
            ws[f'B{row}'] = ", ".join(values)
            row += 1
        
        # Field Requirements
        ws[f'A{row + 2}'] = "⚠️ FIELD REQUIREMENTS:"
        ws[f'A{row + 2}'].font = Font(size=14, bold=True, color="D63384")
        
        requirements = [
            "Test_Case_ID: Must be unique, format: SMOKE_PG_001",
            "Test_Case_Name: Required, descriptive name",
            "Timeout_Seconds: Number between 5-3600",
            "Description: Max 500 characters",
            "Prerequisites: Max 1000 characters",
            "Tags: Comma-separated, no spaces in individual tags",
        ]
        
        for i, req in enumerate(requirements, row + 4):
            ws[f'A{i}'] = f"• {req}"
        
        # Set column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 20
        ws.column_dimensions['D'].width = 35
    
    def update_existing_file(self, filename: str) -> bool:
        """
        Update an existing Excel file to add data validation dropdowns
        
        Args:
            filename: Path to existing Excel file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from openpyxl import load_workbook
            
            # Load existing workbook
            wb = load_workbook(filename)
            
            if "SMOKE" not in wb.sheetnames:
                print(f"❌ Worksheet 'SMOKE' not found in {filename}")
                return False
            
            ws = wb["SMOKE"]
            
            # Add data validations to existing file
            self._add_data_validations(ws)
            
            # Create additional worksheets if they don't exist
            if "INSTRUCTIONS" not in wb.sheetnames:
                self._create_instructions_worksheet(wb)
            
            if "REFERENCE" not in wb.sheetnames:
                self._create_reference_worksheet(wb)
            
            # Save updated file
            backup_name = f"{Path(filename).stem}_backup{Path(filename).suffix}"
            wb.save(backup_name)
            wb.save(filename)
            
            print(f"✅ Updated {filename} with data validation dropdowns")
            print(f"📄 Backup saved as: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating Excel file: {e}")
            return False


def main():
    """Main function for testing"""
    generator = ExcelTemplateGenerator()
    
    # Create template with sample data
    print("Creating Excel template with data validation dropdowns...")
    success = generator.create_template("test_suite_template_with_dropdowns.xlsx", True)
    
    if success:
        print("\n🎉 Template created successfully!")
        print("\n📋 What was created:")
        print("• SMOKE worksheet with data validation dropdowns")
        print("• INSTRUCTIONS worksheet with usage guide")
        print("• REFERENCE worksheet with valid values and function mappings")
        print("\n💡 Next steps:")
        print("1. Open the Excel file and try the dropdowns")
        print("2. Copy/modify the sample data for your tests")
        print("3. Validate with: python validate_excel.py test_suite_template_with_dropdowns.xlsx")
        print("4. Execute with: python excel_test_driver.py --excel-file test_suite_template_with_dropdowns.xlsx --reports")


if __name__ == "__main__":
    main()