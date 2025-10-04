#!/bin/bash

# ============================================================
# COMPREHENSIVE TEST SUITE RUNNER - UNIX/LINUX SHELL SCRIPT
# ============================================================
# This script runs all enabled tests from the unified Excel workbook
# Usage: ./run_all_tests.sh

echo ""
echo "============================================================"
echo "COMPREHENSIVE TEST SUITE RUNNER"
echo "============================================================"
echo "Starting comprehensive test execution..."
echo "Excel File: enhanced_unified_sdm_test_suite.xlsx"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python and try again"
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "Using Python command: $PYTHON_CMD"

# Check if the Excel file exists
if [ ! -f "enhanced_unified_sdm_test_suite.xlsx" ]; then
    echo "ERROR: enhanced_unified_sdm_test_suite.xlsx not found"
    echo "Please ensure the Excel file is in the current directory"
    exit 1
fi

# Check if the test runner exists
if [ ! -f "run_all_enabled_tests.py" ]; then
    echo "ERROR: run_all_enabled_tests.py not found"
    echo "Please ensure the test runner script is in the current directory"
    exit 1
fi

# Run the comprehensive test suite
echo "Running comprehensive test suite..."
echo ""
$PYTHON_CMD run_all_enabled_tests.py enhanced_unified_sdm_test_suite.xlsx

# Check the exit code
exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo ""
    echo "============================================================"
    echo "TEST EXECUTION COMPLETED WITH ISSUES"
    echo "============================================================"
    echo "Some tests may have failed or been skipped."
    echo "Review the detailed output above for more information."
    echo "Exit code: $exit_code"
else
    echo ""
    echo "============================================================"
    echo "TEST EXECUTION COMPLETED SUCCESSFULLY"
    echo "============================================================"
    echo "All enabled tests passed successfully."
fi

echo ""
echo "Test execution finished."
exit $exit_code