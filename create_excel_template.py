#!/usr/bin/env python
"""
Excel Template Generator CLI Tool

Creates Excel test suite templates with data validation dropdowns to prevent user input errors.

Usage:
    python create_excel_template.py                    # Create template with sample data
    python create_excel_template.py --no-samples       # Create empty template
    python create_excel_template.py --output my_template.xlsx
    python create_excel_template.py --update existing_file.xlsx
"""
import sys
import argparse
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.utils.excel_template_generator import ExcelTemplateGenerator
except ImportError as e:
    print(f"❌ Error importing template generator: {e}")
    print("   Make sure you're running from the project root directory")
    sys.exit(1)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Create Excel test suite templates with data validation dropdowns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_excel_template.py                              # Create template with sample data
  python create_excel_template.py --no-samples                 # Create empty template
  python create_excel_template.py --output my_template.xlsx    # Custom output filename
  python create_excel_template.py --update existing.xlsx       # Add dropdowns to existing file
  
Features:
  • Data validation dropdowns for critical fields
  • Sample test data to get started quickly
  • Instructions worksheet with usage guide
  • Reference worksheet with valid values and function mappings
  • Professional styling and formatting
        """
    )
    
    parser.add_argument(
        "--output", "-o",
        default="test_suite_template_with_dropdowns.xlsx",
        help="Output Excel file name (default: test_suite_template_with_dropdowns.xlsx)"
    )
    
    parser.add_argument(
        "--no-samples", "-n",
        action="store_true",
        help="Create empty template without sample data"
    )
    
    parser.add_argument(
        "--update", "-u",
        help="Update existing Excel file with data validation dropdowns"
    )
    
    parser.add_argument(
        "--show-dropdowns", "-s",
        action="store_true",
        help="Show what dropdown options will be available"
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = ExcelTemplateGenerator()
    
    # Show dropdown options if requested
    if args.show_dropdowns:
        print("🔽 DROPDOWN OPTIONS THAT WILL BE AVAILABLE:")
        print("=" * 50)
        for field, options in generator.dropdown_options.items():
            print(f"\n📋 {field}:")
            for option in options:
                print(f"   • {option}")
        
        print(f"\n🎯 TEST_CATEGORY → FUNCTION MAPPING:")
        print("=" * 40)
        for category, function in generator.validator.VALID_TEST_CATEGORIES.items():
            status = "✅" if category in ["SETUP", "CONFIGURATION", "SECURITY", "CONNECTION", "QUERIES", "PERFORMANCE"] else "⚠️"
            print(f"   {status} {category:<15} → {function}")
        
        return 0
    
    # Update existing file
    if args.update:
        if not Path(args.update).exists():
            print(f"❌ Error: File '{args.update}' not found!")
            return 1
        
        print(f"🔄 Updating existing file: {args.update}")
        success = generator.update_existing_file(args.update)
        
        if success:
            print(f"\n✅ Successfully updated {args.update} with data validation dropdowns!")
            print(f"📄 Backup created: {Path(args.update).stem}_backup{Path(args.update).suffix}")
            print("\n💡 What was added:")
            print("   • Data validation dropdowns for critical fields")
            print("   • INSTRUCTIONS worksheet (if not present)")
            print("   • REFERENCE worksheet with valid values (if not present)")
        else:
            print(f"\n❌ Failed to update {args.update}")
            return 1
        
        return 0
    
    # Create new template
    print(f"📊 Creating Excel template: {args.output}")
    
    include_samples = not args.no_samples
    if include_samples:
        print("📝 Including sample test data")
    else:
        print("📝 Creating empty template")
    
    success = generator.create_template(args.output, include_samples)
    
    if success:
        print(f"\n🎉 Excel template created successfully: {args.output}")
        print("\n📋 What was created:")
        print("   • SMOKE worksheet with data validation dropdowns")
        print("   • INSTRUCTIONS worksheet with detailed usage guide")
        print("   • REFERENCE worksheet with valid values and function mappings")
        
        print(f"\n🔽 Dropdown fields available:")
        for field in generator.dropdown_options.keys():
            print(f"   • {field}")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Open {args.output} in Excel")
        print(f"   2. Try clicking on dropdown fields (Enable, Priority, Test_Category, etc.)")
        print(f"   3. Add your test cases using the dropdowns")
        print(f"   4. Validate: python validate_excel.py {args.output}")
        print(f"   5. Execute: python excel_test_driver.py --excel-file {args.output} --reports")
        
        return 0
    else:
        print(f"\n❌ Failed to create Excel template")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Template generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)