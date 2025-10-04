#!/usr/bin/env python3
"""
Workspace Cleanup Utility
=========================
Analyzes and organizes files in the py_db_validator workspace
to clean up Excel workbooks, markdown files, and other temporary files.

Author: Multi-Database Data Validation Framework
Date: October 4, 2025
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def analyze_workspace():
    """Analyze current workspace and categorize files"""
    
    print("🧹 WORKSPACE CLEANUP ANALYSIS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    root_path = Path(".")
    
    # File categories
    categories = {
        "excel_workbooks": [],
        "markdown_docs": [],
        "python_scripts": [],
        "temp_files": [],
        "important_files": [],
        "directories": []
    }
    
    # Define important files to keep
    important_files = {
        # Main Excel templates
        "enhanced_unified_sdm_test_suite.xlsx",  # Latest and best
        "sdm_test_suite.xlsx",  # Original reference
        
        # Core documentation
        "README.md",
        "application_requirements.md", 
        "SETUP.md",
        
        # Core Python files
        "main.py",
        "requirements.txt",
        "pytest.ini",
        
        # Key execution scripts
        "execute_enhanced_data_validation_tests.py",
        "execute_unified_smoke_tests.py",
        "enhanced_excel_validator.py",
        "create_enhanced_unified_excel_template.py"
    }
    
    # Scan workspace
    for item in root_path.iterdir():
        if item.is_file():
            filename = item.name
            
            if filename in important_files:
                categories["important_files"].append(filename)
            elif filename.endswith('.xlsx'):
                categories["excel_workbooks"].append(filename)
            elif filename.endswith('.md'):
                categories["markdown_docs"].append(filename)
            elif filename.endswith('.py'):
                categories["python_scripts"].append(filename)
            elif any(filename.startswith(prefix) for prefix in ['temp_', 'test_', 'debug_', 'check_', 'analyze_']):
                categories["temp_files"].append(filename)
        elif item.is_dir() and not item.name.startswith('.'):
            categories["directories"].append(item.name)
    
    # Print analysis
    print("📊 WORKSPACE ANALYSIS:")
    print("-" * 40)
    
    for category, files in categories.items():
        if files:
            print(f"\n🔹 {category.upper().replace('_', ' ')} ({len(files)}):")
            for file in sorted(files):
                print(f"   • {file}")
    
    return categories

def create_cleanup_recommendations(categories):
    """Generate cleanup recommendations"""
    
    print("\n")
    print("🎯 CLEANUP RECOMMENDATIONS:")
    print("=" * 60)
    
    # Excel workbooks cleanup
    excel_files = categories["excel_workbooks"]
    if excel_files:
        print("\n📁 EXCEL WORKBOOKS CLEANUP:")
        print("-" * 30)
        
        # Keep these
        keep_excel = [
            "enhanced_unified_sdm_test_suite.xlsx",  # Latest unified template
            "sdm_test_suite.xlsx"  # Original reference
        ]
        
        # Archive these
        archive_excel = [f for f in excel_files if f not in keep_excel]
        
        print("✅ KEEP (2 files):")
        for file in keep_excel:
            if file in excel_files:
                print(f"   • {file} - Current working template")
        
        if archive_excel:
            print(f"\n📦 ARCHIVE ({len(archive_excel)} files):")
            for file in archive_excel:
                print(f"   • {file}")
    
    # Markdown files cleanup
    md_files = categories["markdown_docs"]
    if md_files:
        print(f"\n📄 MARKDOWN FILES CLEANUP:")
        print("-" * 30)
        
        # Keep essential docs
        keep_md = [
            "README.md",
            "application_requirements.md",
            "SETUP.md"
        ]
        
        # Archive status/summary docs
        archive_md = [f for f in md_files if f not in keep_md]
        
        print("✅ KEEP (3 files):")
        for file in keep_md:
            if file in md_files:
                print(f"   • {file}")
        
        if archive_md:
            print(f"\n📦 ARCHIVE ({len(archive_md)} files):")
            for file in archive_md[:10]:  # Show first 10
                print(f"   • {file}")
            if len(archive_md) > 10:
                print(f"   • ... and {len(archive_md) - 10} more")
    
    # Python scripts cleanup
    py_files = categories["python_scripts"]
    if py_files:
        print(f"\n🐍 PYTHON SCRIPTS CLEANUP:")
        print("-" * 30)
        
        # Keep core scripts
        keep_py = [
            "main.py",
            "execute_enhanced_data_validation_tests.py",
            "execute_unified_smoke_tests.py", 
            "enhanced_excel_validator.py",
            "create_enhanced_unified_excel_template.py"
        ]
        
        # Archive utility/debug scripts
        archive_py = [f for f in py_files if f not in keep_py and any(f.startswith(prefix) for prefix in ['debug_', 'check_', 'analyze_', 'test_', 'temp_', 'examine_', 'read_'])]
        
        print(f"✅ KEEP ({len([f for f in keep_py if f in py_files])} core files)")
        print(f"📦 ARCHIVE ({len(archive_py)} utility/debug files)")

def create_cleanup_script():
    """Create a cleanup script to organize files"""
    
    cleanup_script = '''#!/usr/bin/env python3
"""
Execute Workspace Cleanup
"""

import os
import shutil
from pathlib import Path

def create_directories():
    """Create archive directories"""
    dirs = ["archive", "archive/excel", "archive/docs", "archive/scripts"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Created directory: {dir_name}")

def move_excel_files():
    """Move old Excel files to archive"""
    excel_keep = ["enhanced_unified_sdm_test_suite.xlsx", "sdm_test_suite.xlsx"]
    
    for file in Path(".").glob("*.xlsx"):
        if file.name not in excel_keep:
            target = Path("archive/excel") / file.name
            shutil.move(str(file), str(target))
            print(f"Moved: {file.name} -> archive/excel/")

def move_markdown_files():
    """Move status/summary markdown files to archive"""
    md_keep = ["README.md", "application_requirements.md", "SETUP.md"]
    
    for file in Path(".").glob("*.md"):
        if file.name not in md_keep:
            target = Path("archive/docs") / file.name
            shutil.move(str(file), str(target))
            print(f"Moved: {file.name} -> archive/docs/")

def move_utility_scripts():
    """Move utility/debug scripts to archive"""
    py_keep = [
        "main.py",
        "execute_enhanced_data_validation_tests.py", 
        "execute_unified_smoke_tests.py",
        "enhanced_excel_validator.py",
        "create_enhanced_unified_excel_template.py"
    ]
    
    prefixes = ["debug_", "check_", "analyze_", "test_", "temp_", "examine_", "read_"]
    
    for file in Path(".").glob("*.py"):
        if (file.name not in py_keep and 
            any(file.name.startswith(prefix) for prefix in prefixes)):
            target = Path("archive/scripts") / file.name
            shutil.move(str(file), str(target))
            print(f"Moved: {file.name} -> archive/scripts/")

def main():
    print("🧹 EXECUTING WORKSPACE CLEANUP")
    print("=" * 50)
    
    create_directories()
    print()
    
    print("📁 Moving Excel files...")
    move_excel_files()
    print()
    
    print("📄 Moving markdown files...")
    move_markdown_files()
    print()
    
    print("🐍 Moving utility scripts...")
    move_utility_scripts()
    print()
    
    print("✅ CLEANUP COMPLETE!")
    print("\\nWorkspace now contains:")
    print("   • Core working files in root directory")
    print("   • Archived files in archive/ subdirectories")

if __name__ == "__main__":
    main()
'''
    
    with open("cleanup_workspace.py", "w", encoding="utf-8") as f:
        f.write(cleanup_script)
    
    print("\n🔧 CLEANUP EXECUTION:")
    print("-" * 30)
    print("Created cleanup_workspace.py script")
    print("\nTo execute cleanup:")
    print("   python cleanup_workspace.py")

def main():
    """Main execution"""
    categories = analyze_workspace()
    create_cleanup_recommendations(categories)
    create_cleanup_script()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("   • Analyzed workspace files")
    print("   • Generated cleanup recommendations") 
    print("   • Created cleanup_workspace.py script")
    print("   • Ready to organize files into archive directories")

if __name__ == "__main__":
    main()