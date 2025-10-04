#!/usr/bin/env python3
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
    print("\nWorkspace now contains:")
    print("   • Core working files in root directory")
    print("   • Archived files in archive/ subdirectories")

if __name__ == "__main__":
    main()
